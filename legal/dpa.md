# Data Processing Agreement (DPA) — CogOps Growth

**DRAFT v0.9 — lawyer review pending (LEGAL.md A3).**
Between **CogOps Group**, Switzerland (entity in formation; "Processor") and the client identified in the order ("Controller"), pursuant to **Art. 28 GDPR** and **Art. 9 nFADP (Swiss FADP)**, for processing of personal data in the performance of services.

## 1. Definitions and interpretation
"Personal data", "processing", "controller", "processor" as in GDPR/nFADP. Where the two acts differ, the stricter obligation prevails for the affected data. References to GDPR articles include the nFADP equivalent.

## 2. Subject matter, duration, nature and purpose
2.1 Subject matter: validation, enrichment, deduplication and copy-drafting of business contact records; publication of pages from Controller-supplied data; delivery reporting.
2.2 Duration: term of the service contract plus the deletion period of §8.
2.3 Nature: collection from public business sources named in Annex 1, automated validation, human review, delivery to Controller, storage for delivery evidence.
2.4 Purpose: enabling Controller's own B2B communication; Processor uses the data for no other purpose, in particular not for own marketing, model training beyond the Controller's own batches, or third-party sale.

## 3. Types of data and categories of data subjects (Annex 1 detail)
Business contact data: name, work email, work phone where published, professional role/title, employer, professional public profile references, validation metadata (source URL, check results, timestamps). **No special categories (Art. 9 GDPR), no children's data, no financial or health data.**

## 4. Controller obligations and instructions
4.1 Controller instructs via the written target definition and order; documented instructions outside the contract require written form. Processor may refuse instructions violating law (Art. 28(3)) and notifies Controller.
4.2 Controller warrants it is entitled to commission the processing and that its use of deliverables complies with applicable outreach law in recipients' jurisdictions.

## 5. Processor obligations
5.1 Process only on documented instructions; confidentiality undertakings for all persons acting under Processor's authority (personnel and agents).
5.2 Security per Art. 32 GDPR / Art. 8 nFADP as specified in **Annex 2 (TOMs)**.
5.3 **Sub-processors:** the list in Annex 3 is approved. New sub-processors: 14 days' prior notice with objection right; on objection without agreement, either party may terminate the affected service pro-rata.
5.4 **International transfers:** processing on Swiss and EU/EEA infrastructure (Annex 3). Transfers to third countries without adequacy only under SCCs (2021/914) + supplementary measures; the LLM-routing sub-processor operates under this rule.
5.5 Assistance with data-subject rights: requests received are forwarded to Controller within 3 business days; Processor executes Controller's decision within **30 days** and provides deletion evidence.
5.6 **Breach notification:** without undue delay, at latest **48 hours** after becoming aware, with facts, categories, approximate volumes, likely consequences, measures — updated in phases if needed.
5.7 Assistance with DPIAs and prior consultation where the processing requires them.
5.8 **No automated decision-making** with legal or similarly significant effect on data subjects.
5.9 Records: Processor maintains its own Art. 30(2) record and makes it available to Controller or the supervisory authority on request.

## 6. Controller's review rights
Audit once per year on 10 business days' notice, during business hours, without disrupting delivery; Processor may satisfy first-line audits with current security reports, TOM attestations and ledger extracts (delivery evidence is hash-chained and extractable per batch).

## 7. Deletion and return (end of processing)
On termination or instruction: deliver or return Controller-supplied inputs as agreed; delete or irreversibly anonymize personal data in Processor systems within 30 days, except where §8 retention applies; certify deletion in writing.

## 8. Statutory retention
Delivery evidence (record hashes, validation metadata, invoice-related data) retained for the statutory period (Art. 958f CO: 10 years) under confidentiality; such retained subsets are sealed from operational use and deleted at period end.

## 9. Liability between the parties
Per service contract §8; each party liable to data subjects per Art. 82 GDPR / nFADP regardless.

## 10. Form
Written form (email sufficient) for amendments; severability; governing law and jurisdiction as in the service contract.

---

### Annex 1 — Processing operations
| Activity | Data fields | Subjects | Source | Retention |
|---|---|---|---|---|
| Record validation/enrichment | name, work email/phone, role, employer, source URL, check results, timestamps | business contacts | public business sources (company sites, public directories, published professional profiles) | until delivery + 90 days, then deleted or per §8 |
| Deduplication | hashes of Controller-supplied list | Controller's contacts | Controller | deleted with batch |
| Copy drafting | the above + researched public facts | business contacts | as above | until delivery + 90 days |
| Delivery & evidence | batch content hashes, validation report | — | Processor systems | §8 statutory period |

### Annex 2 — Technical and organisational measures (TOMs)
Encryption in transit (TLS 1.3) and at rest (vendor-managed); access control: named accounts, MFA on administration, least privilege; IP addresses pseudonymized (SHA-256 truncated) in operational logs; separation of client batches by namespace; immutable, hash-chained delivery ledgers; backups encrypted, restore-tested quarterly; vulnerability hygiene: dependency scanning, rate limits, input validation on all public endpoints; incident process with 48 h notification chain; personnel confidentiality signed; sub-processor security reviewed before onboarding; data minimization: fields limited to Annex 1; retention automation per schedule.

### Annex 3 — Sub-processors
| Sub-processor | Function | Location | Safeguard |
|---|---|---|---|
| Cloudflare (Pages, KV, WAF) | hosting, storage, edge security | global (data at rest EU-configurable) | SCCs where required |
| Supabase (Postgres) | CRM/delivery database | eu-west-3 | EU processing |
| OpenRouter (LLM routing) | copy-drafting inference | US | SCCs + minimization (no special categories; business fields only) |
| [TO FILL: email/booking providers once enabled] | | | |

**Signatures:** Processor: [TO FILL: name, function, date] · Controller: [TO FILL]
