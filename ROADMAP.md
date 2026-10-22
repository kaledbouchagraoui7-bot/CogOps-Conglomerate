# ROADMAP — from blueprint to real business

> The founder's plan (2026-10-22), operationalized with owners: **[YOU]** = real-world action only the founder can take · **[ME]** = buildable in this workspace · **[DONE ✓]** = shipped and verified. Status lives here; the machine tracks the rest.

## 1 · Skeleton (legal & financial)

| # | Item | Owner | Status |
|---|---|---|---|
| 1.1 | One real legal entity — **GmbH, CHF 20k**, ten companies as brands/divisions; separate subsidiaries only on trigger (own revenue/liability) | YOU (notary, ~2 wks) | Doctrine fixed in **DR-0004**; form when first real revenue or liability demands (GmbH can't be "pre-formed" cheaply — CHF 20k blocked until then) |
| 1.2 | Single legal name everywhere (GmbH, domain, GitHub, invoices) | YOU + ME | **DR-0003**: "CogOps Group" settled; handles + email already consistent; **domain purchase is yours** (cogops.ch/.com — check availability, wire to Pages) |
| 1.3 | Group bank account + internal ledgers — one cost centre per company, real numbers | YOU (bank) + DONE (code) | Cost centres are real in `cogops-os` (per-company P&L, envelope accounting, platform charges); bank feed/QR-bill reconciliation after account exists |
| 1.4 | Bookkeeping + VAT with a Swiss fiduciary; chart of accounts matching the ten companies | YOU | Pick a Treuhänder (e.g. via canton fiduciary association); hand them `research/09-swiss-holding-law.md` + DR-0004; VAT registration at CHF 100k global turnover (8.1%) |
| 1.5 | Standard contracts: client terms w/ liability cap, DPA (nFADP/GDPR), "never the signatory" clauses (Dossia/Sentinel/Medtech) | ME (drafts) → YOU (lawyer review) | **DRAFTS v0.9 DONE ✓** `legal/tos.md` · `legal/dpa.md` · `legal/ropa.md` · `legal/retention.md`; checklist/triggers in `LEGAL.md`; lawyer review = yours |
| 1.6 | Professional liability insurance (priority: Sentinel, Dossia, Capital) | YOU | Get quotes once entity exists; brokers ask for the service descriptions — `OFFER.md` + blueprint serve directly |
| 1.7 | Lawyer boundary check: Capital (FINMA), Dossia (Swissmedic), Medtech (MDR) stay on the safe side | YOU | One-off review (~CHF 500–1,500); boundaries as drawn: tools-not-advice / never-signatory / research-use-not-device — written to be defensible, need confirming. Full document/registration memory: **`LEGAL.md` §C** |

## 2 · Base (infrastructure)

| # | Item | Owner | Status |
|---|---|---|---|
| 2.1 | Code in GitHub | — | **DONE ✓** private repo `CogOps-Conglomerate`, pushed + verified |
| 2.2 | Code onto your PC | YOU | `git clone https://github.com/kaledbouchagraoui7-bot/CogOps-Conglomerate.git` → `cd cogops-os && python3 selftest.py` (expect 111/111) |
| 2.3 | 24/7 server (small VPS, backups, logs, secrets in Bitwarden) | YOU (order ~CHF 5–10/mo) → ME (runbook + systemd/docker + automaton daemon) | Automaton already daemonizes (`automaton.py daemon`); runbook queued |
| 2.4 | Persistent shared DB — one CRM for all ten | ME (migration) | Supabase `Jarvis-db` exists with the 6 CRM tables; wire signups/leads export → `leads` table next |
| 2.5 | **A real gate — approvals on your phone** | DONE (code) + YOU (10 s) | `notify.py` pushes every G2/G3 gate to any ntfy.sh topic: install ntfy app → subscribe to a private topic → set `COGOPS_NOTIFY_URL` (locally) and/or the `NOTIFY_URL` secret on the Pages projects |
| 2.6 | Payments & invoicing | DONE (tool) + YOU (accounts) | **Swiss QR-bill generator shipped** (`growth/tools/qr_invoice.py`, spec-verified; bank scan-check on first real invoice). Stripe/TWINT accounts = yours when first franc lands |
| 2.7 | Email, calendar, analytics | YOU (accounts) → ME (wiring) | **Analytics DONE ✓** (Cloudflare Web Analytics, cookieless, beacon + CSP + honest privacy text). Remaining: Gmail sending + Cal.com = yours |
| 2.8 | LLM gateway + **cost cap per company** | — | **DONE ✓** provider chain + `LLM_MONTHLY_CAP_USD` (default $5/company/month, conservative estimates; free tier & KB always available) |
| 2.9 | Real data — replace flagged placeholders | ME (next) | Carbon factors are loudly labeled placeholder-grade; replacement = licensed/current factor set before any client sees Verde output |
| 2.10 | Automated tests + version history per deliverable engine | — | **DONE ✓** 111/111 selftest (run before/after any change, anti-snowball protocol); deliverables carry content-hash version stamps + as-of dates |

## 3 · Organs (the parts that make money)

| # | Item | Owner | Status |
|---|---|---|---|
| 3.1f | Intelligence live + star to all nine (DR-0010) | ME + YOU | **LIVE ✓** 2026-10-22 |
| 3.1e | Clique live: Sentinel, Capital, Dossia, Medtech + K5 links (DR-0009) | ME + YOU | **LIVE ✓** 2026-10-22 |
| 3.1d | Verde + Terra live-validation & climate-pair link (DR-0008) | ME + YOU | **LIVE ✓** 2026-10-22 |
| 3.1c | Talent live-validation (DR-0007) + Growth↔Talent link | ME + YOU | **LIVE ✓** 2026-10-22 |
| 3.1b | Helix live-validation (DR-0006): landing https://cogops-helix.pages.dev, free 48 h QC sample, 90-day window | ME (machine) + YOU (outreach) | **LIVE ✓** 2026-10-22 |
| 3.1 | One company with a paying stranger — **Growth chosen** | ME (machine) + YOU (outreach) | **Landing live: https://cogops-growth.pages.dev** — signup machine verified end-to-end (validation, dedupe, honeypot, rate-limit, live counter, admin export). Targets (DR-0005): 100 signups OR 3 pre-orders OR CHF 200 paid in 90 days |
| 3.2 | Sales routine: ICP, offer, price page, weekly quota | — | **DONE ✓** `growth/OFFER.md` (ICP, 6-rung ladder, 20 touches/5 batches/week quota, follow-up rule) |
| 3.3 | Delivery procedure per product (AI does / human reviews / turnaround) | — | **DONE ✓** `growth/OFFER.md` §4 (48 h samples; 100%→20% human review taper; branded version-hashed report) |
| 3.4 | Client portal / handover flow | ME (next) | Interim: email handover + ledger-recorded delivery hashes (OFFER §5); branded portal = JARVIS portal adaptation, queued |
| 3.5 | Real P&L — status reads real transactions | YOU (bank) → ME (reconciler) | Cost centres + envelope accounting real in code; bank/QR-bill import lands after 1.3/2.6 |

## 4 · Governance (what makes it a conglomerate)

| # | Item | Owner | Status |
|---|---|---|---|
| 4.1 | Capital allocation with numbers | — | **DONE ✓ DR-0001** (40/30/20/10 split after tax reserve & fortress; fund/kill thresholds exact) |
| 4.2 | Internal price list (Growth sells leads to the others) | — | **DONE ✓ DR-0002** |
| 4.3 | Brand architecture decided once | — | **DONE ✓ DR-0003** ("CogOps X" endorsed brands; accent color per company in `theme.json`) |
| 4.4 | Key-person plan: runbooks, backup person, partners of record | ME (runbook) + YOU (people) | CBS chapters + this roadmap ARE the runbook base; **you must name**: a trusted backup (gate approver #2) and partners of record (RA lead, security pro) — no code fixes this |

## 5 · Aesthetics (the skin)

| # | Item | Owner | Status |
|---|---|---|---|
| 5.1 | Brand system: name, logo, 2 colors, typeface, tone (Penpot) | YOU (Penpot polish) + DONE (code side: `brand/` lockups generated from theme.json, DR-0012) | Name ✓ · colors ✓ (`theme.json`: group + 10 accents) · type ✓ (system stack) · tone ✓ (candor-first) · **logo = yours in Penpot** |
| 5.2 | One theme file the site factory reads | — | **DONE ✓** `cogops-os/data/theme.json` — code reads brand, never hardcodes; Growth's report + landing follow it; favicon + OG image shipped from the same palette |
| 5.3 | Branded report templates (highest-value visual work) | ME | **First one DONE ✓** (lead-batch report, themed + version-hashed); carbon/audit/backtest templates queued |
| 5.4 | Group website + one page per company | ME | **DONE ✓** cogops-group.pages.dev (state-assembled: live trade graph, invariants, DR trail) + ten company sites = the ten pages |
| 5.5 | Visual founder dashboard (live map, replaces CLI status) | ME | **DONE ✓** `cogops.py dashboard [--serve]` — the nervous system's consciousness (OS §16, DR-0011) |

## Critical path to the first franc

```
[YOU] share the landing everywhere (LinkedIn, communities, build-in-public)  ──┐
[auto] signups accumulate → live counter → phone push per signup               ├─→ 100 signups / 3 pre-orders / CHF 200
[YOU] run the weekly quota: 20 touches, 5 sample batches (OFFER.md §3)        ──┘         │
[ME]  deliver batches via the engines + branded report                                    ▼
[YOU] QR-bill invoice (bank scan-check first) ──────────────────────────→ FIRST FRANC → DR-0004 entity decision
```
