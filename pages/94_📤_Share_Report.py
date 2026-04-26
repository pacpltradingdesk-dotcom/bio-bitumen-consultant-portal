"""
94 · Share Report
==================
WhatsApp / Email one-click report sharing.
Builds a formatted summary from all portal data and creates share links.
"""
import sys
from pathlib import Path
from datetime import datetime

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import init_state, get_config
from engines.share_engine import (
    build_summary_text, whatsapp_link, email_link,
    build_html_summary, save_share_log,
)
from config import COMPANY

st.set_page_config(page_title="Share Report · Bio Bitumen", page_icon="📤", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#15130F;}
[data-testid="stSidebar"]{background:#1A1710;}
h1,h2,h3,h4,label,.stMarkdown p{color:#F0E6D3;}
[data-testid="stMetricValue"]{color:#E8B547 !important;}
[data-testid="stMetricLabel"]{color:#B09060 !important;}
.stButton>button{background:#E8B547;color:#15130F;font-weight:700;
  border:none;border-radius:6px;padding:8px 22px;}
.stButton>button:hover{background:#F5C842;}
.share-card{background:#1E1B14;border:1px solid #3A3520;border-radius:10px;
  padding:20px;text-align:center;}
.wa-btn{background:#25D366 !important;color:#fff !important;}
.wa-btn:hover{background:#20b558 !important;}
.share-preview{background:#1E1B14;border:1px solid #3A3520;border-radius:8px;
  padding:14px;font-family:monospace;font-size:12px;color:#C8B88A;
  white-space:pre-wrap;max-height:300px;overflow-y:auto;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="color:#E8B547;margin-bottom:2px;">📤 Share Report</h1>
<p style="color:#9A8A6A;margin-top:0;">
  Send project summary via WhatsApp · Email · Copy to Clipboard
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Project snapshot ──────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Project", cfg.get("project_name", "Bio-Bitumen Plant")[:18])
m2.metric("Capacity", f"{cfg.get('capacity_tpd', 20)} TPD")
m3.metric("IRR", f"{cfg.get('irr_pct', 0):.1f}%")
m4.metric("Investment", f"₹ {cfg.get('investment_cr', 0):.2f} Cr")

st.markdown("---")

# ── Recipient details ─────────────────────────────────────────────────────
st.subheader("Recipient Details")
rc1, rc2, rc3 = st.columns(3)
with rc1:
    phone = st.text_input(
        "WhatsApp Number (with country code)",
        value=cfg.get("client_phone", ""),
        placeholder="919876543210",
        key="share_phone",
    )
with rc2:
    email_to = st.text_input(
        "Email Address",
        value=cfg.get("client_email", ""),
        placeholder="investor@example.com",
        key="share_email",
    )
with rc3:
    share_note = st.text_area(
        "Custom Note (optional)",
        value="",
        placeholder="Please find the Bio-Bitumen project summary…",
        height=90,
        key="share_note",
    )

st.markdown("---")

# ── Summary preview ───────────────────────────────────────────────────────
st.subheader("Report Preview")

summary_text = build_summary_text(cfg)
if share_note.strip():
    summary_text = share_note.strip() + "\n\n" + summary_text

with st.expander("Preview Message Text", expanded=True):
    st.markdown(f'<div class="share-preview">{summary_text}</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Share buttons ─────────────────────────────────────────────────────────
st.subheader("Share via")
sh1, sh2, sh3 = st.columns(3)

with sh1:
    st.markdown('<div class="share-card">', unsafe_allow_html=True)
    st.markdown("**📱 WhatsApp**")
    if phone.strip():
        wa_url = whatsapp_link(cfg, phone.strip())
        st.markdown(
            f'<a href="{wa_url}" target="_blank" style="display:block;'
            f'background:#25D366;color:#fff;text-align:center;padding:10px;'
            f'border-radius:8px;font-weight:700;text-decoration:none;margin-top:8px;">'
            f'📱 Open WhatsApp</a>',
            unsafe_allow_html=True,
        )
        if st.button("Log WhatsApp Share", key="log_wa"):
            save_share_log("whatsapp", cfg)
            st.success("Logged!")
    else:
        st.caption("Enter phone number above to enable")
    st.markdown('</div>', unsafe_allow_html=True)

with sh2:
    st.markdown('<div class="share-card">', unsafe_allow_html=True)
    st.markdown("**📧 Email**")
    if email_to.strip():
        em_url = email_link(cfg, email_to.strip())
        st.markdown(
            f'<a href="{em_url}" style="display:block;'
            f'background:#E8B547;color:#15130F;text-align:center;padding:10px;'
            f'border-radius:8px;font-weight:700;text-decoration:none;margin-top:8px;">'
            f'📧 Open Email Client</a>',
            unsafe_allow_html=True,
        )
        if st.button("Log Email Share", key="log_em"):
            save_share_log("email", cfg)
            st.success("Logged!")
    else:
        st.caption("Enter email address above to enable")
    st.markdown('</div>', unsafe_allow_html=True)

with sh3:
    st.markdown('<div class="share-card">', unsafe_allow_html=True)
    st.markdown("**📋 Copy Text**")
    st.text_area(
        "Copy from here",
        value=summary_text,
        height=120,
        key="copy_area",
        label_visibility="collapsed",
    )
    if st.button("Log Copy Share", key="log_cp"):
        save_share_log("copy", cfg)
        st.success("Logged!")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ── HTML card download ────────────────────────────────────────────────────
st.subheader("HTML Summary Card")
st.caption("Download a formatted HTML card to attach to emails or embed in documents")

hc1, hc2 = st.columns([1, 3])
with hc1:
    if st.button("Generate HTML Card", key="gen_html"):
        html_card = build_html_summary(cfg)
        st.session_state["html_summary"] = html_card
        st.success("HTML card ready!")

if st.session_state.get("html_summary"):
    with hc2:
        st.download_button(
            "⬇ Download HTML Summary",
            st.session_state["html_summary"],
            file_name=f"summary_{cfg.get('project_name','plant').replace(' ','_')}_{datetime.now():%Y%m%d}.html",
            mime="text/html",
            key="dl_html",
        )

    with st.expander("Preview HTML Card"):
        import streamlit.components.v1 as _stc
        _stc.html(st.session_state["html_summary"], height=400, scrolling=True)

st.markdown("---")

# ── Share log ─────────────────────────────────────────────────────────────
st.subheader("Share Log")
try:
    import json
    log_path = Path(__file__).parent.parent / "data" / "share_log.json"
    if log_path.exists():
        log_data = json.loads(log_path.read_text(encoding="utf-8"))
        if log_data:
            import pandas as pd
            df_log = pd.DataFrame(log_data[-20:])
            st.dataframe(df_log[["timestamp", "method", "project_name", "capacity_tpd"]].iloc[::-1],
                         use_container_width=True, hide_index=True)
        else:
            st.caption("No shares logged yet.")
    else:
        st.caption("No shares logged yet.")
except Exception:
    st.caption("Share log unavailable.")

st.markdown("---")
st.caption(f"{COMPANY['name']} | Share Report | {datetime.now().strftime('%d %B %Y')}")

try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "94")
except Exception:
    pass
