"""CogOps Capital — quantitative finance tools & research (OS §13; blueprint
co. 3; Swiss #4, gap 8.5). Seed: the JARVIS Investment Automaton. Engines:
guarded DCA backtest (deterministic, seeded, Swiss-guard-checked every order),
factor brief on supplied datasets, treasury-policy document generator.
Boundary: tools & research only — clients hold their own keys and approvals;
no custody, no advice, no fund (blueprint).
"""
from __future__ import annotations

import json
import math

import capital as core
import config
import ledger
import statsnr

META = {
    "name": "CogOps Capital",
    "dan": "Private investors get institutional discipline cheaply: guarded "
           "DCA engines, backtests and quant briefs — under their own keys.",
    "stage_at_v10": 3,
    "seed_assets": "JARVIS Investment Automaton (guard, sweep, DCA, gate)",
    "human_of_record": "client holds keys/approvals",
    "input_metrics": [
        {"key": "tool_users", "layer": "F", "owner": "treasury-accountant", "floor": 5},
        {"key": "aum_under_tooling_chf", "layer": "F", "owner": "sweep-planner", "floor": 1000},
        {"key": "guard_pass_rate_pct", "layer": "Q", "owner": "compliance-checker", "floor": 95},
    ],
    "squad_roles": ["backtest-analyst", "factor-researcher", "compliance-checker",
                    "treasury-accountant", "dca-operator"],
}


def backtest(params: dict, slug: str) -> dict:
    """Deterministic seeded DCA backtest: monthly amount over a price series;
    EVERY simulated order passes the Swiss guard (I10) before filling —
    compliance is inside the loop, not a report on top of it."""
    prices = params.get("prices", [])          # e.g. 120 monthly VWRL marks
    monthly = float(params.get("monthly_chf", 900))
    if len(prices) < 2:
        raise ValueError("need ≥2 price points")
    shares = 0.0
    invested = 0.0
    fills, blocks = [], []
    for i, p in enumerate(prices):
        p = float(p)
        qty_whole = int(monthly // p)
        qty = qty_whole if qty_whole > 0 else round(monthly / p, 6)
        fractional = qty_whole == 0
        notional = round(min(qty * p, monthly), 2)
        order = {"side": "BUY", "sec_type": "STK", "ticker": params.get("ticker", "VWRL"),
                 "qty": qty, "notional_chf": notional, "fractional": fractional}
        # guard against the running portfolio value (fresh-capital base rule)
        pv = shares * p
        rep = _guard_stateless(order, pv, [f["notional"] for f in fills])
        if rep["ok"]:
            shares += qty
            invested += notional
            fills.append({"month": i, "price": p, "qty": qty, "notional": notional,
                          "fractional": fractional})
        else:
            blocks.append({"month": i, "why": rep["violations"][0]})
    final_value = shares * float(prices[-1])
    ret = (final_value - invested) / invested if invested else 0.0
    artifact = {"mode": "engine", "months": len(prices), "fills": len(fills),
                "blocked_orders": blocks, "invested_chf": round(invested, 2),
                "shares": round(shares, 6),
                "final_value_chf": round(final_value, 2),
                "return_pct": round(100 * ret, 2),
                "determinism_hash": _hash(json.dumps(fills, sort_keys=True)),
                "asof": config.today(),
                "disclaimer": "research tooling; not financial advice; client keys & approvals"}
    _emit(slug, "backtest", artifact)
    return artifact


def _guard_stateless(order: dict, pv: float, prior_notionals: list[float]) -> dict:
    """Backtest-local guard (stateless): same invariants as core.guard_check_order
    without touching the live ledger — margin/derivatives/shorts/min-floor/turnover."""
    v = []
    if order.get("margin") or order.get("derivative") or order.get("short"):
        v.append("prohibited instrument")
    if order["notional_chf"] < config.MIN_ORDER_CHF:
        v.append("below one-cent floor")
    traded = sum(prior_notionals) + order["notional_chf"]
    contributed = sum(prior_notionals) + (order["notional_chf"]
                                          if order["side"] == "BUY" else 0.0)
    base = max(pv, contributed, 1.0)
    if traded / base > config.MAX_TURNOVER_RATIO:
        v.append(f"turnover {traded / base:.2f}x > {config.MAX_TURNOVER_RATIO}x")
    return {"ok": not v, "violations": v}


def factor_brief(params: dict, slug: str) -> dict:
    """Factor study on a supplied dataset: returns per-factor summary stats +
    Welch t between top/bottom terciles of the target. SciPy-free, validated
    stats (statsnr). Dataset comes from the client — no data exfiltration."""
    rows = params.get("rows", [])               # [{"factor": x, "target": y}, ...]
    factor = params.get("factor", "factor")
    target = params.get("target", "target")
    pts = [(float(r[factor]), float(r[target])) for r in rows
           if r.get(factor) is not None and r.get(target) is not None]
    if len(pts) < 6:
        raise ValueError("need ≥6 complete rows")
    pts.sort()
    k = len(pts) // 3
    lo = [t for _, t in pts[:k]]
    hi = [t for _, t in pts[-k:]]
    test = statsnr.welch_t(hi, lo)
    n = len(pts)
    mx = sum(p[1] for p in pts) / n
    sd = math.sqrt(sum((p[1] - mx) ** 2 for p in pts) / (n - 1))
    artifact = {"mode": "engine", "n": n, "tercile_split": k,
                "target_mean": round(mx, 4), "target_sd": round(sd, 4),
                "hi_vs_lo_tercile": {kk: (round(vv, 4) if isinstance(vv, float) else vv)
                                     for kk, vv in test.items()},
                "asof": config.today(),
                "disclaimer": "research brief on client-supplied data; not advice"}
    _emit(slug, "factor_brief", artifact)
    return artifact


def treasury_policy(params: dict, slug: str) -> dict:
    """Sweep-policy document for a small company: profit share, Pillar-3a
    routing, ETF DCA cadence, guard invariants — generated from live config so
    the document can never drift from the machine (CBS Ch.5)."""
    pol = {
        "sweep_share_of_net_profit": config.SWEEP_PROFIT_SHARE,
        "pillar3a": {"annual_cap_chf": core.PILLAR_3A_ANNUAL_CAP_CHF,
                     "routing": "40% of sweep, cap-aware, QR-reference manual execution"},
        "etf_dca": {"primary": "VWRL/VT-class", "cadence": "monthly",
                    "order_type": "LIMIT ≤ mid+25bps; fractional below one share",
                    "floor_chf": config.MIN_ORDER_CHF, "ceiling": None},
        "guard_invariants": ["no margin/leverage", "no derivatives", "no shorts",
                             "STK + CASH only", "180-day FIFO min holding",
                             "trailing turnover ≤ 5x (fresh-capital base)",
                             f"≤ {config.MAX_ORDERS_PER_MONTH} orders/month"],
        "human_gate": "every live order = Type-1/G2 approval; money movement = G3",
        "asof": config.today()}
    artifact = {"mode": "engine", "policy": pol}
    _emit(slug, "treasury_policy", artifact)
    return artifact


def _hash(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def _emit(slug: str, kind: str, artifact: dict) -> None:
    p = config.OUTBOX / f"{slug}_{kind}_{config.today()}.json"
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")


TASKS = {
    "backtest": {"fn": backtest, "role": "backtest-analyst"},
    "factor_brief": {"fn": factor_brief, "role": "factor-researcher"},
    "treasury_policy": {"fn": treasury_policy, "role": "treasury-accountant"},
}
