"""The Nervous System (OS §16, DR-0011) — senses, reflexes, pain, consciousness.

Anatomy:
  SENSES   sense() scans every organ (ledgers, gates, tickets, metrics, missions,
           capital fortress, LLM caps, optionally the live sites) and emits
           typed signals onto the bus (signals.jsonl).
  REFLEXES reflexes() react to signals WITHOUT waiting for the founder where the
           reaction is protective (spend freeze, kill-review staging, dependency
           flags); protective reflexes never spend, never send, never approve.
  PAIN     critical signals (ledger-integrity failure, fortress breach) write a
           FREEZE file: lifecycle.spend() refuses while it exists. Integrity
           freezes are released ONLY by a human keystroke (cogops.py unfreeze
           --confirm); fortress freezes auto-release when the fortress recovers.
           The machine stops; it does not limp.
  NERVES   the dependency graph is derived from the companies' LINKS registries:
           when a company degrades, every company that BUYS from it is flagged
           (evidence-chain degraded) — propagation along real trade edges.
  CONSCIOUSNESS  dashboard() renders the whole body: nodes, edges, signals,
           gates, fortress, missions — static HTML or a live localhost server.

The nervous system has no authority to act externally: it freezes, flags,
stages reviews and informs. Approval remains human (invariant I3).
"""
from __future__ import annotations

import hashlib
import json
import time

import config
import ledger

SIGNALS = config.RUNTIME_DIR / "signals.jsonl"
REFLEX_LOG = config.RUNTIME_DIR / "reflex_log.json"
FREEZE_FILE = config.RUNTIME_DIR / "FREEZE.json"


# ------------------------------------------------------------------ senses --
def _emit_signal(kind: str, subject: str, severity: str, payload: dict | None = None) -> dict:
    sid = hashlib.sha256(f"{kind}|{subject}|{config.today()}".encode()).hexdigest()[:12]
    rec = {"id": sid, "kind": kind, "subject": subject, "severity": severity,
           "payload": payload or {}, "at": config.stamp()}
    with open(SIGNALS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def _seen(sid: str) -> bool:
    if not SIGNALS.exists():
        return False
    return any(sid == l.get("id") for l in
               (json.loads(x) for x in SIGNALS.read_text(encoding="utf-8").splitlines() if x))


def signals(limit: int = 50) -> list[dict]:
    if not SIGNALS.exists():
        return []
    rows = [json.loads(x) for x in SIGNALS.read_text(encoding="utf-8").splitlines() if x]
    return rows[-limit:][::-1]


def sense(check_sites: bool = False) -> list[dict]:
    """One sweep of the body. Idempotent per day per condition (signal ids hash
    kind+subject+date)."""
    import capital
    import gates
    import lifecycle
    import metrics
    import platformsvc
    import squad
    out = []

    def emit(kind, subject, severity, payload=None):
        sid = hashlib.sha256(f"{kind}|{subject}|{config.today()}".encode()).hexdigest()[:12]
        if _seen(sid):
            return None
        r = _emit_signal(kind, subject, severity, payload)
        out.append(r)
        return r

    # fortress (pain precursor)
    fm = capital.fortress_months()
    if fm < config.FORTRESS_MONTHS - 1e-9:
        emit("fortress_below_floor", "group", "critical",
             {"months": round(fm, 2), "floor": config.FORTRESS_MONTHS})
    # ledger integrity (worst pain)
    if not ledger.verify_chain(ledger.DECISIONS) or not ledger.verify_chain(ledger.EVENTS):
        emit("ledger_integrity_failed", "group", "critical",
             {"note": "hash chain broken — hard freeze; human release only"})
    # gates: stale pending (>48h)
    for g in gates.queue("PENDING"):
        age_h = (config.now() - time.mktime(time.strptime(g["staged_at"], "%Y-%m-%dT%H:%M:%SZ"))
                 + time.timezone) / 3600.0
        if age_h > 48:
            emit("gate_stale", g["id"], "warn", {"age_h": round(age_h, 1),
                                                 "company": g["company"]})
    # tickets past SLA
    for t in platformsvc.open_tickets():
        sla = platformsvc.CATALOG.get(t["service"], {}).get("sla_h", 24)
        age_h = (config.now() - time.mktime(time.strptime(t["requested_at"], "%Y-%m-%dT%H:%M:%SZ"))
                 + time.timezone) / 3600.0
        if sla and age_h > sla:
            emit("ticket_sla_breached", t["id"], "warn",
                  {"service": t["service"], "age_h": round(age_h, 1), "sla_h": sla})
    # metric floor breaches (≥2 on record → review)
    db = metrics._db()
    for rid, reg in db["registry"].items():
        if reg["floor"] is None:
            continue
        breaches = [o for o in db["observations"] if o["id"] == rid and o["breach"]]
        if len(breaches) >= 2:
            emit("metric_floor_repeat", rid, "warn", {"breaches": len(breaches),
                                                      "floor": reg["floor"]})
    # missions blocked
    for slug, m in squad.mission_status().items():
        if m.get("status") == "BLOCKED":
            emit("mission_blocked", slug, "warn", {"why": m.get("blocked", "")})
    # LLM caps hit
    import llm
    for slug in lifecycle.all_slugs():
        if llm.spent_usd(slug) >= llm.MONTHLY_CAP_USD:
            emit("llm_cap_hit", slug, "info",
                 {"spent_usd": llm.spent_usd(slug), "cap": llm.MONTHLY_CAP_USD,
                  "mode": "free-tier + KB only until month roll"})
    # contribution-negative at operate stage
    for slug in lifecycle.all_slugs():
        c = lifecycle.load(slug)
        if c["stage"] == 3 and c.get("contribution_chf", 0) < 0 and c.get("revenue_chf", 0) > 0:
            emit("contribution_negative", slug, "warn",
                 {"contribution": c["contribution_chf"]})
    # optional: live site pulses
    if check_sites:
        import urllib.request
        for dom in ("growth", "talent", "helix", "verde", "terra", "sentinel",
                    "capital", "dossia", "medtech", "intelligence"):
            try:
                r = urllib.request.Request(f"https://cogops-{dom}.pages.dev/api/count",
                                           headers={"User-Agent": "CogOpsNervousSystem/1.0"})
                j = json.loads(urllib.request.urlopen(r, timeout=8).read())
                emit("site_pulse", dom, "info", {"signups": j.get("count")})
            except Exception as e:
                emit("site_down", dom, "warn", {"error": str(e)[:80]})
    return out


# ------------------------------------------------------------------ nerves --
def dependency_map() -> dict:
    """seller -> [buyers], derived from every company's LINKS registry."""
    import registry
    deps = {}
    for slug in registry.COMPANIES:
        links = getattr(registry.module(slug), "LINKS", {})
        for partner in links:
            deps.setdefault(partner, []).append(slug)
    return deps


def dependents_of(slug: str) -> list[str]:
    return sorted(set(dependency_map().get(slug, [])))


# ------------------------------------------------------------------ pain ----
def freeze(reason: str, auto_release: bool = True) -> dict:
    cur = json.loads(FREEZE_FILE.read_text(encoding="utf-8")) if FREEZE_FILE.exists() \
        else {"reasons": []}
    entry = {"reason": reason, "auto_release": auto_release, "at": config.stamp()}
    if not any(r["reason"] == reason for r in cur["reasons"]):
        cur["reasons"].append(entry)
    FREEZE_FILE.write_text(json.dumps(cur, indent=1, sort_keys=True), encoding="utf-8")
    ledger.event("freeze", "group", {"reason": reason, "auto_release": auto_release})
    return cur


def frozen() -> dict | None:
    if not FREEZE_FILE.exists():
        return None
    cur = json.loads(FREEZE_FILE.read_text(encoding="utf-8"))
    return cur if cur.get("reasons") else None


def unfreeze(reason: str | None = None, confirm: str = "") -> dict:
    """Human-only release for integrity freezes (checked by CLI confirm phrase)."""
    if confirm.strip().lower() != config.CONFIRM_PHRASE:
        raise PermissionError("unfreeze requires the founder confirmation phrase")
    cur = json.loads(FREEZE_FILE.read_text(encoding="utf-8")) if FREEZE_FILE.exists() \
        else {"reasons": []}
    before = len(cur["reasons"])
    cur["reasons"] = [r for r in cur["reasons"]
                      if (reason and r["reason"] != reason) or (not reason and r.get("auto_release"))]
    FREEZE_FILE.write_text(json.dumps(cur, indent=1, sort_keys=True), encoding="utf-8")
    ledger.decide("unfreeze", "group", {"removed": before - len(cur["reasons"]),
                                        "remaining": len(cur["reasons"])})
    return cur


# ---------------------------------------------------------------- reflexes --
def _reflexed(sid: str) -> bool:
    log = json.loads(REFLEX_LOG.read_text(encoding="utf-8")) if REFLEX_LOG.exists() else []
    return sid in log


def _mark_reflex(sid: str, action: str) -> None:
    log = json.loads(REFLEX_LOG.read_text(encoding="utf-8")) if REFLEX_LOG.exists() else []
    log.append({"signal": sid, "action": action, "at": config.stamp()})
    REFLEX_LOG.write_text(json.dumps(log, indent=1, sort_keys=True), encoding="utf-8")


def reflexes() -> list[dict]:
    """Protective reactions to fresh signals. Never spend, never send, never
    approve: freeze, flag, stage reviews, inform."""
    import capital
    import gates
    import lifecycle
    acted = []
    for s in signals(60):
        if _reflexed(s["id"]):
            continue
        if s["kind"] == "ledger_integrity_failed":
            freeze("ledger_integrity", auto_release=False)
            _mark_reflex(s["id"], "hard freeze (human release only)")
            acted.append({"signal": s["kind"], "action": "HARD FREEZE"})
        elif s["kind"] == "fortress_below_floor":
            freeze("fortress", auto_release=True)
            _mark_reflex(s["id"], "spend freeze until fortress restored")
            acted.append({"signal": s["kind"], "action": "SPEND FREEZE"})
        elif s["kind"] == "metric_floor_repeat":
            slug = s["subject"].split(":")[0]
            aid = gates.stage(slug, {"kind": "kill", "notify": True,
                                     "reason_preview": f"repeat floor breach: {s['subject']}"},
                              proposed_by="nervous-system")
            _mark_reflex(s["id"], f"kill-review staged {aid}")
            acted.append({"signal": s["kind"], "action": f"kill-review {aid}"})
        elif s["kind"] == "contribution_negative":
            aid = gates.stage(s["subject"], {"kind": "kill", "notify": True,
                                             "reason_preview": "contribution negative at operate stage"},
                              proposed_by="nervous-system")
            _mark_reflex(s["id"], f"spin-down review staged {aid}")
            acted.append({"signal": s["kind"], "action": f"spin-down review {aid}"})
        elif s["kind"] in ("site_down", "llm_cap_hit", "mission_blocked",
                           "gate_stale", "ticket_sla_breached"):
            deps = dependents_of(s["subject"]) if s["kind"] == "site_down" else []
            for d in deps:
                _emit_signal("evidence_chain_degraded", d, "info",
                             {"because": s["subject"], "cause": s["kind"]})
            _mark_reflex(s["id"], "flagged" + (f" + propagated to {deps}" if deps else ""))
            acted.append({"signal": s["kind"], "action": "flag/propagate"})
    # auto-release healed fortress freezes
    fz = frozen()
    if fz:
        keep = []
        for r in fz["reasons"]:
            if r["reason"] == "fortress" and r.get("auto_release") and capital.fortress_ok():
                ledger.event("freeze_released", "group", {"reason": "fortress"})
                acted.append({"signal": "fortress", "action": "freeze auto-released"})
            else:
                keep.append(r)
        if len(keep) != len(fz["reasons"]):
            FREEZE_FILE.write_text(json.dumps({"reasons": keep}, indent=1, sort_keys=True),
                                   encoding="utf-8")
    return acted


def cycle(check_sites: bool = False) -> dict:
    fresh = sense(check_sites=check_sites)
    acted = reflexes()
    return {"signals_new": len(fresh), "reflexes": acted,
            "frozen": bool(frozen()),
            "freeze_reasons": [r["reason"] for r in (frozen() or {}).get("reasons", [])]}


# --------------------------------------------------------- consciousness ----
def state() -> dict:
    """The body, as data: nodes, edges, vitals, signals, gates, missions."""
    import capital
    import gates
    import lifecycle
    import metrics
    import registry
    import squad
    registry.ensure_registered()   # consciousness boots the body if needed
    nodes = []
    for slug in registry.COMPANIES:
        c = lifecycle.load(slug)
        sc = metrics.scorecard(slug, c)
        nodes.append({"slug": slug, "name": c["name"], "stage": c["stage"],
                      "stage_name": lifecycle.STAGES[c["stage"]],
                      "contribution": c["contribution_chf"], "revenue": c["revenue_chf"],
                      "envelope": lifecycle.envelope_of(c), "spent": c["spent_chf"],
                      "breaches": sum(1 for lay in sc["spqp"].values() for m in lay if m["breach"]),
                      "links": sorted(getattr(registry.module(slug), "LINKS", {}).keys())})
    edges = []
    seen = set()
    for slug in registry.COMPANIES:
        for partner in getattr(registry.module(slug), "LINKS", {}):
            key = tuple(sorted((slug, partner)))
            if key not in seen:
                seen.add(key)
                edges.append(list(key))
    return {"generated_at": config.stamp(),
            "cbs_version": __import__("cbs").version()["cbs_version"],
            "fortress_months": round(capital.fortress_months(), 2),
            "fortress_ok": capital.fortress_ok(),
            "freeze": frozen(),
            "nodes": nodes, "edges": edges,
            "gates_pending": [{"id": g["id"], "company": g["company"], "level": g["level"],
                               "kind": g["action"].get("kind")} for g in gates.queue("PENDING")],
            "missions": {k: v.get("status") for k, v in squad.mission_status().items()},
            "signals": signals(30),
            "health": metrics.portfolio_health([lifecycle.load(s) for s in lifecycle.all_slugs()])}
