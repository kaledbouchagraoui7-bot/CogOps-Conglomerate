# Decision Records (DR) — append-only (OS §15)

> Created 2026-10-22 on the first structural amendments. Format per OS §15: date · trigger · evidence · decision · approval. Amendments to the Operating Structure require a DR; DRs are never edited or deleted — supersede instead.

---

## DR-0001 — Profit allocation numbers (OS §4 concretized)
- **Date:** 2026-10-22 · **Trigger:** roadmap demand — "capital allocation with numbers"
- **Evidence:** Berkshire deployment ladder (research/01 §M3); Constellation FCF discipline (research/04); existing JARVIS sweep (30%, compliance-guarded); fortress invariant I2.
- **Decision:** After tax reserve and fortress top-up (≥6 months fixed costs, I2), every CHF of distributable profit allocates:
  - **40%** → reinvest in operating subsidiaries clearing their stage gates (ladder rungs 1–2),
  - **30%** → Capital sweep (Pillar 3a cap-aware + guarded ETF DCA — existing engine, invariant I10),
  - **20%** → group reserve until fortress reaches **12 months** (then rejoins the ladder),
  - **10%** → experiments: tools, insurance premiums, legal, new Stage-0/1 validations (≤ CHF 500 per idea, build-slot cap applies).
  Funding a new company past Stage 1 requires: Stage-1 evidence thresholds met (OS §5) AND ladder rung order respected. Kill threshold: OS §5 kill criteria, reviewed quarterly (kill-rate is a health metric, I8).
- **Approval:** proposed by OS per founder roadmap instruction 2026-10-22; effective immediately; amendable only by new DR.

## DR-0002 — Internal price list (Haier internal-market rule, OS §2.3)
- **Date:** 2026-10-22 · **Trigger:** roadmap — "Growth sells leads to the other companies; decide what they pay"
- **Evidence:** Haier M1 (internal work at market terms keeps P&Ls honest, research/06); Constellation no-synergy-illusions (research/04); platform notional charges already implemented (`platformsvc.CATALOG`).
- **Decision:** Inter-company work is charged at **50% of external list** (notional — no cash moves; it exists to keep standalone P&Ls honest, I7):
  - validated lead: **CHF 1.00** internal (external CHF 1–3)
  - pSEO page: **CHF 10** internal (external CHF 15–60)
  - newsletter slot: **CHF 25** internal (external from CHF 250/issue sponsorship)
  - platform services: unchanged `platformsvc.CATALOG` rates (site factory CHF 50, gateway CHF 5, CRM CHF 10, verification CHF 15, legal templates CHF 20, brand kit CHF 10, media CHF 25, gate/agent core CHF 0)
  - labor (agent compute) is free internally; **LLM spend is capped per company** at USD 5/month (env-tunable) and charged to the consuming company's P&L at cost estimate.
- **Approval:** as DR-0001.

## DR-0003 — Brand architecture: "CogOps X" endorsed brands
- **Date:** 2026-10-22 · **Trigger:** roadmap — "brand architecture, decided once"
- **Evidence:** Alphabet subsidiary independence under one capital doctrine (research/02); Tiny's kept-name autonomy (research/08); solo-scale trust economics: one reputation pool beats ten unknowns; handles/email/domain already CogOps-consistent.
- **Decision:** Endorsed-brand architecture. Legal name **CogOps Group** everywhere (entity, invoices, contracts, GitHub). Market-facing companies named **CogOps <Name>** (Growth, Helix, Sentinel, …), each with its own accent color (`cogops-os/data/theme.json`), own site, own inbox, own voice — under the shared endorsement line "a CogOps Group company". At Stage-5 graduation a company MAY rename/rebrand independently (Type-1 decision). Logos: group wordmark + per-company accent glyph (Penpot, founder).
- **Approval:** as DR-0001.

## DR-0004 — Single-entity doctrine (divisions-first)
- **Date:** 2026-10-22 · **Trigger:** roadmap — "one real legal entity… ten companies as brands or divisions"
- **Evidence:** Swiss no-group-taxation (research/09 §2): premature entities trap losses and cost CHF 3–5k/yr each; Constellation/Alphabet graduate entities only at scale triggers; GmbH CHF 20k fully paid, free naming (surname rule blocks "CogOps Group" as Einzelfirma).
- **Decision:** Exactly one legal entity until a spin-out trigger fires (OS §12 / research/09 §3): client-liability isolation need · external capital at company level · sustained profit making participation-exemption routing attractive · human GM with equity. Sequence: **[now]** operate under founder's civil-name structure with CogOps branding · **[first real revenue or first liability-bearing contract]** found **CogOps Group GmbH** (CHF 20k) · **[trigger per company]** subsidiary GmbH under the holding (holding keeps ≥10% for participation exemption) · **[investors/privacy ever]** AG conversion. All ten companies are cost centres with standalone P&L from day one (I7) regardless of legal form.
- **Approval:** as DR-0001. Founder actions required: fiduciary engagement (roadmap 1.4), boundary-lawyer check (1.7).

## DR-0005 — Growth enters real-market validation
- **Date:** 2026-10-22 · **Trigger:** founder instruction — "let's start with Growth and make it real"
- **Evidence:** Landing + signup machine deployed and verified end-to-end this session (validation, dedupe, disposable-domain screen incl. subdomains, honeypot, per-IP rate limit, live counter, token-protected export; test data purged, store clean at 0); delivery engines regression-tested 100/100; QR-bill tool spec-verified (mod-10-recursive against canonical PostFinance example, ISO-1339 IBAN); offer/playbook written (`growth/OFFER.md`).
- **Decision:** CogOps Growth is in **real-world Stage-1 validation**. Public URL: **https://cogops-growth.pages.dev**. Evidence window: **90 days from 2026-10-22**. Success = ANY of: 100 waitlist signups · 3 pre-orders · CHF 200+ paid by an unrelated customer → promote to real-world Stage 2 (launch: first paying retainer/pilot). Miss ⇒ kill review recorded as KILL_WIN with the data (I8 — the machine means it). Admin export token: founder secret store only (never in repo). First real QR-bill invoice requires bank/fiduciary scan-check before client delivery (CBS Ch.3 honesty flag on the tool).
- **Approval:** enacted by founder instruction 2026-10-22 ("start with Growth and make it real").

---
*Next DR numbers: 0006+. Remember: append-only; supersede, never edit.*

## DR-0006 — Helix enters real-market validation
- **Date:** 2026-10-22 · **Trigger:** founder instruction — Growth audit closed, "move unto Helix"
- **Evidence:** engines regression-tested (sequence QC with cross-check gates, audit-trailed Table 1 on NR-validated stats, PMID-traceable surveillance; branded version-hashed report task added); landing + signup machine deployed and verified end-to-end at https://cogops-helix.pages.dev (KV binding attached via API after wrangler sync gap — documented in SECRETS.md); offer/pricing/guarantee written (`helix/OFFER.md`); group Terms v1.0 linked.
- **Decision:** Helix is in real-world Stage-1 validation. Window: 90 days from 2026-10-22. Success = ANY of: 100 signups · 3 pre-orders · CHF 200+ paid by unrelated customers. Miss ⇒ kill review as KILL_WIN (I8). Reproducibility guarantee published: byte-identical re-run on request within 14 days, else free re-run or refund. Human-of-record (client PI) field mandatory on every scientific deliverable (I12).
- **Approval:** enacted by founder instruction 2026-10-22.
