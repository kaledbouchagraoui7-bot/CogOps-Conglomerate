"""dormancy.py — DR-0013 focus decree, executable.

Dormant companies keep their live evidence machines but generate NO outreach,
NO spend and NO public statements; reactivation requires a Decision Record
override flag on the staged action. Enforced in gates.stage(); proved in
selftest; displayed on the group site (transparency over polish, DR-0012).
"""
from __future__ import annotations

import json
from pathlib import Path

import config

FILE = config.ROOT / "data" / "dormancy.json"


def load() -> dict:
    if not FILE.exists():
        return {"dormant": [], "active": [], "dr": "", "effective": ""}
    return json.loads(FILE.read_text(encoding="utf-8"))


def is_dormant(company: str) -> bool:
    return company in load().get("dormant", [])


def modes() -> dict:
    d = load()
    return {s: ("dormant" if s in d.get("dormant", []) else "active")
            for s in list(d.get("dormant", [])) + list(d.get("active", []))}


def blocked(company: str, action: dict) -> str:
    """Reason string if DR-0013 blocks this action, else ''."""
    if not is_dormant(company):
        return ""
    if action.get("dr_override"):
        return ""                       # reactivation by DR: routed to G3 anyway
    if action.get("external") or action.get("money_movement") \
            or action.get("public_statement"):
        return f"DR-0013 dormancy: {company} is passive; reactivation needs a DR"
    return ""


def assert_consistent(registry_companies: tuple, decisions_text: str) -> list:
    """Structural proof used by selftest: partition + DR reference + dates."""
    errs = []
    d = load()
    dorm, act, dr = set(d.get("dormant", [])), set(d.get("active", [])), d.get("dr", "")
    if dorm | act != set(registry_companies):
        errs.append("dormancy list is not a partition of the registry")
    if dorm & act:
        errs.append("company both dormant and active")
    if not dr or dr not in decisions_text:
        errs.append("dormancy decree must cite an existing Decision Record")
    if not d.get("effective"):
        errs.append("dormancy decree needs an effective date")
    return errs
