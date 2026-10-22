"""Squads & missions (OS §10) — agents in place of employees.

A squad = the JARVIS agent hierarchy instantiated per company: roles drawn
from the roster (7 universes), a single-threaded squad-lead (Amazon STL — one
accountable role, never a committee), and mission mode (JARVIS automaton DNA:
`mission set` keeps working across cycles until done/blocked/ended).

Execution honesty (JARVIS principle): an agent task either runs a REAL engine
(deterministic code / live LLM call) or is recorded as `template` — never
faked as AI. Mode labels on every artifact.
"""
from __future__ import annotations

import json

import config
import ledger

SQUAD_FILE = config.RUNTIME_DIR / "squads.json"
MISSION_FILE = config.RUNTIME_DIR / "missions.json"


def _load(p) -> dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _save(p, d: dict) -> None:
    p.write_text(json.dumps(d, indent=1, sort_keys=True), encoding="utf-8")


# ------------------------------------------------------------------ roster --
def roster() -> dict:
    """7-universe roster condensed from the JARVIS 110-agent hierarchy — the
    roles squads actually draw from (agent_universes.json lineage)."""
    p = config.ROOT / "data" / "agent_roles.json"
    return json.loads(p.read_text(encoding="utf-8"))


def propose_roles(slug: str, roles: list[str], by: str = "squad-lead") -> dict:
    """Staffing right (OS §6): squad proposes composition from the roster;
    validation against the roster is the only center involvement."""
    r = roster()
    known = {a["role"] for u in r["universes"].values() for a in u}
    unknown = [x for x in roles if x not in known]
    if unknown:
        raise ValueError(f"roles not in roster: {unknown}")
    sq = _load(SQUAD_FILE)
    sq[slug] = {"roles": roles, "proposed_by": by, "at": config.stamp()}
    _save(SQUAD_FILE, sq)
    ledger.event("squad_staffed", slug, {"roles": roles})
    return sq[slug]


def squad_of(slug: str) -> dict:
    return _load(SQUAD_FILE).get(slug, {"roles": []})


def credit_kill(slug: str) -> None:
    """Budget credibility (OS §5/§6): a well-evidenced kill raises delegated
    caps +10% (max +50%) — the Alphabet X kill-bonus translation."""
    sq = _load(SQUAD_FILE)
    e = sq.setdefault(slug, {"roles": []})
    e["kill_credits"] = e.get("kill_credits", 0) + 1
    _save(SQUAD_FILE, sq)
    ledger.event("kill_credit", slug, {"credits": e["kill_credits"]})


def cap_multiplier(slug: str) -> float:
    return 1.0 + min(0.5, 0.10 * _load(SQUAD_FILE).get(slug, {}).get("kill_credits", 0))


# ----------------------------------------------------------------- missions --
def mission_set(slug: str, text: str) -> dict:
    """JARVIS mission mode: persistent 'keep working' instruction. The automaton
    advances it every cycle until done/blocked/ended."""
    m = _load(MISSION_FILE)
    m[slug] = {"text": text, "status": "ACTIVE", "set_at": config.stamp(),
               "cycles": 0, "log": []}
    _save(MISSION_FILE, m)
    ledger.decide("mission_set", slug, {"text": text})
    return m[slug]


def mission_status(slug: str | None = None) -> dict:
    m = _load(MISSION_FILE)
    return m if slug is None else m.get(slug, {})


def mission_end(slug: str, outcome: str = "ended") -> dict:
    m = _load(MISSION_FILE)
    if slug in m:
        m[slug]["status"] = outcome.upper()
        m[slug]["ended_at"] = config.stamp()
        _save(MISSION_FILE, m)
        ledger.decide("mission_ended", slug, {"outcome": outcome})
    return m.get(slug, {})


def mission_progress(slug: str, note: str, done: bool = False,
                     blocked: str | None = None) -> dict:
    m = _load(MISSION_FILE)
    if slug not in m:
        raise ValueError(f"no mission for {slug}")
    m[slug]["cycles"] += 1
    m[slug]["log"].append({"at": config.stamp(), "note": note})
    if blocked:
        m[slug]["status"] = "BLOCKED"
        m[slug]["blocked"] = blocked
        ledger.event("mission_blocked", slug, {"why": blocked})
    elif done:
        m[slug]["status"] = "DONE"
        ledger.decide("mission_done", slug, {"cycles": m[slug]["cycles"]})
    _save(MISSION_FILE, m)
    return m[slug]


# ------------------------------------------------------------------ runner --
def run_task(slug: str, role: str, task: str, engine, mode_fallback: str = "template"):
    """Execute one squad task through the real engine. Returns an artifact dict
    with an honest `mode` label (llm | engine | template)."""
    import llm
    sq = squad_of(slug)
    if role not in sq.get("roles", []):
        raise PermissionError(f"role {role!r} not in {slug}'s squad — staffing right "
                              f"belongs to the squad via propose_roles (OS §6)")
    try:
        out = engine(slug, role, task)
        mode = out.get("mode", "engine") if isinstance(out, dict) else "engine"
        artifact = out if isinstance(out, dict) else {"result": out, "mode": "engine"}
    except llm.LLMUnavailable:
        artifact = {"mode": mode_fallback, "note": "no LLM provider reachable — "
                    "honest template fallback (JARVIS principle)", "task": task}
    artifact.update({"company": slug, "role": role, "task": task,
                     "at": config.stamp()})
    ledger.event("squad_run", slug, {"role": role, "task": task,
                                     "mode": artifact["mode"]})
    return artifact
