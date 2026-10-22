# CogOps Helix — Offer, Sales Routine & Delivery Procedures

> Mirror of `growth/OFFER.md` for the dry-lab company. Landing live: https://cogops-helix.pages.dev · Engines: `../cogops-os/companies/helix.py` · Governance: `../structure/decisions.md` DR-0006.

## 1. ICP
**Primary:** academic labs and biotech startups (CH/DACH/EU) with wet-lab strength and no bioinformatician on staff — they have sequences and cohorts, not analysis capacity.
**Secondary:** CROs and regulatory consultancies with overflow QC/EDA/literature work and hard deadlines.
**Disqualified:** anyone wanting a scientific signature, authorship, or wet-lab work — refused and referred (boundary is the product).

## 2. Offer ladder
| Rung | Offer | Price | Purpose |
|---|---|---|---|
| 0 | **Free QC report — one sequence, 48 h** (FASTA + expected values in, branded report out) | CHF 0 | proof of pipeline quality |
| 1 | QC pack | CHF 120 / sequence | first franc |
| 2 | QC batch of 10 | CHF 900 | volume entry |
| 3 | Cohort EDA + regulatory Table 1 + reproducibility pack | CHF 2,400 / study | flagship |
| 4 | Literature surveillance feed | CHF 300 / topic / month | recurring |
| 5 | Evidence matrix (IB/RIM-ready) | CHF 1,200 | regulatory add-on |

Guarantee: **if our pipeline cannot reproduce its own delivered artifact byte-identically on request within 14 days, the re-run is free or the study fee is refunded.**

## 3. Sales routine (weekly quota)
- **10 outreach touches/week** to lab heads/CRO project leads (touch sequence 0/+3/+7 via `growth touch_draft` pattern; human sends only).
- **3 free QC samples/week** cap (protects the 48 h promise).
- Channels: preprint servers' corresponding authors with QC-adjacent needs, lab websites (sourced via `growth source_leads`-style provenance fetching, validated before any touch), conference attendee lists where publicly posted, referrals from Dossia's regulatory network (internal pull at DR-0002 prices).
- Every touch logged in CRM; quota adherence reviewed weekly (`quota_status`).

## 4. Delivery procedures
### 4.1 Sequence QC
1. Intake: FASTA + expected values + NDA if requested (human, 15 min).
2. Agents run `sequence_qc` (GC, ORF both strands, cross-check gates); evidence per record.
3. Human review: QC table + gate outcomes read before delivery (100% first 10 reports, then 20% sample).
4. Deliverable: `helix_report_html` branded report (violet theme, version hash, methods, human-of-record line). Turnaround 48 h.
### 4.2 EDA + Table 1
1. Intake: cohort file + spec (bounds, arms, fields) — human signs the spec with client.
2. Agents run `table1`: audit-trailed cleaning (dedupe/range/imputation logged per row), Welch/χ² (NR-validated <1e-9 vs SciPy).
3. Human review: audit trail + table read end-to-end before delivery (always, for studies).
4. Deliverable: report + reproducibility pack (seed, inputs hash, environment note). Turnaround 5 business days.
### 4.3 Surveillance feed
1. Intake: topic + relevance keywords.
2. Agents run `lit_surveil` weekly (PubMed primary, EuropePMC fallback, PMID/DOI traceability); RA-filter for regulatory clients via Dossia hand-off.
3. Human review: first issue 100%, then sampled; feed never ships partial (pipeline refuses by design).
4. Deliverable: monthly digest + live matrix. Cadence weekly computation, monthly delivery unless client asks weekly.

## 5. Handover & compliance
Deliverables by email + ledger-recorded version hashes; client PI signs scientifically (human-of-record field on every artifact); sequences deleted ≤30 days post-project (privacy page promise); NDA-first transfer on request. Group Terms v1.0 apply (linked from site).

## 6. Validation plan (DR-0006)
90-day window from 2026-10-22: **100 waitlist signups OR 3 pre-orders OR CHF 200+ paid** (evidence via landing counter/export). Miss ⇒ kill review as KILL_WIN. First franc target: one CHF 120 QC pack or one feed month.
