"""
Analytics Dashboard — UPGRADED with time-series, revenue forecast,
geographic distribution, executive summary, and export capabilities.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from state_manager import init_state, get_config
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
from database import (init_db, get_all_customers, get_all_packages,
                       get_all_communications, get_customer_count_by_status,
                       get_package_stats, get_communication_stats, get_events,
                       get_report_generations)
from config import CUSTOMER_STATUSES, CAPACITY_LABELS, INDUSTRY_NETWORK, STATES, NHAI_TENDERS
from engines.auto_doc_sync import get_sync_log

st.set_page_config(page_title="Analytics & BI", page_icon="📊", layout="wide")
init_state()
cfg = get_config()
init_db()
st.title("Analytics & Business Intelligence")
st.markdown("**Pipeline | Revenue Forecast | Conversion | Geographic | Executive Summary**")
st.markdown("---")

customers = get_all_customers()
packages = get_all_packages()
comms = get_all_communications()
status_counts = get_customer_count_by_status()
pkg_stats = get_package_stats()
comm_stats = get_communication_stats()

# ══════════════════════════════════════════════════════════════════════
# TOP METRICS (with trend indicators)
# ══════════════════════════════════════════════════════════════════════
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Total Customers", len(customers))
m2.metric("Packages Created", pkg_stats["total"])
m3.metric("Communications", comm_stats["total"])
active = sum(1 for c in customers if c.get("status") not in ("Closed Won", "Closed Lost"))
m4.metric("Active Pipeline", active)
won = sum(1 for c in customers if c.get("status") == "Closed Won")
m5.metric("Closed Won", won)
conv_rate = f"{won/len(customers)*100:.0f}%" if customers else "0%"
m6.metric("Conversion Rate", conv_rate)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY (Auto-generated text)
# ══════════════════════════════════════════════════════════════════════
st.subheader("Executive Summary")

total_pipeline_cr = sum(float(c.get("budget_cr", 0) or 0) for c in customers if c.get("status") not in ("Closed Won", "Closed Lost"))
won_value_cr = sum(float(c.get("budget_cr", 0) or 0) for c in customers if c.get("status") == "Closed Won")

# Weighted pipeline (probability by stage)
stage_prob = {"New": 0.10, "Contacted": 0.20, "Proposal Sent": 0.40, "Follow-up": 0.50,
              "Negotiation": 0.70, "Closed Won": 1.0, "Closed Lost": 0.0}
weighted_pipeline = sum(float(c.get("budget_cr", 0) or 0) * stage_prob.get(c.get("status", "New"), 0.1) for c in customers)

# NHAI opportunity
open_tenders = [t for t in NHAI_TENDERS if t["status"] == "Open"]
total_tender_budget = sum(t["budget_cr"] for t in open_tenders)
total_tender_bitumen = sum(t["bitumen_mt"] for t in open_tenders)

exec_col1, exec_col2 = st.columns([2, 1])
with exec_col1:
    st.markdown(f"""
    **Pipeline Overview:**
    - **{len(customers)}** total customers in CRM | **{active}** active in pipeline
    - Pipeline Value: **Rs {total_pipeline_cr:.1f} Cr** | Weighted: **Rs {weighted_pipeline:.1f} Cr**
    - Won Revenue: **Rs {won_value_cr:.1f} Cr** | Conversion: **{conv_rate}**
    - Communications Sent: **{comm_stats['total']}** ({comm_stats.get('email', 0)} emails, {comm_stats.get('whatsapp', 0)} WhatsApp)

    **Market Opportunity:**
    - **{len(open_tenders)}** NHAI/PWD tenders open worth **Rs {total_tender_budget:,} Cr**
    - Bitumen demand from tenders: **{total_tender_bitumen:,} MT**
    - Industry network: **{INDUSTRY_NETWORK['total']:,}** contacts across India
    """)

with exec_col2:
    # Pipeline value gauge
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=weighted_pipeline,
        title={"text": "Weighted Pipeline (Rs Cr)"},
        gauge={"axis": {"range": [0, max(total_pipeline_cr * 1.5, 10)]},
               "bar": {"color": "#003366"},
               "steps": [{"range": [0, total_pipeline_cr * 0.3], "color": "#ffcccc"},
                          {"range": [total_pipeline_cr * 0.3, total_pipeline_cr * 0.7], "color": "#ffffcc"},
                          {"range": [total_pipeline_cr * 0.7, total_pipeline_cr * 1.5], "color": "#ccffcc"}]},
    ))
    fig_gauge.update_layout(height=250, margin=dict(t=60, b=10))
    st.plotly_chart(fig_gauge, width="stretch")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# SALES FUNNEL + REVENUE FORECAST
# ══════════════════════════════════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales Funnel")
    if status_counts:
        funnel_data = [{"Status": s, "Count": status_counts.get(s, 0)} for s in CUSTOMER_STATUSES]
        fig = go.Figure(go.Funnel(
            y=[d["Status"] for d in funnel_data],
            x=[d["Count"] for d in funnel_data],
            textinfo="value+percent initial",
            marker=dict(color=["#003366", "#004c8c", "#006699", "#0088cc", "#00aadd", "#00cc44", "#cc4444"]),
        ))
        fig.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Add customers to see funnel")

with col2:
    st.subheader("Revenue Pipeline Forecast")
    if customers:
        stage_data = []
        for status in CUSTOMER_STATUSES:
            cust_in_stage = [c for c in customers if c.get("status") == status]
            total_budget = sum(float(c.get("budget_cr", 0) or 0) for c in cust_in_stage)
            prob = stage_prob.get(status, 0.1)
            stage_data.append({
                "Stage": status,
                "Total Value (Cr)": round(total_budget, 1),
                "Weighted Value (Cr)": round(total_budget * prob, 1),
                "Count": len(cust_in_stage),
                "Probability": f"{prob*100:.0f}%",
            })
        stage_df = pd.DataFrame(stage_data)

        fig_rev = go.Figure()
        fig_rev.add_trace(go.Bar(x=stage_df["Stage"], y=stage_df["Total Value (Cr)"],
                                  name="Total Value", marker_color="#003366", opacity=0.4))
        fig_rev.add_trace(go.Bar(x=stage_df["Stage"], y=stage_df["Weighted Value (Cr)"],
                                  name="Weighted Value", marker_color="#006699"))
        fig_rev.update_layout(title="Pipeline Value by Stage (Rs Cr)", barmode="overlay",
                               template="plotly_white", height=400)
        st.plotly_chart(fig_rev, width="stretch")
    else:
        st.info("Add customers to see revenue forecast")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# GEOGRAPHIC DISTRIBUTION + CAPACITY INTEREST
# ══════════════════════════════════════════════════════════════════════
geo_col, cap_col = st.columns(2)

with geo_col:
    st.subheader("Customer Geographic Distribution")
    if customers:
        state_dist = {}
        for c in customers:
            s = c.get("state", "Unknown")
            state_dist[s] = state_dist.get(s, 0) + 1
        geo_df = pd.DataFrame([{"State": k, "Customers": v} for k, v in state_dist.items()])
        geo_df = geo_df.sort_values("Customers", ascending=False)

        fig_geo = px.bar(geo_df, x="State", y="Customers", color="Customers",
                          title="Customers by State", color_continuous_scale="Blues")
        fig_geo.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig_geo, width="stretch")
    else:
        st.info("Add customers with state data to see distribution")

with cap_col:
    st.subheader("Capacity Interest Distribution")
    if customers:
        cap_dist = {}
        for c in customers:
            cap = c.get("interested_capacity", "Unknown")
            cap_dist[cap] = cap_dist.get(cap, 0) + 1
        cap_df = pd.DataFrame([{"Capacity": k, "Count": v} for k, v in cap_dist.items()])

        fig_cap = px.pie(cap_df, names="Capacity", values="Count",
                          title="Interest by Plant Capacity",
                          color_discrete_sequence=["#003366", "#006699", "#0088cc", "#00aadd",
                                                    "#FF8800", "#CC3333", "#00AA44"])
        fig_cap.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig_cap, width="stretch")
    else:
        st.info("Add customers to see capacity distribution")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# INDUSTRY NETWORK + TENDER OPPORTUNITY
# ══════════════════════════════════════════════════════════════════════
net_col, tender_col = st.columns(2)

with net_col:
    st.subheader("Industry Network")
    net = INDUSTRY_NETWORK
    net_df = pd.DataFrame([{"Category": k.title(), "Count": v} for k, v in net.items() if k != "total"])
    fig_net = px.bar(net_df, x="Category", y="Count", color="Count", text="Count",
                      title=f"Live Network: {net['total']:,} Contacts", color_continuous_scale="Blues")
    fig_net.update_traces(textposition="outside")
    fig_net.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig_net, width="stretch")

with tender_col:
    st.subheader("NHAI Tender Opportunity Map")
    tender_by_state = {}
    for t in open_tenders:
        s = t["state"]
        tender_by_state[s] = tender_by_state.get(s, 0) + t["budget_cr"]
    tender_df = pd.DataFrame([{"State": k, "Total Budget (Cr)": v} for k, v in tender_by_state.items()])
    tender_df = tender_df.sort_values("Total Budget (Cr)", ascending=True)

    fig_tender = px.bar(tender_df, y="State", x="Total Budget (Cr)", orientation="h",
                         title=f"{len(open_tenders)} Open Tenders by State",
                         color="Total Budget (Cr)", color_continuous_scale="Reds")
    fig_tender.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig_tender, width="stretch")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# COMMUNICATION EFFECTIVENESS + DOCUMENT SYNC
# ══════════════════════════════════════════════════════════════════════
comm_col, sync_col = st.columns(2)

with comm_col:
    st.subheader("Communication Channel Mix")
    if comms:
        channel_counts = {}
        for c in comms:
            ch = c.get("channel", "Email")
            channel_counts[ch] = channel_counts.get(ch, 0) + 1
        ch_df = pd.DataFrame([{"Channel": k, "Count": v} for k, v in channel_counts.items()])
        fig_ch = px.pie(ch_df, names="Channel", values="Count", title="Messages by Channel",
                         color_discrete_sequence=["#003366", "#00AA44", "#FF8800"])
        fig_ch.update_layout(template="plotly_white", height=350)
        st.plotly_chart(fig_ch, width="stretch")
    else:
        st.info("Send communications to see channel distribution")

with sync_col:
    st.subheader("Auto-Generated Documents")
    sync_log = get_sync_log()
    reports = get_report_generations(limit=10)

    if reports:
        st.markdown("**Recent DPR/Reports:**")
        for r in reports[:5]:
            st.markdown(f"- **{r['report_type']}** — {r.get('capacity_tpd', 0):.0f} MT — {r['created_at']}")
    else:
        st.info("No reports generated yet")

    if sync_log:
        st.markdown("**Auto-Sync Log:**")
        for s in sync_log[-5:]:
            st.markdown(f"- {s.get('time', '')} — {s.get('capacity', 0):.0f} MT — {s.get('files_generated', 0)} files")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# ACTIVITY FEED
# ══════════════════════════════════════════════════════════════════════
st.subheader("Recent Activity Feed")
events = get_events(limit=20)
if events:
    events_df = pd.DataFrame([{
        "Time": e.get("created_at", ""),
        "Event": e.get("event_type", "").replace("_", " ").title(),
        "Details": str(e.get("details", {}))[:80]
    } for e in events])
    st.dataframe(events_df, width="stretch", hide_index=True, height=300)
else:
    st.info("Activity will appear as you use the system")

# ══════════════════════════════════════════════════════════════════════
# EXPORT
# ══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Export Analytics")

exp1, exp2 = st.columns(2)
with exp1:
    if customers:
        cust_df = pd.DataFrame(customers)
        csv = cust_df.to_csv(index=False)
        st.download_button("Download Customer Data (CSV)", csv, "customers_export.csv", "text/csv")
    else:
        st.info("No customer data to export")

with exp2:
    # Summary report text
    summary = f"""Bio Bitumen Analytics Report — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
================================================================================

PIPELINE SUMMARY
- Total Customers: {len(customers)}
- Active Pipeline: {active}
- Closed Won: {won}
- Conversion Rate: {conv_rate}
- Pipeline Value: Rs {total_pipeline_cr:.1f} Cr
- Weighted Pipeline: Rs {weighted_pipeline:.1f} Cr
- Won Revenue: Rs {won_value_cr:.1f} Cr

COMMUNICATIONS
- Total Sent: {comm_stats['total']}
- Packages Created: {pkg_stats['total']}

MARKET OPPORTUNITY
- Open NHAI Tenders: {len(open_tenders)}
- Tender Value: Rs {total_tender_budget:,} Cr
- Bitumen Demand: {total_tender_bitumen:,} MT
- Industry Network: {INDUSTRY_NETWORK['total']:,} contacts

Generated by PPS Anantams Bio Bitumen Consulting System
"""
    st.download_button("Download Summary Report (TXT)", summary, "analytics_report.txt", "text/plain")

st.markdown("---")
st.caption("PPS Anantams Corporation | Analytics & Business Intelligence")


# ── AI Skill: Business Insights ──────────────────────────────────────
st.markdown("---")
try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("🤖 AI: Business Insights"):
            if st.button("Generate", type="primary", key="ai_45Analy"):
                with st.spinner("AI working..."):
                    _p = f"As a senior bio-bitumen consultant, generate: Business Insights. "
                    _p += f"Plant: {cfg.get('capacity_tpd',20):.0f} TPD, Investment: Rs {cfg.get('investment_cr',8):.2f} Cr, "
                    _p += f"Location: {cfg.get('location','')}, {cfg.get('state','')}. "
                    _p += "Be specific with numbers. Professional format."
                    _r, _pv = ask_ai(_p, "Senior industrial consultant.", 1000)
                if _r:
                    st.markdown(_r)
except Exception:
    pass
