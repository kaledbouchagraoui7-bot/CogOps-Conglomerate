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

## DR-0007 — Talent enters real-market validation; Growth↔Talent internal market link
- **Date:** 2026-10-22 · **Trigger:** founder instruction — "move to Talent… create a link between them, both in the same category"
- **Evidence:** engines regression-tested (explainable matcher, evidence-cited curricula, market briefs; branded version-hashed scan report added); landing + signup machine deployed and verified at https://cogops-talent.pages.dev (KV bound via API per the Helix lesson); two-way internal-market tasks implemented and tested: `talent.employer_prospects` (pulls Growth lead_gen via ticket) and `growth.sister_digest` (pulls Talent career_intel via ticket); cross-links live on both sites.
- **Decision:** Talent is in real-world Stage-1 validation; window 90 days from 2026-10-22; success = 100 signups OR 3 pre-orders OR CHF 200+ paid, else KILL_WIN review (I8). The Growth↔Talent link is priced at DR-0002 internal rates and recorded on both P&Ls (I7). Honesty boundary published: certificates of completion, never accredited-degree claims.
- **Approval:** enacted by founder instruction 2026-10-22.

## DR-0008 — Verde & Terra enter real-market validation; climate-pair internal prices
- **Date:** 2026-10-22 · **Trigger:** founder instruction — create Verde and Terra, link them as a pair (pairs now: verde-terra, growth-talent)
- **Evidence:** engines regression-tested (GHG-Protocol carbon maths exact; CSRD-lite with mandatory limitations; heuristic-v0 labeling enforced; ≥5-source brief rule; overlay formula published); both landings deployed & verified (signup machines, pair cross-links, model-grade honesty banners); internal-market tasks `verde.csrd_full` ↔ `terra.portfolio_carbon_overlay` implemented and tested via platform tickets.
- **Decision:** (a) Verde and Terra each enter 90-day Stage-1 validation from 2026-10-22 (100 signups / 3 pre-orders / CHF 200 paid, else KILL_WIN per I8). (b) Internal price list (DR-0002) extended: `carbon_books` CHF 8/book, `climate_risk` CHF 10/screen. (c) Boundaries reaffirmed as publishable promises: Verde never issues assured statements; Terra never issues ratings or insured-risk assessments; both model-grade/factor-grade disclosures stay on every artifact (evidence-over-claims principle).
- **Approval:** enacted by founder instruction 2026-10-22.

## DR-0009 — The Regulatory-Science Clique: complete graph K5 + internal prices
- **Date:** 2026-10-22 · **Trigger:** founder instruction — create Medtech, Capital, Sentinel (Helix/Dossia existing) "connected in the same way a complete graph is connected"
- **Evidence:** all five live with evidence machines (sentinel/capital/dossia/medtech pages.dev + helix); 20 directional internal-market trades implemented (10 edges × 2); LINKS registries per company; selftest asserts K5 completeness structurally (every unordered pair has buy-tasks in both directions) and executes sampled edges; free samples added (edge snapshot, plan check).
- **Decision:** (a) the five form the **Regulatory-Science Clique**: every pair trades verified services; combined deliverables may carry multi-company provenance chains (e.g. CSRD-style evidence packs, certified briefs, trail-logged runs). (b) Internal prices added to DR-0002 list: drylab_stats 12 · alcoa_trail 4 · alcoa_qc 6 · treasury_policy 15 · ai_sec_review 20 · lit_feed 9 · mdr_tree 15 · ra_feed 9. (c) Each of the five enters 90-day Stage-1 validation (100 signups / 3 pre-orders / CHF 200 paid; else KILL_WIN). (d) Boundaries published per site (defensive-only / no-advice / never-signatory / research-use) are contractual, not marketing.
- **Approval:** enacted by founder instruction 2026-10-22.

## DR-0010 — Intelligence live; the star graph (Intelligence ↔ all nine)
- **Date:** 2026-10-22 · **Trigger:** founder instruction — "create Intelligence, as smart as possible right now, connect it to every company"
- **Evidence:** brain implemented & tested (think/research/recall + labeled synthesis + memory + EU AI Act watch as-of 2026-10); 18 star trades (9 buys + 9 sells via `intelligence_ops`); LINKS registries on all ten modules; selftest proves star completeness structurally and executes samples; landing live at cogops-intelligence.pages.dev with nine-company band, verified end-to-end and purged clean.
- **Decision:** (a) Intelligence is the group's multiplier company and the only one linked to every other; internal price `ai_ops` CHF 25/job added to DR-0002 list. (b) "As smart as possible now" = orchestrator over the internal market + cited research + memory + labeled brains + per-company token caps — NOT unbounded autonomy: Type-1 gates and honesty labels remain invariants (I3, I11). (c) Intelligence enters 90-day Stage-1 validation like its siblings.
- **Approval:** enacted by founder instruction 2026-10-22.

## DR-0011 — The Nervous System (senses, reflexes, pain, consciousness)
- **Date:** 2026-10-22 · **Trigger:** founder instruction — "create the nervous system of it all" (platform-layer diagram: AI core, gate, capital engine, site factory, shared spine)
- **Evidence:** nervous.py + dashboard.py implemented; 9 new regression checks (145/145): fortress-freeze engages and blocks spend, auto-release on heal, ledger-tamper hard freeze with human-only release (wrong phrase refused), repeat-breach kill-review staging, dependency propagation from LINKS, dashboard renders all organs/edges/signals.
- **Decision:** (a) the nervous system has NO external authority: it freezes, flags, stages reviews and informs; approvals stay human (I3). (b) Pain doctrine: integrity freezes are human-release-only; fortress freezes auto-release on heal. (c) The dashboard (localhost-only serve mode) is the founder's daily consciousness view; the automaton runs nervous.cycle() every cycle. (d) OS amended to v1.1 with §16.
- **Approval:** enacted by founder instruction 2026-10-22.

## DR-0012 — The central business exists: CogOps Group as code, clothes and skin
- **Date:** 2026-10-22 · **Trigger:** founder instruction — "create the central business that holds everything together… the clothes… create the 'CogOps Group'"
- **Evidence:** `holding.py` (brand lockup generator from theme.json; executable invariants I1–I12 with proof methods; allocator view; DR parser) + `groupsite.py` (group site assembled from LIVE state: trade graph from LINKS registries, ten organ cards, principles, invariants table, DR trail) + `brand/` (11 deterministic SVG lockups) + group site deployed & verified (21 edges rendered, 12/12 invariants PASS from code, signup machine + token export verified, purged clean) + `holding/README.md` (what the holding owns — and all it owns).
- **Decision:** (a) The holding's public face is cogops-group.pages.dev; its governance page is the transparency door (doctrine public, consciousness private). (b) Brand governance: theme.json is the only brand source; lockups are generated, never hand-edited; theme changes require a DR. (c) The public invariants table is code-generated and may publish FAILs — transparency over polish. (d) Group site is rebuilt (`cogops.py group build`) after every structural change; staleness is a documentation defect.
- **Approval:** enacted by founder instruction 2026-10-22.

## DR-0013 — Focus decree: two active lines, eight dormant (not dead)
- **Date:** 2026-10-22 · **Trigger:** analyst round 3 — weak points A (legal-capacity wall) and D (unproven demand); founder instruction to eliminate them and lower failure probability.
- **Evidence:** round-3 verification (analysis/round3.md §2): minor cannot hold a micro-entreprise (service-public F31627); CNIL B2B legitimate-interest doctrine confirmed; zero unrelated-party demand evidence to date; Bac blackout June–July 2027.
- **Decision:** (a) ACTIVE lines: **Growth** (FR/CH lead-gen + pSEO, CNIL-compliant channels; DE/AT cold email forbidden) and **Dossia** (conditional on an expert co-signer LoI by end of month 4, else it joins dormancy). (b) The other eight companies are **DORMANT**: live evidence machines stay up, outreach/spend/public statements refused by `gates.stage()` via `data/dormancy.json` (fail-closed); reactivation = new DR + `dr_override` on the staged action (G3). (c) Exam shield: June–July 2027 is a declared blackout for campaign work on both active lines. (d) Dormancy is an option preserved, not a kill: I8 kill-reviews still apply only to active lines.
- **Approval:** enacted by founder instruction 2026-10-22 (round-3 request: "make it more stable, lower chance of failure").

## DR-0014 — Deferred-start reservation instrument; no commerce before majority; dated kill criteria
- **Date:** 2026-10-22 · **Trigger:** analyst round 3 §2.1–2.2 (minor contract voidability, art. 1181/1182 C.civ.; micro-entreprise impossible before 18) and the founder's F clarification (home-based earning permitted, off-premises employment not).
- **Evidence:** service-public F31627 (no micro-entreprise for minors; EURL/SASU only with parental authorization — unavailable); Code civil art. 1181 (relative nullity runs only for the protected party), art. 1182 (confirmation at majority); URSSAF 2026 rates/thresholds consulted 2026-10-22.
- **Decision:** (a) **Zero consideration before 2027-06-16**: no fee, deposit or payment data; any payment offered earlier is refused. (b) Pre-sales use `legal/reservation-agreement.md` v1.0: zero-consideration reservation, price lock, expiry 2027-09-30, paid contract re-signed FRESH at majority (voidability never arises; art. 1182 confirmation kept as fallback §7 only). (c) Month-8 day-1 kit (micro-entreprise registration, invoice template, insurance trigger) is pre-written; first lawful invoice ≥ 2027-06-16. (d) Kill criteria: **0 signed reservations out of ≥100 qualified conversations by end of month 5 ⇒ pivot** to portfolio-only + fallback track; **month-9 revenue < CHF 1,000 ⇒ same pivot**. Both recorded as KILL_WIN per I8. (e) Every reservation instance is Type-2 gated (founder keystroke) and archived in the vault.
- **Approval:** enacted by founder instruction 2026-10-22.

## DR-0015 — Reactivation: all ten companies active (founder override of round-3 focus recommendation)
- **Date:** 2026-10-22 · **Trigger:** founder instruction — "Make the dormant companies active."
- **Evidence:** dormancy enforced since DR-0013 (gates refused external/money/public actions of dormant companies); analyst round 3 recommended two active lines; overridden here by the founder with the trade-off recorded.
- **Decision:** (a) `data/dormancy.json`: dormant = [], active = all ten; the refusal mechanism stays in code and stays tested (selftest exercises it via a temporary override), so dormancy remains available as an instrument. (b) Breadth is governed by per-company weekly quotas + real weekly sample caps surfaced to visitors as live scarcity (DR-0016). (c) DR-0014 kill criteria apply per active line, reviewed in the quarterly portfolio review. (d) Group site rebuilt without dormancy chips.
- **Approval:** enacted by founder instruction 2026-10-22.

## DR-0016 — Persuasion & experience pack with honesty constraints (all company sites)
- **Date:** 2026-10-22 · **Trigger:** founder instruction — apply the aesthetic/persuasion/conversion matrix (hierarchy, micro-interactions, social proof, frictionless flows, value prop, ethical scarcity, focused CTAs, progress indicators, personalization) to every company site.
- **Evidence:** matrix supplied by founder; audit found missing: visible progress path, sticky CTA, live scarcity signal, consolidated trust band, hover/focus micro-interactions, per-choice personalization line.
- **Decision:** (a) `tools/polish.py` pack v1 on all ten sites: trust band (verifiable signals only), 3-step stepper, scroll-aware sticky CTA reusing each site's own hero label, personalization line driven by the product select, micro-interaction/focus/selection CSS, live sample-slot counter. (b) **Honesty constraints (non-negotiable):** social proof = verifiable signals only (live queue counter, public governance page, published guarantees, evidence-per-record); **no fabricated testimonials, reviews, press logos or client names, ever**; scarcity = real weekly sample caps from each OFFER file, computed live from the signup store (`slots_left` in `/api/count` via `SAMPLE_CAP` project var), never invented countdowns. (c) Pack v2 (identity/motion/interactive estimators/delight/404 microcopy) follows under the same constraints.
- **Approval:** enacted by founder instruction 2026-10-22.
