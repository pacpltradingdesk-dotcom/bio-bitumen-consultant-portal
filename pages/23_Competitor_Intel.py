"""
Competitor Intelligence — SWOT, Radar, Market Positioning, Differentiation
============================================================================
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from state_manager import init_state
from config import COMPANY, COMPETITORS, PPS_SWOT

st.set_page_config(page_title="Competitor Intelligence", page_icon="🕵️", layout="wide")
init_state()

st.title("Competitor Intelligence")
st.markdown("**Market Positioning | SWOT Analysis | Competitive Radar | Differentiation**")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# TOP METRICS
# ══════════════════════════════════════════════════════════════════════
high_threat = [c for c in COMPETITORS if c["threat_level"] == "High"]
med_threat = [c for c in COMPETITORS if c["threat_level"] == "Medium"]
low_threat = [c for c in COMPETITORS if c["threat_level"] == "Low"]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Competitors", len(COMPETITORS))
m2.metric("High Threat", len(high_threat))
m3.metric("Medium Threat", len(med_threat))
m4.metric("Low Threat", len(low_threat))
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# COMPETITOR DATABASE TABLE
# ══════════════════════════════════════════════════════════════════════
st.subheader("Competitor Database")
comp_df = pd.DataFrame(COMPETITORS)
display_cols = ["name", "location", "capacity_tpd", "technology", "product", "threat_level", "year_started"]
display_df = comp_df[display_cols].copy()
display_df.columns = ["Company", "Location", "Capacity (TPD)", "Technology", "Product", "Threat", "Since"]
st.dataframe(display_df, width="stretch", hide_index=True)
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# COMPETITIVE RADAR CHART
# ══════════════════════════════════════════════════════════════════════
st.subheader("Competitive Positioning Radar")

categories = ["Experience", "Network", "Technology", "Scale", "Bio-Bitumen\nCapability"]

def score_competitor(c):
    exp = min((2026 - c["year_started"]) / 25 * 100, 100)
    network = 20 if c["threat_level"] == "Low" else (50 if c["threat_level"] == "Medium" else 70)
    tech = 90 if "CSIR" in c["technology"] else (60 if "Conventional" in c["technology"] else 40)
    scale = min(c["capacity_tpd"] / 50 * 100, 100)
    bio = 90 if "Bio" in c["product"] else (40 if "trial" in c["product"].lower() else 10)
    return [exp, network, tech, scale, bio]

# PPS Anantams scores
pps_scores = [100, 95, 75, 60, 85]

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
    r=pps_scores + [pps_scores[0]],
    theta=categories + [categories[0]],
    fill="toself", name="PPS Anantams",
    line=dict(color="#003366", width=3), opacity=0.7,
))

colors = ["#CC3333", "#FF8800", "#006699", "#00AA44"]
for i, comp in enumerate(high_threat + med_threat[:2]):
    scores = score_competitor(comp)
    fig_radar.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=categories + [categories[0]],
        fill="toself", name=comp["name"][:20],
        line=dict(color=colors[i % len(colors)]), opacity=0.4,
    ))

fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    title="PPS Anantams vs Key Competitors",
    template="plotly_white", height=500, showlegend=True,
)
st.plotly_chart(fig_radar, width="stretch")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# SWOT ANALYSIS
# ══════════════════════════════════════════════════════════════════════
st.subheader("PPS Anantams — SWOT Analysis")

sw_col, ot_col = st.columns(2)

with sw_col:
    st.markdown("""
    <div style="background: #e6f3e6; border-left: 4px solid #00AA44; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <h4 style="color: #00AA44; margin: 0 0 10px 0;">STRENGTHS</h4>
    """, unsafe_allow_html=True)
    for s in PPS_SWOT["strengths"]:
        st.markdown(f"- {s}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #fff3e6; border-left: 4px solid #FF8800; padding: 15px; border-radius: 8px;">
        <h4 style="color: #FF8800; margin: 0 0 10px 0;">WEAKNESSES</h4>
    """, unsafe_allow_html=True)
    for w in PPS_SWOT["weaknesses"]:
        st.markdown(f"- {w}")
    st.markdown("</div>", unsafe_allow_html=True)

with ot_col:
    st.markdown("""
    <div style="background: #e6f0ff; border-left: 4px solid #003366; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <h4 style="color: #003366; margin: 0 0 10px 0;">OPPORTUNITIES</h4>
    """, unsafe_allow_html=True)
    for o in PPS_SWOT["opportunities"]:
        st.markdown(f"- {o}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #ffe6e6; border-left: 4px solid #CC3333; padding: 15px; border-radius: 8px;">
        <h4 style="color: #CC3333; margin: 0 0 10px 0;">THREATS</h4>
    """, unsafe_allow_html=True)
    for t in PPS_SWOT["threats"]:
        st.markdown(f"- {t}")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# DETAILED COMPETITOR PROFILES
# ══════════════════════════════════════════════════════════════════════
st.subheader("Detailed Competitor Profiles")

for comp in COMPETITORS:
    threat_color = {"High": "red", "Medium": "orange", "Low": "green"}[comp["threat_level"]]
    with st.expander(f"{'🔴' if comp['threat_level']=='High' else '🟡' if comp['threat_level']=='Medium' else '🟢'} {comp['name']} — {comp['location']} | Threat: {comp['threat_level']}"):
        dc1, dc2 = st.columns(2)
        with dc1:
            st.markdown(f"**Capacity:** {comp['capacity_tpd']} TPD")
            st.markdown(f"**Technology:** {comp['technology']}")
            st.markdown(f"**Product:** {comp['product']}")
            st.markdown(f"**Since:** {comp['year_started']}")
        with dc2:
            st.markdown(f"**Strengths:** {comp['strengths']}")
            st.markdown(f"**Weaknesses:** {comp['weaknesses']}")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# WHY PPS ANANTAMS WINS
# ══════════════════════════════════════════════════════════════════════
st.subheader("Why PPS Anantams Wins")
st.markdown(f"""
<div style="background: linear-gradient(135deg, #003366, #006699); padding: 25px; border-radius: 12px; color: white;">
    <h3 style="color: white;">Competitive Moat — What Others Cannot Replicate</h3>
    <div style="display: flex; gap: 30px; flex-wrap: wrap; margin-top: 15px;">
        <div style="flex: 1; min-width: 200px;">
            <h4 style="color: #99ccff;">Network Effect</h4>
            <p>{COMPANY['industry_contacts']:,} live contacts — contractors, traders, importers built over 25 years. Cannot be replicated quickly.</p>
        </div>
        <div style="flex: 1; min-width: 200px;">
            <h4 style="color: #99ccff;">Supply Chain Lock</h4>
            <p>International VG-30 contract (2.4 Lakh MT/yr from Iraq/USA). No other consultant has this.</p>
        </div>
        <div style="flex: 1; min-width: 200px;">
            <h4 style="color: #99ccff;">Full-Stack Expertise</h4>
            <p>Only consultant covering ALL 4 stages: Site Selection > Plant Setup > Production > Sales Network.</p>
        </div>
        <div style="flex: 1; min-width: 200px;">
            <h4 style="color: #99ccff;">Proven Track Record</h4>
            <p>{COMPANY['plants_built']} plants built, {COMPANY['product_types']} product types, {COMPANY['states_network']}-state distribution. BSE-listed founder.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption(f"{COMPANY['name']} | {COMPANY['owner']} | {COMPANY['phone']}")
