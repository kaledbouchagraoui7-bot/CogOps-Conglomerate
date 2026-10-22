"""CogOps Medtech — MedTech R&D enablement software (OS §13; blueprint co. 6;
Swiss domain #7, gap 7.5). Engines: MDR technical-documentation tree (Annex
II/III mapped, from data/mdr_sections.json), ALCOA+ audit-trail logger for
experiment data, pre-clinical imaging-pipeline SPEC writer (research-use only
— never a medical device; client QA is the human of record).
"""
from __future__ import annotations

import json

import config
import ledger

META = {
    "name": "CogOps Medtech",
    "dan": "MedTech R&D teams offload MDR documentation burden and get "
           "audit-trailed experiment data management — software only.",
    "stage_at_v10": 0,
    "seed_assets": "CBS verification instruments; Dossia RA patterns",
    "human_of_record": "client's QA/regulatory signatory",
    "input_metrics": [
        {"key": "docs_generated_month", "layer": "F", "owner": "mdr-documenter", "floor": 1},
        {"key": "audit_trail_completeness_pct", "layer": "Q", "owner": "audit-trail-clerk", "floor": 100},
        {"key": "pilot_lois", "layer": "P", "owner": "partnership-scout", "floor": 1},
    ],
    "squad_roles": ["mdr-documenter", "audit-trail-clerk", "regulatory-monitor",
                    "verifier", "process-auditor",
                    "treasury-accountant",
                    "ai-security-reviewer"],
}


def mdr_doc_tree(params: dict, slug: str) -> dict:
    """MDR Annex II/III documentation tree for a device class: sections with
    owner placeholders, status tracking, and gap list. Generation ≠ approval:
    the client's QA signs (I12)."""
    tree = json.loads((config.ROOT / "data" / "mdr_sections.json")
                      .read_text(encoding="utf-8"))
    device = params.get("device", "DEVICE")
    klass = params.get("risk_class", "IIa")
    sections = []
    for s in tree["sections"]:
        applies = klass in s.get("classes", ["I", "IIa", "IIb", "III"])
        sections.append({"annex": s["annex"], "id": s["id"], "title": s["title"],
                         "applies_to_class": applies,
                         "status": "todo" if applies else "n/a",
                         "owner": "client-QA" if s.get("signoff") else "mdr-documenter"})
    gaps = [s["id"] for s in sections if s["status"] == "todo"]
    artifact = {"mode": "engine", "device": device, "risk_class": klass,
                "sections": sections, "applicable": len(sections) - sum(
                    1 for s in sections if not s["applies_to_class"]),
                "gaps": gaps, "signoff_by": META["human_of_record"],
                "asof": config.today()}
    _emit(slug, f"mdr_{device.lower()}", artifact)
    return artifact


def alcoa_log(params: dict, slug: str) -> dict:
    """ALCOA+ experiment-data entries: every write is attributable,
    timestamped, original-value-preserving (corrections are additions, never
    overwrites) — the audit trail IS the product."""
    entry = params.get("entry", {})
    rec = {"experiment": entry.get("experiment", "?"),
           "subject": entry.get("subject", "?"),
           "value": entry.get("value"),
           "unit": entry.get("unit", ""),
           "recorded_by": entry.get("recorded_by", "agent"),   # attributable
           "recorded_at": config.stamp(),                       # contemporaneous
           "original": True,                                    # original preserved
           "correction_of": entry.get("correction_of")}         # never overwrite
    p = config.RUNTIME_DIR / "alcoa_trail.jsonl"
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    ledger.event("alcoa_entry", slug, {"experiment": rec["experiment"]})
    return {"mode": "engine", "record": rec, "trail_lines":
            sum(1 for _ in open(p, encoding="utf-8"))}


def imaging_pipeline_spec(params: dict, slug: str) -> dict:
    """Pre-clinical imaging-analysis pipeline DESIGN (research-use): modality →
    stages (ingest, QC, preprocess, model, evaluate, report) with data-lease
    honesty: the spec is deterministic; model training is the client's, on
    their data, under their ethics approval."""
    modality = params.get("modality", "MRI")
    spec = {"modality": modality, "use": "RESEARCH ONLY — not a medical device",
            "stages": [
                {"stage": "ingest", "checks": ["DICOM conformance", "de-identification"]},
                {"stage": "qc", "checks": ["artifact scoring", "motion threshold"]},
                {"stage": "preprocess", "checks": ["registration", "normalization", modality]},
                {"stage": "model", "checks": ["train/val/test split frozen", "seed logged"]},
                {"stage": "evaluate", "checks": ["metrics pre-registered", "confidence intervals"]},
                {"stage": "report", "checks": ["limitations section mandatory",
                                               "as-of dated", "reproducibility pack"]}],
            "ethics_approval_required": True,
            "signoff_by": META["human_of_record"], "asof": config.today()}
    artifact = {"mode": "engine", "spec": spec}
    _emit(slug, f"imaging_spec_{modality.lower()}", artifact)
    return artifact




def mdr_with_evidence(params: dict, slug: str) -> dict:
    """K5 link H-M: medtech buys drylab_stats FROM Helix via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on medtech's P&L (I7)."""
    import platformsvc
    from companies import helix as seller
    ticket = platformsvc.request(slug, "drylab_stats", spec="verification evidence for MDR 6.1", units=1)
    bought = seller.sequence_qc({"fasta": params.get("fasta", ">NM_TEST\nATGGGCTAA"), "cross_checks": params.get("cross_checks", {})}, "helix")
    platformsvc.serve(ticket["id"], {"ref": f"medtech-mdr_with_evidence:{ticket['id']}"})
    out = mdr_doc_tree(params, slug)
    out["internal_purchase"] = {"from": "Helix", "service": "drylab_stats",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["verification_evidence"] = {"qc": bought["qc"], "ticket_ref": ticket["id"]}
    return out



def mdr_with_surveillance(params: dict, slug: str) -> dict:
    """K5 link D-M: medtech buys ra_feed FROM Dossia via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on medtech's P&L (I7)."""
    import platformsvc
    from companies import dossia as seller
    ticket = platformsvc.request(slug, "ra_feed", spec="MDR/PMS regulatory watch", units=1)
    bought = seller.surveillance_feed({"topic": params.get("topic", "medical device software safety"), "max": 10}, "dossia")
    platformsvc.serve(ticket["id"], {"ref": f"medtech-mdr_with_surveillance:{ticket['id']}"})
    out = mdr_doc_tree(params, slug)
    out["internal_purchase"] = {"from": "Dossia", "service": "ra_feed",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["surveillance"] = {"n": bought.get("n", 0), "feed": bought.get("feed", {}), "ticket_ref": ticket["id"]}
    return out



def treasury_setup(params: dict, slug: str) -> dict:
    """K5 link M-C: medtech buys treasury_policy FROM Capital via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on medtech's P&L (I7)."""
    import platformsvc
    from companies import capitalco as seller
    ticket = platformsvc.request(slug, "treasury_policy", spec="treasury policy for Medtech sweep", units=1)
    bought = seller.treasury_policy({}, "capitalco")
    platformsvc.serve(ticket["id"], {"ref": f"medtech-treasury_setup:{ticket['id']}"})
    out = {"mode":"engine","company":"medtech"}
    out["internal_purchase"] = {"from": "Capital", "service": "treasury_policy",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["policy"] = bought["policy"]
    return out



def secure_deployment(params: dict, slug: str) -> dict:
    """K5 link M-S: medtech buys ai_sec_review FROM Sentinel via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on medtech's P&L (I7)."""
    import platformsvc
    from companies import sentinel as seller
    ticket = platformsvc.request(slug, "ai_sec_review", spec="security review of R&D portal", units=1)
    bought = seller.ai_security_review({"kb_first":True,"provider_labels":True,"refuses_advice":True,"gated_actions":True}, "sentinel")
    platformsvc.serve(ticket["id"], {"ref": f"medtech-secure_deployment:{ticket['id']}"})
    out = {"mode":"engine","company":"medtech"}
    out["internal_purchase"] = {"from": "Sentinel", "service": "ai_sec_review",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["security"] = {"config": bought["config_checks"], "ticket_ref": ticket["id"]}
    return out

def _emit(slug: str, kind: str, artifact: dict) -> None:
    p = config.OUTBOX / f"{slug}_{kind}_{config.today()}.json"
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")


# K5 clique links: partner -> OUR buying task (complete graph, DR-0009)
LINKS = {'helix': 'mdr_with_evidence', 'dossia': 'mdr_with_surveillance', 'capitalco': 'treasury_setup', 'sentinel': 'secure_deployment'}

TASKS = {
    "mdr_with_evidence": {"fn": mdr_with_evidence, "role": "mdr-documenter"},
    "mdr_with_surveillance": {"fn": mdr_with_surveillance, "role": "regulatory-monitor"},
    "treasury_setup": {"fn": treasury_setup, "role": "treasury-accountant"},
    "secure_deployment": {"fn": secure_deployment, "role": "ai-security-reviewer"},
    "mdr_doc_tree": {"fn": mdr_doc_tree, "role": "mdr-documenter"},
    "alcoa_log": {"fn": alcoa_log, "role": "audit-trail-clerk"},
    "imaging_pipeline_spec": {"fn": imaging_pipeline_spec, "role": "process-auditor"},
}
