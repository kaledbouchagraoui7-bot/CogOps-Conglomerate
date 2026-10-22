# Analyst Round 3 — F clarified, weak points A+D, verification batch
**Date:** 2026-10-22 · **Role:** skeptical business analyst (honesty rules apply) · **Prior rounds:** round1.md (superseded where contradicted), round2 (override stipulation)
**New evidence this round:** founder clarification of constraint F: *"I can't work outside of the home as a student. I can make money before September — what I meant was I can't work outside of the house, like a summer job."* Standing stipulation retained: the business overrides anything that hinders it and is the founder's income source because he cannot work.

---

## 0. What the F clarification changes — and what it does not

[FACT] The binding constraint on revenue was never "no income before September 2027" as a self-imposed rule; it is **legal capacity to contract and invoice**, which ends at majority on **2026-06-16… correction: 2027-06-16**. Verified this round (service-public.fr, F31627, checked 2025-08-13): a non-emancipated minor **cannot create a micro-entreprise at all** — the only vehicles open before 18 are EURL/SASU, and only with written parental authorization limited to acts of administration. [FACT] Parental authorization is unavailable (hostile home, founder-stated across rounds). **Therefore: no invoice, no paid engagement, no company entity before 2027-06-16. This is law, not policy, and no stipulation overrides it.**

[FACT] The clarification removes a *different* blocker: home-based, self-directed work (production, portfolio artifacts, pipeline building, reservations, study) is permitted by the founder's own rules before September 2027. Only off-premises employment (summer job) is excluded. So the pre-majority months are **not dead months** — they are production and pre-sale months with zero invoicing.

[OPINION] Net effect on the plan: the shape I prescribed in round 2 (pre-sell now, contract and invoice at 18) stops being a workaround and becomes the **only lawful shape**. Confidence in the shape rises; confidence in the revenue number does not, because the number was never limited by the founder's rules — it is limited by (a) the invoice wall (unchanged), (b) unproven demand (unchanged), (c) exam bandwidth June–July 2027 (unchanged).

[FACT] Consequence for the "income source" stipulation: between now and 2027-06-16 the business **cannot** be an income source. Anyone who tells you otherwise is selling something. The earliest lawful first invoice is on/after the 18th birthday, i.e. month 8 of the 10-month window. The window for "CHF 3,000/month" therefore contains exactly **three invoicing months** (months 8, 9, 10). Plan against that arithmetic, not against a 10-month ramp.

---

## 1. The portfolio double-use, explained

Claim under review: *"Dossia/Helix artifacts are simultaneously saleable output and the admission/scholarship weapons your docs prescribe (Werner Siemens CHF 19,800; UNIL grant CHF 1,600×10 + housing) [FACT doc 2/3]."*

- [FACT doc 2/3 — as stated in the founder's documents, not independently verified by me] The scholarship targets: Werner Siemens Stiftung ≈ CHF 19,800; UNIL grant ≈ CHF 1,600 × 10 months + housing. These figures come from the founder's PDFs 2 and 3; I have not audited the foundations' current call texts.
- [FACT] Dossia/Helix-class artifacts (ICH M4 module drafts, clinical-study-report Table 1 packs, PMID-traceable surveillance matrices, plain-language summaries) are exactly the kind of written evidence a admissions jury or scholarship committee can inspect: they are dated, versioned, reproducible, and show method under regulatory standards. The repo already ships them with reproducibility guarantees (DR-0006).
- [OPINION — the mechanism] One work product, two buyers, near-zero marginal cost for the second:
  1. **Buyer 1 (market):** a client pays for the artifact (post-majority), or reserves it now at a locked price (deferred-start reservation, DR-0014).
  2. **Buyer 2 (institutions):** the *same* artifact, anonymized/redacted where client confidentiality requires, enters the admissions and scholarship file as proof of capability — which the founder's own documents prescribe as the lever for the conditional UNIL/UNIGE offers and the scholarship stack.
  3. Because buyer 2 consumes a copy, the artifact's cost is amortized twice; a month with **zero sales** still produces admission/scholarship value. That is the stability property: the portfolio sprint has a **non-market floor** on its return.
- [OPINION] Caveat, stated plainly: scholarships and grants are **not business revenue** and arrive on academic calendars (application deadlines, jury rounds), not on your cashflow schedule. They strengthen the *runway*, they do not prove the *market*. Never let a scholarship hope substitute for a signed reservation in the demand evidence ledger.

---

## 2. Verification batch — results of the eight checks

### 2.1 French minor contract voidability + ratification at majority
[FACT] A contract concluded by a non-emancipated minor is not void outright; it is **relatively null** — only the protected party (the minor, then the adult he becomes) may seek nullity (Code civil art. 1181: "la nullité relative ne peut être demandée que par la partie que la loi entend protéger"). The adult counterparty **cannot** invoke the minority to escape. [FACT] Relative nullity is curable by **confirmation** (ratification): art. 1182 — confirmation can only occur after conclusion, and voluntary performance with knowledge of the defect counts as confirmation; at majority the former minor may confirm the act and it becomes fully binding.
**Design consequence [OPINION]:** do *not* rely on ratification. A deferred-start reservation signed today should be drafted as a **zero-consideration reservation** (price lock, slot, no obligation to perform on either side), and the paid contract should be a **fresh contract signed at majority**, not a ratified minor's act. Fresh signature kills the voidability question entirely instead of managing it. Ratification at majority is kept only as a fallback clause for anything inadvertently signed early.

### 2.2 Micro-entreprise at 18 — categories, VAT, cotisations
[FACT, urssaf.fr / service-public.fr, consulted 2026-10-22]
- Vehicle at 18: micro-entreprise (EI), open to artisan / commerçant / profession libérale, principal or complementary (student status compatible). His lines (B2B services, consulting, writing) fall in **prestations de services** — category BNC (libéral non réglementé) or BIC services depending on exact activity wording; classify at registration, do not guess now.
- Minor before 18: **micro-entreprise impossible**; only EURL/SASU with parental authorization (art. 388-1-2 Code civil). Rejected for this plan: authorization unavailable + corporate accounting burden disproportionate to a 3-month invoicing window.
- Micro ceilings (2026): services **€83,600/yr** (prorated in year one); VAT franchise: base threshold services **€37,500**, upper **€41,250** (crossing the upper threshold makes you VAT-liable in the same year); invoice mention "TVA non applicable – art. 293 B CGI". Irrelevant at planned volume (CHF 3k/month ≈ €36k/yr run-rate sits under the base threshold) — [ASSUMPTION] volume stays under €37,500/yr in the window; if it doesn't, that is a good problem with a known procedure.
- Cotisations (services): URSSAF publishes a rise of the "autre prestation de services" rate to **25.6% from 1 Jan 2026**; a reduced new-activity rate applies at first (50% of the normal rate, raised to **75% from 1 July 2026** per economie.gouv.fr). [ASSUMPTION on exact category mapping; confirm in the simulator at registration — the order of magnitude is: roughly a quarter of revenue in social charges, less in the first months.]
- Versement libératoire (optional): 2.2% of revenue for BNC services, subject to reference-income conditions; flat expense deduction 34% (BNC) if not opted.
**Design consequence:** registration is a same-day online act at 18; the kit (activity wording, category choice, option choices) is pre-written so month 8 day 1 = SIRET + first invoice. No revenue before that day.

### 2.3 CNIL current practice — B2B legitimate-interest prospecting
[FACT, cnil.fr pages consulted 2026-10-22] For electronic B2B prospecting, CNIL's doctrine: consent for B2C; for B2B, prospecting a person at their **professional** address is admissible without prior consent when the purpose is **related to the recipient's professional function**, on the basis of **legitimate interest**, with prior information and a functional **opt-out** in every message. [FACT] CNIL sanctions prospecting that lacks a valid legal basis or ignores opt-out — the doctrine is enforced, not decorative.
**Design consequence [OPINION]:** Growth's FR channel is lawful *if* every contact is a professional address, function-relevant, sourced with legitimate-interest documentation, and carries opt-out + identity + (once live) impressum mentions. This is already the Growth outreach quota engine's design; the check confirms it. DE/AT cold email remains **prohibited** (UWG §7 / consent regime) — unchanged from round 2. CH: personalized individual contact, no mass email — unchanged.

### 2.4 Cantonal practice — self-employment on a student B permit (Vaud/Geneva)
[UNVERIFIED — cannot be resolved from published sources; requires the founder's written inquiry] Published federal material confirms the student accessory-work frame (15 h/week; art. 38 OASA for third-state nationals; EU/EFTA students under FMEL with cantonal authorization practice), but **self-employment by an EU student on a study permit is not addressed in a public, citable rule I could find**. Cantons administer the permit conditions.
**Instrument delivered:** draft written inquiry (Vaud + Geneva variants) in `analysis/founder-actions.md` §C4 — asks three yes/no questions: (1) is self-employment compatible with the study permit, (2) does the 15 h/week cap apply to self-employed activity, (3) required documents. [OPINION] Expect the answer to shape *post-Sept-2027* structure only; it does not touch the 10-month window (founder remains FR-resident throughout it).

### 2.5 Cross-border: FR micro-entreprise while resident in CH
[ASSUMPTION, treaty mechanics per FR-CH convention + EU Reg. 883/2004 logic; fiduciary to confirm] Within the 10-month window this is **not live**: the founder is FR-resident until the Sept-2027 relocation, so months 8–10 invoicing is a pure FR micro-entreprise case. At relocation: social security follows the place where the activity is exercised (working from a CH home ⇒ Swiss affiliation), and a FR micro run from CH residence raises permanent-establishment and affiliation conflicts. [OPINION] Planned sequence: keep FR micro only while FR-resident; at relocation either (a) open a CH sole proprietorship and close the FR micro, or (b) keep FR micro only if a fiduciary confirms in writing that the cross-border configuration is clean. Do not decide now; decide in Aug 2027 with a paid fiduciary hour. Fiduciary question list in `analysis/founder-actions.md` §C5.

### 2.6 Insurance — start date and premium
[FACT per insurer pages consulted 2026-10-22 (Insify, Stello): online RC Pro for micro-entrepreneurs starts around **€10–12/month** for low-risk consulting/IT activities, with immediate attestation and chooser start dates.] [OPINION] Yes — a policy can be in force on the day of the first invoice: subscribe the day before, start date = invoice date. Budget line: €120–150/yr, first outlay at month 8, not before. Cyber/RC-pro extension for data-handling services: quote at the same sitting. [UNVERIFIED until an actual simulator quote is run with his exact activity codes — founder action, 20 minutes.]

### 2.7 Live competitor quotes (two surviving lines)
[OPINION] Published price intel gathered this round is in `analysis/founder-actions.md` §C7 (what competitors publicly charge for lead-gen retainers and regulatory/medical-writing support). True RFQs (3 anonymous requests per line, from a neutral address, identical scope text) **must be sent by the founder** — I will not impersonate a buyer; that would poison the evidence and, if traced, the brand. The RFQ kit (scope text, target list criteria, response-coding sheet: price / turnaround / proof offered) is delivered; 45 minutes of work; results feed the pricing page before month-8 contract templates are fixed.

### 2.8 Do buyers accept deferred-start contracts?
[UNVERIFIED — by construction.] Only the pipeline answers this. It is the proof metric of action #1: **reservations signed per 100 qualified conversations**. [OPINION] Threshold I will defend: if by end of month 5 the reservation campaign has produced **zero** signed reservations out of ≥100 qualified conversations, the demand hypothesis for the deferred shape is dead and the plan pivots to portfolio-only mode (scholarship/admissions floor) plus employment-track fallback (Nantes Bridge). That kill criterion is now in DR-0014.

---

## 3. Eliminating weak points A and D — and the stability design

Reading of "D + A" as flagged in round 2: **A = the legal-capacity / invoicing wall** (nothing can be billed before 2027-06-16) and **D = demand is unproven** (zero unrelated-party signatures or payments to date). If you meant other letters, say so; the verification batch above covers both clusters either way.

**Honesty first: neither can be "eliminated."** A is statute; D is a fact about the world only customers can reveal. What can be done — and is now done in this repo — is convert both from *open-ended risks* into *bounded, dated, binary tests* with pre-committed consequences. That is what "lower chance of failure" actually means for a plan like this: not higher hope, earlier truth, smaller burn.

### A — legal-capacity wall: eliminated as a *risk*, kept as a *calendar*
1. **No contract, no invoice, no money before 2027-06-16.** Not a policy preference — the only lawful configuration (minor cannot hold a micro-entreprise; EURL/SASU route needs the one input you don't have: parental signatures). DR-0014.
2. **Deferred-start reservation instrument** (`legal/reservation-agreement.md`): zero consideration today, price lock + slot + expiry; paid contract re-signed fresh at majority (voidability never arises; art. 1182 confirmation kept only as fallback wording).
3. **Month-8 day-1 kit**: micro-entreprise registration walkthrough with pre-chosen activity wording/category/options, QR/FR invoice template already built and SIX/URSSAF-checked, insurance trigger, bank check of first invoice. The wall becomes a date on a calendar with a checklist behind it.
4. **Everything pre-majority is production, not commerce**: portfolio artifacts (double-use, §1), pipeline conversations, reservations, competitor RFQs, scholarship applications. Lawful, home-based, and exactly what the clarification permits.

### D — unproven demand: eliminated as a *fog*, kept as a *meter*
1. **Two lines only** (DR-0013): Growth (FR/CH lead-gen + pSEO) and Dossia (co-signed with an expert of record). Eight companies go **dormant, not dead**: sites stay live as evidence machines, spend and outreach stop, reactivation is one DR away. Focus is the cheapest variance reducer available.
2. **Three binary demand probes, each ≤ CHF 0 and ≤ 1 hour of founder time per week:** reservation campaign (metric: signed reservations / qualified conversations), competitor RFQs (metric: their published vs quoted price vs yours), expert co-signer conversations (metric: one signed co-signer letter of intent — Dossia's legality hinge).
3. **Pre-committed kill/pivot dates** (DR-0014): month 5 zero-reservations rule; month 9 (one full invoicing month) below CHF 1,000 → pivot to portfolio-only + fallback track. Killing early is a win (I8), not a failure.
4. **Channel legality locked** (§2.3): FR B2B legitimate-interest with opt-out discipline; CH personalized; DE/AT cold email forbidden. A channel ban is a demand-risk reducer too — one CNIL or UWG letter would end the plan outright.

### The stability stack (why failure probability is lower than round 2, not higher)
- **Fixed cost ≈ 0 until first revenue**: domains + Pages free tier + free LLM tier; first paid outlays (insurance ~€12/mo, URSSAF cotisations as % of revenue, fiduciary hour) all trigger *after* money arrives. Burn cannot outrun income. [FACT on current cost base: all live infrastructure is free-tier as of 2026-10-22.]
- **Non-market floor**: portfolio double-use (§1) means zero-sales months still compound admissions/scholarship value; the fallback track (Nantes Bridge, MSW/RA salary band per doc 1) survives every business outcome.
- **Exam shield**: June–July 2027 = Bac blackout, pre-declared in DR-0013; no campaign depends on those two months.
- **Options preserved, not burned**: dormancy ≠ kill; the nine other companies keep their evidence machines and can be reactivated on one DR if a signal appears.
- **Hinges named with dates and owners**: co-signer LoI (month 4), cantonal answer (ask month 6, needed month 12+), fiduciary cross-border opinion (month 10, needed month 12+). Nothing unnamed, nothing "later".

### Updated scores (1–10, higher = stronger) and probabilities
| Dimension | R2 | R3 | Why |
|---|---|---|---|
| Coherence & plausibility | 5 | 6 | F clarification removes the self-contradiction between founder rules and the build |
| Offer | 6 | 6 | unchanged; RFQs may move it either way |
| Market | 4 | 4 | unchanged until reservations/RFQs land |
| GTM | 5 | 6 | channel legality confirmed (CNIL doctrine); DE/AT ban kept |
| Unit economics | 5 | 5 | unchanged; cotisations ~quarter of revenue priced in |
| Delivery | 7 | 7 | unchanged |
| Legal & capacity | 3 | 4 | the wall is now a dated calendar with instruments, not a fog; cantonal/cross-border still open |
| Focus | 4 | 7 | DR-0013 dormancy: two lines, eight dormant |
| Moat | 3 | 3 | unchanged |
| Founder bandwidth | 3 | 3 | Bac June–July 2027 unchanged; clarification adds permission, not hours |
**Probabilities (bands, deliberately coarse):** CHF 3,000 in any single month by month 10: **30–40%** (was 30–35%; structure improved, arithmetic unchanged — three invoicing months). Run-rate CHF 3,000/month sustained at month 10: **15–25%** (unchanged). By month 18–24: **50–60%** (unchanged). Probability the *downside* is orderly (portfolio + fallback track, no debt, no legal incident): **high — that is what this round bought.**

---

## 4. Action queue (replaces round-2 list)
Machine-side, done this turn: DR-0013, DR-0014, dormancy enforced in gates, reservation template, vault site, this document, founder-actions kit.
Founder-side, in order: (1) reservation campaign launch (copy staged, needs his keystroke); (2) co-signer conversations; (3) competitor RFQs; (4) insurance simulator sitting (month 8 minus 1 day, not now); (5) cantonal written inquiry (month 6); (6) fiduciary hour (month 10). Details and scripts: `analysis/founder-actions.md`.

*Labels used per role rules: [FACT] verified this round against cited free sources; [FACT doc n] as stated in founder documents, not independently verified; [ASSUMPTION] reasoned but unverified; [OPINION] my judgment; [UNVERIFIED] needs a human act I cannot perform.*
