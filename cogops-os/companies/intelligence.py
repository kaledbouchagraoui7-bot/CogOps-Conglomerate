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
                    "site-factory-engineer", "process-auditor"],
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
    artifact = {"mode": "engine",
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


def _emit(slug: str, kind: str, artifact: dict) -> None:
    p = config.OUTBOX / f"{slug}_{kind}_{config.today()}.json"
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")


TASKS = {
    "deploy_client": {"fn": deploy_client, "role": "deployment-engineer"},
    "automation_audit": {"fn": automation_audit, "role": "process-auditor"},
    "kb_ground": {"fn": kb_ground, "role": "kb-librarian"},
}
