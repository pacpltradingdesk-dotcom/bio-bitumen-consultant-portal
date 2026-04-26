"""
90 · DPR PDF Auto-Generator
============================
One-click full Detailed Project Report PDF.
Uses master_connector to pull financial + carbon + schemes + ratings
into one enriched dataset before generating the PDF.
"""
import sys
from pathlib import Path
from datetime import datetime

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import init_state, get_config
from config import COMPANY

st.set_page_config(page_title="DPR PDF · Bio Bitumen", page_icon="📄", layout="wide")
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
h1,h2,h3,h4,label,.stMarkdown p,.stMarkdown li{color:#F0E6D3;}
[data-testid="stMetricValue"]{color:#E8B547 !important;}
[data-testid="stMetricLabel"]{color:#B09060 !important;}
.stButton>button{background:#E8B547;color:#15130F;font-weight:700;
  border:none;border-radius:6px;padding:8px 22px;}
.stButton>button:hover{background:#F5C842;}
.section-card{background:#1E1B14;border-left:4px solid #E8B547;
  border-radius:0 8px 8px 0;padding:10px 16px;margin:4px 0;}
.data-ok{color:#51CF66;font-weight:700;}
.data-miss{color:#FF6B6B;font-weight:700;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="color:#E8B547;margin-bottom:2px;">📄 DPR PDF Auto-Generator</h1>
<p style="color:#9A8A6A;margin-top:0;">
  One-click investor-ready Detailed Project Report — all portal data in one PDF
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Live data preview via master_connector ────────────────────────────────
st.subheader("Live Data Connected to This DPR")

try:
    from engines.master_connector import get_full_project_data
    preview = get_full_project_data(cfg, run_engines=False)

    p1, p2, p3, p4, p5, p6 = st.columns(6)
    p1.metric("Capacity",    f"{cfg.get('capacity_tpd',20)} TPD")
    p2.metric("Investment",  f"₹ {cfg.get('investment_cr',0):.2f} Cr")
    p3.metric("Revenue (Yr3)", preview["fmt_revenue"])
    p4.metric("IRR",         preview["fmt_irr"])
    p5.metric("Break-even",  preview["break_even_str"])
    p6.metric("Grade",       preview.get("viability_grade","—"))

    with st.expander("Full Data Checklist — what's in your DPR", expanded=False):
        checks = [
            ("Project Name",       bool(cfg.get("project_name"))),
            ("Client Name",        bool(cfg.get("client_name"))),
            ("State / Location",   bool(cfg.get("state") and cfg.get("location"))),
            ("Investment (₹ Cr)",  cfg.get("investment_cr", 0) > 0),
            ("Revenue (Lac)",      cfg.get("revenue_lac", 0) > 0),
            ("Net Profit (Lac)",   cfg.get("net_profit_lac", 0) > 0),
            ("IRR %",              cfg.get("irr_pct", 0) > 0),
            ("5-Year P&L Table",   len(cfg.get("roi_timeline", [])) >= 5),
            ("Feedstock Mix",      sum(cfg.get(f"mix_{k}",0) for k in
                                   ["rice_straw_loose","rice_straw_baled",
                                    "wheat_straw","bagasse","lignin","other_agro_waste"]) > 0),
            ("Carbon Profile",     bool(preview.get("total_co2_saved_tpa",0))),
            ("Govt Schemes",       preview.get("schemes_count", 0) > 0),
            ("Viability Rating",   bool(preview.get("viability_grade","—") != "—")),
        ]
        c1, c2 = st.columns(2)
        for i, (label, ok) in enumerate(checks):
            col = c1 if i % 2 == 0 else c2
            icon = "✅" if ok else "⚠️"
            with col:
                st.markdown(f"{icon} **{label}**")

except Exception as e:
    st.warning(f"Preview unavailable: {e}")

st.markdown("---")

# ── Options ───────────────────────────────────────────────────────────────
st.subheader("DPR Options")
oc1, oc2, oc3 = st.columns(3)
with oc1:
    inc_schemes  = st.checkbox("Include Govt Schemes",          value=True, key="dpr_schemes")
    inc_carbon   = st.checkbox("Include Carbon Profile",        value=True, key="dpr_carbon")
with oc2:
    inc_timeline = st.checkbox("Include Implementation Timeline", value=True, key="dpr_tl")
    inc_risk     = st.checkbox("Include Risk Analysis",         value=True, key="dpr_risk")
with oc3:
    dpr_ver    = st.text_input("DPR Version",  value=cfg.get("dpr_version","1.0"), key="dpr_ver_in")
    prepared_by = st.text_input("Prepared By", value=cfg.get("prepared_by",""),   key="dpr_prep")

st.markdown("---")

# ── Sections preview ──────────────────────────────────────────────────────
st.subheader("Sections Included")
sections = [
    ("1",  "Cover Page",                True),
    ("2",  "Executive Summary",         True),
    ("3",  "Project Overview & Site",   True),
    ("4",  "Technical Process",         True),
    ("5",  "Financial Projections",     True),
    ("6",  "Govt Schemes & Subsidies",  inc_schemes),
    ("7",  "Sustainability & Carbon",   inc_carbon),
    ("8",  "Implementation Timeline",   inc_timeline),
    ("9",  "Risk Analysis",             inc_risk),
    ("10", "Conclusion",                True),
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

# ── Generate ──────────────────────────────────────────────────────────────
gen_col, dl_col = st.columns([1, 2])

with gen_col:
    generate = st.button("📄 Generate Full DPR PDF", type="primary", key="gen_dpr")

if generate:
    with st.spinner("Pulling all portal data and generating professional DPR PDF…"):
        try:
            from engines.dpr_pdf_engine import generate_dpr_pdf
            from engines.master_connector import get_full_project_data

            cfg_copy = dict(cfg)
            cfg_copy["dpr_version"] = dpr_ver
            cfg_copy["prepared_by"] = prepared_by

            # Get fully enriched data (runs carbon + scheme engines)
            full_data = get_full_project_data(cfg_copy, run_engines=True)

            schemes = full_data.get("schemes") if inc_schemes else None
            carbon  = full_data.get("carbon")  if inc_carbon  else None

            # Merge enriched flat fields back into cfg_copy for PDF
            for key in ("revenue_lac", "net_profit_lac", "gross_profit_lac",
                        "operating_cost_lac", "output_tpd", "biomass_price_per_mt",
                        "total_co2_saved_tpa", "trees_equivalent", "viability_grade"):
                cfg_copy[key] = full_data.get(key, cfg_copy.get(key, 0))

            pdf_bytes = generate_dpr_pdf(cfg_copy, schemes=schemes, carbon=carbon)
            st.session_state["dpr_pdf_bytes"] = pdf_bytes
            st.session_state["dpr_pdf_name"]  = (
                f"DPR_{cfg_copy.get('project_name','Plant').replace(' ','_')}"
                f"_{datetime.now():%Y%m%d}.pdf"
            )
            included_count = sum(1 for _, _, inc in sections if inc)
            st.success(
                f"✅ DPR generated — {len(pdf_bytes)//1024} KB  |  "
                f"{included_count} sections  |  "
                f"Carbon: {'✅' if carbon else '—'}  |  "
                f"Schemes: {len(schemes) if schemes else 0}"
            )
        except ImportError as e:
            st.error(f"Missing library: {e} — run: pip install fpdf2")
        except Exception as e:
            st.error(f"PDF generation error: {e}")

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
        st.info("PDF ready — click Download")

st.markdown("---")

# ── What's in the DPR ─────────────────────────────────────────────────────
with st.expander("What's in the DPR PDF?"):
    st.markdown("""
| Section | Content | Data Source |
|---------|---------|-------------|
| Cover | Project name, capacity, investment, client, date | Project Setup (page 10) |
| Executive Summary | All key financials in a table | Financial engine (auto) |
| Project Overview | Site details, address, land, utilities | Project Setup (page 10) |
| Technical Process | Pyrolysis params, yields, feedstock mix | Raw Material (page 24) |
| Financial Projections | Investment, revenue, profit, IRR, 7-year P&L | Financial (page 30) |
| Govt Schemes | All applicable central + state subsidies | Scheme Finder (page 92) |
| Sustainability | CO₂ savings, carbon credits, trees equivalent | Carbon Credits (page 93) |
| Implementation | 10-month month-by-month plan | Standard template |
| Risk Analysis | 7 risks with live mitigation using your data | Live from config |
| Conclusion | Recommendation + sign-off | Live IRR/ROI values |
""")

# ── AI executive summary ──────────────────────────────────────────────────
try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("AI Assist — Generate Executive Summary"):
            if st.button("Write AI Executive Summary", type="primary", key="ai_90"):
                p = (
                    f"Write a professional 3-paragraph executive summary for a DPR of a "
                    f"{cfg.get('capacity_tpd',20)} TPD bio-bitumen plant in {cfg.get('state','')}. "
                    f"Investment: ₹{cfg.get('investment_cr',0):.2f} Cr, "
                    f"Revenue (Yr3): ₹{cfg.get('revenue_lac',0):.0f} Lac, "
                    f"Net Profit: ₹{cfg.get('net_profit_lac',0):.0f} Lac, "
                    f"IRR: {cfg.get('irr_pct',0):.1f}%, ROI: {cfg.get('roi_pct',0):.1f}%, "
                    f"Break-even: {cfg.get('break_even_months',0)} months. "
                    "Investor-ready language, mention MNRE subsidies and IS 73:2013 compliance."
                )
                with st.spinner("AI writing…"):
                    resp, prov = ask_ai(p, "Senior DPR consultant specialising in bio-energy India.")
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
