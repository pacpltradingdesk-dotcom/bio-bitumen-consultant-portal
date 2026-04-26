"""
90 · DPR PDF Auto-Generator
============================
One-click full Detailed Project Report PDF from all portal data.
9 sections: Cover · Executive Summary · Overview · Technical ·
Financials · Govt Schemes · Sustainability · Timeline · Risk · Conclusion
Dark gold theme.
"""
import sys
from pathlib import Path
from datetime import datetime

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import init_state, get_config
from config import COMPANY

st.set_page_config(page_title="DPR PDF Generator · Bio Bitumen", page_icon="📄", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

# ── CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#15130F;}
[data-testid="stSidebar"]{background:#1A1710;}
h1,h2,h3,h4,label,.stMarkdown p,.stMarkdown li{color:#F0E6D3;}
[data-testid="stMetricValue"]{color:#E8B547 !important;}
[data-testid="stMetricLabel"]{color:#B09060 !important;}
.stButton>button{background:#E8B547;color:#15130F;font-weight:700;
  border:none;border-radius:6px;padding:8px 22px;}
.stButton>button:hover{background:#F5C842;}
.section-card{background:#1E1B14;border-left:4px solid #E8B547;
  border-radius:0 8px 8px 0;padding:10px 16px;margin:4px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="color:#E8B547;margin-bottom:2px;">📄 DPR PDF Auto-Generator</h1>
<p style="color:#9A8A6A;margin-top:0;">
  One-click professional Detailed Project Report — 9 sections, IS standards, investor-ready
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Project info summary ──────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Project", cfg.get("project_name", "Bio-Bitumen Plant")[:18])
m2.metric("Capacity", f"{cfg.get('capacity_tpd',20)} TPD")
m3.metric("Investment", f"₹ {cfg.get('investment_cr',0):.2f} Cr")
m4.metric("IRR", f"{cfg.get('irr_pct',0):.1f}%")
m5.metric("Break-even", f"{cfg.get('break_even_months',0)} mo")
st.markdown("---")

# ── Options ───────────────────────────────────────────────────────────────
st.subheader("DPR Options")
oc1, oc2, oc3 = st.columns(3)
with oc1:
    inc_schemes  = st.checkbox("Include Govt Schemes", value=True, key="dpr_schemes")
    inc_carbon   = st.checkbox("Include Carbon Profile", value=True, key="dpr_carbon")
with oc2:
    inc_timeline = st.checkbox("Include Implementation Timeline", value=True, key="dpr_tl")
    inc_risk     = st.checkbox("Include Risk Analysis", value=True, key="dpr_risk")
with oc3:
    dpr_ver = st.text_input("DPR Version", value=cfg.get("dpr_version","1.0"), key="dpr_ver_in")
    prepared_by = st.text_input("Prepared By", value=cfg.get("prepared_by",""), key="dpr_prep")

st.markdown("---")

# ── DPR sections preview ─────────────────────────────────────────────────
st.subheader("Sections Included")
sections = [
    ("1", "Cover Page",             True),
    ("2", "Executive Summary",      True),
    ("3", "Project Overview & Site",True),
    ("4", "Technical Process",      True),
    ("5", "Financial Projections",  True),
    ("6", "Govt Schemes & Subsidies", inc_schemes),
    ("7", "Sustainability & Carbon", inc_carbon),
    ("8", "Implementation Timeline", inc_timeline),
    ("9", "Risk Analysis",          inc_risk),
    ("10","Conclusion",             True),
]
sc1, sc2 = st.columns(2)
for i, (num, name, included) in enumerate(sections):
    col = sc1 if i % 2 == 0 else sc2
    with col:
        icon = "✅" if included else "⬜"
        st.markdown(
            f'<div class="section-card">'
            f'<span style="color:#E8B547;font-weight:700;">{num}.</span> '
            f'{icon} {name}</div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── Generate button ───────────────────────────────────────────────────────
gen_col, dl_col = st.columns([1, 2])

with gen_col:
    generate = st.button("📄 Generate DPR PDF", type="primary", key="gen_dpr")

if generate:
    with st.spinner("Generating professional DPR PDF — 9 sections…"):
        try:
            from engines.dpr_pdf_engine import generate_dpr_pdf
            from engines.scheme_finder_engine import find_schemes
            from engines.carbon_engine import calculate_carbon

            # Update cfg with current form values
            cfg_copy = dict(cfg)
            cfg_copy["dpr_version"] = dpr_ver
            cfg_copy["prepared_by"] = prepared_by

            schemes = find_schemes(cfg_copy) if inc_schemes else None
            carbon  = calculate_carbon(cfg_copy) if inc_carbon else None

            pdf_bytes = generate_dpr_pdf(cfg_copy, schemes=schemes, carbon=carbon)
            st.session_state["dpr_pdf_bytes"] = pdf_bytes
            st.session_state["dpr_pdf_name"]  = (
                f"DPR_{cfg_copy.get('project_name','Plant').replace(' ','_')}"
                f"_{datetime.now():%Y%m%d}.pdf"
            )
            st.success(f"✅ DPR generated — {len(pdf_bytes)//1024} KB | "
                       f"{len(sections)} sections")
        except ImportError as e:
            st.error(f"Missing library: {e} — run: pip install fpdf2")
        except Exception as e:
            st.error(f"PDF generation error: {e}")

# Download button
if st.session_state.get("dpr_pdf_bytes"):
    with dl_col:
        st.download_button(
            "⬇ Download DPR PDF",
            st.session_state["dpr_pdf_bytes"],
            file_name=st.session_state.get("dpr_pdf_name", "DPR.pdf"),
            mime="application/pdf",
            type="primary",
            key="dl_dpr_pdf",
        )
        st.info("PDF is ready — click Download")

st.markdown("---")

# ── What's included guide ─────────────────────────────────────────────────
with st.expander("What's in the DPR PDF?"):
    st.markdown("""
| Section | Content |
|---------|---------|
| Cover | Project name, capacity, investment, client name, date |
| Executive Summary | All key financials in a table |
| Project Overview | Site details, address, land area, utilities |
| Technical Process | Pyrolysis parameters, product yields, feedstock mix |
| Financial Projections | Investment, revenue, profit, IRR, ROI, 5-year table |
| Govt Schemes | All applicable central + state subsidies |
| Sustainability | CO₂ savings, carbon credit revenue, trees equivalent |
| Implementation | Month-by-month 10-month plan |
| Risk Analysis | 7 risks with mitigation strategies |
| Conclusion | Recommendation + consultant sign-off |
""")

# ── AI assist ─────────────────────────────────────────────────────────────
try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("AI Assist — Improve Executive Summary"):
            if st.button("Generate AI Executive Summary", type="primary", key="ai_90"):
                p = (
                    f"Write a professional 3-paragraph executive summary for a DPR of a "
                    f"{cfg.get('capacity_tpd',20)} TPD bio-bitumen plant in {cfg.get('state','')}. "
                    f"Investment: ₹{cfg.get('investment_cr',0):.2f} Cr, IRR: {cfg.get('irr_pct',0):.1f}%, "
                    f"ROI: {cfg.get('roi_pct',0):.1f}%, Break-even: {cfg.get('break_even_months',0)} months. "
                    "Investor-ready language, mention MNRE subsidies and IS 73:2013 compliance."
                )
                with st.spinner("AI writing…"):
                    resp, prov = ask_ai(p, "Senior DPR consultant specialising in bio-energy.")
                if resp:
                    st.markdown(f"**via {prov.upper()}:**")
                    st.markdown(resp)
except Exception:
    pass

st.markdown("---")
st.caption(f"{COMPANY['name']} | DPR PDF Generator | {datetime.now().strftime('%d %B %Y')}")

try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "90")
except Exception:
    pass
