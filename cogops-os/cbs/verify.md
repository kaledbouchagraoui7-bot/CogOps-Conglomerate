# CBS Ch.3 — Verify (FIXES-method)
1. Every defect/claim: **reproduce → fix → verify**, each step with an evidence entry (`cbs.verify()` writes the log).
2. Selftest before release: each product ships a regression suite; green is a release gate, not an aspiration.
3. Determinism: artifacts carry `generated_at`; with FROZEN clock, byte-identical reruns (comp-bio lineage).
4. As-of rule (I11): every published number carries `(as of <date>; source: <ref>)`. Unverifiable ⇒ marked *(unverified)*, never propagated.
