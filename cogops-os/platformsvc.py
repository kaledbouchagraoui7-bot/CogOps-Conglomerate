"""Shared platform services (OS §7) — PULL-ONLY by construction.

This module exposes `request()` (subsidiary → platform) and `serve()`
(platform fulfills) and NOTHING that pushes into a subsidiary. The center-NEVER
list (OS §6) is enforced by absence of API: there is no push_process,
demand_synergy, rotate_squad or silent_topup function to call — and
`autonomy.center_audit()` verifies none was ever added (invariant I6).

Every served ticket charges the requesting company at notional cost (Haier M1
internal-market rule → honest standalone P&Ls, invariant I7).
"""
from __future__ import annotations

import json

import config
import ledger

TICKETS_FILE = config.RUNTIME_DIR / "tickets.json"

# The service catalog (OS §7 table). Notional costs keep P&Ls honest.
CATALOG = {
    "site_factory":   {"chf": 50.0, "sla_h": 24, "provides": "brand site + portal + assistant instance"},
    "llm_gateway":    {"chf": 5.0,  "sla_h": 1,  "provides": "multi-provider chain + KB-first routing"},
    "crm_portal":     {"chf": 10.0, "sla_h": 4,  "provides": "leads/clients/deliverables/invoices tables + auth"},
    "verification":   {"chf": 15.0, "sla_h": 8,  "provides": "FIXES-method instruments + selftest scaffolding"},
    "legal_templates":{"chf": 20.0, "sla_h": 24, "provides": "privacy/impressum/ToS baselines (CH)"},
    "brand_kit":      {"chf": 10.0, "sla_h": 8,  "provides": "name/visual/voice config for the factory"},
    "media_network":  {"chf": 25.0, "sla_h": 48, "provides": "newsletter slot in the company's domain journal"},
    "lead_gen":       {"chf": 1.0,  "sla_h": 48, "per": "lead",  "provides": "validated lead (internal price, DR-0002)"},
    "career_intel":   {"chf": 5.0,  "sla_h": 24, "per": "brief", "provides": "market brief / curriculum extract (internal, DR-0002)"},
    "carbon_books":   {"chf": 8.0,  "sla_h": 48, "per": "book",  "provides": "carbon books computation (internal, DR-0008)"},
    "climate_risk":   {"chf": 10.0, "sla_h": 48, "per": "screen","provides": "physical/transition risk screen (internal, DR-0008)"},
    "pseo_page":      {"chf": 10.0, "sla_h": 24, "per": "page",  "provides": "QA-passed programmatic page (internal, DR-0002)"},
    "gate_services":  {"chf": 0.0,  "sla_h": 0,  "provides": "Nexus gate, decision ledger, sweep engine"},
    "agent_core":     {"chf": 0.0,  "sla_h": 0,  "provides": "roster access + mission runtime"},
}


def _db() -> dict:
    if TICKETS_FILE.exists():
        return json.loads(TICKETS_FILE.read_text(encoding="utf-8"))
    return {"tickets": []}


def _save(db: dict) -> None:
    TICKETS_FILE.write_text(json.dumps(db, indent=1, sort_keys=True), encoding="utf-8")


def catalog() -> dict:
    return dict(CATALOG)


def request(slug: str, service: str, spec: str, units: int = 1) -> dict:
    if service not in CATALOG:
        raise ValueError(f"unknown platform service {service!r} — catalog: {sorted(CATALOG)}")
    db = _db()
    per = CATALOG[service].get("per")
    notional = round(CATALOG[service]["chf"] * (units if per else 1), 2)
    t = {"id": f"PT-{len(db['tickets']) + 1:05d}", "slug": slug, "service": service,
         "spec": spec, "units": units if per else 1, "status": "OPEN",
         "notional_chf": notional, "requested_at": config.stamp()}
    db["tickets"].append(t)
    _save(db)
    ledger.event("platform_request", slug, {"service": service, "ticket": t["id"]})
    return t


def serve(ticket_id: str, result: dict) -> dict:
    """Platform fulfills a ticket; notional cost posts to the company's P&L."""
    import lifecycle
    db = _db()
    t = next((x for x in db["tickets"] if x["id"] == ticket_id), None)
    if t is None:
        raise ValueError(f"unknown ticket {ticket_id}")
    if t["status"] != "OPEN":
        raise ValueError(f"ticket {ticket_id} already {t['status']}")
    t["status"] = "SERVED"
    t["served_at"] = config.stamp()
    t["result_ref"] = result.get("ref", "")
    _save(db)
    if t["notional_chf"] > 0:
        c = lifecycle.load(t["slug"])
        c["platform_charges_chf"] = round(c["platform_charges_chf"] + t["notional_chf"], 2)
        lifecycle.save(c)
    ledger.event("platform_served", t["slug"], {"ticket": ticket_id,
                                                "service": t["service"],
                                                "chf": t["notional_chf"]})
    return t


def open_tickets(slug: str | None = None) -> list[dict]:
    return [t for t in _db()["tickets"]
            if t["status"] == "OPEN" and (slug is None or t["slug"] == slug)]
