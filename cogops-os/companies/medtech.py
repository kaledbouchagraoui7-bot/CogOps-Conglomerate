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
                    "verifier", "process-auditor"],
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


def _emit(slug: str, kind: str, artifact: dict) -> None:
    p = config.OUTBOX / f"{slug}_{kind}_{config.today()}.json"
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")


TASKS = {
    "mdr_doc_tree": {"fn": mdr_doc_tree, "role": "mdr-documenter"},
    "alcoa_log": {"fn": alcoa_log, "role": "audit-trail-clerk"},
    "imaging_pipeline_spec": {"fn": imaging_pipeline_spec, "role": "process-auditor"},
}
