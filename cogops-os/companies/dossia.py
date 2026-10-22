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
                    "literature-synthesizer", "audit-trail-clerk", "verifier"],
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


def _emit(slug: str, kind: str, artifact: dict) -> None:
    p = config.OUTBOX / f"{slug}_{kind}_{config.today()}.json"
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")


TASKS = {
    "m4_assemble": {"fn": m4_assemble, "role": "dossier-assembler"},
    "surveillance_feed": {"fn": surveillance_feed, "role": "regulatory-monitor"},
    "qc_checklist": {"fn": qc_checklist, "role": "verifier"},
}
