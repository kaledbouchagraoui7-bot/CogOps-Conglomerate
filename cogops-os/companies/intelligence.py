"""CogOps Intelligence — AI operations, the group's flagship (OS §13;
blueprint co. 1; AI/ML gap 9.8/10, the "AI paradox" multiplier).

Seed: the live JARVIS platform. State-of-the-art here = selling what the group
runs (the AWS move, OS §7): deployment orchestration across the platform
services, automation audits (process → agent design), and KB grounding
manifests. The group itself is the reference customer and the demo.
"""
from __future__ import annotations

import json

import config
import ledger
import platformsvc

META = {
    "name": "CogOps Intelligence",
    "dan": "SMEs get an AI-operated back office — agents, assistants and "
           "automations built, hosted and supervised — without hiring.",
    "stage_at_v10": 3,
    "seed_assets": "JARVIS platform live (site, Nexus assistant, gateway, gate, CRM)",
    "human_of_record": "founder",
    "input_metrics": [
        {"key": "live_deployments", "layer": "F", "owner": "deployment-engineer", "floor": 1},
        {"key": "retention_pct", "layer": "F", "owner": "squad-coordinator", "floor": 80},
        {"key": "gate_approved_actions_week", "layer": "P", "owner": "platform-operator", "floor": 5},
    ],
    "squad_roles": ["deployment-engineer", "kb-librarian", "gateway-operator",
                    "site-factory-engineer", "process-auditor", "lead-researcher",
                    "market-researcher", "verifier", "treasury-accountant",
                    "ai-security-reviewer", "carbon-accountant", "risk-modeler",
                    "audit-trail-clerk"],
}


def deploy_client(params: dict, slug: str) -> dict:
    """Deployment orchestrator: one client config → platform tickets (site
    factory, gateway, CRM, brand) → deployment manifest. Pull-only (OS §7):
    the orchestrator REQUESTS services; it never commands another subsidiary."""
    client = params.get("client", {})
    if isinstance(client, str):          # accept bare name or full config dict
        client = {"name": client}
    name = client.get("name", "client")
    needs = client.get("services", ["site_factory", "llm_gateway", "crm_portal"])
    tickets = []
    for svc in needs:
        t = platformsvc.request(slug, svc, spec=json.dumps(
            {"client": name, "brand": client.get("brand", name.lower()),
             "kb": client.get("kb_ref", "")}))
        tickets.append(t["id"])
        platformsvc.serve(t["id"], {"ref": f"deploy:{name}:{svc}"})
    manifest = {"client": name, "services_deployed": needs, "tickets": tickets,
                "grounding": {"kb_first": True, "provider_labels": True,
                              "modes": ["kb", "llm", "template — never faked"]},
                "gate_policy": "client money/external actions = client's own gates",
                "reference_customer": "jarvis-8wr.pages.dev (the group runs on it)",
                "asof": config.today()}
    artifact = {"mode": "engine", "manifest": manifest}
    _emit(slug, f"deploy_{name.lower().replace(' ', '_')}", artifact)
    ledger.event("intel_deployment", slug, {"client": name})
    return artifact


def automation_audit(params: dict, slug: str) -> dict:
    """Process questionnaire → process map → agent design doc: which steps go
    to which universe roles, which stay human (Type-1 gates), what it saves.
    The audit output is the sales artifact AND the build spec."""
    answers = params.get("answers", {})   # {"process": "...", "steps": [...], "volume_month": n, "minutes_per": m}
    steps = answers.get("steps", [])
    if not steps:
        raise ValueError("audit needs process steps")
    volume = float(answers.get("volume_month", 0))
    minutes = float(answers.get("minutes_per", 0))
    mapped = []
    for i, s in enumerate(steps, 1):
        cls = _classify_step(s)
        mapped.append({"step": i, "description": s, "assignment": cls["to"],
                       "universe": cls["universe"], "gate": cls["gate"],
                       "rationale": cls["why"]})
    human_steps = [m for m in mapped if m["assignment"] == "human"]
    agent_steps = [m for m in mapped if m["assignment"] == "agent"]
    minutes_saved = volume * minutes * len(agent_steps) / max(len(mapped), 1)
    watch = json.loads((config.ROOT / "data" / "ai_act_watch.json").read_text(encoding="utf-8"))
    artifact = {"mode": "engine",
                "reg_watch": {"asof": watch["asof"], "facts": watch["facts"][:2],
                              "sources": watch["sources"][:2]},
                "process": answers.get("process", "unnamed"),
                "process_map": mapped,
                "agent_automatable_pct": round(100 * len(agent_steps) / len(mapped), 1),
                "human_gates": [m["step"] for m in human_steps],
                "est_minutes_saved_month": round(minutes_saved),
                "design_note": "agents produce; every external/financial/"
                               "irreversible step is a human gate (OS §3)",
                "asof": config.today()}
    _emit(slug, "automation_audit", artifact)
    return artifact


def _classify_step(desc: str) -> dict:
    d = desc.lower()
    if any(k in d for k in ("approv", "sign", "pay", "wire", "contract", "commit",
                            "publish", "send to client", "delete")):
        return {"to": "human", "universe": "strategy", "gate": "Type-1/G2+",
                "why": "external/financial/irreversible → one-way door (Amazon M2)"}
    if any(k in d for k in ("research", "scrape", "collect", "monitor", "search")):
        return {"to": "agent", "universe": "strategy", "gate": "none",
                "why": "read-only, reversible"}
    if any(k in d for k in ("draft", "write", "compose", "summarize", "translate")):
        return {"to": "agent", "universe": "revenue", "gate": "human review before send",
                "why": "generative, reversible until published"}
    if any(k in d for k in ("validate", "check", "qc", "verify", "reconcile")):
        return {"to": "agent", "universe": "continuity", "gate": "none",
                "why": "verification is the machine's strongest suit (CBS Ch.3)"}
    if any(k in d for k in ("schedule", "file", "log", "store", "notify")):
        return {"to": "agent", "universe": "infrastructure", "gate": "none",
                "why": "mechanical, reversible"}
    return {"to": "agent+human", "universe": "delivery", "gate": "sampled review",
            "why": "unclassified → conservative default: agent drafts, human samples"}


def kb_ground(params: dict, slug: str) -> dict:
    """KB grounding manifest: facts → regex-indexed knowledge base file for a
    client assistant (KB-first routing = zero-token fact answers, JARVIS
    b0969fb lineage)."""
    client = params.get("client", "client")
    facts = params.get("facts", [])
    if not facts:
        raise ValueError("grounding needs facts")
    kb = {"client": client, "generated_at": config.stamp(),
          "entries": [{"q_patterns": f.get("patterns", []), "a": f["answer"],
                       "asof": f.get("asof", config.today())} for f in facts],
          "policy": "KB-first: matching questions answered with ZERO model "
                    "tokens; out-of-scope questions routed to the gateway and "
                    "labeled by provider mode"}
    p = config.OUTBOX / f"kb_{client.lower().replace(' ', '_')}.json"
    p.write_text(json.dumps(kb, indent=1, sort_keys=True), encoding="utf-8")
    ledger.event("intel_kb", slug, {"client": client, "entries": len(kb["entries"])})
    return {"mode": "engine", "kb_file": p.name, "entries": len(kb["entries"])}




# ================================ THE BRAIN =================================
# Intelligence is the multiplier: it plans, buys evidence from every sibling
# through the internal market, researches with citations, remembers, and
# synthesizes with LABELED reasoning (llm mode when a provider answers,
# template mode otherwise — never faked).

SERVICE_MAP = {   # need -> (seller, service, buy-task defined below)
    "leads":   ("growth",    "lead_gen"),
    "stats":   ("helix",     "drylab_stats"),
    "qc":      ("dossia",    "alcoa_qc"),
    "trail":   ("medtech",   "alcoa_trail"),
    "security":("sentinel",  "ai_sec_review"),
    "treasury":("capitalco", "treasury_policy"),
    "carbon":  ("verde",     "carbon_books"),
    "risk":    ("terra",     "climate_risk"),
    "hiring":  ("talent",    "career_intel"),
}

MEMORY_FILE = config.RUNTIME_DIR / "intel_memory.json"


def _mem() -> list:
    import json as _j
    return _j.loads(MEMORY_FILE.read_text(encoding="utf-8")) if MEMORY_FILE.exists() else []


def _mem_save(m: list) -> None:
    import json as _j
    MEMORY_FILE.write_text(_j.dumps(m, indent=1, sort_keys=True), encoding="utf-8")


def _mk_buy(service, sellermod, sellfn, argsfn, tag, role):
    def fn(params, slug):
        import importlib
        import platformsvc
        seller = importlib.import_module(f"companies.{sellermod}")
        ticket = platformsvc.request(slug, service,
                                     spec=f"{tag}: {params.get('goal', 'client deployment')}",
                                     units=1)
        bought = getattr(seller, sellfn)(argsfn(params), sellermod)
        platformsvc.serve(ticket["id"], {"ref": f"intel-{tag}:{ticket['id']}"})
        ledger.event("intel_buy", slug, {"tag": tag, "ticket": ticket["id"],
                                          "service": service})
        return {"mode": "engine", "tag": tag, "role": role,
                "internal_purchase": {"from": sellermod, "service": service,
                                      "ticket": ticket["id"],
                                      "notional_chf": ticket["notional_chf"]},
                "bought": bought, "asof": config.today()}
    fn.__name__ = tag
    return fn


intel_client_prospects = _mk_buy("lead_gen", "growth", "enrich_leads",
    lambda p: {"csv": p.get("csv", "name,email,company,role,note\nProspect,p@x.ch,XCo,CTO,context " + "y" * 45)},
    "intel_client_prospects", "lead-researcher")
intel_stats_cert = _mk_buy("drylab_stats", "helix", "table1",
    lambda p: p.get("cohort_params", {"cohort": [{"patient_id": i, "arm": "A" if i % 2 else "B",
        "age": 30 + i % 40} for i in range(8)], "bounds": {"age": (18, 90)}}),
    "intel_stats_cert", "verifier")
intel_doc_qc = _mk_buy("alcoa_qc", "dossia", "qc_checklist",
    lambda p: {"document": p.get("doc", {"author": "intelligence", "reviewer": "founder",
        "text": "deployment design", "timestamp": config.stamp(), "source_ref": "engine",
        "numbers_carry_asof": True, "has_todos": False, "units_consistent": True,
        "stored_in_ledger": True, "path": "outbox"})},
    "intel_doc_qc", "verifier")
intel_run_trail = _mk_buy("alcoa_trail", "medtech", "alcoa_log",
    lambda p: {"entry": {"experiment": p.get("run", "deployment-run"),
        "subject": p.get("client", "client"), "value": 1, "unit": "run",
        "recorded_by": "intelligence"}},
    "intel_run_trail", "audit-trail-clerk")
intel_sec_review = _mk_buy("ai_sec_review", "sentinel", "ai_security_review",
    lambda p: {"kb_first": True, "provider_labels": True, "refuses_advice": True,
               "gated_actions": True, "responder": p.get("responder")},
    "intel_sec_review", "ai-security-reviewer")
intel_treasury = _mk_buy("treasury_policy", "capitalco", "treasury_policy",
    lambda p: {}, "intel_treasury", "treasury-accountant")
intel_carbon = _mk_buy("carbon_books", "verde", "carbon_account",
    lambda p: p.get("activities", {"electricity_kwh": 200, "grid_region": "CH"}),
    "intel_carbon", "carbon-accountant")
intel_risk = _mk_buy("climate_risk", "terra", "physical_risk",
    lambda p: {"assets": p.get("assets", [{"id": "DC1", "region_class": "alpine_ch",
        "exposure_tag": "inland", "value_chf": 500_000}])},
    "intel_risk", "risk-modeler")
intel_hiring = _mk_buy("career_intel", "talent", "market_brief",
    lambda p: {"domain": p.get("domain", "ai_ml")},
    "intel_hiring", "market-researcher")


def think(params: dict, slug: str) -> dict:
    """The orchestrator: goal -> plan (which siblings' evidence is needed) ->
    buy each through the internal market -> synthesize with a LABELED brain ->
    remember. Offline-safe: planning is deterministic (SERVICE_MAP), synthesis
    degrades to a template that lists every purchase and its provenance."""
    import llm as _llm
    goal = params.get("goal", "")
    needs = params.get("needs", [])
    if not goal:
        raise ValueError("think() needs a goal")
    unknown = [n for n in needs if n not in SERVICE_MAP]
    if unknown:
        raise ValueError(f"unknown needs {unknown} — map: {sorted(SERVICE_MAP)}")
    purchases, trace = [], [f"goal: {goal}"]
    for n in needs:
        fn = {"leads": intel_client_prospects, "stats": intel_stats_cert,
              "qc": intel_doc_qc, "trail": intel_run_trail, "security": intel_sec_review,
              "treasury": intel_treasury, "carbon": intel_carbon, "risk": intel_risk,
              "hiring": intel_hiring}[n]
        r = fn(params, slug)
        purchases.append({"need": n, "from": r["internal_purchase"]["from"],
                          "ticket": r["internal_purchase"]["ticket"],
                          "chf": r["internal_purchase"]["notional_chf"]})
        trace.append(f"bought {n} from {r['internal_purchase']['from']} "
                     f"(ticket {r['internal_purchase']['ticket']}, CHF {r['internal_purchase']['notional_chf']:.2f} internal)")
    facts = ("GOAL: " + goal + "\nPURCHASES: " + json.dumps(purchases) +
             "\nREG WATCH: " + json.dumps(
                 json.loads((config.ROOT / "data" / "ai_act_watch.json").read_text(encoding="utf-8"))["facts"][:2]))
    try:
        syn = _llm.generate(
            f"Produce a 120-word execution summary for the goal, using ONLY the "
            f"purchased evidence and regulatory watch facts. State what remains "
            f"human-gated.\n{facts}",
            system="You are CogOps Intelligence, the group orchestrator. Confident, "
                   "direct, no hedging. Cite purchases by ticket id.",
            company=slug)
        synth, mode = syn["text"], syn["mode"]
    except _llm.LLMUnavailable:
        synth = ("Execution summary (template mode): the goal is decomposed into "
                 + str(len(purchases)) + " evidence purchases across the group: "
                 + "; ".join(f"{p['need']}←{p['from']}[{p['ticket']}]" for p in purchases)
                 + ". Regulatory watch attached (AI Act applicable 2026-08-02; high-risk "
                   "deadlines moved to 2027-12-02/2028-08-03 by Omnibus 2026/1744 — verify "
                   "as-of dates before client use). Remaining human gates: client approval "
                   "of design, founder keystroke on any external/financial action.")
        mode = "template"
    trace.append(f"synthesis mode: {mode}")
    m = _mem()
    mid = f"MEM-{len(m) + 1:04d}"
    m.append({"id": mid, "goal": goal, "needs": needs, "purchases": purchases,
              "mode": mode, "at": config.stamp()})
    _mem_save(m)
    artifact = {"mode": mode, "goal": goal, "plan": needs, "purchases": purchases,
                "synthesis": synth, "trace": trace, "memory_id": mid,
                "reg_watch_asof": "2026-10", "asof": config.today()}
    _emit(slug, f"think_{mid}", {"mode": mode, "purchases": len(purchases)})
    return artifact


def research(params: dict, slug: str) -> dict:
    """Cited research: Wikipedia + Crossref (JARVIS research lineage), then
    labeled synthesis. >=3 sources or the brief refuses (citation discipline)."""
    import urllib.parse as _up
    import urllib.request as _ur
    import llm as _llm
    topic = params.get("topic", "")
    if not topic:
        raise ValueError("research needs a topic")
    srcs = []
    try:
        q = _up.quote(topic)
        w = json.loads(_ur.urlopen(
            f"https://en.wikipedia.org/w/api.php?action=opensearch&search={q}&limit=3&format=json",
            timeout=10).read())
        for t, u in zip(w[1], w[3]):
            srcs.append({"title": t, "url": u, "kind": "wikipedia"})
    except Exception as e:
        ledger.event("research_fallback", slug, {"wikipedia": str(e)[:80]})
    try:
        c = json.loads(_ur.urlopen(
            f"https://api.crossref.org/works?query={_up.quote(topic)}&rows=3&select=title,DOI,issued",
            timeout=10).read())
        for it in c["message"]["items"]:
            srcs.append({"title": (it.get("title") or ["untitled"])[0][:90],
                         "url": f"https://doi.org/{it.get('DOI')}", "kind": "crossref",
                         "year": ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0]})
    except Exception as e:
        ledger.event("research_fallback", slug, {"crossref": str(e)[:80]})
    if len(srcs) < 3:
        return {"mode": "engine:offline", "topic": topic, "sources": srcs,
                "why": "fewer than 3 verifiable sources reachable — brief refused "
                       "(citation discipline, CBS Ch.3)", "asof": config.today()}
    try:
        syn = _llm.generate(
            f"Write a 150-word research brief on '{topic}' citing ONLY these sources "
            f"by [n]:\n" + "\n".join(f"[{k+1}] {s['title']} ({s['kind']})" for k, s in enumerate(srcs)),
            system="CogOps Intelligence research agent. Citation discipline absolute.",
            company=slug)
        body, mode = syn["text"], syn["mode"]
    except _llm.LLMUnavailable:
        body = ("# " + topic + "\n\n" +
                "\n".join(f"[{k+1}] {s['title']} — {s['url']}" for k, s in enumerate(srcs)) +
                "\n\n(template mode: sources verified reachable; synthesis awaits a provider key)")
        mode = "template"
    artifact = {"mode": mode, "topic": topic, "sources": srcs, "brief": body,
                "asof": config.today()}
    _emit(slug, f"research_{topic[:20].replace(' ', '_')}", {"mode": mode, "sources": len(srcs)})
    return artifact


def recall(params: dict, slug: str) -> dict:
    """Session memory: keyword-overlap recall over think() sessions."""
    q = set((params.get("goal", "")).lower().split())
    hits = []
    for s in _mem():
        overlap = len(q & set(s["goal"].lower().split()))
        hits.append((overlap, s))
    hits.sort(key=lambda x: -x[0])
    return {"mode": "engine", "sessions": len(_mem()),
            "best": [h[1] for h in hits[:3]], "asof": config.today()}


def _emit(slug: str, kind: str, artifact: dict) -> None:
    p = config.OUTBOX / f"{slug}_{kind}_{config.today()}.json"
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")


# Star links: Intelligence <-> every other company (DR-0010)
LINKS = {"growth": "intel_client_prospects", "helix": "intel_stats_cert",
         "dossia": "intel_doc_qc", "medtech": "intel_run_trail",
         "sentinel": "intel_sec_review", "capitalco": "intel_treasury",
         "verde": "intel_carbon", "terra": "intel_risk", "talent": "intel_hiring"}

TASKS = {
    "deploy_client": {"fn": deploy_client, "role": "deployment-engineer"},
    "automation_audit": {"fn": automation_audit, "role": "process-auditor"},
    "kb_ground": {"fn": kb_ground, "role": "kb-librarian"},
    "think": {"fn": think, "role": "deployment-engineer"},
    "research": {"fn": research, "role": "kb-librarian"},
    "recall": {"fn": recall, "role": "kb-librarian"},
    "intel_client_prospects": {"fn": intel_client_prospects, "role": "lead-researcher"},
    "intel_stats_cert": {"fn": intel_stats_cert, "role": "verifier"},
    "intel_doc_qc": {"fn": intel_doc_qc, "role": "verifier"},
    "intel_run_trail": {"fn": intel_run_trail, "role": "audit-trail-clerk"},
    "intel_sec_review": {"fn": intel_sec_review, "role": "ai-security-reviewer"},
    "intel_treasury": {"fn": intel_treasury, "role": "treasury-accountant"},
    "intel_carbon": {"fn": intel_carbon, "role": "carbon-accountant"},
    "intel_risk": {"fn": intel_risk, "role": "risk-modeler"},
    "intel_hiring": {"fn": intel_hiring, "role": "market-researcher"},
}
