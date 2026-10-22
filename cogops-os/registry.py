"""Company registry & task dispatch (OS §13 instantiation).

Each company module in `companies/` exposes META (dan, stage at v1.0, input
metrics, squad roles, human-of-record — straight from OPERATING-STRUCTURE §13)
and TASKS (the state-of-the-art engine for its domain work).

`ensure_registered()` is idempotent: it instantiates all ten companies into
runtime state, registers their metrics with owners, and forms their squads
with CBS immersion — the group boots from zero to operating with one call.
"""
from __future__ import annotations

import importlib

import cbs
import config
import lifecycle
import metrics
import squad

COMPANIES = ("intelligence", "sentinel", "capitalco", "helix", "dossia",
             "medtech", "verde", "terra", "growth", "talent")

_MODULES = {}


def module(slug: str):
    if slug not in _MODULES:
        if slug not in COMPANIES:
            raise ValueError(f"unknown company {slug!r} — registry: {COMPANIES}")
        _MODULES[slug] = importlib.import_module(f"companies.{slug}")
    return _MODULES[slug]


def meta(slug: str) -> dict:
    return module(slug).META


def ensure_registered() -> dict:
    """Idempotent group boot (OS §10 immersion-on-entry for every squad)."""
    out = {}
    for slug in COMPANIES:
        m = meta(slug)
        try:
            c = lifecycle.load(slug)
        except lifecycle.CompanyNotFound:
            c = lifecycle.register(slug, m["name"], m["dan"], m["input_metrics"],
                                   m["squad_roles"], stage=m["stage_at_v10"],
                                   seed_assets=m.get("seed_assets", ""))
        for im in m["input_metrics"]:
            rid = f"{slug}:{im['key']}"
            try:
                metrics.register(slug, im["key"], im["layer"], im["owner"],
                                 floor=im.get("floor"), unit=im.get("unit", ""))
            except Exception:
                pass  # already registered
        if not squad.squad_of(slug).get("roles"):
            squad.propose_roles(slug, m["squad_roles"], by="registry")
        pack = cbs.immersion(slug, m["dan"], company_kb=m.get("kb", ""))
        out[slug] = {"stage": lifecycle.load(slug)["stage"],
                     "cbs_version": pack["cbs"]["cbs_version"]}
    return out


def tasks(slug: str) -> list[str]:
    return sorted(module(slug).TASKS.keys())


def run_task(slug: str, task: str, params: dict | None = None,
             role: str | None = None) -> dict:
    """Dispatch a company task through its engine. The engine call is wrapped
    by the squad runner (role check + honest mode labels) and the autonomy
    contract is verified around it."""
    import autonomy
    mod = module(slug)
    if task not in mod.TASKS:
        raise ValueError(f"{slug}: unknown task {task!r} — engine offers {tasks(slug)}")
    role = role or mod.TASKS[task].get("role", mod.META["squad_roles"][0])
    params = params or {}
    autonomy.check(lifecycle.load(slug), {"kind": "company_task", "task": task,
                                          "external": False})
    engine = mod.TASKS[task]["fn"]
    artifact = squad.run_task(slug, role, task,
                              lambda s, r, t: engine(params, s))
    return artifact


def list_all() -> list[dict]:
    ensure_registered()
    out = []
    for slug in COMPANIES:
        c = lifecycle.load(slug)
        m = meta(slug)
        out.append({"slug": slug, "name": c["name"], "stage": c["stage"],
                    "stage_name": lifecycle.STAGES[c["stage"]],
                    "dan": m["dan"][:90],
                    "human_of_record": m.get("human_of_record", config.FOUNDER),
                    "tasks": tasks(slug)})
    return out
