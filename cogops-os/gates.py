"""The Gate — Nexus pattern (JARVIS nexus_gate.py lineage), generalized to the
group's three gate levels and decision typology (OS §3, §11, invariant I3).

Fail-closed by construction: unknown/expired/unapproved ids raise; there is no
code path that executes a Type-1 action without an APPROVED record.

Levels:  G1 notify      — executed, visible in the weekly sheet
         G2 approve      — standard Type-1: evidence pack + keystroke
         G3 dual-confirm — Type-1 + irreversible/financial/legal: keystroke AND
                           the confirmation phrase (config.CONFIRM_PHRASE)
"""
from __future__ import annotations

import json
from pathlib import Path

import config
import ledger

GATE_FILE = config.RUNTIME_DIR / "gate_queue.json"

CLASSIFICATION_RULES = (
    # (predicate on action dict, decision type, gate level, reason)
    (lambda a: a.get("money_movement") or a.get("legal_act"), "type1", "G3",
     "money movement / legal act"),
    (lambda a: a.get("irreversible"), "type1", "G3", "irreversible (one-way door)"),
    (lambda a: a.get("external") or a.get("public_statement"), "type1", "G2",
     "external-facing action"),
    (lambda a: a.get("above_cap"), "type1", "G2", "spend above delegated cap"),
    (lambda a: a.get("kind") in ("launch", "kill", "promote", "graduate"), "type1", "G2",
     "lifecycle transition"),
)


def classify(action: dict) -> tuple[str, str, str]:
    """Return (decision_type, gate_level, reason). Default: type2/None —
    reversible, inside envelope → squad executes freely (OS §3)."""
    for pred, dtype, level, reason in CLASSIFICATION_RULES:
        try:
            if pred(action):
                return dtype, level, reason
        except Exception:
            continue
    return "type2", "G1" if action.get("notify") else "none", "reversible, inside envelope"


def _load() -> dict:
    if GATE_FILE.exists():
        return json.loads(GATE_FILE.read_text(encoding="utf-8"))
    return {}


def _save(q: dict) -> None:
    GATE_FILE.write_text(json.dumps(q, indent=1, sort_keys=True), encoding="utf-8")


def stage(company: str, action: dict, proposed_by: str = "squad") -> str:
    """Stage an action. Returns action id. G1 actions are auto-approved (notify)."""
    dtype, level, reason = classify(action)
    aid = f"GA-{config.today().replace('-', '')}-{len(_load()) + 1:04d}"
    q = _load()
    q[aid] = {"id": aid, "company": company, "action": action, "type": dtype,
              "level": level, "reason": reason, "status": "PENDING",
              "proposed_by": proposed_by, "staged_at": config.stamp()}
    if level == "G1":
        q[aid]["status"] = "NOTIFIED"       # executed, appears on weekly sheet
    _save(q)
    ledger.decide("gate_staged", aid, {"company": company, "level": level,
                                       "type": dtype, "reason": reason})
    return aid


def approve(aid: str, confirm: str = "") -> str:
    q = _load()
    if aid not in q:
        raise GateDenied(f"unknown action {aid} — fail-closed")
    item = q[aid]
    if item["level"] == "G3" and confirm.strip().lower() != config.CONFIRM_PHRASE:
        raise GateDenied(f"{aid} is G3 (dual-confirm): confirmation phrase required")
    item["status"] = "APPROVED"
    item["decided_at"] = config.stamp()
    _save(q)
    ledger.decide("gate_approved", aid, {"level": item["level"], "company": item["company"]})
    return aid


def refute(aid: str, why: str) -> str:
    q = _load()
    if aid not in q:
        raise GateDenied(f"unknown action {aid} — fail-closed")
    q[aid]["status"] = "REFUTED"
    q[aid]["why"] = why
    q[aid]["decided_at"] = config.stamp()
    _save(q)
    ledger.decide("gate_refuted", aid, {"why": why, "company": q[aid]["company"]})
    return aid


class GateDenied(RuntimeError):
    pass


def require_approval(aid: str) -> dict:
    """Blocking check before execution. Raises GateDenied unless APPROVED/NOTIFIED."""
    q = _load()
    if aid not in q:                      # fail-closed on unknown id (JARVIS rule)
        raise GateDenied(f"unknown action id {aid!r} — refusing (fail-closed)")
    item = q[aid]
    if item["status"] in ("APPROVED", "NOTIFIED"):
        return item
    raise GateDenied(f"action {aid} is {item['status']}, not APPROVED — "
                     f"The Gate blocks execution (human approval required)")


def mark_consumed(aid: str) -> None:
    q = _load()
    if aid in q:
        q[aid]["status"] = "CONSUMED"
        q[aid]["consumed_at"] = config.stamp()
        _save(q)
        ledger.event("gate_consumed", aid, {"company": q[aid]["company"]})


def queue(status: str = "PENDING") -> list[dict]:
    return [i for i in _load().values() if status is None or i["status"] == status]


def run_if_approved(company: str, action: dict, fn, *a, proposed_by: str = "squad",
                    confirm: str = "", **kw):
    """The one execution funnel: classify → stage → require → run.
    Type-2 actions execute immediately (logged); Type-1 wait for the keystroke.
    Returns (status, result_or_id)."""
    aid = stage(company, action, proposed_by)
    dtype, level, _ = classify(action)
    if dtype == "type2" or level == "G1":
        ledger.event("type2_executed", aid, {"company": company})
        return "executed", fn(*a, **kw)
    try:
        require_approval(aid)
    except GateDenied as e:
        return "gated", f"{aid}: {e}"
    ledger.event("type1_executed", aid, {"company": company})
    return "executed", fn(*a, **kw)
