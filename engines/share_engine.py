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
    """Build a concise project summary suitable for WhatsApp/Email."""
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
    client   = cfg.get("client_name", "")
    prepared = cfg.get("prepared_by", "Consultant")
    date_str = datetime.now().strftime("%d %B %Y")

    lines = [
        f"*{name}* — Project Summary",
        f"Date: {date_str}",
        f"Prepared by: {prepared}",
        "",
        f"📍 Location: {loc}, {state}",
        f"🏭 Capacity: {cap} TPD bio-bitumen plant",
        f"💰 Investment: ₹ {inv:.2f} Cr",
        "",
        f"📊 Financial Highlights:",
        f"  • Revenue / Year: ₹ {rev:.0f} Lac",
        f"  • Net Profit / Year: ₹ {np_:.0f} Lac",
        f"  • ROI: {roi:.1f}%",
        f"  • IRR: {irr:.1f}%",
        f"  • Break-even: {bev} months",
        "",
        f"🌱 Sustainable bio-bitumen from agricultural waste",
        f"🛣️ Meets IS 73:2013 VG grade standards",
        f"🏛️ Eligible for MNRE & state biomass subsidies",
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
    """Build an HTML snippet for embedding in reports."""
    name  = cfg.get("project_name", "Bio-Bitumen Plant")
    cap   = cfg.get("capacity_tpd", 20)
    inv   = cfg.get("investment_cr", 0)
    roi   = cfg.get("roi_pct", 0)
    irr   = cfg.get("irr_pct", 0)
    bev   = cfg.get("break_even_months", 0)
    state = cfg.get("state", "")
    loc   = cfg.get("location", "")

    return f"""
<div style="font-family:Arial;border:2px solid #E8B547;border-radius:10px;
  padding:20px;background:#15130F;color:#F0E6D3;max-width:500px;">
  <h2 style="color:#E8B547;margin:0 0 8px;">{name}</h2>
  <p style="color:#9A8A6A;margin:0 0 16px;">{cap} TPD Plant · {loc}, {state}</p>
  <table style="width:100%;border-collapse:collapse;">
    <tr><td style="padding:4px 8px;color:#9A8A6A;">Investment</td>
        <td style="padding:4px 8px;color:#E8B547;font-weight:700;">₹ {inv:.2f} Cr</td></tr>
    <tr><td style="padding:4px 8px;color:#9A8A6A;">ROI</td>
        <td style="padding:4px 8px;color:#51CF66;font-weight:700;">{roi:.1f}%</td></tr>
    <tr><td style="padding:4px 8px;color:#9A8A6A;">IRR</td>
        <td style="padding:4px 8px;color:#51CF66;font-weight:700;">{irr:.1f}%</td></tr>
    <tr><td style="padding:4px 8px;color:#9A8A6A;">Break-even</td>
        <td style="padding:4px 8px;color:#FFD43B;font-weight:700;">{bev} months</td></tr>
  </table>
  <p style="color:#7A6A4A;font-size:11px;margin:12px 0 0;">
    Generated {datetime.now().strftime('%d %b %Y %H:%M')} · Bio Bitumen Consultant Portal
  </p>
</div>"""


def save_share_log(method: str, cfg: dict):
    path = _HERE / "data" / "share_log.json"
    try:
        log = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    except Exception:
        log = []
    log.append({
        "method": method,
        "project": cfg.get("project_name", ""),
        "shared_at": datetime.now().isoformat(),
    })
    log = log[-50:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
