"""CogOps OS — configuration (OS §3–§5, §14).

Everything env-driven (JARVIS config.py doctrine): no hardcoded secrets, no
hardcoded ports, safe paper/dry-run defaults. Every constant cites the OS
section it instantiates; numbers marked (default) are DR-tunable per §15.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

try:  # optional, same pattern as JARVIS
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
RUNTIME_DIR = Path(os.environ.get("COGOPS_RUNTIME_DIR", ROOT / "runtime"))
OUTBOX = RUNTIME_DIR / "outbox"          # cadence artifacts & company deliverables
LEDGER_DIR = RUNTIME_DIR / "ledger"       # append-only decision + event ledgers
COMPANY_DIR = RUNTIME_DIR / "companies"   # per-company state
for d in (OUTBOX, LEDGER_DIR, COMPANY_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- clock ----
# FREEZE_CLOCK (epoch seconds) makes every artifact byte-reproducible —
# the comp-bio portfolio's determinism rule, applied group-wide (CBS Ch. Verify).
FREEZE_CLOCK = os.environ.get("COGOPS_FREEZE_CLOCK")

def now() -> float:
    return float(FREEZE_CLOCK) if FREEZE_CLOCK else time.time()

def today() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime(now()))

def stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now()))

# ------------------------------------------------- envelopes & gates (§5) --
STAGE_ENVELOPES_CHF = {          # (defaults, DR-tunable) OS §5 table
    0: 0.0,
    1: float(os.environ.get("ENV_STAGE1_CHF", "500")),
    2: float(os.environ.get("ENV_STAGE2_CHF", "2000")),
    3: float(os.environ.get("ENV_STAGE3_MONTHLY_CHF", "500")),
    4: None,                     # reinvestment ladder: 50% of contribution, quarterly cap
    5: float(os.environ.get("ENV_STAGE5_WINDOWN_CHF", "500")),
}
STAGE_TIMEBOX_DAYS = {0: 7, 1: 28, 2: 56, 3: 182, 4: None, 5: 90}   # OS §5
STAGE3_REVENUE_REINVEST_PCT = 0.10      # ≤10% of revenue reinvested (OS §5)
STAGE4_CONTRIBUTION_REINVEST_PCT = 0.50 # up to 50% of contribution (OS §5)
DELEGATED_CAPS_CHF = {1: 100.0, 2: 250.0, 3: 500.0, 4: 500.0}      # OS §3 (defaults)
INCUBATION_SLOTS_PER_QUARTER = int(os.environ.get("BUILD_SLOTS", "3"))  # OS §5 rule

# ------------------------------------------------------ capital (§4, §12) --
FORTRESS_MONTHS = float(os.environ.get("FORTRESS_MONTHS", "6"))     # invariant I2
MONTHLY_FIXED_COSTS_CHF = float(os.environ.get("MONTHLY_FIXED_COSTS_CHF", "150"))
SWEEP_PROFIT_SHARE = float(os.environ.get("SWEEP_PROFIT_SHARE", "0.30"))  # JARVIS DNA
# Swiss investment guard (invariant I10) — condensed from JARVIS
MIN_ORDER_CHF = 0.01          # one-cent floor, no ceiling (JARVIS fix 6c7429a)
MIN_HOLDING_DAYS = 180
MAX_TURNOVER_RATIO = 5.0
MAX_ORDERS_PER_MONTH = 12

# ------------------------------------------------- lifecycle kill rules (§5)
STAGE1_EVIDENCE = {             # exit evidence, any ONE suffices (OS §5)
    "waitlist_min": 100, "preorders_min": 3, "pilot_paid_chf_min": 200.0,
}
KILL_REVIEW_AFTER_NEG_MONTHS = 2

# ---------------------------------------------------------- identity (§1) --
GROUP = "CogOps Group"
FOUNDER = os.environ.get("COGOPS_FOUNDER", "founder")
CONFIRM_PHRASE = os.environ.get("COGOPS_CONFIRM_PHRASE", "cogops approves")
CURRENCY = "CHF"

# ------------------------------------------------------------- roster (§10)
UNIVERSES = ("revenue", "delivery", "capital", "people",
             "infrastructure", "strategy", "continuity")   # JARVIS 7-universe DNA

def summary() -> str:
    return (f"{GROUP} OS · runtime={RUNTIME_DIR} · fortress≥{FORTRESS_MONTHS:.0f}mo "
            f"× {MONTHLY_FIXED_COSTS_CHF:,.0f} {CURRENCY} · sweep {SWEEP_PROFIT_SHARE:.0%} · "
            f"caps {DELEGATED_CAPS_CHF} · clock={'FROZEN' if FREEZE_CLOCK else 'live'}")
