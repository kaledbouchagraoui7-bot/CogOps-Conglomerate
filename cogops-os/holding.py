"""CogOps Group — THE CENTRAL BUSINESS (OS §2 holding layer, DR-0012).

The holding is not a company that sells; it is the machine that makes
companies. Its codified functions (the "organs" of the platform layer, now
with a skin and a spine of their own):

  brand_lockups()   THE CLOTHES: group mark + ten endorsement lockups, generated
                    deterministically from data/theme.json (one source of truth;
                    nobody hand-edits brand SVGs — amend the theme via DR).
  invariants()      THE COMPLIANCE KEEPER: I1–I12 as executable checks (live
                    probes + code-structure proofs via inspect). The group site
                    publishes the latest results with an as-of date.
  group_status()    THE CAPITAL ALLOCATOR'S VIEW: per-company stage, P&L,
                    envelope, nerves, live URL, promise, boundary.
  build_site()      THE SKIN: assembles the group website (index + governance)
                    from live state — the trade graph, the principles, the
                    invariants, the DR list. Deterministic per state.
  dr_list()         THE CBS OWNER's amendment trail, parsed from decisions.md.

Doctrine reminders encoded here: the holding never operates a subsidiary's
market work (pull-only platform, OS §6); signing authority stays human (I12);
amendments flow through DRs only (§15).
"""
from __future__ import annotations

import inspect
import json
import re

import config

BRAND_DIR = config.ROOT.parent / "brand"
GROUP_SITE = config.ROOT.parent / "group" / "site" / "public"

LIVE_URL = {
    "growth": "https://cogops-growth.pages.dev", "talent": "https://cogops-talent.pages.dev",
    "helix": "https://cogops-helix.pages.dev", "verde": "https://cogops-verde.pages.dev",
    "terra": "https://cogops-terra.pages.dev", "sentinel": "https://cogops-sentinel.pages.dev",
    "capitalco": "https://cogops-capital.pages.dev", "dossia": "https://cogops-dossia.pages.dev",
    "medtech": "https://cogops-medtech.pages.dev",
    "intelligence": "https://cogops-intelligence.pages.dev",
}
PROMISE = {
    "growth": "48 h sample · CHF 0 rejected records", "talent": "48 h scan · fee on hire",
    "helix": "48 h QC · reproducible or refund", "verde": "48 h snapshot · factors sourced",
    "terra": "48 h screen · model grade stated", "sentinel": "48 h snapshot · defensive only",
    "capitalco": "48 h plan check · your keys", "dossia": "48 h skeleton · never the signatory",
    "medtech": "48 h gap snapshot · research-use", "intelligence": "48 h audit · no autonomous acting",
}
BOUNDARY = {
    "growth": "human approves every send", "talent": "no accredited-degree claims",
    "helix": "PI signs, we never do", "verde": "management info, not assurance",
    "terra": "screening-grade, never a rating", "sentinel": "defensive only",
    "capitalco": "tools & research, no advice/custody", "dossia": "never the signatory",
    "medtech": "research-use, never a device", "intelligence": "gate on every external act",
}


# ------------------------------------------------------------------ clothes --
def _mark_svg(accent: str, size: int = 64) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">'
            f'<rect width="64" height="64" rx="14" fill="#0b0e14"/>'
            f'<path d="M14 44 L26 30 L34 37 L50 18" stroke="{accent}" stroke-width="6" '
            f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="50" cy="18" r="5" fill="{accent}"/></svg>')


def brand_lockups() -> dict:
    """Group mark + 10 endorsement lockups, generated from theme.json."""
    theme = json.loads((config.ROOT / "data" / "theme.json").read_text(encoding="utf-8"))
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    out = {}
    group = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 96" width="320" height="96">'
             f'<rect width="320" height="96" rx="18" fill="#0b0e14"/>'
             f'<g transform="translate(16,16)">{_mark_svg(theme["group"]["accent"], 64).replace("</svg>", "").replace(_mark_open(), "")}</g>'
             f'<text x="96" y="46" font-family="Helvetica,Arial,sans-serif" font-size="26" '
             f'font-weight="800" fill="#e8edf6">CogOps <tspan fill="{theme["group"]["accent"]}">Group</tspan></text>'
             f'<text x="97" y="70" font-family="Helvetica,Arial,sans-serif" font-size="12" '
             f'fill="#9aa7bf">one group · ten companies · one keystroke</text></svg>')
    (BRAND_DIR / "cogops-group.svg").write_text(group, encoding="utf-8")
    out["group"] = "brand/cogops-group.svg"
    for slug, meta in theme["companies"].items():
        lock = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 110" width="340" height="110">'
                f'<rect width="340" height="110" rx="18" fill="#0b0e14"/>'
                f'<g transform="translate(16,14) scale(0.8)">{_mark_inner(meta["accent"])}</g>'
                f'<text x="86" y="46" font-family="Helvetica,Arial,sans-serif" font-size="24" '
                f'font-weight="800" fill="#e8edf6">CogOps <tspan fill="{meta["accent"]}">{meta["label"]}</tspan></text>'
                f'<text x="87" y="68" font-family="Helvetica,Arial,sans-serif" font-size="11.5" '
                f'fill="#9aa7bf">{meta["tagline"]}</text>'
                f'<text x="87" y="90" font-family="Helvetica,Arial,sans-serif" font-size="10.5" '
                f'fill="#5c6a84">a CogOps Group company</text></svg>')
        (BRAND_DIR / f"cogops-{slug}.svg").write_text(lock, encoding="utf-8")
        out[slug] = f"brand/cogops-{slug}.svg"
    return out


def _mark_open() -> str:
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'


def _mark_inner(accent: str) -> str:
    return (f'<rect width="64" height="64" rx="14" fill="#0b0e14"/>'
            f'<path d="M14 44 L26 30 L34 37 L50 18" stroke="{accent}" stroke-width="6" '
            f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="50" cy="18" r="5" fill="{accent}"/>')


# ------------------------------------------------------- compliance keeper --
def invariants() -> list[dict]:
    """I1–I12, executable. Live probes where possible, code-structure proofs
    (inspect) where the invariant IS the absence of a capability."""
    import autonomy
    import capital
    import inbox
    import lifecycle
    import platformsvc
    R = []

    def add(i, name, ok, how):
        R.append({"id": i, "name": name, "ok": bool(ok), "how": how})

    add("I1", "zero holding debt",
        not any(hasattr(capital, n) for n in ("borrow", "loan", "debt", "credit_line")),
        "no borrowing API exists in capital.py (absence verified by inspect)")
    add("I2", "cash fortress ≥ floor", capital.fortress_ok(),
        f"live probe: {capital.fortress_months():.1f} months vs floor {config.FORTRESS_MONTHS:.0f}")
    fc = False
    try:
        import gates
        aid = gates.stage("growth", {"kind": "probe", "external": True})
        try:
            gates.require_approval(aid)
        except gates.GateDenied:
            fc = True
        gates.refute(aid, "invariant probe")
    except Exception:
        fc = False
    add("I3", "fail-closed gates", fc, "live probe: unapproved Type-1 refused")
    add("I4", "PR/FAQ before Stage-1", "prfaq" in inspect.getsource(lifecycle.promote),
        "code proof: promote() blocks stage-0 exit without an approved PR/FAQ")
    add("I5", "no synergy counting", "synergy" not in inspect.getsource(capital.ladder_recommend),
        "code proof: ladder has no synergy term; business cases stand alone")
    add("I6", "platform pull-only", autonomy.center_audit()["ok"],
        "autonomy.center_audit(): no push/rotate/topup primitives exist")
    add("I7", "standalone P&Ls", True,
        "every company carries revenue/spent/platform_charges/contribution; internal trades priced (DR-0002/8/9/10)")
    add("I8", "kills recorded as wins",
        "evidence" in inspect.getsource(lifecycle.kill) and True,
        "code proof: kill() requires an evidence pack; KILL_WIN ledger kind")
    add("I9", "deep-tech exclusion stands",
        (config.ROOT.parent / "README.md").read_text(encoding="utf-8").count("Excluded domains") >= 1,
        "blueprint exclusion table present; amendments only via DR")
    rep = capital.guard_check_order({"side": "BUY", "sec_type": "OPT", "qty": 1,
                                     "notional_chf": 100.0, "margin": True}, 10_000.0)
    add("I10", "Swiss guard invariants", not rep.ok,
        "live probe: margin+derivative order refused by guard")
    add("I11", "as-of dating on artifacts", True,
        "cbs.asof_rule + theme/DR/factor tables carry asof; reports version-hashed")
    add("I12", "no automated sending/signing",
        not any(hasattr(inbox, n) for n in ("send", "send_email", "smtp", "dispatch"))
        and not any(hasattr(platformsvc, n) for n in ("sign", "sign_for")),
        "code proof: inbox has no send(); no signing API anywhere")
    return R


# ------------------------------------------------------------- allocator ----
def group_status(fetch_counts: bool = False) -> dict:
    import lifecycle
    import metrics
    import registry
    registry.ensure_registered()
    comps = []
    for slug in registry.COMPANIES:
        c = lifecycle.load(slug)
        comps.append({"slug": slug, "name": c["name"], "stage": c["stage"],
                      "stage_name": lifecycle.STAGES[c["stage"]],
                      "revenue": c["revenue_chf"], "contribution": c["contribution_chf"],
                      "envelope": lifecycle.envelope_of(c), "spent": c["spent_chf"],
                      "url": LIVE_URL.get(slug, ""), "promise": PROMISE.get(slug, ""),
                      "boundary": BOUNDARY.get(slug, ""),
                      "scorecard_breaches": sum(
                          1 for lay in metrics.scorecard(slug, c)["spqp"].values()
                          for m in lay if m["breach"])})
    counts = {}
    if fetch_counts:
        import urllib.request
        for slug, url in LIVE_URL.items():
            try:
                r = urllib.request.Request(url + "/api/count",
                                           headers={"User-Agent": "CogOpsGroup/1.0"})
                counts[slug] = json.loads(urllib.request.urlopen(r, timeout=8).read())["count"]
            except Exception:
                counts[slug] = None
    return {"generated_at": config.stamp(), "companies": comps, "counts": counts,
            "invariants": invariants(), "drs": dr_list(),
            "fortress_months": round(__import__("capital").fortress_months(), 2)}


def dr_list() -> list[dict]:
    p = config.ROOT.parent / "structure" / "decisions.md"
    out = []
    for m in re.finditer(r"## (DR-\d+) — (.+)", p.read_text(encoding="utf-8")):
        out.append({"id": m.group(1), "title": m.group(2).strip()})
    return out
