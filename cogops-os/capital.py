"""Capital doctrine (OS §4, §12) — Berkshire ladder + Constellation scoreboard
+ the Swiss compliance guard (invariant I10, condensed from JARVIS
swiss_compliance_guard.py) + the profit sweep (JARVIS cashflow_bridge DNA).

Invariant I1 (zero holding debt) is enforced STRUCTURALLY: this module has no
borrowing API at all. There is no code path to violate it.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

import config
import ledger

WALLET_FILE = config.RUNTIME_DIR / "capital.json"


# ------------------------------------------------------------------ wallet --
def _wallet() -> dict:
    if WALLET_FILE.exists():
        return json.loads(WALLET_FILE.read_text(encoding="utf-8"))
    w = {"cash_chf": float(config.MONTHLY_FIXED_COSTS_CHF * config.FORTRESS_MONTHS),
         "portfolio_value_chf": 0.0, "pillar3a_paid_ytd_chf": 0.0,
         "fixed_costs_monthly_chf": config.MONTHLY_FIXED_COSTS_CHF}
    _save_wallet(w)
    return w


def _save_wallet(w: dict) -> None:
    WALLET_FILE.write_text(json.dumps(w, indent=1, sort_keys=True), encoding="utf-8")


def fortress_months() -> float:
    w = _wallet()
    fc = max(w["fixed_costs_monthly_chf"], 1e-9)
    return w["cash_chf"] / fc


def fortress_ok() -> bool:
    return fortress_months() >= config.FORTRESS_MONTHS - 1e-9


def deposit(chf: float, source: str) -> dict:
    w = _wallet()
    if chf <= 0:
        raise ValueError("deposits are positive; costs go through spend()")
    w["cash_chf"] = round(w["cash_chf"] + chf, 2)
    _save_wallet(w)
    ledger.event("capital_deposit", "group", {"chf": chf, "source": source})
    return w


def spend(chf: float, what: str) -> dict:
    """Group-level spend (platform costs, envelopes funding). Fortress is NOT
    spendable: blocking below the 6-month floor is the point of I2."""
    w = _wallet()
    floor = config.FORTRESS_MONTHS * w["fixed_costs_monthly_chf"]
    if w["cash_chf"] - chf < floor - 1e-9:
        raise CapitalBlocked(
            f"spend CHF {chf:.2f} would breach the cash fortress "
            f"({w['cash_chf']:.2f} < {floor:.2f}+{chf:.2f}) — invariant I2")
    w["cash_chf"] = round(w["cash_chf"] - chf, 2)
    _save_wallet(w)
    ledger.event("capital_spend", "group", {"chf": chf, "what": what})
    return w


class CapitalBlocked(RuntimeError):
    pass


# ------------------------------------------------------ deployment ladder --
def ladder_recommend(surplus_chf: float, opportunities: list[dict]) -> list[dict]:
    """Berkshire's deployment ladder as an ordered recommendation engine.
    `opportunities`: [{"kind": reinvest|launch|marketable|acquire, "id", "chf",
    "expected_return", "evidence_ok": bool}]
    Rungs (OS §4): fortress top-up → reinvest gated subsidiaries → launch stage-
    gated new ones → marketable sweep → (Phase-2 dormant) acquisitions.
    Never forces deployment: unallocated surplus stays cash — that IS a result."""
    w = _wallet()
    plan, remaining = [], surplus_chf
    # rung 0: fortress top-up first, always
    deficit = max(0.0, config.FORTRESS_MONTHS * w["fixed_costs_monthly_chf"] - w["cash_chf"])
    if deficit > 0:
        amt = min(deficit, remaining)
        plan.append({"rung": 0, "kind": "fortress_topup", "chf": round(amt, 2),
                     "why": "invariant I2: 6-month fortress before anything"})
        remaining -= amt
    def _take(rung, kind, opp):
        nonlocal remaining
        amt = min(opp["chf"], remaining)
        if amt <= 0:
            return
        plan.append({"rung": rung, "kind": kind, "id": opp["id"], "chf": round(amt, 2),
                     "why": opp.get("why", ""), "expected_return": opp.get("expected_return")})
        remaining -= amt
    ok = [o for o in opportunities if o.get("evidence_ok")]
    for o in sorted([x for x in ok if x["kind"] == "reinvest"],
                    key=lambda x: -x.get("expected_return", 0)):
        _take(1, "reinvest", o)
    for o in sorted([x for x in ok if x["kind"] == "launch"],
                    key=lambda x: -x.get("expected_return", 0)):
        _take(2, "launch", o)                       # build-slot cap applied by caller
    for o in [x for x in ok if x["kind"] == "marketable"]:
        _take(3, "marketable_sweep", o)
    for o in [x for x in ok if x["kind"] == "acquire"]:
        o = {**o, "why": (o.get("why", "") + " [PHASE-2 DOCTRINE DORMANT — activate by DR]").strip()}
        _take(4, "acquisition", o)
    if remaining > 0.005:
        plan.append({"rung": 9, "kind": "hold_cash", "chf": round(remaining, 2),
                     "why": "never force deployment (Berkshire M3)"})
    return plan


# ------------------------------------------------------------- sweep (§12) --
import os
PILLAR_3A_ANNUAL_CAP_CHF = float(os.environ.get("PILLAR_3A_ANNUAL_CAP_CHF", "7258.0"))


def monthly_sweep(net_profit_chf: float, primary_ticker_price_chf: float,
                  period: str) -> dict:
    """30% profit sweep → Pillar 3a (cap-aware) + guarded ETF DCA.
    JARVIS cashflow_bridge + ibkr_dca_engine logic, condensed: same routing,
    same guard, fractional orders, one-cent floor, no ceiling."""
    if net_profit_chf <= 0:
        return {"period": period, "routed_chf": 0.0,
                "note": "net ≤ 0 — bootstrap month: NOTHING routed (zero-capital discipline)"}
    sweep = round(net_profit_chf * config.SWEEP_PROFIT_SHARE, 2)
    cap_left = max(0.0, PILLAR_3A_ANNUAL_CAP_CHF - _wallet()["pillar3a_paid_ytd_chf"])
    p3a = round(min(sweep * 0.40, cap_left), 2)
    ibkr = round(sweep - p3a, 2)
    order = None
    if ibkr >= config.MIN_ORDER_CHF:
        order = guard_dca_order(ibkr, primary_ticker_price_chf)
    w = _wallet()
    w["pillar3a_paid_ytd_chf"] = round(w["pillar3a_paid_ytd_chf"] + p3a, 2)
    if order and order["ok"]:
        w["portfolio_value_chf"] = round(w["portfolio_value_chf"] + order["notional_chf"], 2)
    _save_wallet(w)
    ledger.event("sweep", period, {"net": net_profit_chf, "sweep": sweep,
                                   "pillar3a": p3a, "ibkr": ibkr,
                                   "order_ok": bool(order and order["ok"])})
    return {"period": period, "net_profit_chf": net_profit_chf, "sweep_chf": sweep,
            "pillar3a_chf": p3a, "ibkr_chf": ibkr, "order": order}


# --------------------------------- Swiss private-investor guard (I10, §4) ----
FILLS_FILE = config.RUNTIME_DIR / "investment_fills.json"


def _fills() -> dict:
    if FILLS_FILE.exists():
        return json.loads(FILLS_FILE.read_text(encoding="utf-8"))
    return {"fills": [], "lots": []}


def _save_fills(f: dict) -> None:
    FILLS_FILE.write_text(json.dumps(f, indent=1, sort_keys=True), encoding="utf-8")


@dataclass
class GuardReport:
    ok: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: dict = field(default_factory=dict)


def guard_check_order(order: dict, portfolio_value_chf: float) -> GuardReport:
    """Condensed JARVIS guard, fix 6c7429a semantics preserved exactly:
    no margin/derivatives/shorts; STK+CASH only; 180-day FIFO min holding on
    sells; trailing turnover ≤5x with FRESH-CAPITAL base (100k one-off passes,
    churn sells blocked); order-frequency cap."""
    v, info = [], {}
    if order.get("sec_type", "STK") != "STK":
        v.append("only plain STK (stocks/ETFs) allowed — derivatives hard-prohibited")
    if order.get("margin") or order.get("derivative") or order.get("short"):
        v.append("leverage/derivatives/shorts hard-prohibited (I10)")
    if order.get("side") not in ("BUY", "SELL"):
        v.append(f"side {order.get('side')} not allowed")
    notional = float(order.get("notional_chf", 0.0))
    if order.get("side") == "BUY" and notional < config.MIN_ORDER_CHF:
        v.append(f"notional below one-cent floor {config.MIN_ORDER_CHF}")
    f = _fills()
    month = config.today()[:7]
    month_orders = sum(1 for x in f["fills"] if x["date"].startswith(month))
    info["orders_this_month"] = month_orders + 1
    if month_orders + 1 > config.MAX_ORDERS_PER_MONTH:
        v.append(f"order #{month_orders + 1} exceeds MAX_ORDERS_PER_MONTH")
    year_ago = config.now() - 365 * 86400
    recent = [x for x in f["fills"] if x["ts"] >= year_ago]
    traded = sum(x["notional_chf"] for x in recent) + notional
    contributed = sum(x["notional_chf"] for x in recent if x["side"] == "BUY")
    if order.get("side") == "BUY":
        contributed += notional          # fresh capital raises the base (no maximum)
    base = max(portfolio_value_chf, contributed, 1.0)
    ratio = traded / base
    info["trailing_turnover_ratio"] = round(ratio, 3)
    if ratio > config.MAX_TURNOVER_RATIO:
        v.append(f"trailing turnover {ratio:.2f}x > {config.MAX_TURNOVER_RATIO}x ceiling "
                 f"(private-investor status)")
    if order.get("side") == "SELL":      # FIFO 180-day min holding
        remaining, youngest = float(order.get("qty", 0)), None
        for lot in f["lots"]:
            if lot["qty"] <= 1e-12:
                continue
            age_days = (config.now() - lot["opened_ts"]) / 86400
            if age_days < config.MIN_HOLDING_DAYS:
                youngest = age_days
            take = min(lot["qty"], remaining)
            remaining -= take
            if remaining <= 1e-12:
                break
        if remaining > 1e-12:
            v.append("sell qty exceeds FIFO lots")
        elif youngest is not None:
            v.append(f"lot younger than {config.MIN_HOLDING_DAYS}d "
                     f"({youngest:.0f}d) — min holding period")
    return GuardReport(ok=not v, violations=v, info=info)


def guard_dca_order(amount_chf: float, price_chf: float, ticker: str = "VWRL") -> dict:
    """Fractional-aware DCA sizing (JARVIS ibkr_dca_engine.build_order):
    whole shares when possible; below one share → fractional cash-qty order;
    floor one cent, NO ceiling."""
    if price_chf <= 0:
        return {"ok": False, "why": "no price"}
    qty = int(amount_chf // price_chf)
    fractional = False
    if qty <= 0 and amount_chf >= config.MIN_ORDER_CHF:
        qty = round(amount_chf / price_chf, 6)
        fractional = True
    notional = round(min(qty * price_chf, amount_chf), 2)
    order = {"side": "BUY", "sec_type": "STK", "ticker": ticker, "qty": qty,
             "fractional": fractional, "notional_chf": notional,
             "residual_chf": round(max(amount_chf - notional, 0.0), 2)}
    rep = guard_check_order(order, _wallet()["portfolio_value_chf"])
    order["ok"] = rep.ok
    order["guard"] = {"violations": rep.violations, "info": rep.info}
    if rep.ok:                          # record fill + lot (dry-run ledger)
        f = _fills()
        f["fills"].append({"side": "BUY", "ticker": ticker, "qty": qty,
                           "notional_chf": notional, "ts": config.now(),
                           "date": config.today()})
        f["lots"].append({"ticker": ticker, "qty": qty, "opened_ts": config.now(),
                          "opened_date": config.today()})
        _save_fills(f)
        ledger.event("guard_fill", ticker, {"qty": qty, "notional": notional,
                                            "fractional": fractional})
    return order


def contribution_pnl(slug: str, c: dict) -> dict:
    """Constellation scoreboard at company level: standalone contribution
    (revenue − direct spends − platform charges). No synergy credits (I5)."""
    contrib = round(c["revenue_chf"] - c["spent_chf"] - c["platform_charges_chf"], 2)
    c["contribution_chf"] = contrib
    return {"slug": slug, "revenue": c["revenue_chf"], "spent": c["spent_chf"],
            "platform_charges": c["platform_charges_chf"], "contribution": contrib,
            "recurring_share": (round(c.get("recurring_revenue_chf", 0.0) / c["revenue_chf"], 3)
                                if c["revenue_chf"] > 0 else None)}
