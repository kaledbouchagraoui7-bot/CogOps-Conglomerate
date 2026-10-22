"""Subsidiary lifecycle (OS §5) — the stage machine with envelopes, time-boxes,
evidence gates and kill-as-win. Lifecycle transitions are Type-1 (gated);
envelope spends are Type-2 inside caps, auto-escalate above them (OS §3).

Company state lives in runtime/companies/<slug>.json — single source of truth.
"""
from __future__ import annotations

import json
from pathlib import Path

import config
import gates
import ledger
import squad

STAGES = {0: "screen", 1: "validate", 2: "launch", 3: "operate",
          4: "scale", 5: "graduate/exit/kill"}


class CompanyNotFound(RuntimeError):
    pass


class EnvelopeExceeded(RuntimeError):
    pass


class FreezeActive(RuntimeError):
    """The nervous system's pain response: protective freeze on spending."""


def _path(slug: str) -> Path:
    return config.COMPANY_DIR / f"{slug}.json"


def load(slug: str) -> dict:
    p = _path(slug)
    if not p.exists():
        raise CompanyNotFound(slug)
    return json.loads(p.read_text(encoding="utf-8"))


def save(c: dict) -> None:
    _path(c["slug"]).write_text(json.dumps(c, indent=1, sort_keys=True), encoding="utf-8")


def all_slugs() -> list[str]:
    return sorted(p.stem for p in config.COMPANY_DIR.glob("*.json"))


def register(slug: str, name: str, dan: str, metrics: list[dict],
             squad_roles: list[str], stage: int = 0, seed_assets: str = "") -> dict:
    """Instantiate a company from data/company_defaults.json (Stage 0)."""
    c = {"slug": slug, "name": name, "dan": dan, "stage": stage,
         "stage_started": config.stamp(), "metrics": metrics,
         "squad_roles": squad_roles, "seed_assets": seed_assets,
         "spent_chf": 0.0, "revenue_chf": 0.0, "contribution_chf": 0.0,
         "platform_charges_chf": 0.0, "negative_months": 0,
         "evidence": [], "pd_objectives": [], "history": []}
    save(c)
    ledger.event("company_registered", slug, {"stage": stage})
    return c


# ------------------------------------------------------------- envelopes --
def envelope_of(c: dict) -> float | None:
    if c["stage"] == 3:
        return (config.STAGE_ENVELOPES_CHF[3]
                + config.STAGE3_REVENUE_REINVEST_PCT * c["revenue_chf"])
    if c["stage"] == 4:
        return config.STAGE4_CONTRIBUTION_REINVEST_PCT * max(c["contribution_chf"], 0.0)
    return config.STAGE_ENVELOPES_CHF.get(c["stage"], 0.0)


def spend(slug: str, amount_chf: float, what: str, by: str = "squad") -> dict:
    """Envelope accounting + delegated-cap escalation (OS §3/§5).
    amount ≤ cap  → Type-2, recorded.
    amount > cap  → auto Type-1: staged at the gate, NOT executed until approved.
    Envelope breach → hard stop (invariant: no silent top-ups, OS §4)."""
    fz = config.RUNTIME_DIR / "FREEZE.json"
    if fz.exists():
        import json as _j
        reasons = [r["reason"] for r in _j.loads(fz.read_text(encoding="utf-8")).get("reasons", [])]
        if reasons:
            raise FreezeActive(f"group FREEZE active {reasons} — spend refused; "
                               f"integrity freezes release only by founder keystroke "
                               f"(cogops.py unfreeze --confirm)")
    c = load(slug)
    if amount_chf <= 0:
        raise ValueError("spend must be positive")
    env = envelope_of(c)
    if env is not None and c["spent_chf"] + amount_chf > env + 1e-9:
        raise EnvelopeExceeded(
            f"{slug}: CHF {amount_chf:.2f} would breach stage-{c['stage']} envelope "
            f"({c['spent_chf']:.2f}/{env:.2f}) — replenishment is a Type-1 decision")
    cap = config.DELEGATED_CAPS_CHF.get(c["stage"], 100.0)
    # consume an already-APPROVED spend gate for this exact (amount, what)
    approved = next((g for g in gates.queue("APPROVED")
                     if g["company"] == slug and g["action"].get("kind") == "spend"
                     and g["action"].get("amount_chf") == amount_chf
                     and g["action"].get("what") == what), None)
    if approved:
        gates.mark_consumed(approved["id"])
        c["spent_chf"] = round(c["spent_chf"] + amount_chf, 2)
        save(c)
        ledger.event("spend", slug, {"chf": amount_chf, "what": what, "by": by,
                                     "via_gate": approved["id"]})
        return {"status": "executed", "spent_chf": c["spent_chf"],
                "via_gate": approved["id"]}
    action = {"kind": "spend", "amount_chf": amount_chf, "what": what,
              "above_cap": amount_chf > cap}
    status, res = gates.run_if_approved(slug, action, lambda: None, proposed_by=by)
    if status == "executed":
        c["spent_chf"] = round(c["spent_chf"] + amount_chf, 2)
        save(c)
        ledger.event("spend", slug, {"chf": amount_chf, "what": what, "by": by})
        return {"status": "executed", "spent_chf": c["spent_chf"]}
    return {"status": "gated", "gate": res}


# ------------------------------------------------------------- evidence ---
def log_evidence(slug: str, kind: str, value, source: str, asof: str | None = None) -> dict:
    """Evidence is the only currency that moves the lifecycle (OS §5, I4)."""
    c = load(slug)
    ev = {"kind": kind, "value": value, "source": source,
          "asof": asof or config.today(), "at": config.stamp()}
    c["evidence"].append(ev)
    save(c)
    ledger.event("evidence", slug, ev)
    return ev


def stage1_evidence_met(c: dict) -> tuple[bool, str]:
    ev = c["evidence"]
    if any(e["kind"] == "waitlist" and e["value"] >= config.STAGE1_EVIDENCE["waitlist_min"] for e in ev):
        return True, "waitlist ≥ 100"
    if any(e["kind"] == "preorders" and e["value"] >= config.STAGE1_EVIDENCE["preorders_min"] for e in ev):
        return True, "pre-orders ≥ 3"
    if any(e["kind"] == "pilot_paid_chf" and e["value"] >= config.STAGE1_EVIDENCE["pilot_paid_chf_min"] for e in ev):
        return True, "paid pilot ≥ CHF 200"
    return False, "no qualifying evidence yet"


# ------------------------------------------------------------ transitions --
def promote(slug: str, confirm: str = "") -> dict:
    """Stage promotion: evidence-checked, Type-1 gated (OS §5 exit criteria).
    Flow: first call stages the request and returns {status: gated}; the
    founder approves the gate; re-running promote() consumes the APPROVED
    gate and executes the transition."""
    c = load(slug)
    nxt = c["stage"] + 1
    if nxt > 4:
        raise ValueError("stage 5 is reached via graduate()/kill(), not promote()")
    blockers = []
    if c["stage"] == 0 and not c.get("prfaq"):
        blockers.append("Stage 0 exit needs an approved PR/FAQ (cogops.py prfaq)")
    if c["stage"] == 1:
        ok, why = stage1_evidence_met(c)
        if not ok:
            blockers.append(f"Stage 1 exit needs market evidence ({why})")
    if c["stage"] == 2 and c.get("paying_customers", 0) < 1:
        blockers.append("Stage 2 exit needs ≥1 unrelated paying customer")
    if c["stage"] == 3 and c["contribution_chf"] <= 0:
        blockers.append("Stage 3 exit (→scale) needs contribution-positive P&L")
    # consume an already-APPROVED promote gate for this transition, if any
    approved = next((g for g in gates.queue("APPROVED")
                     if g["company"] == slug and g["action"].get("kind") == "promote"
                     and g["action"].get("to_stage") == nxt), None)
    if approved and not blockers:
        gates.mark_consumed(approved["id"])
    else:
        aid = gates.stage(slug, {"kind": "promote", "to_stage": nxt,
                                 "blockers_cleared": not blockers},
                          proposed_by="lifecycle")
        if blockers:
            return {"status": "blocked", "gate": aid, "blockers": blockers}
        if not approved:
            try:
                gates.require_approval(aid)
            except gates.GateDenied as e:
                return {"status": "gated", "gate": aid, "detail": str(e)}
    c["history"].append({"from": c["stage"], "to": nxt, "at": config.stamp()})
    c["stage"] = nxt
    c["stage_started"] = config.stamp()
    c["spent_chf"] = 0.0            # fresh envelope per stage
    save(c)
    ledger.decide("promoted", slug, {"to_stage": nxt})
    return {"status": "promoted", "stage": nxt, "name": STAGES[nxt]}


def kill(slug: str, evidence: dict, confirm: str = "") -> dict:
    """Kill = Type-1 (G2) and is RECORDED AS A WIN (invariant I8, Alphabet X
    kill-bonus translation). Requires an evidence pack — no vibes-based kills."""
    if not evidence or not evidence.get("reason"):
        raise ValueError("kill requires an evidence pack with a reason (I8)")
    c = load(slug)
    aid = gates.stage(slug, {"kind": "kill", "external": False}, proposed_by="lifecycle")
    try:
        gates.approve(aid, confirm=confirm)  # founder keystroke simulated via CLI confirm
    except gates.GateDenied as e:
        return {"status": "gated", "gate": aid, "detail": str(e)}
    gates.require_approval(aid)
    c["history"].append({"from": c["stage"], "to": 5, "at": config.stamp(), "kind": "kill"})
    c["stage"] = 5
    save(c)
    ledger.decide("KILL_WIN", slug, evidence)      # the win record
    squad.credit_kill(slug)                        # budget credibility (OS §5)
    return {"status": "killed_as_win", "gate": aid}


def graduate(slug: str, entity_form: str = "GmbH", confirm: str = "") -> dict:
    """Stage-5 legal spin-out (OS §12; triggers per research/09 §3) — G3:
    legal act + irreversible."""
    c = load(slug)
    if c["stage"] < 4:
        raise ValueError("graduation requires Stage 4 (spin-out trigger list, OS §12)")
    aid = gates.stage(slug, {"kind": "graduate", "legal_act": True, "irreversible": True,
                             "entity_form": entity_form}, proposed_by="lifecycle")
    try:
        gates.approve(aid, confirm=confirm)
        gates.require_approval(aid)
    except gates.GateDenied as e:
        return {"status": "gated", "gate": aid, "detail": str(e)}
    c["history"].append({"from": c["stage"], "to": 5, "at": config.stamp(),
                         "kind": "graduate", "entity_form": entity_form})
    c["stage"] = 5
    save(c)
    ledger.decide("graduated", slug, {"entity_form": entity_form})
    return {"status": "graduated", "entity_form": entity_form}


def timebox_report(slug: str) -> dict:
    """Time-box status (OS §5): days in stage vs limit."""
    import time as _t
    c = load(slug)
    limit = config.STAGE_TIMEBOX_DAYS.get(c["stage"])
    started = _t.mktime(_t.strptime(c["stage_started"], "%Y-%m-%dT%H:%M:%SZ")) - _t.timezone
    days = (config.now() - started) / 86400.0
    return {"slug": slug, "stage": c["stage"], "days_in_stage": round(days, 1),
            "timebox_days": limit,
            "breached": bool(limit and days > limit and c["stage"] in (0, 1, 2))}


def attach_prfaq(slug: str, press_release: str, faq: list[tuple[str, str]],
                 premortem: str) -> dict:
    """Stage-0 exit artifact (Amazon working-backwards, OS §5/I4): imagined PR +
    FAQ + pre-mortem ('why did this fail in 12 months?' — OS §11)."""
    c = load(slug)
    c["prfaq"] = {"press_release": press_release, "faq": faq, "premortem": premortem,
                  "at": config.stamp()}
    save(c)
    ledger.event("prfaq_attached", slug, {"chars": len(press_release),
                                          "faq_items": len(faq)})
    return c["prfaq"]


def register_revenue(slug: str, chf: float, recurring: bool, customer_unrelated: bool = True):
    c = load(slug)
    c["revenue_chf"] = round(c["revenue_chf"] + chf, 2)
    if recurring:
        c["recurring_revenue_chf"] = round(c.get("recurring_revenue_chf", 0.0) + chf, 2)
    if customer_unrelated and chf > 0:
        c["paying_customers"] = c.get("paying_customers", 0) + 1
    save(c)
    ledger.event("revenue", slug, {"chf": chf, "recurring": recurring})
    return c
