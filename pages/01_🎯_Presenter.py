"""
CONSULTANT PRESENTER — Slider-Based Interactive Presentation System
=====================================================================
14 Slides | Client Input → Auto-Update ALL | One-Click Document Generation
Used by consultant (Prince) in client meetings, bank discussions, investor pitches.

THIS REPLACES PPT — All data is LIVE, all documents are READY.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io, datetime
from state_manager import get_config, update_fields, init_state
from config import (COMPANY, STATES, STATE_SCORES, LOCATION_WEIGHTS, STATE_COSTS,
                    NHAI_TENDERS, COMPETITORS, PPS_SWOT, RISK_REGISTRY,
                    ENVIRONMENTAL_FACTORS, WHY_NOW, FOUR_STAGES, LICENSE_TYPES,
                    INDUSTRY_NETWORK, KEY_CREDENTIALS, TARGET_AUDIENCES)

st.set_page_config(page_title="Consultant Presenter", page_icon="🎯", layout="wide")
init_state()
cfg = get_config()

TOTAL_SLIDES = 15  # 0-14

# ══════════════════════════════════════════════════════════════════════
# SLIDE STATE + DISPLAY MODE + PRINT
# ══════════════════════════════════════════════════════════════════════
if "slide" not in st.session_state:
    st.session_state["slide"] = 0
if "display_mode" not in st.session_state:
    st.session_state["display_mode"] = False

slide = st.session_state["slide"]
display_mode = st.session_state["display_mode"]

# Sidebar controls
st.sidebar.markdown("### Presentation Controls")
if st.sidebar.toggle("Meeting Display Mode", value=display_mode, key="dm_toggle"):
    st.session_state["display_mode"] = True
    display_mode = True
else:
    st.session_state["display_mode"] = False
    display_mode = False

if display_mode:
    st.sidebar.success("Display Mode ON — Clean presentation view")
    # Hide sidebar content in display mode via CSS
    st.markdown("""<style>
    [data-testid="stSidebar"] {width: 0px !important; min-width: 0px !important;}
    [data-testid="stSidebarContent"] {display: none !important;}
    header {display: none !important;}
    </style>""", unsafe_allow_html=True)

# Print button (always available)
st.sidebar.markdown("---")
if st.sidebar.button("🖨️ Print Current Slide", key="print_btn"):
    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

# ── Slide Title Bar ──────────────────────────────────────────────────
SLIDE_TITLES = [
    "Client & Project Setup",
    "The Opportunity",
    "Market Analysis",
    "Raw Material & Biomass",
    "Location & Feasibility",
    "Technology & Process",
    "Process Flow & Plant Sections",
    "Plant Layout & Drawings",
    "Financial Model",
    "ROI & Profitability",
    "Compliance & Licenses",
    "Subsidy & Government Support",
    "Project Timeline",
    "Risk Analysis",
    "Final Proposal & Documents",
]

# Header with slide counter
client_name = cfg.get("client_name", "")
header_text = f"**{COMPANY['trade_name']}** | Presenting to: **{client_name}**" if client_name else f"**{COMPANY['trade_name']}** — Consultant Presenter"

st.markdown(f"""
<div style="background: #003366; padding: 10px 20px; border-radius: 10px; margin-bottom: 10px;
            display: flex; justify-content: space-between; align-items: center; color: white;">
    <span style="font-size: 1.1em;">{header_text}</span>
    <span style="background: white; color: #003366; padding: 4px 15px; border-radius: 15px; font-weight: bold;">
        Slide {slide + 1} / {TOTAL_SLIDES}
    </span>
</div>
""", unsafe_allow_html=True)

# Slide progress dots
dot_html = ""
for i in range(TOTAL_SLIDES):
    color = "#003366" if i == slide else ("#006699" if i < slide else "#cccccc")
    dot_html += f'<span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:{color}; margin:0 3px;"></span>'
st.markdown(f'<div style="text-align:center; margin-bottom:10px;">{dot_html}</div>', unsafe_allow_html=True)

st.markdown(f"## {SLIDE_TITLES[slide]}")
st.markdown("---")


# ══════════════════════════════════════════════════════════════════════
# SLIDE 0: CLIENT & PROJECT INPUT
# ══════════════════════════════════════════════════════════════════════
if slide == 0:
    st.markdown("### Enter client details — ALL slides will auto-update")

    c1, c2 = st.columns(2)
    with c1:
        inp_name = st.text_input("Client Name *", value=cfg.get("client_name", ""), key="p_name")
        inp_company = st.text_input("Company", value=cfg.get("client_company", ""), key="p_company")
        inp_state = st.selectbox("State *", STATES, index=STATES.index(cfg["state"]) if cfg["state"] in STATES else 0, key="p_state")
        inp_city = st.text_input("City", value=cfg.get("location", ""), key="p_city")
        inp_address = st.text_area("Site Address", value=cfg.get("site_address", ""), height=80, key="p_addr")
    with c2:
        inp_cap = st.selectbox("Plant Capacity (TPD) *", [5, 10, 15, 20, 30, 40, 50],
                                index=[5,10,15,20,30,40,50].index(int(cfg["capacity_tpd"])) if int(cfg["capacity_tpd"]) in [5,10,15,20,30,40,50] else 3, key="p_cap")
        inp_budget = st.number_input("Budget (Rs Crore)", 0.5, 50.0, float(cfg.get("investment_cr", 8)), 0.5, key="p_budget")
        inp_biomass = st.selectbox("Primary Biomass", ["Rice Straw", "Wheat Straw", "Sugarcane Bagasse",
                                    "Cotton Stalk", "Groundnut Shell", "Mixed"], key="p_biomass")
        inp_phone = st.text_input("Phone", value=cfg.get("client_phone", ""), key="p_phone")
        inp_project = st.text_input("Project Name", value=cfg.get("project_name", ""),
                                     placeholder=f"Bio-Bitumen Plant — {inp_city}", key="p_project")

    if st.button("SAVE & START PRESENTATION", type="primary", key="save_client"):
        update_fields({
            "client_name": inp_name, "client_company": inp_company,
            "state": inp_state, "location": inp_city, "site_address": inp_address,
            "capacity_tpd": float(inp_cap), "client_phone": inp_phone,
            "project_name": inp_project or f"Bio-Bitumen Plant — {inp_city}",
            "biomass_source": inp_biomass,
        })
        st.session_state["slide"] = 1
        st.rerun()

# ══════════════════════════════════════════════════════════════════════
# SLIDE 1: THE OPPORTUNITY
# ══════════════════════════════════════════════════════════════════════
elif slide == 1:
    st.markdown(f"### Why Bio-Bitumen NOW — The Rs 25,000 Crore Opportunity")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("India Bitumen Market", "Rs 25,000+ Cr/yr")
    m2.metric("Import Dependency", f"{ENVIRONMENTAL_FACTORS['india_import_dependency_pct']}%")
    m3.metric("Plants Needed", "130-216 in 5-7 yrs")
    m4.metric("NHAI Green Mandate", "15% bio-bitumen by 2030")

    for i, point in enumerate(WHY_NOW, 1):
        st.markdown(f"**{i}.** {point}")

    st.markdown("---")
    st.markdown(f"""
    ### Why {COMPANY['trade_name']}?
    - **{COMPANY['years_experience']} years** bitumen industry experience
    - **{COMPANY['plants_built']} plants** built across India
    - **{COMPANY['industry_contacts']:,} contacts** — contractors, traders, importers
    - **International VG-30 supply** — 2.4 Lakh MT/yr (Getka USA-Iraq contract)
    """)

# ══════════════════════════════════════════════════════════════════════
# SLIDE 2: MARKET ANALYSIS
# ══════════════════════════════════════════════════════════════════════
elif slide == 2:
    try:
        from engines.market_data_api import get_market_summary
        market = get_market_summary()
        vg30 = market.get("vg30_estimate", {})
        fx = market.get("usd_inr", {})
        crude = market.get("crude_oil")
        crude_price = crude.get("latest_price", 0) if isinstance(crude, dict) else 0

        mk1, mk2, mk3, mk4 = st.columns(4)
        mk1.metric("Crude Oil", f"${crude_price:.1f}/bbl")
        mk2.metric("USD/INR", f"Rs {fx.get('rate', 84):.2f}")
        mk3.metric("VG30 Price", f"Rs {vg30.get('vg30_estimated', 38000):,.0f}/MT")
        mk4.metric("Gold", f"${market.get('gold', {}).get('price_usd', 0):,.0f}")
    except Exception:
        st.info("Market data loading...")

    # NHAI Tenders
    open_tenders = [t for t in NHAI_TENDERS if t["status"] == "Open"]
    st.metric("Open NHAI/PWD Tenders", f"{len(open_tenders)} projects worth Rs {sum(t['budget_cr'] for t in open_tenders):,} Cr")

    tender_df = pd.DataFrame(open_tenders[:8])[["project", "state", "budget_cr", "bitumen_mt", "deadline"]]
    tender_df.columns = ["Project", "State", "Budget (Cr)", "Bitumen (MT)", "Deadline"]
    st.dataframe(tender_df, width="stretch", hide_index=True)

    st.page_link("pages/04_📈_Market.py", label="See Full Market Intelligence", icon="📈")

# ══════════════════════════════════════════════════════════════════════
# SLIDE 3: RAW MATERIAL
# ══════════════════════════════════════════════════════════════════════
elif slide == 3:
    st.markdown(f"### Biomass Sourcing for {cfg.get('location', 'Your')} Plant")

    try:
        from engines.agro_engine import calculate_procurement_cost, calculate_plant_requirement, get_quality_specs
        state_short = cfg.get("state", "Gujarat")[:2] if len(cfg.get("state", "")) > 2 else cfg.get("state", "default")

        req = calculate_plant_requirement(cfg["capacity_tpd"], cfg.get("biomass_source", "Rice Straw"))
        cost = calculate_procurement_cost(cfg.get("biomass_source", "Rice Straw"), state_short)

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Daily Biomass Need", f"{req.get('daily_biomass_mt', 50):.0f} MT")
        r2.metric("Annual Need", f"{req.get('annual_biomass_mt', 15000):,.0f} MT")
        r3.metric("Delivered Cost", f"Rs {cost.get('total_delivered_rs_mt', 3000):,.0f}/MT")
        r4.metric("90-Day Buffer", f"{req.get('buffer_90_days_mt', 4500):,.0f} MT")

        st.markdown(f"**Primary Source:** {cfg.get('biomass_source', 'Rice Straw')} — available from farmers within 50-100 km radius")
        st.markdown(f"**Output:** Bio-Oil {req.get('bio_oil_output_mt_day', 8):.1f} MT/day + Biochar {req.get('biochar_output_mt_day', 6):.1f} MT/day")
    except Exception:
        st.markdown("- Rice Straw, Sugarcane Bagasse, Cotton Stalk, Groundnut Shell")
        st.markdown(f"- Daily requirement: ~{cfg['capacity_tpd']*2.5:.0f} MT for {cfg['capacity_tpd']:.0f} TPD plant")

    st.page_link("pages/06_🌾_Raw_Material.py", label="See Full Raw Material Analysis", icon="🌾")

# ══════════════════════════════════════════════════════════════════════
# SLIDE 4: LOCATION & FEASIBILITY
# ══════════════════════════════════════════════════════════════════════
elif slide == 4:
    st.markdown(f"### Site: {cfg.get('location', 'TBD')}, {cfg.get('state', 'TBD')}")

    if cfg.get("site_address"):
        st.info(f"**Site Address:** {cfg['site_address']}")

    # State scores
    scores = STATE_SCORES.get(cfg.get("state", "Gujarat"), {})
    total = sum(scores.get(k, 50) * LOCATION_WEIGHTS[k] for k in LOCATION_WEIGHTS)

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Overall Score", f"{total:.0f}/100")
    s2.metric("Biomass", f"{scores.get('biomass', 50)}/100")
    s3.metric("Subsidy", f"{scores.get('subsidy', 50)}/100")
    s4.metric("Logistics", f"{scores.get('logistics', 50)}/100")
    s5.metric("Power", f"{scores.get('power', 50)}/100")

    # State cost details
    sc = STATE_COSTS.get(cfg.get("state", "Gujarat"), {})
    st.markdown(f"""
    | Factor | Value |
    |--------|-------|
    | Power Rate | Rs {sc.get('power_rate', 7)}/kWh |
    | Labor Cost | Rs {sc.get('labor_daily', 450)}/day |
    | Land Cost | Rs {sc.get('land_lac_acre', 15)} Lac/acre |
    | Subsidy | {sc.get('subsidy_pct', 15)}% |
    | Bitumen Demand | {sc.get('bitumen_demand_mt', 200000):,} MT/yr |
    """)

    st.page_link("pages/05_📍_Location.py", label="See Full Location Analysis", icon="📍")

# ══════════════════════════════════════════════════════════════════════
# SLIDE 5: TECHNOLOGY
# ══════════════════════════════════════════════════════════════════════
elif slide == 5:
    st.markdown("### CSIR-CRRI Licensed Technology — Proven & Certified")

    for stage in FOUR_STAGES:
        with st.expander(f"Stage {stage['stage']}: {stage['name']}", expanded=(stage['stage'] <= 2)):
            st.markdown(f"{stage['description']}")
            st.markdown(f"**CAPEX:** {stage['capex']} | **Manpower:** {stage['manpower']}")

    st.markdown("""
    **Key Facts:**
    - Technology by CSIR-CRRI / CSIR-IIP (Government of India)
    - KrishiBind bio-binder — 22% less rutting, 18% better fatigue life
    - Meets all IS:73 and MoRTH 2026 specifications
    - India became FIRST country to commercially produce bio-bitumen (Jan 2026)
    """)

    st.page_link("pages/51_Technology.py", label="See Technology Details", icon="🔬")

# ══════════════════════════════════════════════════════════════════════
# SLIDE 6: PROCESS FLOW
# ══════════════════════════════════════════════════════════════════════
elif slide == 6:
    st.markdown(f"### 13-Step Manufacturing Process — {cfg['capacity_tpd']:.0f} TPD")

    steps = [
        ("1. Biomass Receiving", "Truck unloading, weighbridge, quality check"),
        ("2. Size Reduction", "Shredder + Hammer Mill → 10-30mm"),
        ("3. Drying", "Rotary dryer → Moisture <15%"),
        ("4. Pelletization", "Uniform pellets for consistent feed"),
        ("5. Pyrolysis", "450-550°C in oxygen-free reactor → Bio-Oil 40% + Biochar 30% + Syngas 25%"),
        ("6. Bio-Oil Condensation", "Condenser HE-101 → Liquid bio-oil collection"),
        ("7. Bio-Oil Storage", "Intermediate storage tank"),
        ("8. VG-30 Heating", "Heat conventional bitumen to 160-180°C"),
        ("9. Blending", "High shear mixer — 15-30% bio-oil + 70-85% VG-30"),
        ("10. Quality Testing", "Penetration, softening point, viscosity (IS:73)"),
        ("11. Storage", "Heated bio-bitumen storage tanks"),
        ("12. Packaging", "Steel drums (181 kg) or bulk tanker"),
        ("13. Dispatch", "To NHAI/PWD contractors"),
    ]

    for step, desc in steps:
        st.markdown(f"**{step}** — {desc}")

    st.page_link("pages/53_Process_Flow.py", label="See Detailed Process Flow", icon="🔄")

# ══════════════════════════════════════════════════════════════════════
# SLIDE 7: PLANT LAYOUT
# ══════════════════════════════════════════════════════════════════════
elif slide == 7:
    st.markdown(f"### Plant Layout — {cfg['capacity_tpd']:.0f} TPD")

    # Show drawing if available
    from pathlib import Path
    draw_dir = Path(__file__).parent.parent / "data" / "all_drawings"
    cap_str = f"{int(cfg['capacity_tpd'])}TPD"
    layout_files = list(draw_dir.glob(f"*Layout*{cap_str}*")) if draw_dir.exists() else []

    if layout_files:
        st.image(str(layout_files[0]), caption=f"Plant Layout — {cap_str}", use_container_width=True)
    else:
        st.info(f"Drawing available for {cap_str} — see Drawings page")

    # Area breakdown
    sections = ["Raw Material Area (15%)", "Processing Area (20%)", "Reactor Section (15%)",
                "Blending Section (15%)", "Storage Area (10%)", "Pollution Control (5%)",
                "Dispatch Area (5%)", "Utility Area (5%)", "Admin & Lab (10%)"]
    for s in sections:
        st.markdown(f"- {s}")

    st.page_link("pages/08_📐_Drawings.py", label="See All Engineering Drawings", icon="📐")

# ══════════════════════════════════════════════════════════════════════
# SLIDE 8: FINANCIAL MODEL
# ══════════════════════════════════════════════════════════════════════
elif slide == 8:
    st.markdown(f"### Financial Model — {cfg['capacity_tpd']:.0f} TPD | Rs {cfg['investment_cr']:.2f} Crore")

    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("Investment", f"Rs {cfg['investment_cr']:.2f} Cr")
    f2.metric("Loan (60%)", f"Rs {cfg.get('loan_cr', cfg['investment_cr']*0.6):.2f} Cr")
    f3.metric("Equity (40%)", f"Rs {cfg.get('equity_cr', cfg['investment_cr']*0.4):.2f} Cr")
    f4.metric("EMI/Month", f"Rs {cfg.get('emi_lac_mth', 0):.2f} Lac")
    f5.metric("Rev Yr5", f"Rs {cfg.get('revenue_yr5_lac', 0):.0f} Lac")

    # 7-year chart
    if cfg.get("roi_timeline"):
        roi_df = pd.DataFrame(cfg["roi_timeline"])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=roi_df["Year"], y=roi_df["Revenue (Lac)"], name="Revenue", marker_color="#003366"))
        fig.add_trace(go.Bar(x=roi_df["Year"], y=roi_df["Variable Cost (Lac)"], name="Cost", marker_color="#CC3333"))
        fig.add_trace(go.Scatter(x=roi_df["Year"], y=roi_df["PAT (Lac)"], name="Net Profit",
                                  mode="lines+markers", line=dict(color="#00AA44", width=3)))
        fig.update_layout(title="7-Year Revenue vs Cost vs Profit (Rs Lakhs)",
                           barmode="group", template="plotly_white", height=400)
        st.plotly_chart(fig, width="stretch")

    st.page_link("pages/09_💰_Financial.py", label="Open Full Financial Model (Editable)", icon="💰")

# ══════════════════════════════════════════════════════════════════════
# SLIDE 9: ROI & PROFITABILITY
# ══════════════════════════════════════════════════════════════════════
elif slide == 9:
    st.markdown(f"### Return on Investment — {cfg['capacity_tpd']:.0f} TPD")

    g1, g2, g3 = st.columns(3)
    with g1:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=cfg.get("roi_pct", 0),
            title={"text": "ROI %"}, gauge={"axis": {"range": [0, 60]}, "bar": {"color": "#003366"},
            "steps": [{"range": [0,15], "color": "#ffcccc"}, {"range": [15,30], "color": "#ffffcc"},
                       {"range": [30,60], "color": "#ccffcc"}]}))
        fig.update_layout(height=250, margin=dict(t=60, b=10))
        st.plotly_chart(fig, width="stretch")
    with g2:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=cfg.get("irr_pct", 0),
            title={"text": "IRR %"}, gauge={"axis": {"range": [0, 80]}, "bar": {"color": "#006699"}}))
        fig.update_layout(height=250, margin=dict(t=60, b=10))
        st.plotly_chart(fig, width="stretch")
    with g3:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=cfg.get("break_even_months", 0),
            title={"text": "Break-Even (Months)"}, gauge={"axis": {"range": [0, 60]}, "bar": {"color": "#FF8800"},
            "steps": [{"range": [0,24], "color": "#ccffcc"}, {"range": [24,42], "color": "#ffffcc"},
                       {"range": [42,60], "color": "#ffcccc"}]}))
        fig.update_layout(height=250, margin=dict(t=60, b=10))
        st.plotly_chart(fig, width="stretch")

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Monthly Profit", f"Rs {cfg.get('monthly_profit_lac', 0):.1f} Lac")
    p2.metric("Profit/MT", f"Rs {cfg.get('profit_per_mt', 0):,.0f}")
    p3.metric("DSCR Yr3", f"{cfg.get('dscr_yr3', 0):.2f}x")
    p4.metric("Annual Revenue Yr5", f"Rs {cfg.get('revenue_yr5_lac', 0):.0f} Lac")

    st.page_link("pages/60_ROI_Quick_Calc.py", label="Interactive ROI Calculator", icon="🎯")

# ══════════════════════════════════════════════════════════════════════
# SLIDE 10: COMPLIANCE & LICENSES
# ══════════════════════════════════════════════════════════════════════
elif slide == 10:
    mandatory = [lt for lt in LICENSE_TYPES if lt.get("mandatory")]
    optional = [lt for lt in LICENSE_TYPES if not lt.get("mandatory")]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Licenses", len(LICENSE_TYPES))
    c2.metric("Mandatory", len(mandatory))
    c3.metric("Optional", len(optional))

    st.markdown("### Key Mandatory Licenses")
    for lt in mandatory[:12]:
        st.markdown(f"- **{lt['name']}** — {lt['authority']} (~{lt['typical_days']} days)")

    st.markdown(f"\n*...and {len(mandatory)-12} more. We handle ALL compliance for you.*")
    st.page_link("pages/11_📋_Compliance.py", label="Full Compliance Tracker", icon="📋")

# ══════════════════════════════════════════════════════════════════════
# SLIDE 11: SUBSIDY & GOVERNMENT SUPPORT
# ══════════════════════════════════════════════════════════════════════
elif slide == 11:
    st.markdown("### Government Schemes & Subsidies Available")

    schemes = [
        ("MNRE Waste-to-Wealth Mission", "25% capital subsidy", "Bio-bitumen from agro-waste eligible"),
        (f"State MSME Subsidy ({cfg.get('state', 'Gujarat')})", f"{STATE_COSTS.get(cfg.get('state', 'Gujarat'), {}).get('subsidy_pct', 15)}%", "State industrial policy"),
        ("CGTMSE Guarantee", "Collateral-free up to Rs 5 Cr", "For MSME manufacturing units"),
        ("Technology Development Board", "Up to 50% for new tech", "Bio-bitumen qualifies as new technology"),
        ("Carbon Credits", f"Rs {cfg['capacity_tpd']*300*0.35*12*84/100000:.1f} Lac/yr", "Voluntary carbon market"),
        ("PM MUDRA Yojana", "Up to Rs 10 Lakh", "For micro manufacturing units"),
    ]

    for name, benefit, detail in schemes:
        st.markdown(f"**{name}** — {benefit}")
        st.caption(f"  {detail}")

    subsidy_pct = STATE_COSTS.get(cfg.get("state", "Gujarat"), {}).get("subsidy_pct", 15)
    subsidy_amt = cfg["investment_cr"] * subsidy_pct / 100
    st.success(f"**Potential subsidy for your project: Rs {subsidy_amt:.2f} Cr ({subsidy_pct}%) → Effective investment: Rs {cfg['investment_cr'] - subsidy_amt:.2f} Cr**")

# ══════════════════════════════════════════════════════════════════════
# SLIDE 12: PROJECT TIMELINE
# ══════════════════════════════════════════════════════════════════════
elif slide == 12:
    st.markdown("### 10-Phase Implementation — 12 to 18 Months")

    phases = [
        ("Pre-Feasibility & DPR", 1, "Month 1"),
        ("Company Setup (ROC/GST)", 1, "Month 1-2"),
        ("Land & Approvals", 3, "Month 2-4"),
        ("Environmental Clearances", 5, "Month 3-7"),
        ("Bank Loan Sanction", 3, "Month 3-5"),
        ("Engineering & Design", 3, "Month 4-6"),
        ("Equipment Procurement", 4, "Month 5-8"),
        ("Civil Construction", 5, "Month 6-10"),
        ("Installation & Commissioning", 3, "Month 10-12"),
        ("Commercial Production", 6, "Month 13-18"),
    ]

    gantt_data = []
    start = datetime.date(2026, 6, 1)
    offset = 0
    for name, duration, period in phases:
        gantt_data.append({"Task": name, "Start": start + datetime.timedelta(days=offset*30),
                            "Finish": start + datetime.timedelta(days=(offset+duration)*30), "Duration": f"{duration} months"})
        offset += max(1, duration - 1)

    gantt_df = pd.DataFrame(gantt_data)
    fig = px.timeline(gantt_df, x_start="Start", x_end="Finish", y="Task",
                       title="Project Gantt Chart", color_discrete_sequence=["#003366"])
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(template="plotly_white", height=450)
    st.plotly_chart(fig, width="stretch")

    st.page_link("pages/64_Project_Gantt.py", label="Customer-Specific Timeline", icon="📅")

# ══════════════════════════════════════════════════════════════════════
# SLIDE 13: RISK ANALYSIS
# ══════════════════════════════════════════════════════════════════════
elif slide == 13:
    risk_df = pd.DataFrame(RISK_REGISTRY)
    risk_df["score"] = risk_df["probability"] * risk_df["impact"]
    top_risks = risk_df.nlargest(8, "score")

    r1, r2, r3 = st.columns(3)
    r1.metric("Total Risks Identified", len(RISK_REGISTRY))
    high = len(risk_df[risk_df["score"] >= 12])
    r2.metric("High/Critical", high)
    r3.metric("Overall Rating", "Manageable" if high <= 3 else "Needs Attention")

    for _, r in top_risks.iterrows():
        sev = "🔴" if r["score"] >= 15 else ("🟠" if r["score"] >= 10 else "🟡")
        with st.expander(f"{sev} {r['category']}: {r['risk'][:60]} (Score: {r['score']}/25)"):
            st.markdown(f"**Mitigation:** {r['mitigation']}")

    st.page_link("pages/66_Risk_Matrix.py", label="Full Risk Matrix", icon="⚠️")

# ══════════════════════════════════════════════════════════════════════
# SLIDE 14: FINAL PROPOSAL & DOCUMENTS
# ══════════════════════════════════════════════════════════════════════
elif slide == 14:
    st.markdown(f"### Final Proposal for {cfg.get('client_name', 'Client')}")

    # Summary card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #003366, #006699); padding: 25px; border-radius: 15px; color: white;">
        <h2 style="color: white; margin: 0;">{cfg.get('project_name', 'Bio-Bitumen Plant')}</h2>
        <p style="color: #99ccff; margin: 5px 0;">For: {cfg.get('client_name', 'Client')} | {cfg.get('client_company', '')}</p>
        <hr style="border-color: #99ccff33;">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 10px;">
            <div><span style="font-size: 1.8em; font-weight: bold;">{cfg['capacity_tpd']:.0f}</span><br>MT/Day</div>
            <div><span style="font-size: 1.8em; font-weight: bold;">Rs {cfg['investment_cr']:.1f}Cr</span><br>Investment</div>
            <div><span style="font-size: 1.8em; font-weight: bold;">{cfg.get('roi_pct', 0):.0f}%</span><br>ROI</div>
            <div><span style="font-size: 1.8em; font-weight: bold;">{cfg.get('break_even_months', 0)}</span><br>Month Break-Even</div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 10px;">
            <div><span style="font-size: 1.4em;">{cfg.get('location', '')}, {cfg.get('state', '')}</span><br>Location</div>
            <div><span style="font-size: 1.4em;">Rs {cfg.get('monthly_profit_lac', 0):.1f}L</span><br>Monthly Profit</div>
            <div><span style="font-size: 1.4em;">{cfg.get('dscr_yr3', 0):.2f}x</span><br>DSCR Yr3</div>
            <div><span style="font-size: 1.4em;">{cfg.get('irr_pct', 0):.0f}%</span><br>IRR</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Document Generation Buttons
    st.subheader("Generate Submission-Ready Documents")

    d1, d2, d3 = st.columns(3)
    d1.page_link("pages/13_📁_Document_Hub.py", label="Generate ALL Documents (ZIP)", icon="📁")
    d2.page_link("pages/44_DPR_Generator.py", label="Generate DPR", icon="📄")
    d3.page_link("pages/61_Loan_EMI.py", label="Loan EMI Calculator", icon="🏦")

    d4, d5, d6 = st.columns(3)
    d4.page_link("pages/67_Export_Center.py", label="Export All Data", icon="📤")
    d5.page_link("pages/03_📝_Project_Setup.py", label="Edit Project Details", icon="📝")
    d6.page_link("pages/15_🤖_AI_Advisor.py", label="Ask AI Advisor", icon="🤖")

    st.markdown("---")
    st.markdown(f"""
    ### Next Steps
    1. Review and finalize project parameters
    2. Generate DPR for bank submission
    3. Apply for government subsidies (MNRE, State MSME)
    4. Identify and finalize site
    5. Start equipment procurement

    **{COMPANY['trade_name']} will support you at EVERY step — from site selection to first production.**
    """)

    st.markdown(f"**Contact:** {COMPANY['owner']} | {COMPANY['phone']} | {COMPANY['email']}")


# ══════════════════════════════════════════════════════════════════════
# NAVIGATION BAR (Bottom of every slide)
# ══════════════════════════════════════════════════════════════════════
st.markdown("---")

nav1, nav2, nav3, nav4, nav5 = st.columns([1, 1, 4, 1, 1])

with nav1:
    if slide > 0:
        if st.button("◀ Previous", key="prev", use_container_width=True):
            st.session_state["slide"] = slide - 1
            st.rerun()

with nav2:
    if slide > 0:
        if st.button("⏮ Start", key="first", use_container_width=True):
            st.session_state["slide"] = 0
            st.rerun()

with nav3:
    # Slide selector
    jump = st.selectbox("Jump to slide", range(TOTAL_SLIDES),
                          index=slide, format_func=lambda x: f"{x+1}. {SLIDE_TITLES[x]}",
                          key="jump_slide", label_visibility="collapsed")
    if jump != slide:
        st.session_state["slide"] = jump
        st.rerun()

with nav4:
    if slide < TOTAL_SLIDES - 1:
        if st.button("⏭ End", key="last", use_container_width=True):
            st.session_state["slide"] = TOTAL_SLIDES - 1
            st.rerun()

with nav5:
    if slide < TOTAL_SLIDES - 1:
        if st.button("Next ▶", key="next", type="primary", use_container_width=True):
            st.session_state["slide"] = slide + 1
            st.rerun()

# Action buttons
st.markdown("---")
act1, act2, act3, act4 = st.columns(4)
act1.page_link("pages/13_📁_Document_Hub.py", label="Generate Documents", icon="📄")
act2.page_link("pages/09_💰_Financial.py", label="Edit Financials", icon="💰")
act3.page_link("pages/15_🤖_AI_Advisor.py", label="AI Advisor", icon="🤖")
act4.page_link("pages/03_📝_Project_Setup.py", label="Edit Project Info", icon="📝")

# ══════════════════════════════════════════════════════════════════════
# AI MEETING COPILOT (Sidebar — Available on EVERY slide)
# ══════════════════════════════════════════════════════════════════════
try:
    from engines.ai_engine import is_ai_available
    if is_ai_available():
        from engines.meeting_copilot import (live_qa, handle_objection, COMMON_OBJECTIONS,
            generate_cma_narrative, compare_competitor, generate_meeting_minutes,
            analyze_govt_schemes, generate_investment_thesis, narrate_scenario)

        st.sidebar.markdown("---")
        st.sidebar.markdown("### AI Meeting Copilot")

        audience = st.sidebar.selectbox("Presenting to:",
            ["Investor", "Bank Officer", "Govt Officer", "Farmer", "Competitor Client"],
            key="audience_type")

        copilot_mode = st.sidebar.radio("Mode:",
            ["Live Q&A", "Handle Objection", "CMA for Bank", "Compare Competitor",
             "Govt Schemes", "Investment Thesis", "Meeting Notes"],
            key="copilot_mode")

        if copilot_mode == "Live Q&A":
            qa_input = st.sidebar.text_input("Client's question:", key="qa_input",
                                              placeholder="Type what the client asked...")
            if qa_input and st.sidebar.button("Answer Now", key="qa_go", type="primary"):
                with st.sidebar:
                    with st.spinner("AI thinking..."):
                        answer, prov = live_qa(qa_input, audience, cfg)
                    st.markdown(answer)
                    st.caption(f"Powered by {prov}")

        elif copilot_mode == "Handle Objection":
            obj_list = COMMON_OBJECTIONS.get(audience.split()[0], COMMON_OBJECTIONS["Investor"])
            obj_select = st.sidebar.selectbox("Common objections:", ["Custom..."] + obj_list, key="obj_sel")
            if obj_select == "Custom...":
                obj_text = st.sidebar.text_input("Type objection:", key="obj_custom")
            else:
                obj_text = obj_select
            if obj_text and st.sidebar.button("Destroy Objection", key="obj_go", type="primary"):
                with st.sidebar:
                    with st.spinner("Building response..."):
                        response, prov = handle_objection(obj_text, audience, cfg)
                    st.markdown(response)

        elif copilot_mode == "CMA for Bank":
            if st.sidebar.button("Generate CMA Narrative", key="cma_go", type="primary"):
                with st.sidebar:
                    with st.spinner("Generating bank-ready CMA..."):
                        cma, prov = generate_cma_narrative(cfg)
                    st.markdown(cma)

        elif copilot_mode == "Compare Competitor":
            comp_names = [c["name"] for c in COMPETITORS]
            comp_sel = st.sidebar.selectbox("Select competitor:", comp_names, key="comp_sel")
            if st.sidebar.button("Compare Now", key="comp_go", type="primary"):
                with st.sidebar:
                    with st.spinner("Analyzing..."):
                        comp_result, prov = compare_competitor(comp_sel, audience, cfg)
                    st.markdown(comp_result)

        elif copilot_mode == "Govt Schemes":
            if st.sidebar.button("Analyze All Schemes", key="scheme_go", type="primary"):
                with st.sidebar:
                    with st.spinner("Analyzing eligibility..."):
                        schemes, prov = analyze_govt_schemes(cfg)
                    st.markdown(schemes)

        elif copilot_mode == "Investment Thesis":
            if st.sidebar.button("Generate Thesis", key="thesis_go", type="primary"):
                with st.sidebar:
                    with st.spinner("Building investment case..."):
                        thesis, prov = generate_investment_thesis(cfg, audience)
                    st.markdown(thesis)

        elif copilot_mode == "Meeting Notes":
            notes = st.sidebar.text_area("Type meeting notes:", height=150, key="meeting_notes",
                placeholder="Client interested in 20TPD\nAsked about DSCR\nWants DPR by Friday...")
            if notes and st.sidebar.button("Generate Minutes", key="notes_go", type="primary"):
                with st.sidebar:
                    with st.spinner("Generating minutes..."):
                        minutes, prov = generate_meeting_minutes(notes, cfg)
                    st.markdown(minutes)

    else:
        st.sidebar.markdown("---")
        st.sidebar.info("Add API keys in AI Settings for AI Meeting Copilot")
        st.sidebar.page_link("pages/17_🔑_AI_Settings.py", label="AI Settings", icon="🔑")
except Exception:
    pass

st.caption(f"{COMPANY['name']} | {COMPANY['owner']} | {COMPANY['phone']} | Consultant Presentation System")
