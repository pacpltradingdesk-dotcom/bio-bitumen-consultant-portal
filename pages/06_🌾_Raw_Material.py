"""
Raw Material — State-wise biomass availability, cost, supplier list, seasonality
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from state_manager import get_config, update_field, init_state
from config import STATES

st.set_page_config(page_title="Raw Material", page_icon="🌾", layout="wide")
init_state()
st.title("Raw Material Analysis")
st.markdown("**Agro-waste biomass availability, cost analysis, and seasonality planning**")
st.markdown("---")

cfg = get_config()

# ── State-wise Biomass Availability ──────────────────────────────────
st.subheader("State-wise Biomass Availability (Million MT/Year)")

biomass_data = {
    "Uttar Pradesh":   {"rice_straw": 25, "wheat_straw": 20, "sugarcane": 15, "cotton": 5, "total": 65},
    "Punjab":          {"rice_straw": 20, "wheat_straw": 18, "sugarcane": 3, "cotton": 8, "total": 49},
    "Madhya Pradesh":  {"rice_straw": 8, "wheat_straw": 15, "sugarcane": 5, "cotton": 4, "total": 32},
    "Maharashtra":     {"rice_straw": 5, "wheat_straw": 8, "sugarcane": 25, "cotton": 10, "total": 48},
    "Haryana":         {"rice_straw": 12, "wheat_straw": 10, "sugarcane": 5, "cotton": 8, "total": 35},
    "Bihar":           {"rice_straw": 15, "wheat_straw": 8, "sugarcane": 8, "cotton": 2, "total": 33},
    "Rajasthan":       {"rice_straw": 3, "wheat_straw": 12, "sugarcane": 2, "cotton": 5, "total": 22},
    "Gujarat":         {"rice_straw": 5, "wheat_straw": 8, "sugarcane": 10, "cotton": 12, "total": 35},
    "Karnataka":       {"rice_straw": 8, "wheat_straw": 5, "sugarcane": 15, "cotton": 3, "total": 31},
    "Tamil Nadu":      {"rice_straw": 10, "wheat_straw": 2, "sugarcane": 12, "cotton": 2, "total": 26},
    "Andhra Pradesh":  {"rice_straw": 12, "wheat_straw": 3, "sugarcane": 8, "cotton": 5, "total": 28},
    "Telangana":       {"rice_straw": 10, "wheat_straw": 2, "sugarcane": 5, "cotton": 6, "total": 23},
    "West Bengal":     {"rice_straw": 18, "wheat_straw": 3, "sugarcane": 2, "cotton": 1, "total": 24},
    "Odisha":          {"rice_straw": 10, "wheat_straw": 2, "sugarcane": 3, "cotton": 1, "total": 16},
    "Chhattisgarh":    {"rice_straw": 8, "wheat_straw": 5, "sugarcane": 2, "cotton": 1, "total": 16},
    "Jharkhand":       {"rice_straw": 5, "wheat_straw": 3, "sugarcane": 2, "cotton": 1, "total": 11},
    "Assam":           {"rice_straw": 8, "wheat_straw": 1, "sugarcane": 3, "cotton": 0, "total": 12},
    "Kerala":          {"rice_straw": 3, "wheat_straw": 0, "sugarcane": 1, "cotton": 0, "total": 4},
}

bio_df = pd.DataFrame([
    {"State": s, **d} for s, d in biomass_data.items()
]).sort_values("total", ascending=False)

# Stacked bar chart
fig_bio = px.bar(bio_df, x="State", y=["rice_straw", "wheat_straw", "sugarcane", "cotton"],
                  title="State-wise Agro-Waste Biomass (Million MT/Year)",
                  labels={"value": "Million MT", "variable": "Crop Type"},
                  barmode="stack", color_discrete_sequence=["#006400", "#FFD700", "#8B4513", "#FF6347"])
fig_bio.update_layout(xaxis_tickangle=-45, template="plotly_white", height=450)
st.plotly_chart(fig_bio, width="stretch")

st.markdown("---")

# ── Cost per Ton ──────────────────────────────────────────────────────
st.subheader("Biomass Cost Analysis (Rs/MT)")

cost_data = [
    {"Type": "Rice Straw", "Farm Gate": 1500, "Transport (50km)": 500, "Storage": 300, "Total Delivered": 2300},
    {"Type": "Wheat Straw", "Farm Gate": 1800, "Transport (50km)": 500, "Storage": 300, "Total Delivered": 2600},
    {"Type": "Sugarcane Bagasse", "Farm Gate": 1200, "Transport (50km)": 600, "Storage": 200, "Total Delivered": 2000},
    {"Type": "Cotton Stalk", "Farm Gate": 2000, "Transport (50km)": 500, "Storage": 300, "Total Delivered": 2800},
    {"Type": "Groundnut Shell", "Farm Gate": 2500, "Transport (50km)": 400, "Storage": 200, "Total Delivered": 3100},
    {"Type": "Coconut Shell", "Farm Gate": 3000, "Transport (50km)": 500, "Storage": 200, "Total Delivered": 3700},
]
cost_df = pd.DataFrame(cost_data)

fig_cost = px.bar(cost_df, x="Type", y=["Farm Gate", "Transport (50km)", "Storage"],
                   title="Biomass Cost Breakdown (Rs/MT)",
                   barmode="stack", color_discrete_sequence=["#003366", "#006699", "#FF8800"])
fig_cost.update_layout(template="plotly_white", height=350)
st.plotly_chart(fig_cost, width="stretch")

st.dataframe(cost_df, width="stretch", hide_index=True)

# Current config display
st.info(f"**Your current config uses Rs {cfg['raw_material_cost_per_mt']:,}/MT** biomass cost. "
        f"This is per MT of OUTPUT (includes ~2x input ratio). "
        f"Edit in Financial Model tab to see impact on all calculations.")

st.markdown("---")

# ── Seasonality Chart ─────────────────────────────────────────────────
st.subheader("Biomass Availability — Seasonality Calendar")

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
rice = [30, 20, 10, 5, 5, 5, 5, 10, 20, 40, 80, 100]
wheat = [10, 20, 50, 100, 80, 40, 10, 5, 5, 5, 5, 5]
sugarcane = [80, 100, 80, 40, 20, 10, 10, 10, 20, 30, 50, 70]

fig_season = go.Figure()
fig_season.add_trace(go.Scatter(x=months, y=rice, name="Rice Straw", fill="tozeroy",
                                 line=dict(color="#006400")))
fig_season.add_trace(go.Scatter(x=months, y=wheat, name="Wheat Straw", fill="tozeroy",
                                 line=dict(color="#FFD700")))
fig_season.add_trace(go.Scatter(x=months, y=sugarcane, name="Sugarcane Bagasse", fill="tozeroy",
                                 line=dict(color="#8B4513")))
fig_season.update_layout(title="Biomass Availability by Month (Relative %)",
                           yaxis_title="Availability (%)", template="plotly_white", height=350)
st.plotly_chart(fig_season, width="stretch")

st.markdown("""
**Key Insight:** Rice straw peaks Oct-Dec (Kharif harvest), Wheat peaks Mar-May (Rabi harvest).
For year-round operations, multi-crop sourcing strategy is essential.
Sugarcane bagasse provides the most consistent year-round supply from sugar mills.
""")

st.markdown("---")

# ── Supplier List ─────────────────────────────────────────────────────
st.subheader("Biomass Supplier Network")
suppliers = [
    {"Name": "Farmer Producer Organizations (FPO)", "Type": "Rice/Wheat Straw", "Region": "UP, Punjab, Haryana", "Capacity": "5,000+ MT/yr", "Contact": "Via District Agriculture Office"},
    {"Name": "Sugar Mills (Bagasse)", "Type": "Sugarcane Bagasse", "Region": "MH, KA, UP, TN", "Capacity": "10,000+ MT/yr", "Contact": "Mill procurement dept"},
    {"Name": "Cotton Ginning Mills", "Type": "Cotton Stalk/Shell", "Region": "GJ, MH, MP, RJ", "Capacity": "3,000+ MT/yr", "Contact": "APMC contact"},
    {"Name": "Oil Mills (Groundnut)", "Type": "Groundnut Shell", "Region": "GJ, AP, RJ", "Capacity": "2,000+ MT/yr", "Contact": "Oil mill association"},
    {"Name": "Coconut Processing Units", "Type": "Coconut Shell", "Region": "KL, TN, KA", "Capacity": "1,000+ MT/yr", "Contact": "Coconut Board"},
    {"Name": "Biomass Aggregators", "Type": "Mixed Agro-Waste", "Region": "Pan India", "Capacity": "Custom", "Contact": "IndiaMART / TradeIndia"},
]
st.dataframe(pd.DataFrame(suppliers), width="stretch", hide_index=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# PROFESSIONAL AGRO ENGINE INTEGRATION (NEW)
# ══════════════════════════════════════════════════════════════════════
try:
    from engines.agro_engine import (get_crop_list, calculate_procurement_cost,
                                      calculate_plant_requirement, get_monthly_availability,
                                      calculate_inventory_plan, get_quality_specs,
                                      get_supplier_types, MONTH_NAMES)

    st.subheader("Procurement Cost Calculator")
    st.caption("Select crop and state to see detailed cost breakdown")

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        sel_crop = st.selectbox("Select Biomass Type", get_crop_list(), key="agro_crop")
    with pc2:
        sel_state = st.selectbox("State (short code)", ["Punjab", "UP", "Haryana", "Gujarat",
            "Maharashtra", "MP", "Rajasthan", "Bihar", "Karnataka", "TN", "Kerala", "default"], key="agro_state")
    with pc3:
        sel_distance = st.slider("Transport Distance (km)", 10, 200, 50, 10, key="agro_dist")

    proc_cost = calculate_procurement_cost(sel_crop, sel_state, sel_distance, storage_months=2)
    if "error" not in proc_cost:
        cost_df = pd.DataFrame([{"Component": k, "Rs/MT": v} for k, v in proc_cost["components"].items()])

        cc1, cc2 = st.columns(2)
        with cc1:
            st.metric("Total Delivered Cost", f"Rs {proc_cost['total_delivered_rs_mt']:,}/MT")
            st.dataframe(cost_df, width="stretch", hide_index=True)
        with cc2:
            fig_cost = px.pie(cost_df, names="Component", values="Rs/MT",
                               title=f"Cost Breakdown — {sel_crop}",
                               color_discrete_sequence=["#003366", "#006699", "#0088cc", "#FF8800", "#00AA44"])
            fig_cost.update_layout(template="plotly_white", height=300)
            st.plotly_chart(fig_cost, width="stretch")

    st.markdown("---")

    # Plant Requirement Calculator
    st.subheader("Plant Biomass Requirement")
    plant_req = calculate_plant_requirement(cfg["capacity_tpd"], sel_crop)
    if "error" not in plant_req:
        pr1, pr2, pr3, pr4 = st.columns(4)
        pr1.metric("Daily Biomass", f"{plant_req['daily_biomass_mt']:.1f} MT")
        pr2.metric("Annual Biomass", f"{plant_req['annual_biomass_mt']:,.0f} MT")
        pr3.metric("90-Day Buffer", f"{plant_req['buffer_90_days_mt']:,.0f} MT")
        pr4.metric("Storage Area", f"{plant_req['storage_area_sqft']:,.0f} sq ft")

        pr5, pr6, pr7 = st.columns(3)
        pr5.metric("Bio-Oil Output", f"{plant_req['bio_oil_output_mt_day']:.1f} MT/day")
        pr6.metric("Biochar Output", f"{plant_req['biochar_output_mt_day']:.1f} MT/day")
        pr7.metric("Syngas Output", f"{plant_req['syngas_output_mt_day']:.1f} MT/day")

    st.markdown("---")

    # Quality Specifications
    st.subheader("Biomass Quality Specifications")
    specs = get_quality_specs()
    st.dataframe(pd.DataFrame(specs), width="stretch", hide_index=True)

    st.markdown("---")

    # Monthly Inventory Plan
    st.subheader("12-Month Inventory Plan")
    inv_plan = calculate_inventory_plan(cfg["capacity_tpd"], sel_crop, sel_state)
    if inv_plan:
        inv_df = pd.DataFrame(inv_plan)
        st.dataframe(inv_df, width="stretch", hide_index=True)

        fig_inv = go.Figure()
        fig_inv.add_trace(go.Bar(x=inv_df["Month"], y=inv_df["Procurement (MT)"],
                                   name="Procurement", marker_color="#003366"))
        fig_inv.add_trace(go.Bar(x=inv_df["Month"], y=inv_df["Consumption (MT)"],
                                   name="Consumption", marker_color="#CC3333"))
        fig_inv.add_trace(go.Scatter(x=inv_df["Month"], y=inv_df["Buffer (Days)"],
                                      name="Buffer Days", mode="lines+markers",
                                      line=dict(color="#00AA44", width=3), yaxis="y2"))
        fig_inv.update_layout(title="Monthly Procurement vs Consumption + Buffer",
                               template="plotly_white", height=400, barmode="group",
                               yaxis=dict(title="MT"), yaxis2=dict(title="Buffer Days", overlaying="y", side="right"))
        st.plotly_chart(fig_inv, width="stretch")

    st.markdown("---")

    # Supplier Types
    st.subheader("Supplier Types & Contract Guide")
    sup_types = get_supplier_types()
    for s in sup_types:
        with st.expander(f"{s['Type']} — Volume: {s['Typical Volume']} | Reliability: {s['Reliability']}"):
            st.markdown(f"**Price Negotiation:** {s['Price Negotiation']}")
            st.markdown(f"**Contract Type:** {s['Contract']}")
            st.markdown(f"**Pros:** {s['Pros']}")
            st.markdown(f"**Cons:** {s['Cons']}")

except Exception as e:
    st.info(f"Advanced agro analysis loading... ({e})")

st.markdown("---")
st.caption("Source: ICAR Biomass Atlas, Ministry of Agriculture, IndiaMART supplier data (March 2026) + Agro Engine v2.0")
