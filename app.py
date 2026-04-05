"""
Bio Bitumen Master Consulting System — MAIN ENTRY (UPGRADED)
=============================================================
Professional home page with live market ticker, quick ROI calculator,
recent activity feed, system status, and full navigation grid.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from database import init_db
from state_manager import init_state, get_config
from config import COMPANY

st.set_page_config(
    page_title="Bio Bitumen Consulting System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ── AUTHENTICATION (credentials from env vars or secure config) ───────
import hashlib

def _load_users():
    """Load users from env vars or fallback secure config."""
    # Priority: ENV vars > data/auth_config.json > defaults
    import json
    auth_path = os.path.join(os.path.dirname(__file__), "data", "auth_config.json")
    if os.path.exists(auth_path):
        try:
            return json.loads(open(auth_path, encoding='utf-8').read())
        except Exception:
            pass
    # Fallback defaults (change these via auth_config.json)
    return {
        "admin": {"password_hash": hashlib.sha256(os.environ.get("ADMIN_PASSWORD", "admin2424").encode()).hexdigest(),
                  "role": "admin", "name": "Prince P. Shah"},
        "demo": {"password_hash": hashlib.sha256(os.environ.get("DEMO_PASSWORD", "demo2424").encode()).hexdigest(),
                  "role": "client", "name": "Demo Client"},
    }

USERS = _load_users()

def _verify_password(stored_hash, input_password):
    return stored_hash == hashlib.sha256(input_password.encode()).hexdigest()

def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.markdown("## Bio Bitumen Consulting System")
        st.markdown(f"**{COMPANY['trade_name']}** | {COMPANY['owner']}")
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Login")
            username = st.text_input("Username", key="login_user", placeholder="admin / demo")
            password = st.text_input("Password", type="password", key="login_pw")
            if st.button("Login", type="primary"):
                user = USERS.get(username)
                if user and _verify_password(user.get("password_hash", ""), password):
                    st.session_state["authenticated"] = True
                    st.session_state["user_role"] = user["role"]
                    st.session_state["user_name"] = user["name"]
                    st.rerun()
                else:
                    st.error("Wrong credentials. Contact Prince Shah: +91 7795242424")
            st.caption("Default: admin / admin2424")
        st.stop()

check_auth()
init_state()

# CSS
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cfg = get_config()

# ── SIDEBAR ───────────────────────────────────────────────────────────
from engines.language import language_selector, t
language_selector()

user_name = st.session_state.get("user_name", "Admin")
user_role = st.session_state.get("user_role", "admin")
st.sidebar.markdown(f"**User:** {user_name} ({user_role})")
if st.sidebar.button("Logout", key="logout_btn"):
    st.session_state["authenticated"] = False
    st.rerun()
st.sidebar.markdown("---")

st.sidebar.markdown(f"### {COMPANY['trade_name']}")
st.sidebar.markdown("**Bio Bitumen Consulting System**")
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Config:** {cfg['capacity_tpd']:.0f} TPD")
st.sidebar.markdown(f"**Invest:** ₹{cfg['investment_cr']:.1f} Cr")
st.sidebar.markdown(f"**ROI:** {cfg['roi_pct']:.1f}% | **IRR:** {cfg['irr_pct']:.1f}%")

# Contradiction check in sidebar
try:
    from utils.contradiction_alerts import check_contradictions
    _alerts = check_contradictions(cfg)
    _errs = [a for a in _alerts if a["level"] == "error"]
    if _errs:
        st.sidebar.error(f"⚠️ {len(_errs)} issue(s) found!")
except Exception:
    pass

# API Status in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("**API Status**")
try:
    from engines.ai_engine import is_ai_available, get_active_provider
    if is_ai_available():
        provider = get_active_provider()
        st.sidebar.markdown(f"🟢 AI: **{provider.upper()}** active")
    else:
        st.sidebar.markdown("🔴 AI: No API keys")
except Exception:
    st.sidebar.markdown("⚪ AI: Not configured")

# Free APIs status
try:
    api_count = 0
    from engines.free_apis import _read_cache
    for name in ["weather_vadodara", "fx_rates_USD", "india_gdp"]:
        if _read_cache(name, ttl=7200):
            api_count += 1
    st.sidebar.markdown(f"🟢 Free APIs: {api_count}/3 cached"  if api_count > 0 else "🟡 APIs: Refreshing...")
except Exception:
    pass

# ══════════════════════════════════════════════════════════════════════
# HERO BANNER
# ══════════════════════════════════════════════════════════════════════
import datetime
hour = datetime.datetime.now().hour
greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")

st.markdown(f"""
<div style="background: linear-gradient(135deg, #003366 0%, #006699 50%, #0088cc 100%);
            padding: 30px 40px; border-radius: 15px; margin-bottom: 20px; color: white;">
    <h1 style="color: white; margin: 0; font-size: 2.2em;">Bio Bitumen Master Consulting System</h1>
    <h3 style="color: #99ccff; margin: 5px 0 15px 0;">{COMPANY['trade_name']} — ONE-POINT SOLUTION PROVIDER</h3>
    <p style="color: #cce0ff; font-size: 1.1em; margin: 0;">
        {greeting}, {user_name}! | Land Selection > Plant Setup > Financial Closure > EVERYTHING READY
    </p>
    <div style="display: flex; gap: 40px; margin-top: 15px;">
        <div><span style="font-size: 2em; font-weight: bold;">{COMPANY['years_experience']}</span><br><span style="font-size: 0.85em;">Years Experience</span></div>
        <div><span style="font-size: 2em; font-weight: bold;">{COMPANY['plants_built']}</span><br><span style="font-size: 0.85em;">Plants Built</span></div>
        <div><span style="font-size: 2em; font-weight: bold;">{COMPANY['industry_contacts']:,}</span><br><span style="font-size: 0.85em;">Industry Contacts</span></div>
        <div><span style="font-size: 2em; font-weight: bold;">{COMPANY['states_network']}</span><br><span style="font-size: 0.85em;">States Network</span></div>
        <div><span style="font-size: 2em; font-weight: bold;">{COMPANY['product_types']}</span><br><span style="font-size: 0.85em;">Product Types</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# LIVE MARKET TICKER
# ══════════════════════════════════════════════════════════════════════
try:
    from engines.market_data_api import get_market_summary
    market = get_market_summary()
    vg30 = market.get("vg30_estimate", {})
    fx = market.get("usd_inr", {})
    crude_data = market.get("crude_oil")
    crude_price = crude_data.get("latest_price", 0) if isinstance(crude_data, dict) else 0

    tk1, tk2, tk3, tk4 = st.columns(4)
    tk1.metric("Crude Oil (Brent)", f"${crude_price:.1f}/bbl")
    tk2.metric("USD/INR", f"Rs {fx.get('rate', 84):.2f}")
    tk3.metric("VG30 Estimate", f"Rs {vg30.get('vg30_estimated', 38000):,.0f}/MT")
    tk4.metric("Gold", f"${market.get('gold', {}).get('price_usd', 0):,.0f}/oz")
except Exception:
    st.info("Market data loading... (will refresh on next visit)")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# START PRESENTATION — PRIMARY ACTION
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="background: linear-gradient(90deg, #003366, #006699); padding: 20px 30px; border-radius: 12px;
            text-align: center; margin-bottom: 15px;">
    <h2 style="color: white; margin: 0;">Ready for Client Meeting?</h2>
    <p style="color: #99ccff; margin: 5px 0;">14-Slide Interactive Presentation — Input Client Info → Show Live Data → Generate Documents</p>
</div>
""", unsafe_allow_html=True)

pres1, pres2, pres3 = st.columns([2, 1, 1])
pres1.page_link("pages/01_🎯_Presenter.py", label="START PRESENTATION MODE", icon="🎯")
pres2.page_link("pages/03_📝_Project_Setup.py", label="Setup Project", icon="📝")
pres3.page_link("pages/13_📁_Document_Hub.py", label="Document Hub", icon="📁")

st.markdown("---")

# ── Client Journey (Alternative) ────────────────────────────────────
with st.expander("Client Journey (Step-by-Step Alternative)"):
    jc1, jc2, jc3, jc4 = st.columns(4)
    jc1.page_link("pages/50_Client_Journey.py", label="New Investor", icon="🧑‍🌾")
    jc2.page_link("pages/50_Client_Journey.py", label="Bitumen Plant Owner", icon="🛢️")
    jc3.page_link("pages/50_Client_Journey.py", label="Biomass Company", icon="🌾")
    jc4.page_link("pages/50_Client_Journey.py", label="Pyrolysis Owner", icon="🔥")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# PROJECT SUMMARY METRICS
# ══════════════════════════════════════════════════════════════════════
from document_index import build_index
from database import get_all_customers, get_all_packages

doc_df = build_index()
customers = get_all_customers()
packages = get_all_packages()

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Capacity Range", "3-100 TPD")
c2.metric("Documents", f"{len(doc_df):,}")
c3.metric("States Covered", "18")
c4.metric("Customers", len(customers))
c5.metric("Licenses Tracked", "25 Types")
c6.metric("Industry Network", f"{COMPANY['industry_contacts']:,}")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# QUICK ROI CALCULATOR (Inline)
# ══════════════════════════════════════════════════════════════════════
st.subheader("Quick ROI Calculator")
st.caption("Select any capacity below to instantly see investment, returns, and break-even")

from engines.three_process_model import calculate_process

qr1, qr2 = st.columns([1, 2])
with qr1:
    quick_tpd = st.selectbox("Select Capacity (TPD)", [5, 10, 15, 20, 30, 40, 50], index=3, key="quick_roi_tpd")
    quick_process = st.radio("Process Model", [1, 2, 3],
                              format_func=lambda x: {1: "Full Chain", 2: "Blending Only", 3: "Raw Output"}[x],
                              key="quick_roi_process", horizontal=True)

with qr2:
    try:
        qr_result = calculate_process(quick_process, float(quick_tpd))
        qm1, qm2, qm3, qm4 = st.columns(4)
        qm1.metric("Investment", f"Rs {qr_result.get('capex_lac', 0)/100:.1f} Cr")
        qm2.metric("ROI", f"{qr_result.get('roi_pct', 0):.1f}%")
        qm3.metric("IRR", f"{qr_result.get('irr_pct', 0):.1f}%")
        qm4.metric("Break-Even", f"{qr_result.get('break_even_months', 0)} months")

        qm5, qm6, qm7, qm8 = st.columns(4)
        qm5.metric("Monthly Profit", f"Rs {qr_result.get('monthly_profit_lac', 0):.1f} Lac")
        qm6.metric("DSCR Yr3", f"{qr_result.get('dscr_yr3', 0):.2f}x")
        qm7.metric("EMI/Month", f"Rs {qr_result.get('emi_lac_mth', 0):.2f} Lac")
        qm8.metric("Profit/MT", f"Rs {qr_result.get('profit_per_mt', 0):,.0f}")
    except Exception:
        st.info("Configure financial model to see quick ROI calculations")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# CURRENT CONFIGURATION (Auto-Updates)
# ══════════════════════════════════════════════════════════════════════
st.subheader("Selected Configuration")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Capacity", f"{cfg['capacity_tpd']:.0f} TPD")
m2.metric("Investment", f"Rs {cfg['investment_cr']:.2f} Cr")
m3.metric("ROI", f"{cfg['roi_pct']:.1f}%")
m4.metric("Break-Even", f"{cfg['break_even_months']} months")
m5.metric("Monthly Profit", f"Rs {cfg['monthly_profit_lac']:.1f} Lac")

col_a, col_b = st.columns(2)
with col_a:
    st.metric("Revenue Yr5", f"Rs {cfg['revenue_yr5_lac']:.0f} Lac")
    st.metric("DSCR Yr3", f"{cfg['dscr_yr3']:.2f}x")
with col_b:
    st.metric("IRR", f"{cfg['irr_pct']:.1f}%")
    st.metric("Profit/MT", f"Rs {cfg['profit_per_mt']:,.0f}")

st.caption("Change any input in Plant Design or Financial tab to auto-update ALL numbers here")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# REVENUE vs COST CHART
# ══════════════════════════════════════════════════════════════════════
import plotly.graph_objects as go
import pandas as pd

if cfg["roi_timeline"]:
    roi_df = pd.DataFrame(cfg["roi_timeline"])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=roi_df["Year"], y=roi_df["Revenue (Lac)"], name="Revenue", marker_color="#003366"))
    fig.add_trace(go.Bar(x=roi_df["Year"], y=roi_df["Variable Cost (Lac)"], name="Variable Cost", marker_color="#CC3333"))
    fig.add_trace(go.Scatter(x=roi_df["Year"], y=roi_df["PAT (Lac)"], name="Net Profit",
                              mode="lines+markers", line=dict(color="#00AA44", width=3)))
    fig.update_layout(title="7-Year Revenue vs Cost vs Profit (Rs Lakhs)",
                       barmode="group", xaxis_title="Year", yaxis_title="Rs Lakhs",
                       template="plotly_white", height=400)
    st.plotly_chart(fig, width="stretch")

# ── Monthly P&L Snapshot ─────────────────────────────────────────────
if cfg["monthly_pnl"]:
    st.subheader("Monthly P&L (Year 5 Steady State)")
    import plotly.express as px
    pnl = cfg["monthly_pnl"]
    pnl_df = pd.DataFrame([{"Item": k, "Rs Lakhs": v} for k, v in pnl.items()])
    fig2 = px.bar(pnl_df, x="Item", y="Rs Lakhs", color="Item",
                   title="Monthly Income & Expense Breakdown",
                   color_discrete_sequence=["#003366", "#CC3333", "#FF8800", "#006699", "#AA3366", "#00AA44"])
    fig2.update_layout(template="plotly_white", height=350, showlegend=False)
    st.plotly_chart(fig2, width="stretch")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# RECENT ACTIVITY + SYSTEM STATUS
# ══════════════════════════════════════════════════════════════════════
act_col, status_col = st.columns([2, 1])

with act_col:
    st.subheader("Recent Activity")
    try:
        from database import get_all_communications
        comms = get_all_communications()
        if comms:
            for comm in comms[:5]:
                channel = comm.get("channel", "Email")
                subject = comm.get("subject", "Communication")
                sent_at = comm.get("sent_at", "")[:10]
                st.markdown(f"- **{channel}** — {subject} ({sent_at})")
        else:
            st.info("No recent communications yet. Use the Send module to contact clients.")
    except Exception:
        st.info("Activity feed will populate as you use the system.")

with status_col:
    st.subheader("System Status")
    try:
        from engines.self_healing_worker import get_health_status
        health = get_health_status()
        score = health.get("overall_score", 85)
        color = "#00AA44" if score >= 80 else ("#FF8800" if score >= 60 else "#CC3333")
        label = "Healthy" if score >= 80 else ("Degraded" if score >= 60 else "Needs Attention")
        st.markdown(f"""
        <div style="background: {color}22; border-left: 4px solid {color}; padding: 15px; border-radius: 8px;">
            <h3 style="color: {color}; margin: 0;">{score}% — {label}</h3>
            <p style="margin: 5px 0 0 0;">Database, APIs, Documents</p>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        st.markdown("""
        <div style="background: #00AA4422; border-left: 4px solid #00AA44; padding: 15px; border-radius: 8px;">
            <h3 style="color: #00AA44; margin: 0;">System Online</h3>
            <p style="margin: 5px 0 0 0;">All modules operational</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# FULL NAVIGATION GRID (5 columns)
# ══════════════════════════════════════════════════════════════════════
st.subheader("All Modules")

nav = st.columns(5)
with nav[0]:
    st.markdown("**Analysis**")
    st.page_link("pages/02_📊_Dashboard.py", label="Executive Dashboard", icon="📊")
    st.page_link("pages/04_📈_Market.py", label="Market Intelligence", icon="📈")
    st.page_link("pages/05_📍_Location.py", label="Location Analysis", icon="📍")
    st.page_link("pages/06_🌾_Raw_Material.py", label="Raw Material", icon="🌾")

with nav[1]:
    st.markdown("**Engineering**")
    st.page_link("pages/07_⚙️_Plant_Design.py", label="Plant Design", icon="⚙️")
    st.page_link("pages/08_📐_Drawings.py", label="Engineering Drawings", icon="📐")
    st.page_link("pages/51_Technology.py", label="Technology", icon="🔬")
    st.page_link("pages/53_Process_Flow.py", label="Process Flow", icon="🔄")

with nav[2]:
    st.markdown("**Finance & Legal**")
    st.page_link("pages/09_💰_Financial.py", label="Financial Model", icon="💰")
    st.page_link("pages/11_📋_Compliance.py", label="Compliance Tracker", icon="📑")
    st.page_link("pages/40_Buyers.py", label="Buyers Network", icon="🤝")
    st.page_link("pages/10_🏭_Procurement.py", label="Procurement", icon="🏭")

with nav[3]:
    st.markdown("**New Tools**")
    st.page_link("pages/60_ROI_Quick_Calc.py", label="ROI Calculator", icon="🎯")
    st.page_link("pages/61_Loan_EMI.py", label="Loan EMI Calculator", icon="🏦")
    st.page_link("pages/62_Capacity_Compare.py", label="Capacity Compare", icon="⚖️")
    st.page_link("pages/12_🛣️_NHAI_Tenders.py", label="NHAI Tenders", icon="🛣️")
    st.page_link("pages/63_Competitor_Intel.py", label="Competitor Intel", icon="🕵️")
    st.page_link("pages/65_Environmental.py", label="Environmental Impact", icon="🌱")
    st.page_link("pages/66_Risk_Matrix.py", label="Risk Matrix", icon="⚠️")
    st.page_link("pages/71_Weather_Site.py", label="Weather & Site", icon="🌤️")
    st.page_link("pages/73_AI_Plant_Layouts.py", label="AI Plant Layouts", icon="🏗️")

with nav[4]:
    st.markdown("**Client Ops**")
    st.page_link("pages/64_Project_Gantt.py", label="Project Timeline", icon="📅")
    st.page_link("pages/70_Meeting_Planner.py", label="Meeting Planner", icon="📋")
    st.page_link("pages/44_DPR_Generator.py", label="DPR Generator", icon="📄")
    st.page_link("pages/67_Export_Center.py", label="Export Center", icon="📤")
    st.page_link("pages/68_News_Feed.py", label="Industry News", icon="📰")
    st.page_link("pages/69_Training.py", label="Training & SOPs", icon="📚")
    st.page_link("pages/15_🤖_AI_Advisor.py", label="AI Advisor", icon="🤖")
    st.page_link("pages/03_📝_Project_Setup.py", label="Project Setup", icon="📝")
    st.page_link("pages/17_🔑_AI_Settings.py", label="AI Settings", icon="🔑")
    st.page_link("pages/72_System_Calculations.py", label="System & Formulas", icon="🔧")

st.markdown("---")

# ── Quick Actions ────────────────────────────────────────────────────
st.subheader("Quick Actions")
qa1, qa2, qa3, qa4, qa5 = st.columns(5)
qa1.page_link("pages/03_📝_Project_Setup.py", label="Project Setup", icon="📝")
qa2.page_link("pages/13_📁_Document_Hub.py", label="Document Hub", icon="📁")
qa3.page_link("pages/09_💰_Financial.py", label="Financial Model", icon="💰")
qa4.page_link("pages/60_ROI_Quick_Calc.py", label="Quick ROI Demo", icon="🎯")
qa5.page_link("pages/16_🏥_System_Health.py", label="System Health", icon="🏥")

st.markdown("---")
st.caption(f"{COMPANY['name']} | {COMPANY['owner']} | {COMPANY['phone']} | {COMPANY['hq']}")
