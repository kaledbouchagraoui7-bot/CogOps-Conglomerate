"""CogOps Dossia — regulatory affairs, medical writing & clinical-research
support (OS §13; blueprint co. 5; Swiss domain #9, gap 7.0).

Seed: portfolio pipeline 03 + ICH/ALCOA+ engineering. Engines: ICH M4 dossier
assembly (module tree from data/ich_m4_modules.json), regulatory surveillance
feeds (reuses Helix's PMID-traceable engine with RA filters), ALCOA+ QC
checklist. Boundary: never the signatory — every deliverable routes through
the client's qualified RA/medical lead (human-of-record).
"""
from __future__ import annotations

import json

import config
import ledger

META = {
    "name": "CogOps Dossia",
    "dan": "RA teams get ICH-grade dossiers, CSR statistics and surveillance "
           "feeds at machine cost; a qualified human of record always signs.",
    "stage_at_v10": 1,
    "seed_assets": "portfolio pipeline 03 (PMID-traceable synthesis), FIXES.md discipline",
    "human_of_record": "client's qualified RA/medical lead — always",
    "input_metrics": [
        {"key": "dossiers_delivered_month", "layer": "F", "owner": "dossier-assembler", "floor": 1},
        {"key": "qc_pass_rate_pct", "layer": "Q", "owner": "verifier", "floor": 95},
        {"key": "surveillance_feeds_live", "layer": "P", "owner": "regulatory-monitor", "floor": 1},
    ],
    "squad_roles": ["dossier-assembler", "regulatory-monitor",
                    "literature-synthesizer", "audit-trail-clerk", "verifier",
                    "treasury-accountant",
                    "ai-security-reviewer"],
}

ALCOA_PLUS = ("attributable", "legible", "contemporaneous", "original",
              "accurate", "complete", "consistent", "enduring", "available")


def m4_assemble(params: dict, slug: str) -> dict:
    """CTD module tree → dossier pack: markdown document skeleton per module,
    populated where content is supplied, TODO-marked where not (never invent
    regulatory content — the human of record fills clinical claims)."""
    tree = json.loads((config.ROOT / "data" / "ich_m4_modules.json")
                      .read_text(encoding="utf-8"))
    content = params.get("content", {})       # {"2.3": "...", "3.2.P.1": "..."}
    product = params.get("product", "PRODUCT")
    docs = []
    for mod in tree["modules"]:
        cid = mod["id"]
        body = content.get(cid)
        docs.append({"module": cid, "title": mod["title"],
                     "status": "drafted" if body else "skeleton_todo",
                     "content": body or f"<!-- {mod['title']} — to be authored by "
                                        f"the human of record; Dossia provides "
                                        f"structure, statistics and citations -->"})
    manifest = {"product": product, "standard": "ICH M4 (CTD)",
                "modules_total": len(docs),
                "drafted": sum(1 for d in docs if d["status"] == "drafted"),
                "asof": config.today(),
                "signoff_required_by": META["human_of_record"]}
    artifact = {"mode": "engine", "manifest": manifest, "documents": docs}
    _emit(slug, f"m4_{product.lower()}", artifact)
    return artifact


def surveillance_feed(params: dict, slug: str) -> dict:
    """Regulatory intelligence feed = Helix lit_surveil + RA relevance filter +
    evidence matrix. One live feed per product area (input metric)."""
    from companies import helix
    topic = params.get("topic", "CFTR modulator therapy safety")
    res = helix.lit_surveil({"query": topic, "max": params.get("max", 15)}, slug)
    kw = params.get("relevance_keywords",
                    ["safety", "adverse", "approval", "guideline", "interaction"])
    if res.get("records"):
        res["ra_filtered"] = [r for r in res["records"]
                              if any(k in (r.get("title") or "").lower() for k in kw)]
    res["feed"] = {"topic": topic, "cadence": "weekly",
                   "consumer": "regulatory-monitor", "asof": config.today()}
    ledger.event("dossia_feed", slug, {"topic": topic, "n": res.get("n", 0)})
    return res


def qc_checklist(params: dict, slug: str) -> dict:
    """ALCOA+ conformance QC on a delivered document/dataset."""
    doc = params.get("document", {})
    checks = {}
    checks["attributable"] = bool(doc.get("author") and doc.get("reviewer"))
    checks["legible"] = bool(doc.get("text", "").strip())
    checks["contemporaneous"] = bool(doc.get("timestamp"))
    checks["original"] = bool(doc.get("source_ref"))
    checks["accurate"] = doc.get("numbers_carry_asof", False)
    checks["complete"] = not doc.get("has_todos", True)
    checks["consistent"] = doc.get("units_consistent", False)
    checks["enduring"] = bool(doc.get("stored_in_ledger"))
    checks["available"] = bool(doc.get("path"))
    passed = sum(checks.values())
    rate = round(100.0 * passed / len(checks), 1)
    artifact = {"mode": "engine", "checks": checks, "pass_rate_pct": rate,
                "verdict": "PASS" if rate >= 95 else "REVIEW",
                "standard": "ALCOA+", "asof": config.today()}
    _emit(slug, "qc", artifact)
    return artifact




def dossier_with_stats(params: dict, slug: str) -> dict:
    """K5 link H-D: dossia buys drylab_stats FROM Helix via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on dossia's P&L (I7)."""
    import platformsvc
    from companies import helix as seller
    ticket = platformsvc.request(slug, "drylab_stats", spec="validated stats for CTD 2.7/5.3", units=1)
    bought = seller.table1(params.get("cohort_params", {"cohort": params.get("cohort", []), "bounds": params.get("bounds", {"age": (18, 90)})}), "helix")
    platformsvc.serve(ticket["id"], {"ref": f"dossia-dossier_with_stats:{ticket['id']}"})
    out = m4_assemble(params, slug)
    out["internal_purchase"] = {"from": "Helix", "service": "drylab_stats",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["statistics annex"] = {"tests": bought.get("tests"), "audit_actions": len(bought.get("audit_trail", [])), "ticket_ref": ticket["id"]}
    return out



def combo_dossier(params: dict, slug: str) -> dict:
    """K5 link D-M: dossia buys mdr_tree FROM Medtech via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on dossia's P&L (I7)."""
    import platformsvc
    from companies import medtech as seller
    ticket = platformsvc.request(slug, "mdr_tree", spec="MDR tree for device-combination module", units=1)
    bought = seller.mdr_doc_tree({"device": params.get("device", "ComboDev"), "risk_class": params.get("risk_class", "IIb")}, "medtech")
    platformsvc.serve(ticket["id"], {"ref": f"dossia-combo_dossier:{ticket['id']}"})
    out = m4_assemble(params, slug)
    out["internal_purchase"] = {"from": "Medtech", "service": "mdr_tree",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["mdr_annex"] = {"gaps": bought["gaps"], "sections": len(bought["sections"]), "ticket_ref": ticket["id"]}
    return out



def treasury_setup(params: dict, slug: str) -> dict:
    """K5 link D-C: dossia buys treasury_policy FROM Capital via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on dossia's P&L (I7)."""
    import platformsvc
    from companies import capitalco as seller
    ticket = platformsvc.request(slug, "treasury_policy", spec="treasury policy for Dossia sweep", units=1)
    bought = seller.treasury_policy({}, "capitalco")
    platformsvc.serve(ticket["id"], {"ref": f"dossia-treasury_setup:{ticket['id']}"})
    out = {"mode":"engine","company":"dossia"}
    out["internal_purchase"] = {"from": "Capital", "service": "treasury_policy",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["policy"] = bought["policy"]
    return out



def secure_portal(params: dict, slug: str) -> dict:
    """K5 link D-S: dossia buys ai_sec_review FROM Sentinel via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on dossia's P&L (I7)."""
    import platformsvc
    from companies import sentinel as seller
    ticket = platformsvc.request(slug, "ai_sec_review", spec="security review of client portal", units=1)
    bought = seller.ai_security_review({"kb_first":True,"provider_labels":True,"refuses_advice":True,"gated_actions":True}, "sentinel")
    platformsvc.serve(ticket["id"], {"ref": f"dossia-secure_portal:{ticket['id']}"})
    out = {"mode":"engine","company":"dossia"}
    out["internal_purchase"] = {"from": "Sentinel", "service": "ai_sec_review",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["security"] = {"config": bought["config_checks"], "ticket_ref": ticket["id"]}
    return out



def intelligence_ops(params: dict, slug: str) -> dict:
    """Star link: this company buys Intelligence's deployment/automation service
    via internal ticket (ai_ops, DR-0010 price)."""
    import platformsvc
    from companies import intelligence as intel
    kind = params.get("kind", "automation_audit")
    ticket = platformsvc.request(slug, "ai_ops", spec=f"{kind} for {slug}", units=1)
    if kind == "deploy":
        out = intel.deploy_client({"client": params.get("client", f"{slug}-client"),
                                   "services": params.get("services",
                                       ["site_factory", "llm_gateway", "crm_portal"])},
                                  "intelligence")
    else:
        out = intel.automation_audit({"answers": params.get("answers", {
            "process": f"{slug} delivery", "volume_month": 20, "minutes_per": 30,
            "steps": ["collect client inputs", "draft deliverable", "human review",
                      "approve delivery", "send to client"]})}, "intelligence")
    platformsvc.serve(ticket["id"], {"ref": f"{slug}-intel:{ticket['id']}"})
    return {"mode": "engine", "kind": kind,
            "internal_purchase": {"from": "intelligence", "service": "ai_ops",
                                  "ticket": ticket["id"],
                                  "notional_chf": ticket["notional_chf"]},
            "result": out, "asof": config.today()}


def _emit(slug: str, kind: str, artifact: dict) -> None:
    p = config.OUTBOX / f"{slug}_{kind}_{config.today()}.json"
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")


# K5 clique links: partner -> OUR buying task (complete graph, DR-0009)
LINKS = {"intelligence": "intelligence_ops", 'helix': 'dossier_with_stats', 'medtech': 'combo_dossier', 'capitalco': 'treasury_setup', 'sentinel': 'secure_portal'}

TASKS = {
    "intelligence_ops": {"fn": intelligence_ops, "role": "dossier-assembler"},
    "dossier_with_stats": {"fn": dossier_with_stats, "role": "dossier-assembler"},
    "combo_dossier": {"fn": combo_dossier, "role": "dossier-assembler"},
    "treasury_setup": {"fn": treasury_setup, "role": "treasury-accountant"},
    "secure_portal": {"fn": secure_portal, "role": "ai-security-reviewer"},
    "m4_assemble": {"fn": m4_assemble, "role": "dossier-assembler"},
    "surveillance_feed": {"fn": surveillance_feed, "role": "regulatory-monitor"},
    "qc_checklist": {"fn": qc_checklist, "role": "verifier"},
}
