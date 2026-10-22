"""SPQP metrics (OS §9) — Squad, Plan, Process, Performance, in that causal
order (Danaher 4P). Input metrics have single owners (agent roles); outputs are
reported, never "managed". Every metric carries a floor; breaches flag the
weekly sheet (Amazon WBR exceptions-only).

A principle without a metric+cadence is banned from the OS (Amazon M8) — this
module is the enforcement point: `register()` refuses metrics without owner
and cadence.
"""
from __future__ import annotations

import json
from pathlib import Path

import config
import ledger

METRICS_FILE = config.RUNTIME_DIR / "metrics.json"


class MetricError(RuntimeError):
    pass


def _db() -> dict:
    if METRICS_FILE.exists():
        return json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    return {"registry": {}, "observations": []}


def _save(db: dict) -> None:
    METRICS_FILE.write_text(json.dumps(db, indent=1, sort_keys=True), encoding="utf-8")


def register(company: str, key: str, layer: str, owner_role: str,
             floor: float | None = None, unit: str = "", cadence: str = "weekly") -> dict:
    """layer ∈ S|P|Q|P (Squad, Plan, Quality-process, Performance).
    Owner + cadence mandatory (OS §9 ban on ownerless principles)."""
    if layer not in ("S", "P", "Q", "F"):
        raise MetricError("layer must be S/P/Q/F (Squad/Plan/Process/perFormance)")
    if not owner_role or not cadence:
        raise MetricError("metric without owner+cadence is banned (Amazon M8)")
    db = _db()
    db["registry"][f"{company}:{key}"] = {
        "company": company, "key": key, "layer": layer, "owner_role": owner_role,
        "floor": floor, "unit": unit, "cadence": cadence,
        "registered_at": config.stamp()}
    _save(db)
    return db["registry"][f"{company}:{key}"]


def observe(company: str, key: str, value: float, source: str = "",
            asof: str | None = None) -> dict:
    db = _db()
    rid = f"{company}:{key}"
    if rid not in db["registry"]:
        raise MetricError(f"unregistered metric {rid} — register it first (no shadow metrics)")
    reg = db["registry"][rid]
    breach = reg["floor"] is not None and value < reg["floor"]
    obs = {"id": rid, "value": value, "source": source, "asof": asof or config.today(),
           "at": config.stamp(), "breach": breach}
    db["observations"].append(obs)
    _save(db)
    if breach:
        ledger.event("metric_breach", rid, {"value": value, "floor": reg["floor"]})
    return obs


def latest(company: str, key: str):
    db = _db()
    rid = f"{company}:{key}"
    vals = [o for o in db["observations"] if o["id"] == rid]
    return vals[-1] if vals else None


def scorecard(company: str, c: dict) -> dict:
    """The SPQP scorecard for one company (OS §9). Performance layer pulls the
    contribution P&L (Constellation scoreboard); S/P/Q pull registered inputs."""
    import capital
    db = _db()
    rows = {"S": [], "P": [], "Q": [], "F": []}
    for rid, reg in db["registry"].items():
        if reg["company"] != company:
            continue
        obs = latest(company, reg["key"])
        rows[reg["layer"]].append({
            "metric": reg["key"], "owner": reg["owner_role"],
            "value": obs["value"] if obs else None,
            "floor": reg["floor"],
            "breach": bool(obs and obs["breach"]),
            "asof": obs["asof"] if obs else None})
    pnl = capital.contribution_pnl(company, c)
    return {"company": company, "spqp": rows, "performance_pnl": pnl,
            "user_paid_value_first": pnl["revenue"] > 0,
            "generated_at": config.stamp()}


def portfolio_health(companies: list[dict]) -> dict:
    """Group-level health metrics (OS §9): kill-rate, funnel conversion,
    fortress months, FCF per company-month, build-slot utilization."""
    import capital
    kills = len(ledger.decisions(kind="KILL_WIN"))
    launches = len(ledger.decisions(kind="promoted"))
    live = [c for c in companies if c["stage"] in (2, 3, 4)]
    total_contrib = sum(c.get("contribution_chf", 0.0) for c in live)
    months = max(1, len({c.get("stage_started", "")[:7] for c in live})) if live else 1
    return {
        "kill_wins_recorded": kills,
        "kill_rate_healthy": kills > 0 or all(c["stage"] >= 3 for c in companies),
        "promotions": launches,
        "funnel_conversion": round(launches / max(1, len(companies)), 3),
        "fortress_months": round(capital.fortress_months(), 2),
        "fortress_ok": capital.fortress_ok(),
        "fcf_per_company_month": round(total_contrib / months, 2) if live else 0.0,
        "live_companies": len(live),
        "generated_at": config.stamp(),
    }
