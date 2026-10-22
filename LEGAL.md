# LEGAL & REGISTRATION CHECKLIST — CogOps Group (living document)

> Owner split: **YOU** = real-world execution · **ME** = drafts/code · **DONE ✓** shipped.
> Cross-refs: `research/09-swiss-holding-law.md` (law frame) · `structure/decisions.md` DR-0004 (entity doctrine) · `ROADMAP.md` §1.
> **Not legal advice** — the fiduciary/lawyer rows exist to be booked, not skipped.

## A. Before the first franc (now → first revenue)
| # | Item | Owner | Status |
|---|---|---|---|
| A1 | Impressum + privacy live with honest "entity in formation" disclosure | ME | DONE ✓ (growth site) |
| A2 | Client **terms of service** draft: liability cap, IP assignment of deliverables, replacement guarantee (14 d), cancellation (monthly), governing law CH, place of jurisdiction | ME draft → YOU/lawyer | next |
| A3 | **DPA template** (nFADP + GDPR Art. 28): processors = Cloudflare, Supabase, OpenRouter; sub-processor list; deletion ≤30 d | ME draft → YOU/lawyer | next |
| A4 | Data-processing register (RoPA/VVT, nDSG Art. 12): one row per data flow (signups KV, CRM Supabase, ledgers runtime, KV portal) | ME draft | next |
| A5 | Records-retention policy: commercial records 10 y (OR 958f); client data per DPA; ledgers append-only | ME draft | next |
| A6 | Trademark "CogOps" + word/figurative mark (IPI, ~CHF 550/10 y, classes 9/35/42) + EUIPO if EU-facing | YOU | queued |
| A7 | Domains: cogops.ch / cogops.com / cogops.group (registrar, 2 y) | YOU | queued |

## B. At first real revenue / first liability-bearing contract
| # | Item | Owner | Status |
|---|---|---|---|
| B1 | **Found CogOps Group GmbH** (CHF 20k paid-in; statutes, notary, commercial-register application, signatory rules; beneficial-owner report per GwG) | YOU (notary 1–2 wks) | trigger-based (DR-0004) |
| B2 | UID (enterprise ID) arrives with register entry; put it on imprint + invoices | YOU | post-B1 |
| B3 | AHV/IV: self-employed status ruling (SVA) now; employee registrations with first hire | YOU | ruling recommended early |
| B4 | **Professional liability insurance** (priority Sentinel/Dossia/Capital scopes) + cyber | YOU | quotes post-B1 |
| B5 | Group bank account; QR-bill reconciliation wired to cost centres | YOU + ME | post-B1 |
| B6 | Fiduciary engaged: bookkeeping, chart of accounts = 10 cost centres, annual accounts | YOU | pick now, engage post-B1 |

## C. Thresholds that trigger obligations (watch list)
| Trigger | Obligation | Owner |
|---|---|---|
| Global turnover > **CHF 100k/yr** | VAT (MWST) registration, 8.1% std; quarterly filings; prices then incl./excl. labeled | YOU/fiduciary |
| EU B2C digital sales > **€10k/yr** | EU VAT via OSS in an EU member state | fiduciary |
| First employee | UVG accident insurance, 2nd-pillar pension (BVG), payroll withholding, work-time records | YOU/fiduciary |
| A subsidiary hits a spin-out trigger (DR-0004) | new GmbH under holding; participation exemption ≥10% applies | YOU/fiduciary |
| Any client contract in a regulated domain | boundary check BEFORE signing: Capital (FINMA: no custody/no advice), Dossia (Swissmedic: never signatory), Medtech (MDR: research-use only), Sentinel (defensive only) | YOU/lawyer + ME checklist in contract template |

## D. Per-deliverable legal hygiene (built into engines)
- Dossia/Medtech deliverables carry the **human-of-record signoff field** in every artifact (never the signatory — invariant I12).
- Capital outputs carry "research tooling, not advice; client keys & approvals" disclaimer in every artifact.
- Verde artifacts carry placeholder-factor warnings until licensed factors replace them (CBS Ch.3).
- Terra artifacts are labeled heuristic-v0; not a rating agency (blueprint boundary).
- Growth records: public sources only; provenance per record; deletion ≤30 d; rejected records never billed (published promise).

## E. Documents the machine already produces (evidence-grade)
DONE ✓: QR-bill invoices w/ QRR reference (bank scan-check on first send) · branded version-hashed delivery reports · append-only decision & event ledgers (10-y retention applies) · delivery records w/ content hashes · validation evidence per lead record.

*Living document: amend via DR when structure changes; tick items here directly.*
