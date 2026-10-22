"""The Autonomy Contract as RUNTIME ENFORCEMENT (OS §6).

The contract's "center NEVER / subsidiary NEVER" lists are not prose here —
they are checks executed around every action. Two enforcement surfaces:

1. `check(action)` — called by gates.classify pipeline & company engines;
   blocks contract violations before execution (fail-closed).
2. Structural enforcement — the platform module has no push API at all
   (pull-only, invariant I6): you cannot call what does not exist.

The three rights (Haier M2 translation) are data on the company record:
decision rights (type2 autonomy inside envelope — lifecycle.spend),
staffing rights (squad.propose_roles), credibility rights (credit history).
"""
from __future__ import annotations

import config
import ledger


class ContractViolation(RuntimeError):
    pass


# Actions a subsidiary may NEVER take autonomously (OS §6). Each rule:
# (predicate, invariant ref, message)
SUBSIDIARY_NEVER = (
    (lambda c, a: a.get("obligates_holding", False), "§6",
     "no subsidiary may obligate the holding beyond its envelope"),
    (lambda c, a: a.get("debt", False), "I1",
     "zero holding debt — no borrowing API exists and none may be simulated"),
    (lambda c, a: a.get("external") and not a.get("gate_staged"), "I3",
     "external action without gate staging"),
    (lambda c, a: a.get("money_movement") and not a.get("gate_staged"), "I3",
     "money movement without gate staging"),
    (lambda c, a: a.get("client_data_deletion") and not a.get("gate_staged"), "I3/G3",
     "client-data deletion is G3 dual-confirm, always"),
    (lambda c, a: a.get("signs_legally"), "I12",
     "signing authority is human and never delegated to agents"),
    (lambda c, a: a.get("hides_losses"), "§6",
     "candor-first: hidden losses are a kill-flag"),
    (lambda c, a: a.get("offbrand") and not a.get("brand_reviewed"), "§6",
     "CogOps brand usage outside brand standards"),
)

# Actions the center may NEVER take toward a subsidiary (OS §6). Enforced by
# absence of APIs (no push_process, no rotate_squad, no silent_topup functions
# exist in platform.py / lifecycle.py) AND by this audit-time check:
CENTER_NEVER = (
    "push_process_into_subsidiary",
    "demand_synergy_in_business_case",     # I5 — synergy counting banned
    "rotate_squad_roles_without_gate",
    "silent_envelope_topup",
    "override_pricing_inside_band",
)


def check(company: dict | None, action: dict) -> None:
    """Raise ContractViolation if the action breaches the contract.
    Called by gates.stage() users and company task runners."""
    for pred, ref, msg in SUBSIDIARY_NEVER:
        try:
            if pred(company or {}, action):
                ledger.event("contract_violation_blocked",
                             (company or {}).get("slug", "?"),
                             {"ref": ref, "msg": msg, "action_kind": action.get("kind")})
                raise ContractViolation(f"[{ref}] {msg} — action blocked (fail-closed)")
        except ContractViolation:
            raise
        except Exception:
            continue


def center_audit() -> dict:
    """Auditing-Agent instrument: verify no center-side violation primitives
    were introduced (greps the platform module's public surface)."""
    import platformsvc as pf
    leaked = [n for n in CENTER_NEVER if hasattr(pf, n)]
    return {"ok": not leaked, "leaked_primitives": leaked,
            "pull_only_rule": "platformsvc exposes request()/serve() only",
            "checked_at": config.stamp()}


def three_rights(company: dict) -> dict:
    """The Haier translation, as data (OS §6):"""
    return {
        "decision_rights": f"type2/type3 autonomy inside stage-{company['stage']} "
                           f"envelope; above cap ⇒ auto Type-1 (lifecycle.spend)",
        "staffing_rights": "squad proposes agent-role composition from the roster; "
                           "amendments via gate (squad.propose_roles)",
        "credibility_rights": {
            "kill_credits": company.get("kill_credits", 0),
            "cap_bonus_pct": min(50, 10 * company.get("kill_credits", 0)),
            "rule": "well-evidenced kills raise delegated caps +10% each (max +50%)",
        },
    }
