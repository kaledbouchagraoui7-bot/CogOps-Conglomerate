# CogOps Growth — The Offer, Sales Routine & Delivery Procedures

> The "organs" layer of the roadmap, made concrete. Landing page **live**: https://cogops-growth.pages.dev · This document is the operating playbook; the engines are in `../cogops-os/companies/growth.py`; governance numbers in `../structure/decisions.md`.

## 1. Ideal customer profile (ICP)

**Primary — outbound-hungry service businesses (DACH):** B2B agencies, consultancies, software integrators, fiduciaries/immobilier-style local B2B, 3–50 staff, someone already doing cold outreach badly (or wanting to start). Pain: list-building eats days, personalization is fake, deliverability suffers.
**Secondary — data-rich SaaS & marketplaces:** anyone sitting on a structured dataset (listings, prices, jobs, regions) that should rank on long-tail queries but has no engineering time for programmatic SEO.
**Disqualified (say no, refer elsewhere):** consumer products, crypto/gambling/adult, anyone wanting scraped *private* data, anyone wanting sends without human review (our gate is the product, not a limitation).

## 2. The offer ladder (what the landing page sells)

| Rung | Offer | Price | Purpose |
|---|---|---|---|
| 0 | **Free sample batch: 25 validated leads + per-prospect openers, 48 h** | CHF 0 | Proof before money; top-of-funnel |
| 1 | Paid lead batch | CHF 1–3 / validated lead | First franc (QR-bill invoice) |
| 2 | Lead retainer | CHF 1,500–3,500 / month | Recurring base |
| 3 | pSEO pilot (2 weeks, 1 cluster) | CHF 900 fixed | Product #2 entry |
| 4 | pSEO pages | CHF 15–60 / page, refreshed | Scales with data |
| 5 | Domain journal sponsorship | from CHF 250 / issue | Media network, later |

"Validated" is contractual: syntax-checked, deduplicated, non-disposable domain, public-source provenance per record, timestamp. Rejected records are reported and **never billed**.

## 3. Sales routine (weekly quota — the input metrics that matter)

- **20 outreach touches/week** (email or LinkedIn) to ICP-fit companies — using our own product on ourselves (the engine enriches, a human approves every send; that's the demo).
- **5 sample batches delivered/week** max (protects the 48 h promise).
- **Follow-up rule:** every sample batch gets 2 follow-ups (day +3, day +7) with one concrete addition ("here are 5 more leads for your second persona — free, because the first batch converted 0 and I want to know why").
- **Where the ICP lives:** LinkedIn (agency owners), Swiss startup directories, local B2B communities, the JARVIS reference deployment as proof-of-capability, build-in-public posts about the CogOps OS itself (the machine is the marketing).
- Every touch is logged in the CRM (Supabase `leads`/`campaigns` tables already exist); the weekly sheet reports quota adherence — misses get root-caused, not excused.

## 4. Delivery procedures (what AI does / what the human reviews / turnaround)

### 4.1 Lead batch (sample or paid)
1. **Intake** (human, 15 min): ICP form/call → written target definition (sector, role titles, geo, disqualifiers).
2. **Research & validation** (agents): `growth.enrich_leads` — parse, syntax-check, dedupe, disposable-domain screen (incl. subdomains), score 0–5, per-record provenance.
3. **Copy** (agents draft, LLM-labeled): one opener per prospect, grounded only in supplied facts; template fallback if no provider — always labeled, never faked.
4. **Human review gate (non-negotiable):** first 3 batches 100% reviewed; after 10 clean batches, sampled 20%. Reviewer signs the delivery record in the ledger.
5. **Deliverable**: branded HTML report (`lead_report_html` — themed, evidence per row, version-hashed) + CSV. Turnaround: **48 h sample / 2–4 working days paid batch**.
6. **Invoice**: Swiss QR-bill (`../tools/qr_invoice.py`), reference auto-generated, net 14 days.

### 4.2 pSEO cluster
1. Intake: data source + 20 seed queries (human, 1 h).
2. Agents: schema mapping → template build → `pseo_pages` (byte-deterministic) → sitemap → 10-page QA sample.
3. Human review: legal/impressum check, quality read of the QA sample, no-thin-content rule (each page must answer a real query).
4. Deploy via site factory to client domain/subdomain. Turnaround: **2-week pilot**, then autonomous refresh (monthly) under the same gate.

### 4.3 Domain journal issue
Agents compile + draft → human edits every issue end-to-end (editor of record = founder until a hired editor) → send. No issue ships unreviewed.

## 5. Client handover flow (until the branded portal exists)

Email delivery (branded report + CSV) → client confirms → ledger records delivery hash → invoice. Portal adaptation of the JARVIS client portal is queued in ROADMAP (Base). Deletion/objection requests: honored ≤30 days, suppression list permanent (privacy page promise).

## 6. Real-world validation plan (OS §5 Stage-1 evidence, applied for real)

The landing page **is** the validation instrument. Targets (any one suffices, 90-day window from 2026-10-22):
- **100 waitlist signups** (live counter on the page; `GET /api/count`; export via admin token), or
- **3 pre-orders** (signed intent at rung 1–3 prices), or
- **CHF 200+ paid** by an unrelated customer.

Evidence lands automatically in KV and the ledger. **Miss the window → kill review as KILL_WIN** (the OS means it). Weekly: post the counter publicly (build-in-public = distribution).

## 7. Inquiry triage — AI drafts, the founder decides (founder rule)

Every incoming request enters the **reply queue** (`cogops.py inbox`):
1. `inbox pull` fetches unseen signups from the live export and drafts a reply
   (LLM-labeled; honest template fallback — never faked).
2. The founder reviews: `inbox approve ID` (optionally `--text` to edit), or
   `inbox manual ID --text "…"` for a personally written email.
3. `inbox sent ID` records delivery after the founder pastes into mail.
**No send() function exists in the system — automated outbound mail is not a
capability.** SLA: reply within **1 business day**; sample batch within
**48 hours** of the approved target definition. Both numbers are promises on
the landing page; both are the delivery procedure, not aspirations.

## 8. What is already real (as of 2026-10-22)

- ✅ Landing + pricing + FAQ live: https://cogops-growth.pages.dev (Lovable-grade dark glass)
- ✅ Signup machine: validation, dedupe, disposable-domain screen, honeypot, per-IP rate limit, live counter, admin export (JSON/CSV), optional phone push per signup
- ✅ Legal pages honest: privacy (nFADP/GDPR), impressum with entity-in-formation transparency
- ✅ QR-bill invoicing tool (spec-verified; bank scan-check pending on first real invoice)
- ✅ Delivery engines regression-tested (100/100 selftest)
- ✅ Branded, version-hashed lead report template
- ⏳ Next: outreach quota starts, first sample batches, CRM wiring of signups → `leads` table
