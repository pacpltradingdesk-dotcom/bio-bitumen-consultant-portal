"""
Report Share Engine
====================
Generate shareable links and formatted summaries for WhatsApp, Email, PDF.
No external API keys needed — uses wa.me and mailto: links.
"""
from __future__ import annotations
import urllib.parse
from datetime import datetime
from pathlib import Path
import json

_HERE = Path(__file__).parent.parent


def build_summary_text(cfg: dict) -> str:
    """Build a comprehensive project summary for WhatsApp/Email.
    Delegates to master_connector so all calculated fields are included."""
    try:
        from engines.master_connector import get_summary_for_share
        return get_summary_for_share(cfg)
    except Exception:
        pass

    # Fallback — direct reads (revenue_lac / net_profit_lac populated by recalculate())
    name     = cfg.get("project_name", "Bio-Bitumen Plant")
    cap      = cfg.get("capacity_tpd", 20)
    state    = cfg.get("state", "")
    loc      = cfg.get("location", "")
    inv      = cfg.get("investment_cr", 0)
    roi      = cfg.get("roi_pct", 0)
    irr      = cfg.get("irr_pct", 0)
    bev      = cfg.get("break_even_months", 0)
    rev      = cfg.get("revenue_lac", 0)
    np_      = cfg.get("net_profit_lac", 0)
    out_tpd  = cfg.get("output_tpd", 0)
    co2      = cfg.get("total_co2_saved_tpa", 0)
    client   = cfg.get("client_name", "")
    prepared = cfg.get("prepared_by", "Consultant")
    date_str = datetime.now().strftime("%d %B %Y")

    lines = [
        f"*{name}* — Project Summary",
        f"Date: {date_str}",
        f"Prepared by: {prepared}",
        "",
        f"📍 Location: {loc}, {state}",
        f"🏭 Capacity: {cap} TPD input  |  {out_tpd:.1f} TPD bio-oil output",
        f"💰 Investment: ₹ {inv:.2f} Cr",
        "",
        f"📊 Financial Highlights (Year 3 steady-state):",
        f"  • Revenue / Year  : ₹ {rev:.0f} Lac",
        f"  • Net Profit / Year: ₹ {np_:.0f} Lac",
        f"  • ROI: {roi:.1f}%  |  IRR: {irr:.1f}%",
        f"  • Break-even: {bev} months",
        f"  • Monthly EMI: ₹ {cfg.get('emi_lac_mth',0):.2f} Lac",
        "",
        f"🌱 CO₂ Saved: {co2:,.0f} tCO₂e/year" if co2 else "🌱 Sustainable from agro-waste biomass",
        f"🛣️ Meets IS 73:2013 VG grade standards",
        f"🏛️ Eligible for MNRE, CGTMSE & state subsidies",
    ]
    if client:
        lines.insert(3, f"Prepared for: {client}")
    return "\n".join(lines)


def whatsapp_link(cfg: dict, phone: str = "") -> str:
    """Generate wa.me link with pre-filled project summary."""
    text = build_summary_text(cfg)
    encoded = urllib.parse.quote(text)
    base = f"https://wa.me/{phone}" if phone else "https://wa.me/"
    return f"{base}?text={encoded}"


def email_link(cfg: dict, to_email: str = "", subject: str = "") -> str:
    """Generate mailto: link with project summary."""
    if not subject:
        subject = f"Bio-Bitumen Project Summary — {cfg.get('project_name', 'Plant')}"
    body = build_summary_text(cfg)
    params = urllib.parse.urlencode({"subject": subject, "body": body})
    return f"mailto:{to_email}?{params}"


def build_html_summary(cfg: dict) -> str:
    """Build a rich HTML card for email attachment / embedding in reports."""
    name  = cfg.get("project_name", "Bio-Bitumen Plant")
    cap   = cfg.get("capacity_tpd", 20)
    inv   = cfg.get("investment_cr", 0)
    roi   = cfg.get("roi_pct", 0)
    irr   = cfg.get("irr_pct", 0)
    bev   = cfg.get("break_even_months", 0)
    rev   = cfg.get("revenue_lac", 0)
    np_   = cfg.get("net_profit_lac", 0)
    emi   = cfg.get("emi_lac_mth", 0)
    state = cfg.get("state", "")
    loc   = cfg.get("location", "")
    co2   = cfg.get("total_co2_saved_tpa", 0)
    trees = cfg.get("trees_equivalent", 0)
    grade = cfg.get("viability_grade", "—")
    client = cfg.get("client_name", "")

    rows = [
        ("Investment",          f"₹ {inv:.2f} Cr",         "#E8B547"),
        ("Annual Revenue (Yr3)",f"₹ {rev:.0f} Lac",        "#74C0FC"),
        ("Net Profit (Yr3)",    f"₹ {np_:.0f} Lac",        "#51CF66"),
        ("ROI",                 f"{roi:.1f}%",              "#51CF66"),
        ("IRR",                 f"{irr:.1f}%",              "#51CF66"),
        ("Break-even",          f"{bev} months",            "#FFD43B"),
        ("Monthly EMI",         f"₹ {emi:.2f} Lac",        "#C8B88A"),
    ]
    table_rows_html = "".join(
        f'<tr><td style="padding:5px 10px;color:#9A8A6A;">{k}</td>'
        f'<td style="padding:5px 10px;color:{c};font-weight:700;">{v}</td></tr>'
        for k, v, c in rows
    )
    carbon_row = (
        f'<p style="color:#51CF66;font-size:12px;margin:8px 0;">'
        f'🌱 CO₂ Saved: {co2:,.0f} tCO₂e/yr  ·  🌳 {trees:,} trees equiv.</p>'
        if co2 else ""
    )
    client_line = f'<p style="color:#9A8A6A;font-size:11px;margin:4px 0;">Prepared for: {client}</p>' if client else ""

    return f"""<!DOCTYPE html>
<html><body style="font-family:Arial,sans-serif;background:#0F0D0A;padding:20px;">
<div style="border:2px solid #E8B547;border-radius:12px;padding:24px;
  background:#15130F;color:#F0E6D3;max-width:560px;margin:auto;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <h2 style="color:#E8B547;margin:0 0 4px;">{name}</h2>
      <p style="color:#9A8A6A;margin:0 0 4px;">{cap} TPD Plant · {loc}, {state}</p>
      {client_line}
    </div>
    <div style="background:#1B3A25;color:#51CF66;padding:6px 14px;
      border-radius:20px;font-weight:700;font-size:14px;">Grade {grade}</div>
  </div>
  <hr style="border-color:#3A3520;margin:12px 0;">
  <table style="width:100%;border-collapse:collapse;">{table_rows_html}</table>
  {carbon_row}
  <p style="color:#7A6A4A;font-size:10px;margin:14px 0 0;text-align:right;">
    Generated {datetime.now().strftime('%d %b %Y %H:%M')} · Bio Bitumen Consultant Portal
  </p>
</div>
</body></html>"""


def save_share_log(method: str, cfg: dict):
    path = _HERE / "data" / "share_log.json"
    try:
        log = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    except Exception:
        log = []
    log.append({
        "timestamp":    datetime.now().strftime("%d %b %Y %H:%M"),
        "method":       method,
        "project_name": cfg.get("project_name", ""),
        "capacity_tpd": cfg.get("capacity_tpd", 0),
        "state":        cfg.get("state", ""),
        "irr_pct":      cfg.get("irr_pct", 0),
    })
    log = log[-50:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
