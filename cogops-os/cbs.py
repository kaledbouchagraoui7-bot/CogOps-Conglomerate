"""CBS — the CogOps Business System (OS §10): culture as a deployable,
versioned artifact (Danaher DBS translation). Chapters live in `cbs/*.md`;
this module versions them, loads immersion packs, and runs the verification
protocol (the FIXES-method: reproduce → fix → verify, with evidence).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import config
import ledger

CBS_DIR = config.ROOT / "cbs"
VERSION_FILE = config.RUNTIME_DIR / "cbs_version.json"
VERIFICATION_FILE = config.RUNTIME_DIR / "verification_log.jsonl"

CHAPTERS = ("birth", "build", "verify", "operate", "money", "kill", "law")


def version() -> dict:
    """CBS version = hash of all chapter files — any amendment changes it
    (change control, OS §15: versioned like software)."""
    h = hashlib.sha256()
    per = {}
    for ch in CHAPTERS:
        p = CBS_DIR / f"{ch}.md"
        blob = p.read_bytes() if p.exists() else b""
        per[ch] = hashlib.sha256(blob).hexdigest()[:12]
        h.update(blob)
    v = {"cbs_version": h.hexdigest()[:12], "chapters": per,
         "checked_at": config.stamp()}
    VERSION_FILE.write_text(json.dumps(v, indent=1, sort_keys=True), encoding="utf-8")
    return v


def immersion(slug: str, dan: str, company_kb: str = "") -> dict:
    """A squad is not formed until CBS + dan + KB are loaded (OS §10
    immersion-on-entry). Returns the context pack; records the event."""
    pack = {"slug": slug, "dan": dan, "company_kb": company_kb,
            "cbs": version(),
            "chapters_loaded": [ch for ch in CHAPTERS
                                if (CBS_DIR / f"{ch}.md").exists()],
            "owner_manual": (config.ROOT.parent / "structure" /
                             "OPERATING-STRUCTURE.md").exists(),
            "loaded_at": config.stamp()}
    ledger.event("cbs_immersion", slug, {"cbs_version": pack["cbs"]["cbs_version"],
                                         "chapters": len(pack["chapters_loaded"])})
    return pack


def chapter(name: str) -> str:
    p = CBS_DIR / f"{name}.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


# ------------------------------------------- verification protocol (Ch. 3) --
def verify(subject: str, claim: str, reproduce, expected) -> dict:
    """FIXES-method instrument: every defect/claim is reproduced first, then
    verified after the fix, with an evidence entry. `reproduce` is a callable
    returning the observed value; `expected` a value or predicate."""
    observed = reproduce()
    ok = expected(observed) if callable(expected) else observed == expected
    rec = {"subject": subject, "claim": claim, "observed": observed,
           "expected": expected if not callable(expected) else "predicate",
           "ok": bool(ok), "at": config.stamp()}
    with open(VERIFICATION_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, default=str) + "\n")
    ledger.event("verification", subject, {"ok": rec["ok"], "claim": claim[:80]})
    return rec


def verification_log() -> list[dict]:
    if not VERIFICATION_FILE.exists():
        return []
    return [json.loads(l) for l in
            VERIFICATION_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]


def asof_rule(number, asof: str, source: str) -> str:
    """Invariant I11 as a function: every published number carries as-of + source."""
    return f"{number} (as of {asof}; source: {source})"
