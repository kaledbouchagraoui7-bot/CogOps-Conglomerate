# Record of Processing Activities (RoPA / VVT) — CogOps Group

**DRAFT v0.9 (LEGAL.md A4).** Basis: Art. 30 GDPR / Art. 12 nFADP. Controller: CogOps Group, Switzerland (entity in formation; contact cogops.engine@gmail.com). DPO: not required (core business not large-scale special-category processing); data-protection contact = founder. Review cycle: quarterly with the portfolio review (OS §8), and on any new processing.

| ID | Activity | Role | Purpose | Legal basis | Data categories | Data subjects | Source | Recipients / sub-processors | Transfer | Retention | TOMs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | Landing signups (waitlist/sample requests) | Controller | Prepare & deliver free sample batch; reply within SLA | Pre-contractual measures (Art. 6(1)(b) GDPR) | work email, company, product interest, ICP line, free-text note, IP hash | prospect contacts | signup form | Cloudflare KV; founder inbox (on export) | CH-configured CF region | 24 months or until deletion request, whichever first | T1 |
| R2 | Client CRM & delivery management | Controller | Contracts, batches, invoices, support | Contract (6(1)(b)) | contact data, contract data, delivery records | client personnel | client | Supabase (eu-west-3), Cloudflare | EU | contract term + 10 y for invoice-related (Art. 958f CO) | T1,T2 |
| R3 | Lead enrichment on client instruction | **Processor** | Validation/dedup/copy per DPA | Art. 28 instruction | business contact data per DPA Annex 1 | third-party business contacts | public business sources | OpenRouter (copy drafting), Cloudflare, Supabase | US (LLM) under SCCs | delivery + 90 days; evidence subset 10 y sealed | T1,T2,T3 |
| R4 | Own B2B outreach touches | Controller | Acquire clients (quota-limited, personalized) | Legitimate interest (6(1)(f)): B2B individual contact; balancing test documented: personalized, single-addressee, opt-out honored at first reply, CH-targeted first; **e-privacy screen per recipient country before sending** | work email, role, company, researched public facts | prospect contacts | public sources | founder mailbox | none (sent from CH mailbox) | until opt-out/refusal, max 12 months | T3 |
| R5 | Invoicing & accounting | Controller | Statutory bookkeeping | Legal obligation (6(1)(c); Art. 958f CO) | invoice data, payment reference | client personnel | own billing | bank, fiduciary | CH | 10 years | T2 |
| R6 | Website operations & security logs | Controller | Availability, abuse defense | Legitimate interest (6(1)(f)) | IP hash (truncated SHA-256), UA, path, status | visitors | server logs | Cloudflare | CF edge | 30 days | T1 |
| R7 | AI reply drafting (inquiries) | Controller | Draft replies for founder approval | Legitimate interest (6(1)(f)) + R1 basis | signup fields only | R1 subjects | R1 queue | OpenRouter | US under SCCs | queue ≤ 90 days post-reply | T3 |
| R8 | Newsletter / journal subscribers | Controller | Media network (when launched) | Consent, double opt-in (6(1)(a)) | email, consent timestamps | subscribers | signup | mailing provider [TO FILL] | [TO FILL] | until revocation + proof 3 y | T1 |
| R9 | Personnel / contractors | Controller | HR (none yet) | Contract / legal obligation | — | — | — | — | — | per law once hired | T2 |
| R10 | Governance ledgers (decisions, deliveries) | Controller | Audit trail, evidence, compliance | Legitimate interest + legal | operational metadata, hashes; personal data only incidentally | mixed | own systems | none (local/runtime + backups) | CH | 10 years (commercial records), append-only | T2 |

## Balancing-test note for R4 (outreach)
Individual, personalized B2B email to business addresses; no purchased lists; no automation of *sending* (human approves/writes every message); opt-out executed immediately and permanently; jurisdictions with stricter e-privacy (e.g. DE/AT B2B consent regimes, CAN-SPAM rules in US) are screened per recipient before first touch — documented per target in the outreach sheet. Where consent is legally required and absent: no touch. This row is the compliance gate the outreach engine enforces.

## TOM reference keys
- **T1** access & minimization: named accounts, MFA on admin, least privilege, field limits per row, IP pseudonymization.
- **T2** integrity & retention: hash-chained ledgers, encrypted backups with quarterly restore tests, retention automation with deletion certificates.
- **T3** third-party discipline: sub-processor list with SCCs, minimization of fields sent to LLMs (no special categories), no training on client data, provider failover labeled per answer.

*Amend via DR; supersede rows, never delete history.*
