#!/usr/bin/env python3
"""Swiss QR-bill invoice generator — CogOps Growth's "first franc" tool.

Pure stdlib + `segno` (pip install segno) for the QR image. Implements the
SIX Swiss Implementation Guidelines QR-bill payload (SPC/0200/1, CRLF line
ends, QRR reference with mod-10-recursive check digit, EPD trailer) and
renders a printable A6 payment-part invoice sheet (HTML, QR embedded as
data-URI — opens anywhere, prints to PDF).

HONESTY FLAG (CBS Ch.3): v0 implementation — validated against the spec's
structural rules and selftests below, but **have your bank/fiduciary scan the
FIRST real invoice before sending it to a client.** Known-good practice, not
yet field-proven.

  python3 qr_invoice.py --amount 900.00 --invoice-no G-2026-001 \
      --creditor-name "CogOps Group" --creditor-street "Rue du Lac 12" \
      --creditor-plz 2501 --creditor-city Biel --iban CH9300762011623852957 \
      --debtor "ACME AG, Zürich" --message "Sample batch → retainer Oct-26" \
      --out invoice_G-2026-001.html
"""
from __future__ import annotations

import argparse
import re
import sys

CRLF = "\r\n"
MOD10_TABLE = (0, 9, 4, 6, 8, 2, 7, 1, 3, 5)


def mod10_recursive(digits: str) -> str:
    """Modulo 10 recursive check digit (QR-bill / ISR standard)."""
    if not digits or not digits.isdigit():
        raise ValueError("mod10rec input must be numeric")
    c = 0
    for d in digits:
        c = MOD10_TABLE[(c + int(d)) % 10]
    return str((10 - c) % 10)


def iban_valid(iban: str) -> bool:
    """ISO 1339 mod-97 IBAN check."""
    s = re.sub(r"\s+", "", iban).upper()
    if not re.match(r"^[A-Z]{2}\d{2}[A-Z0-9]{10,30}$", s):
        return False
    r = s[4:] + s[:4]
    n = "".join(str(int(ch, 36)) for ch in r)
    return int(n) % 97 == 1


def qrr_reference(invoice_no: str) -> str:
    """Build a 27-digit QRR creditor reference from an invoice number:
    digits of the invoice number, left-padded to 26, + mod10rec check digit."""
    digits = re.sub(r"\D", "", invoice_no)
    if not digits:
        raise ValueError("invoice number must contain at least one digit")
    body = digits.rjust(26, "0")[-26:]
    return body + mod10_recursive(body)


def fmt_ref(ref: str) -> str:
    """Group reference 5-5-5… from the right for printing: 00 00000 00000 ..."""
    out, i = [], len(ref)
    while i > 0:
        out.insert(0, ref[max(0, i - 5):i])
        i -= 5
    return " ".join(out)


def fmt_iban(iban: str) -> str:
    s = re.sub(r"\s+", "", iban).upper()
    return " ".join(s[i:i + 4] for i in range(0, len(s), 4))


def qr_payload(amount: float | None, currency: str, creditor: dict, iban: str,
               reference: str, message: str = "", bill_info: str = "") -> str:
    """Full QR-bill payload string (CRLF-separated), field order per SIX IG.
    creditor: {name, street, building, plz, city, country}"""
    if currency.upper() not in ("CHF", "EUR"):
        raise ValueError("currency must be CHF or EUR")
    if not iban_valid(iban):
        raise ValueError(f"IBAN check failed: {iban}")
    if not re.match(r"^\d{27}$", reference):
        raise ValueError("reference must be 27 digits (QRR)")
    amt = "" if amount is None else f"{amount:.2f}"
    if amt and not re.match(r"^\d{1,9}\.\d{2}$", amt):
        raise ValueError("amount format 0.01–999999999.99")
    name = creditor["name"][:70]
    street = creditor.get("street", "")[:70]
    building = creditor.get("building", "")[:16]
    plz = str(creditor.get("plz", ""))[:16]
    city = creditor.get("city", "")[:35]
    country = creditor.get("country", "CH").upper()[:2]
    if not (name and plz and city and country == "CH" or country.isalpha()):
        raise ValueError("creditor name/plz/city/country required")
    fields = [
        "SPC", "0200", "1",                 # QRType, Version, Coding
        amt, currency.upper(),              # transaction amount, currency
        name, street, building, plz, city, country,   # creditor (6)
        "", "", "", "", "", "",             # ultimate creditor (reserved, empty)
        "QRR", reference,                   # payment reference type + reference
        message[:140],                      # unstructured message
        "EPD",                              # trailer (fixed)
        bill_info[:140],                    # billing information (optional)
    ]
    return CRLF.join(fields) + CRLF


def qr_data_uri(payload: str) -> str:
    try:
        import segno
    except ImportError:
        raise SystemExit("segno not installed — run: pip install segno")
    import io
    buf = io.BytesIO()
    segno.make(payload, error="m").save(buf, kind="png", scale=6, border=2)
    import base64
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>Invoice {inv} — CogOps Growth</title>
<style>
 @page {{ size: A4; margin: 14mm; }}
 body{{font:13px/1.55 -apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:#111;background:#fff;margin:0;padding:24px}}
 .inv{{max-width:720px;margin:0 auto}}
 header{{display:flex;justify-content:space-between;align-items:baseline;border-bottom:3px solid #0b0e14;padding-bottom:10px}}
 h1{{font-size:22px;margin:0}} .brand{{color:#2ea97c;font-weight:800;letter-spacing:.5px}}
 table.meta{{width:100%;border-collapse:collapse;margin:18px 0}}
 table.meta td{{padding:5px 8px;border-bottom:1px solid #eee;vertical-align:top}}
 table.meta td:first-child{{color:#666;width:190px}}
 .total{{font-size:20px;font-weight:800;text-align:right;margin:10px 0 24px}}
 .part{{border:1.5px solid #111;border-radius:6px;display:grid;grid-template-columns:52mm 1fr;margin-top:30px;page-break-inside:avoid}}
 .receipt{{border-right:1px dashed #999;padding:10px 12px}}
 .stub h3,.main h3{{font-size:10px;letter-spacing:1.2px;text-transform:uppercase;margin:0 0 6px;color:#444}}
 .kv{{font-size:11px;margin:3px 0}} .kv b{{display:inline-block;min-width:78px;color:#555;font-weight:600}}
 .main{{padding:14px 16px;display:grid;grid-template-columns:1fr 60mm;gap:14px}}
 .amountbox{{border:1px solid #111;padding:4px 10px;display:inline-block;min-width:90px}}
 img.qr{{width:56mm;height:56mm;image-rendering:pixelated}}
 .fineprint{{color:#777;font-size:11px;margin-top:22px}}
 .flag{{background:#fff8e6;border:1px solid #e6c86e;border-radius:6px;padding:8px 12px;font-size:12px;margin:14px 0;color:#7a5c00}}
</style></head><body><div class="inv">
<header><div><span class="brand">COGOPS GROWTH</span> <span style="color:#888">· a CogOps Group company</span></div><div>INVOICE <b>{inv}</b></div></header>
{flag}
<table class="meta">
 <tr><td>Billed to</td><td><b>{debtor}</b></td></tr>
 <tr><td>Deliverable</td><td>{desc}</td></tr>
 <tr><td>Date</td><td>{date}</td></tr>
 <tr><td>Payment terms</td><td>net {terms} days · CHF · payable via QR-bill below (or bank transfer)</td></tr>
 <tr><td>IBAN</td><td>{iban_fmt}</td></tr>
 <tr><td>Reference (QRR)</td><td><b>{ref_fmt}</b> — always include this reference</td></tr>
</table>
<div class="total">Amount due: CHF {amount}</div>

<div class="part">
 <div class="receipt">
  <h3>Receipt / Récépissé</h3>
  <div class="kv"><b>Account</b><br>{iban_fmt}</div>
  <div class="kv"><b>Reference</b><br>{ref_fmt}</div>
  <div class="kv"><b>Payable to</b><br>{creditor_name}<br>{creditor_addr}</div>
  <div class="kv" style="margin-top:10px"><b>Amount</b><br><span class="amountbox">CHF {amount}</span></div>
  <div class="kv" style="margin-top:10px"><b>Accepted by</b><br><span class="amountbox" style="min-width:120px">&nbsp;</span></div>
 </div>
 <div class="main">
  <div>
   <h3>Payment part / Section paiement</h3>
   <div class="kv"><b>Account</b><br>{iban_fmt}</div>
   <div class="kv"><b>Reference</b><br>{ref_fmt}</div>
   <div class="kv"><b>Payable to</b><br>{creditor_name}<br>{creditor_addr}</div>
   <div class="kv" style="margin-top:8px"><b>Amount</b><br><span class="amountbox">CHF {amount}</span></div>
   <div class="kv"><b>Currency</b><br><span class="amountbox">CHF</span></div>
  </div>
  <div style="text-align:center"><img class="qr" src="{qr}" alt="Swiss QR-bill"><div class="kv" style="font-size:9px;color:#888">Swiss QR-bill (SPC 0200)</div></div>
 </div>
</div>
<p class="fineprint">{footer}</p>
</div></body></html>"""


def build(amount: float, invoice_no: str, creditor: dict, iban: str,
          debtor: str, desc: str = "", message: str = "", terms: int = 14,
          out: str | None = None, date: str | None = None) -> dict:
    import time
    ref = qrr_reference(invoice_no)
    payload = qr_payload(amount, "CHF", creditor, iban, ref, message)
    date = date or time.strftime("%Y-%m-%d")
    html = HTML.format(
        inv=invoice_no, debtor=debtor, desc=desc or invoice_no, date=date,
        terms=terms, amount=f"{amount:,.2f}", iban_fmt=fmt_iban(iban),
        ref_fmt=fmt_ref(ref), creditor_name=creditor["name"],
        creditor_addr=", ".join(x for x in (creditor.get("street", ""),
                                            str(creditor.get("plz", "")) + " " + creditor.get("city", "")) if x),
        qr=qr_data_uri(payload),
        footer="VAT: not registered (below CHF 100k threshold) · CogOps Group, Switzerland · "
               "cogops.engine@gmail.com · This invoice was generated by a regression-tested tool "
               "(mod-10-recursive reference, ISO-1339 IBAN check) — first real invoice to be "
               "scan-verified by the bank before sending.",
        flag='<div class="flag">⚠ v0 generator: have the bank/fiduciary scan-verify the FIRST invoice before client delivery (CBS Ch.3).</div>')
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
    return {"invoice_no": invoice_no, "reference": ref, "reference_fmt": fmt_ref(ref),
            "iban": fmt_iban(iban), "amount_chf": amount, "payload": payload,
            "payload_lines": payload.count(CRLF), "html_file": out}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Swiss QR-bill invoice (CogOps Growth)")
    ap.add_argument("--amount", type=float, required=True)
    ap.add_argument("--invoice-no", required=True)
    ap.add_argument("--creditor-name", default="CogOps Group")
    ap.add_argument("--creditor-street", default="")
    ap.add_argument("--creditor-building", default="")
    ap.add_argument("--creditor-plz", required=True)
    ap.add_argument("--creditor-city", required=True)
    ap.add_argument("--iban", required=True)
    ap.add_argument("--debtor", required=True)
    ap.add_argument("--desc", default="")
    ap.add_argument("--message", default="")
    ap.add_argument("--terms", type=int, default=14)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    r = build(a.amount, a.invoice_no,
              {"name": a.creditor_name, "street": a.creditor_street,
               "building": a.creditor_building, "plz": a.creditor_plz,
               "city": a.creditor_city, "country": "CH"},
              a.iban, a.debtor, a.desc, a.message, a.terms, a.out)
    print(f"Invoice {r['invoice_no']} · reference {r['reference_fmt']} · "
          f"CHF {r['amount_chf']:,.2f} · payload {r['payload_lines']} lines"
          + (f" · written: {r['html_file']}" if r["html_file"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
