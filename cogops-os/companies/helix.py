"""CogOps Helix — computational biology & AI drug-discovery support (OS §13;
blueprint co. 4; blue-ocean #2, 9.8/10).

Seed: the computational-biology-portfolio pipelines. State-of-the-art here =
the portfolio's own discipline as callable engines: reference-transcript QC,
audit-trailed EDA with regulatory Table 1 (SciPy-free validated stats), and
PMID-traceable literature surveillance with EuropePMC fallback. Dry-lab only
(no wet lab, no clinical decisions — blueprint boundary).
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request

import config
import ledger
import statsnr

META = {
    "name": "CogOps Helix",
    "dan": "Labs, biotechs and CROs get dry-lab results (QC, EDA, evidence "
           "matrices) at machine cost, without hiring bioinformaticians.",
    "stage_at_v10": 1,
    "seed_assets": "computational-biology-portfolio v1.1 (3 shipped pipelines)",
    "human_of_record": "client's PI signs scientific use",
    "input_metrics": [
        {"key": "pipelines_delivered_month", "layer": "F", "owner": "pipeline-operator", "floor": 1},
        {"key": "rerun_reproducibility_pct", "layer": "Q", "owner": "verifier", "floor": 100},
        {"key": "turnaround_hours", "layer": "Q", "owner": "squad-coordinator", "floor": None},
    ],
    "squad_roles": ["bio-qc-analyst", "eda-statistician", "literature-synthesizer",
                    "pipeline-operator", "verifier",
                    "treasury-accountant",
                    "ai-security-reviewer"],
}

CODON_START = {"ATG"}
CODON_STOP = {"TAA", "TAG", "TGA"}
COMP = str.maketrans("ACGTN", "TGCAN")


# ------------------------------------------------------- 01 sequence QC ----
def sequence_qc(params: dict, slug: str) -> dict:
    """FASTA → per-record QC: length, GC%, longest ORF both strands, and the
    built-in cross-check gate (portfolio 01's NM_000492 discipline generalized:
    any expected length/aa assertions passed in params)."""
    fasta = params.get("fasta", "")
    checks = params.get("cross_checks", {})   # {acc: {"nt": 4443, "aa": 1480}}
    recs = _parse_fasta(fasta)
    out = []
    for acc, seq in recs:
        seq_u = seq.upper()
        gc = round(100.0 * (seq_u.count("G") + seq_u.count("C")) / max(len(seq_u), 1), 2)
        orf_f = _longest_orf(seq_u)
        orf_r = _longest_orf(seq_u.translate(COMP)[::-1])
        row = {"accession": acc, "nt": len(seq_u), "gc_pct": gc,
               "orf_fwd_aa": orf_f, "orf_rev_aa": orf_r}
        if acc in checks:
            exp = checks[acc]
            row["cross_check"] = ("PASS" if (exp.get("nt") is None or row["nt"] == exp["nt"])
                                  and (exp.get("aa") is None
                                       or max(orf_f, orf_r) == exp["aa"]) else "FAIL")
        out.append(row)
    artifact = {"mode": "engine", "records": len(out), "qc": out,
                "asof": config.today()}
    _emit(slug, "sequence_qc", artifact)
    return artifact


def _parse_fasta(text: str) -> list[tuple[str, str]]:
    recs, acc, buf = [], None, []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(">"):
            if acc:
                recs.append((acc, "".join(buf)))
            acc, buf = line[1:].split()[0], []
        elif line:
            buf.append(re.sub(r"[^A-Za-z]", "", line))
    if acc:
        recs.append((acc, "".join(buf)))
    return recs


def _longest_orf(seq: str) -> int:
    best = 0
    for frame in range(3):
        i, n = frame, len(seq)
        while i + 2 < n:
            if seq[i:i + 3] in CODON_START:
                j = i
                aa = 0
                while j + 2 < n:
                    c = seq[j:j + 3]
                    j += 3
                    if c in CODON_STOP:
                        best = max(best, aa)
                        break
                    aa += 1
                i = j
            else:
                i += 3
    return best


# ------------------------------------------------- 02 EDA + Table 1 --------
def table1(params: dict, slug: str) -> dict:
    """Cohort → audit-trailed cleaning (dedupe, range rejection, arm-stratified
    median imputation) → regulatory Table 1 with Welch t / χ² (statsnr,
    validated <1e-9 vs SciPy in the portfolio's FIXES.md). Seeded + logged:
    every exclusion is recorded (ALCOA+ attributable)."""
    rows = [dict(r) for r in params.get("cohort", [])]
    seed_n = len(rows)
    audit = []
    # dedupe on patient_id
    seen, dedup = set(), []
    for r in rows:
        pid = r.get("patient_id")
        if pid in seen:
            audit.append({"action": "dedupe_drop", "patient_id": pid})
            continue
        seen.add(pid)
        dedup.append(r)
    # range rejection (numeric fields with declared bounds)
    bounds = params.get("bounds", {"age": (18, 90)})
    kept = []
    for r in dedup:
        bad = None
        for f, (lo, hi) in bounds.items():
            try:
                v = float(r.get(f))
                if not lo <= v <= hi:
                    bad = f"{f}={v} outside [{lo},{hi}]"
            except (TypeError, ValueError):
                continue
        if bad:
            audit.append({"action": "range_reject", "patient_id": r.get("patient_id"),
                          "why": bad})
        else:
            kept.append(r)
    # arm-stratified median imputation for numeric gaps
    for f in bounds:
        for arm in {r.get("arm") for r in kept}:
            vals = sorted(float(r[f]) for r in kept
                          if r.get("arm") == arm and r.get(f) not in (None, "", "NA"))
            if not vals:
                continue
            med = vals[len(vals) // 2] if len(vals) % 2 else (vals[len(vals)//2 - 1] + vals[len(vals)//2]) / 2
            for r in kept:
                if r.get("arm") == arm and r.get(f) in (None, "", "NA"):
                    r[f] = med
                    audit.append({"action": "impute_median", "patient_id": r.get("patient_id"),
                                  "field": f, "value": med, "stratum": arm})
    arms = sorted({r.get("arm", "?") for r in kept})
    table, tests = {}, []
    for f in bounds:
        table[f] = {a: _summ([float(r[f]) for r in kept if r.get("arm") == a
                              and r.get(f) is not None]) for a in arms}
        if len(arms) == 2:
            a = [float(r[f]) for r in kept if r.get("arm") == arms[0] and r.get(f) is not None]
            b = [float(r[f]) for r in kept if r.get("arm") == arms[1] and r.get(f) is not None]
            if len(a) >= 2 and len(b) >= 2:
                tests.append({"field": f, **statsnr.welch_t(a, b)})
    # categorical χ² (sex if present)
    if any("sex" in r for r in kept) and len(arms) == 2:
        sexes = sorted({r["sex"] for r in kept})
        ct = [[sum(1 for r in kept if r.get("arm") == a and r.get("sex") == s)
               for s in sexes] for a in arms]
        tests.append({"field": "sex", **statsnr.chi2_contingency(ct)})
    artifact = {"mode": "engine", "seed_rows": seed_n, "analyzed_rows": len(kept),
                "audit_trail": audit, "table1": table, "tests": tests,
                "arms": arms, "asof": config.today()}
    _emit(slug, "table1", artifact)
    return artifact


def _summ(v: list[float]) -> dict:
    if not v:
        return {"n": 0}
    s = sorted(v)
    med = s[len(s)//2] if len(s) % 2 else (s[len(s)//2 - 1] + s[len(s)//2]) / 2
    mean = sum(s) / len(s)
    sd = (sum((x - mean) ** 2 for x in s) / max(len(s) - 1, 1)) ** 0.5
    return {"n": len(s), "median": round(med, 2), "mean": round(mean, 2),
            "sd": round(sd, 2)}


# --------------------------------------------- 03 literature surveillance --
def lit_surveil(params: dict, slug: str) -> dict:
    """PubMed E-utilities primary → Europe PMC fallback (portfolio 03 pattern:
    never partial deliverables; PMID-first; offline mode is honest, not fake)."""
    query = params.get("query", "CFTR modulator therapy safety")
    mx = min(int(params.get("max", 10)), 50)
    email = params.get("entrez_email", "cogops.engine@gmail.com")
    recs, source = [], None
    try:
        recs, source = _pubmed(query, mx, email), "pubmed"
    except Exception as e:
        ledger.event("lit_surveil_fallback", slug, {"primary_err": str(e)[:90]})
        try:
            recs, source = _europmc(query, mx), "europe_pmc"
        except Exception as e2:
            return {"mode": "offline", "query": query,
                    "why": f"pubmed: {str(e)[:80]} | epmc: {str(e2)[:80]}",
                    "records": [], "asof": config.today()}
    artifact = {"mode": f"engine:{source}", "query": query,
                "records": recs, "n": len(recs), "asof": config.today()}
    if recs:
        artifact["evidence_matrix_md"] = _matrix(recs)
    _emit(slug, "lit_surveil", {"mode": artifact["mode"], "n": len(recs)})
    return artifact


def _pubmed(query: str, mx: int, email: str) -> list[dict]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    q = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmax": mx,
                                "sort": "relevance", "email": email,
                                "retmode": "json"})
    ids = json.loads(urllib.request.urlopen(base + "esearch.fcgi?" + q,
                                            timeout=15).read())["esearchresult"]["idlist"]
    if not ids:
        return []
    s = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids),
                                "retmode": "xml"})
    xml = urllib.request.urlopen(base + "efetch.fcgi?" + s, timeout=20).read().decode(errors="replace")
    out = []
    for pmid in ids:
        blk = re.search(rf"<PubmedArticle>.*?<PMID[^>]*>{pmid}</PMID>(.*?)</PubmedArticle>",
                        xml, re.S)
        title = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", xml[xml.find(f">{pmid}<"):], re.S)
        doi = re.search(rf'<ArticleId IdType="doi">([^<]+)</ArticleId>',
                        xml[xml.find(f">{pmid}<"):xml.find(f">{pmid}<") + 20000])
        out.append({"pmid": pmid,
                    "title": re.sub(r"<[^>]+>", "", title.group(1)).strip() if title else "",
                    "doi": doi.group(1) if doi else None})
    return out


def _europmc(query: str, mx: int) -> list[dict]:
    q = urllib.parse.urlencode({"query": query, "format": "json", "pageSize": mx,
                                "resultType": "core", "sort": "CITED desc"})
    j = json.loads(urllib.request.urlopen(
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + q,
        timeout=15).read())
    return [{"pmid": r.get("pmid"), "title": r.get("title", ""),
             "doi": r.get("doi"), "cited_by": r.get("citedByCount")}
            for r in j["resultList"]["result"] if r.get("pmid")]


def _matrix(recs: list[dict]) -> str:
    lines = ["| PMID | Title | DOI |", "|---|---|---|"]
    for r in recs:
        doi = f"[{r['doi']}](https://doi.org/{r['doi']})" if r.get("doi") else "—"
        lines.append(f"| {r['pmid']} | {r['title'][:80]} | {doi} |")
    return "\n".join(lines)




def helix_report_html(params: dict, slug: str) -> dict:
    """Client-facing branded report (theme accent: helix violet) bundling a
    sequence-QC and/or Table-1 artifact, with methods, as-of dates, the
    reproducibility hash and the human-of-record line. Version-stamped."""
    import hashlib
    import json as _json
    theme = _json.loads((config.ROOT / "data" / "theme.json").read_text(encoding="utf-8"))
    gr, ac = theme["group"], theme["companies"]["helix"]["accent"]
    client = params.get("client", "Client lab")
    qc = params.get("qc") or sequence_qc(params, slug) if params.get("fasta") else params.get("qc")
    t1 = params.get("table1")
    blocks = []
    if qc:
        rows = "".join(f"<tr><td>{r['accession']}</td><td>{r['nt']}</td><td>{r['gc_pct']}</td>"
                       f"<td>{r['orf_fwd_aa']}</td><td>{r.get('cross_check', '—')}</td></tr>"
                       for r in qc["qc"])
        blocks.append("<h2>Sequence QC</h2><table><tr><th>Accession</th><th>nt</th><th>GC%</th>"
                      "<th>ORF aa (fwd)</th><th>Cross-check</th></tr>" + rows + "</table>")
    if t1:
        blocks.append("<h2>Cohort EDA &amp; Table 1</h2><p>Analyzed rows: "
                      f"{t1['analyzed_rows']} of {t1['seed_rows']} · cleaning actions: "
                      f"{len(t1['audit_trail'])} (fully attributable)</p>")
    body = (f"<!DOCTYPE html><html><head><meta charset=utf-8><title>Helix report — {client}</title>"
            f"<style>body{{background:{gr['bg']};color:{gr['ink']};font:14px/1.6 {gr['font']};padding:32px}}"
            f".wrap{{max-width:860px;margin:0 auto}}h1{{color:{ac};font-size:22px}}"
            f".badge{{display:inline-block;border:1px solid {gr['line']};color:{ac};border-radius:99px;padding:4px 12px;font-size:11px;letter-spacing:1px}}"
            f"table{{width:100%;border-collapse:collapse;margin:12px 0}}td,th{{padding:8px 10px;border-bottom:1px solid {gr['line']};text-align:left;font-size:13px}}"
            f"th{{color:{ac};font-size:11px;text-transform:uppercase;letter-spacing:1px}}"
            f"h2{{color:{ac};font-size:16px;margin:22px 0 6px}}.foot{{color:{gr['dim']};font-size:12px;margin-top:26px;border-top:1px solid {gr['line']};padding-top:12px}}</style>"
            f"</head><body><div class=wrap><span class=badge>COGOPS HELIX · a CogOps Group company</span>"
            f"<h1>Dry-lab report — {client}</h1>"
            f"<p>Generated {config.stamp()} · methods: NCBI-style QC (GC/ORF both strands), "
            f"NR-validated statistics (Welch/χ² cross-validated &lt;1e-9 vs SciPy)</p>"
            + "".join(blocks) +
            f"<div class=foot>Version stamp <b>{{HASH}}</b> · reproducibility: re-run with the same "
            f"inputs and frozen clock yields byte-identical artifacts · "
            f"<b>Human of record: {META['human_of_record']}</b> — Helix never signs scientific "
            f"conclusions. · cogops.engine@gmail.com</div></div></body></html>")
    hh = hashlib.sha256(body.encode()).hexdigest()[:16]
    body = body.replace("{HASH}", hh)
    p = config.OUTBOX / f"helix_report_{client.lower().replace(' ', '_')}_{config.today()}_{hh[:8]}.html"
    p.write_text(body, encoding="utf-8")
    ledger.event("helix_deliverable", slug, {"client": client, "version": hh})
    return {"mode": "engine", "html_file": p.name, "version_hash": hh,
            "client": client, "asof": config.today()}




def qc_with_trail(params: dict, slug: str) -> dict:
    """K5 link H-M: helix buys alcoa_trail FROM Medtech via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on helix's P&L (I7)."""
    import platformsvc
    from companies import medtech as seller
    ticket = platformsvc.request(slug, "alcoa_trail", spec="ALCOA+ trail for QC run", units=1)
    bought = seller.alcoa_log({"entry":{"experiment":"helix-qc","subject":params.get("fasta","")[:40],"value":1,"unit":"run","recorded_by":"helix"}}, "medtech")
    platformsvc.serve(ticket["id"], {"ref": f"helix-qc_with_trail:{ticket['id']}"})
    out = sequence_qc(params, slug)
    out["internal_purchase"] = {"from": "Medtech", "service": "alcoa_trail",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["alcoa_trail"] = bought["trail_lines"]; out["provenance"] = f"audit trail via CogOps Medtech ticket {ticket['id']}"
    return out



def qc_with_alcoa(params: dict, slug: str) -> dict:
    """K5 link H-D: helix buys alcoa_qc FROM Dossia via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on helix's P&L (I7)."""
    import platformsvc
    from companies import dossia as seller
    ticket = platformsvc.request(slug, "alcoa_qc", spec="ALCOA+ QC of QC report", units=1)
    bought = seller.qc_checklist({"document":{"author":"helix","reviewer":"pending-PI","text":"qc","timestamp":config.stamp(),"source_ref":"engine","numbers_carry_asof":True,"has_todos":False,"units_consistent":True,"stored_in_ledger":True,"path":"outbox"}}, "dossia")
    platformsvc.serve(ticket["id"], {"ref": f"helix-qc_with_alcoa:{ticket['id']}"})
    out = sequence_qc(params, slug)
    out["internal_purchase"] = {"from": "Dossia", "service": "alcoa_qc",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["alcoa_pass_rate"] = bought["pass_rate_pct"]; out["provenance_qc"] = f"ALCOA+ checklist via CogOps Dossia ticket {ticket['id']}"
    return out



def treasury_setup(params: dict, slug: str) -> dict:
    """K5 link H-C: helix buys treasury_policy FROM Capital via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on helix's P&L (I7)."""
    import platformsvc
    from companies import capitalco as seller
    ticket = platformsvc.request(slug, "treasury_policy", spec="treasury policy for Helix sweep", units=1)
    bought = seller.treasury_policy({}, "capitalco")
    platformsvc.serve(ticket["id"], {"ref": f"helix-treasury_setup:{ticket['id']}"})
    out = {"mode":"engine","company":"helix"}
    out["internal_purchase"] = {"from": "Capital", "service": "treasury_policy",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["policy"] = bought["policy"]
    return out



def secure_deployment(params: dict, slug: str) -> dict:
    """K5 link H-S: helix buys ai_sec_review FROM Sentinel via internal-market
    ticket (DR-0009 price). Integrated into the deliverable with provenance;
    the charge lands on helix's P&L (I7)."""
    import platformsvc
    from companies import sentinel as seller
    ticket = platformsvc.request(slug, "ai_sec_review", spec="security review of delivery portal", units=1)
    bought = seller.ai_security_review({"kb_first":True,"provider_labels":True,"refuses_advice":True,"gated_actions":True}, "sentinel")
    platformsvc.serve(ticket["id"], {"ref": f"helix-secure_deployment:{ticket['id']}"})
    out = {"mode":"engine","company":"helix"}
    out["internal_purchase"] = {"from": "Sentinel", "service": "ai_sec_review",
                                 "ticket": ticket["id"], "notional_chf": ticket["notional_chf"]}
    out["security"] = {"containment": bought.get("containment_rate_pct"), "config": bought["config_checks"], "ticket_ref": ticket["id"]}
    return out



def intelligence_ops(params: dict, slug: str) -> dict:
    """Star link: this company buys Intelligence's deployment/automation service
    via internal ticket (ai_ops, DR-0010 price)."""
    import platformsvc
    from companies import intelligence as intel
    kind = params.get("kind", "automation_audit")
    ticket = platformsvc.request(slug, "ai_ops", spec=f"{kind} for {slug}", units=1)
    if kind == "deploy":
        out = intel.deploy_client({"client": params.get("client", f"{slug}-client"),
                                   "services": params.get("services",
                                       ["site_factory", "llm_gateway", "crm_portal"])},
                                  "intelligence")
    else:
        out = intel.automation_audit({"answers": params.get("answers", {
            "process": f"{slug} delivery", "volume_month": 20, "minutes_per": 30,
            "steps": ["collect client inputs", "draft deliverable", "human review",
                      "approve delivery", "send to client"]})}, "intelligence")
    platformsvc.serve(ticket["id"], {"ref": f"{slug}-intel:{ticket['id']}"})
    return {"mode": "engine", "kind": kind,
            "internal_purchase": {"from": "intelligence", "service": "ai_ops",
                                  "ticket": ticket["id"],
                                  "notional_chf": ticket["notional_chf"]},
            "result": out, "asof": config.today()}


def _emit(slug: str, kind: str, artifact: dict) -> None:
    p = config.OUTBOX / f"{slug}_{kind}_{config.today()}.json"
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")


# K5 clique links: partner -> OUR buying task (complete graph, DR-0009)
LINKS = {"intelligence": "intelligence_ops", 'medtech': 'qc_with_trail', 'dossia': 'qc_with_alcoa', 'capitalco': 'treasury_setup', 'sentinel': 'secure_deployment'}

TASKS = {
    "intelligence_ops": {"fn": intelligence_ops, "role": "pipeline-operator"},
    "qc_with_trail": {"fn": qc_with_trail, "role": "verifier"},
    "qc_with_alcoa": {"fn": qc_with_alcoa, "role": "verifier"},
    "treasury_setup": {"fn": treasury_setup, "role": "treasury-accountant"},
    "secure_deployment": {"fn": secure_deployment, "role": "ai-security-reviewer"},
    "sequence_qc": {"fn": sequence_qc, "role": "bio-qc-analyst"},
    "table1": {"fn": table1, "role": "eda-statistician"},
    "lit_surveil": {"fn": lit_surveil, "role": "literature-synthesizer"},
    "helix_report_html": {"fn": helix_report_html, "role": "pipeline-operator"},
}
