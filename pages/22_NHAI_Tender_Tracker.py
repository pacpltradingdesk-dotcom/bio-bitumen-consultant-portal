"""
NHAI Tender Tracker — Government Road Project Opportunities
=============================================================
Filter by state, authority, budget. Map visualization. Deadline alerts.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
from state_manager import init_state, get_config
from config import COMPANY, NHAI_TENDERS, STATES

st.set_page_config(page_title="NHAI Tender Tracker", page_icon="🛣️", layout="wide")
init_state()
cfg = get_config()

st.title("NHAI & Government Tender Tracker")
st.markdown("**Track NHAI, State PWD, BRO, PMGSY road project tenders — Filter, Analyze, Act**")
st.markdown("---")

# ── Convert to DataFrame ─────────────────────────────────────────────
df = pd.DataFrame(NHAI_TENDERS)
df["deadline_dt"] = pd.to_datetime(df["deadline"])
df["days_left"] = (df["deadline_dt"] - pd.Timestamp.now()).dt.days

# ══════════════════════════════════════════════════════════════════════
# TOP METRICS
# ══════════════════════════════════════════════════════════════════════
open_df = df[df["status"] == "Open"]
upcoming_df = df[df["status"] == "Upcoming"]

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Tenders", len(df))
m2.metric("Open Now", len(open_df))
m3.metric("Upcoming", len(upcoming_df))
m4.metric("Total Value", f"Rs {df['budget_cr'].sum():,} Cr")
m5.metric("Total Bitumen", f"{df['bitumen_mt'].sum():,} MT")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# FILTERS
# ══════════════════════════════════════════════════════════════════════
f1, f2, f3, f4 = st.columns(4)
with f1:
    filter_state = st.multiselect("Filter by State", sorted(df["state"].unique()), key="tender_state")
with f2:
    filter_authority = st.multiselect("Filter by Authority", sorted(df["authority"].unique()), key="tender_auth")
with f3:
    filter_status = st.multiselect("Filter by Status", df["status"].unique().tolist(), default=["Open"], key="tender_status")
with f4:
    filter_type = st.multiselect("Filter by Type", sorted(df["type"].unique()), key="tender_type")

filtered = df.copy()
if filter_state:
    filtered = filtered[filtered["state"].isin(filter_state)]
if filter_authority:
    filtered = filtered[filtered["authority"].isin(filter_authority)]
if filter_status:
    filtered = filtered[filtered["status"].isin(filter_status)]
if filter_type:
    filtered = filtered[filtered["type"].isin(filter_type)]

# ══════════════════════════════════════════════════════════════════════
# DEADLINE ALERTS
# ══════════════════════════════════════════════════════════════════════
urgent = filtered[filtered["days_left"] <= 30].sort_values("days_left")
if len(urgent) > 0:
    st.warning(f"**{len(urgent)} tenders closing within 30 days!**")
    for _, t in urgent.iterrows():
        days = t["days_left"]
        icon = "🔴" if days <= 7 else ("🟡" if days <= 15 else "🟢")
        st.markdown(f"{icon} **{t['id']}** — {t['project'][:60]} | {t['state']} | "
                    f"Rs {t['budget_cr']} Cr | **{days} days left** (Deadline: {t['deadline']})")
    st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# TENDER TABLE
# ══════════════════════════════════════════════════════════════════════
st.subheader(f"Tenders ({len(filtered)} results)")

display_df = filtered[["id", "project", "authority", "state", "budget_cr", "bitumen_mt",
                         "deadline", "status", "type", "days_left"]].copy()
display_df.columns = ["ID", "Project", "Authority", "State", "Budget (Cr)", "Bitumen (MT)",
                       "Deadline", "Status", "Type", "Days Left"]
display_df = display_df.sort_values("Days Left")

st.dataframe(display_df, width="stretch", height=400, hide_index=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════════════════
chart1, chart2 = st.columns(2)

with chart1:
    st.subheader("Budget by State")
    state_budget = filtered.groupby("state")["budget_cr"].sum().reset_index()
    state_budget.columns = ["State", "Total Budget (Cr)"]
    state_budget = state_budget.sort_values("Total Budget (Cr)", ascending=True)

    fig1 = px.bar(state_budget, y="State", x="Total Budget (Cr)", orientation="h",
                   color="Total Budget (Cr)", color_continuous_scale="Blues",
                   title="Tender Value by State (Rs Cr)")
    fig1.update_layout(template="plotly_white", height=450)
    st.plotly_chart(fig1, width="stretch")

with chart2:
    st.subheader("By Authority")
    auth_counts = filtered.groupby("authority").agg(
        Count=("id", "count"),
        Budget=("budget_cr", "sum"),
        Bitumen=("bitumen_mt", "sum"),
    ).reset_index().sort_values("Budget", ascending=False)

    fig2 = px.bar(auth_counts, x="authority", y="Budget", color="Count",
                   title="Tender Value by Authority", text="Count",
                   color_continuous_scale="Reds")
    fig2.update_layout(template="plotly_white", height=450)
    st.plotly_chart(fig2, width="stretch")

# ── By Type + Timeline ──────────────────────────────────────────────
type_col, timeline_col = st.columns(2)

with type_col:
    st.subheader("By Contract Type")
    type_data = filtered.groupby("type")["budget_cr"].sum().reset_index()
    fig3 = px.pie(type_data, names="type", values="budget_cr",
                   title="Budget Split by Contract Type",
                   color_discrete_sequence=["#003366", "#006699", "#0088cc", "#FF8800"])
    fig3.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig3, width="stretch")

with timeline_col:
    st.subheader("Deadline Timeline")
    timeline_data = filtered[["project", "deadline_dt", "budget_cr", "state"]].copy()
    timeline_data["project_short"] = timeline_data["project"].str[:40]

    fig4 = px.scatter(timeline_data, x="deadline_dt", y="budget_cr",
                       size="budget_cr", color="state",
                       hover_name="project_short",
                       title="Tenders by Deadline & Budget",
                       labels={"deadline_dt": "Deadline", "budget_cr": "Budget (Cr)"})
    fig4.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig4, width="stretch")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# BITUMEN OPPORTUNITY SUMMARY
# ══════════════════════════════════════════════════════════════════════
st.subheader("Bitumen Supply Opportunity")

state_bitumen = filtered.groupby("state")["bitumen_mt"].sum().reset_index()
state_bitumen.columns = ["State", "Bitumen Demand (MT)"]
state_bitumen = state_bitumen.sort_values("Bitumen Demand (MT)", ascending=False)

b1, b2 = st.columns([2, 1])
with b1:
    fig5 = px.bar(state_bitumen, x="State", y="Bitumen Demand (MT)",
                   color="Bitumen Demand (MT)", color_continuous_scale="Oranges",
                   title="Bitumen Demand from Active Tenders (MT)")
    fig5.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig5, width="stretch")

with b2:
    total_bitumen = filtered["bitumen_mt"].sum()
    st.markdown(f"""
    **Total Bitumen Demand:** {total_bitumen:,} MT

    **Bio-Bitumen Potential (15% replacement):**
    - Volume: **{total_bitumen * 0.15:,.0f} MT**
    - Revenue: **Rs {total_bitumen * 0.15 * 35000 / 10000000:.1f} Cr**

    **Your Supply Capacity:**
    - At {cfg['capacity_tpd']:.0f} TPD x 300 days = {cfg['capacity_tpd'] * 300:,.0f} MT/year
    - Market share possible: {min(cfg['capacity_tpd'] * 300 / total_bitumen * 100, 100):.1f}%
    """)

st.markdown("---")

# ── Export ────────────────────────────────────────────────────────────
csv = display_df.to_csv(index=False)
st.download_button("Download Tender Data (CSV)", csv, "nhai_tenders.csv", "text/csv")

st.markdown("---")
st.caption(f"{COMPANY['name']} | {COMPANY['owner']} | {COMPANY['phone']}")
