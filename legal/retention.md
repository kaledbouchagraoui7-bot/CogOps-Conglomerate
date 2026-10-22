# Retention & Deletion Schedule — CogOps Group

**DRAFT v0.9 (LEGAL.md A5).** Principle: keep what law or evidence requires, delete everything else on schedule; every deletion produces a certificate entry in the ledger. Statutory floor: **Art. 958f CO — 10 years** for accounting records (invoices, ledgers, contracts with financial content).

| Data set | Retention | Trigger for earlier deletion | Method | Evidence |
|---|---|---|---|---|
| Invoices, QR-bill references, accounting exports | 10 y | — (statutory) | fiduciary archive + sealed ledger subset | annual archive manifest |
| Client contracts, ToS/DPA signed versions | 10 y | — | same as above | same |
| Delivery reports + validation evidence (batch level) | 10 y sealed (dispute/proof), operational copy 90 days | client deletion request → operational copy deleted, sealed subset stays under confidentiality until statutory end | namespace purge + hash manifest update | deletion certificate in ledger |
| Lead records (enriched third-party contacts) | delivery + 90 days | objection/deletion by data subject (≤30 days, permanent suppression) | KV/DB purge + suppression list append | certificate + suppression entry |
| Landing signups (R1) | 24 months | deletion request (≤30 days) | KV key delete; export copies purged | certificate |
| Inquiry/reply queue (R7) | 90 days after reply sent | — | queue purge (ledger keeps hash, not content) | certificate |
| Outreach touch records (R4) | 12 months or opt-out (immediate on opt-out) | opt-out/refusal | purge + permanent suppression | certificate |
| Newsletter subscribers (R8) | until revocation | revocation | provider delete + local purge | provider receipt |
| Website logs (IP hashes) | 30 days | — | log rotation | rotation log |
| Runtime ledgers (decisions/events) | 10 y, append-only | — (integrity: never edited) | encrypted backup copies offsite | backup manifest |
| Backups | 90 days rolling | deletion requests propagate into backups by expiry (documented exception under Art. 17(1) practice) | rotation | rotation log |

## Deletion procedure (the 30-day promise, operationalized)
1. Request lands (email/portal) → logged same day with deadline = +30 days.
2. Owner row in RoPA identifies every system holding the data (R-table).
3. Purge per system; **suppression list** entry (hashed identifier) prevents re-ingestion — permanent.
4. Certificate entry in ledger: what, where, when, by whom; reply to requester with the certificate reference.
5. Missed deadline is a P1 incident: root-caused in the weekly review, reported to requester with new date.

## Legal hold
Litigation, regulatory inquiry or active dispute freezes the affected subsets (no purge, no rotation-out) until release is recorded by the founder; holds are ledgered with reason and review date.

*Amend via DR. The schedule is enforced by the retention automation once the VPS exists (ROADMAP 2.3); until then it is a manual checklist run monthly.*
