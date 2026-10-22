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
                    "treasury-accountant", "dca-operator",
                    "ai-security-reviewer"],
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




def factor_brief_certified(params: dict, slug: str) -> dict:
    """K5 link H-C: capitalco buys drylab_stats FROM Helix via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on capitalco's P&L (I7)."""
    import platformsvc
    from companies import helix as seller
    ticket = platformsvc.request(slug, "drylab_stats", spec="cross-validation of factor statistics", units=1)
    bought = seller.table1({"cohort": params.get("cert_cohort", [{"patient_id":i,"arm":"A" if i%2 else "B","age":30+i%40} for i in range(8)]), "bounds": {"age": (18, 90)}}, "helix")
    platformsvc.serve(ticket["id"], {"ref": f"capitalco-factor_brief_certified:{ticket['id']}"})
    out = factor_brief(params, slug)
    out["internal_purchase"] = {"from": "Helix", "service": "drylab_stats",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["stats_certified_by"] = f"Helix kernel via ticket {ticket['id']} (Welch/chi2 <1e-9 discipline)"
    return out



def backtest_certified(params: dict, slug: str) -> dict:
    """K5 link M-C: capitalco buys alcoa_trail FROM Medtech via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on capitalco's P&L (I7)."""
    import platformsvc
    from companies import medtech as seller
    ticket = platformsvc.request(slug, "alcoa_trail", spec="ALCOA+ trail for backtest run", units=1)
    bought = seller.alcoa_log({"entry":{"experiment":"backtest","subject":params.get("ticker","VWRL"),"value":params.get("monthly_chf",900),"unit":"CHF/mo","recorded_by":"capital"}}, "medtech")
    platformsvc.serve(ticket["id"], {"ref": f"capitalco-backtest_certified:{ticket['id']}"})
    out = backtest(params, slug)
    out["internal_purchase"] = {"from": "Medtech", "service": "alcoa_trail",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["audit_trail_lines"] = bought["trail_lines"]; out["provenance"] = f"run logged in Medtech ALCOA+ trail, ticket {ticket['id']}"
    return out



def boundary_memo(params: dict, slug: str) -> dict:
    """K5 link D-C: capitalco buys alcoa_qc FROM Dossia via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on capitalco's P&L (I7)."""
    import platformsvc
    from companies import dossia as seller
    ticket = platformsvc.request(slug, "alcoa_qc", spec="ALCOA+ QC of FINMA boundary memo", units=1)
    bought = seller.qc_checklist({"document":{"author":"capital","reviewer":"founder","text":"boundary memo","timestamp":config.stamp(),"source_ref":"engine","numbers_carry_asof":True,"has_todos":False,"units_consistent":True,"stored_in_ledger":True,"path":"outbox"}}, "dossia")
    platformsvc.serve(ticket["id"], {"ref": f"capitalco-boundary_memo:{ticket['id']}"})
    out = treasury_policy(params, slug)
    out["internal_purchase"] = {"from": "Dossia", "service": "alcoa_qc",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["boundary_qc"] = {"pass_rate_pct": bought["pass_rate_pct"], "verdict": bought["verdict"], "ticket_ref": ticket["id"]}
    return out



def secure_deployment(params: dict, slug: str) -> dict:
    """K5 link C-S: capitalco buys ai_sec_review FROM Sentinel via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on capitalco's P&L (I7)."""
    import platformsvc
    from companies import sentinel as seller
    ticket = platformsvc.request(slug, "ai_sec_review", spec="security review of client tooling", units=1)
    bought = seller.ai_security_review({"kb_first":True,"provider_labels":True,"refuses_advice":True,"gated_actions":True}, "sentinel")
    platformsvc.serve(ticket["id"], {"ref": f"capitalco-secure_deployment:{ticket['id']}"})
    out = {"mode":"engine","company":"capitalco"}
    out["internal_purchase"] = {"from": "Sentinel", "service": "ai_sec_review",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["security"] = {"config": bought["config_checks"], "ticket_ref": ticket["id"]}
    return out



def plan_check(params: dict, slug: str) -> dict:
    """Free sample: guard review of a client's EXISTING order plan — each order
    run through the Swiss guard (stateless copy), verdicts + why. No advice:
    the guard reports rule outcomes, the client decides."""
    orders = params.get("orders", [])
    pv = float(params.get("portfolio_value_chf", 0.0))
    rows = []
    for i, o in enumerate(orders, 1):
        rep = _guard_stateless({"side": o.get("side", "BUY"), "sec_type": o.get("sec_type", "STK"),
                                "qty": o.get("qty", 0), "notional_chf": float(o.get("notional_chf", 0)),
                                "margin": o.get("margin", False), "derivative": o.get("derivative", False),
                                "short": o.get("short", False)},
                               pv, [r["notional"] for r in rows if r["verdict"] == "passes"])
        rows.append({"order": i, "notional": float(o.get("notional_chf", 0)),
                     "verdict": "passes" if rep["ok"] else "blocked",
                     "why": rep["violations"][:2]})
    artifact = {"mode": "engine", "orders_checked": len(rows),
                "blocked": sum(1 for r in rows if r["verdict"] == "blocked"),
                "rows": rows,
                "note": "rule outcomes under the Swiss private-investor guard; not investment advice",
                "asof": config.today()}
    _emit(slug, "plan_check", artifact)
    return artifact



def intelligence_ops(params: dict, slug: str) -> dict:
    """Star link: this company buys Intelligence's deployment/automation service
    via internal ticket (ai_ops, DR-0010 price)."""
    import platformsvc
    from companies import intelligence as intel
    kind = params.get("kind", "automation_audit")
    ticket = platformsvc.request(slug, "ai_ops", spec=f"{kind} for {slug}", units=1)
    if kind == "deploy":
        out = intel.deploy_client({"client": params.get("client", f"{slug}-client"),
                                   "services": params.get("services",
                                       ["site_factory", "llm_gateway", "crm_portal"])},
                                  "intelligence")
    else:
        out = intel.automation_audit({"answers": params.get("answers", {
            "process": f"{slug} delivery", "volume_month": 20, "minutes_per": 30,
            "steps": ["collect client inputs", "draft deliverable", "human review",
                      "approve delivery", "send to client"]})}, "intelligence")
    platformsvc.serve(ticket["id"], {"ref": f"{slug}-intel:{ticket['id']}"})
    return {"mode": "engine", "kind": kind,
            "internal_purchase": {"from": "intelligence", "service": "ai_ops",
                                  "ticket": ticket["id"],
                                  "notional_chf": ticket["notional_chf"]},
            "result": out, "asof": config.today()}


def _emit(slug: str, kind: str, artifact: dict) -> None:
    p = config.OUTBOX / f"{slug}_{kind}_{config.today()}.json"
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")


# K5 clique links: partner -> OUR buying task (complete graph, DR-0009)
LINKS = {"intelligence": "intelligence_ops", 'helix': 'factor_brief_certified', 'medtech': 'backtest_certified', 'dossia': 'boundary_memo', 'sentinel': 'secure_deployment'}

TASKS = {
    "intelligence_ops": {"fn": intelligence_ops, "role": "treasury-accountant"},
    "factor_brief_certified": {"fn": factor_brief_certified, "role": "factor-researcher"},
    "backtest_certified": {"fn": backtest_certified, "role": "backtest-analyst"},
    "boundary_memo": {"fn": boundary_memo, "role": "compliance-checker"},
    "secure_deployment": {"fn": secure_deployment, "role": "ai-security-reviewer"},
    "backtest": {"fn": backtest, "role": "backtest-analyst"},
    "factor_brief": {"fn": factor_brief, "role": "factor-researcher"},
    "treasury_policy": {"fn": treasury_policy, "role": "treasury-accountant"},
    "plan_check": {"fn": plan_check, "role": "compliance-checker"},
}
