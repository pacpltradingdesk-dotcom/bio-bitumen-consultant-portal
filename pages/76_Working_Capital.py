"""
Working Capital Calculator — DPR Module
========================================
Reads from DPR cost sheet. Shows current assets, current liabilities,
net working capital requirement, and current ratio.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from state_manager import get_config, init_state, format_inr
from config import COMPANY
from engines.detailed_costing import calculate_complete_cost_sheet
from engines.dpr_financial_engine import calculate_working_capital

st.set_page_config(page_title="Working Capital", page_icon="💳", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.title("Working Capital Requirement Calculator")
st.markdown(f"**{cfg['capacity_tpd']:.0f} TPD plant in {cfg.get('state', 'Maharashtra')} — "
            f"All values computed from DPR cost sheet**")
st.markdown("---")

# Calculate
cs = calculate_complete_cost_sheet(cfg)
wc = calculate_working_capital(cfg, cs)

# ── KPIs ─────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Net Working Capital", format_inr(wc["net_working_capital"]),
          help="Current Assets minus Current Liabilities")
k2.metric("WC in Lakhs", f"₹ {wc['net_wc_lac']:.1f} Lac")
k3.metric("Current Ratio", f"{wc['current_ratio']:.2f}",
          delta="Healthy" if wc["current_ratio"] >= 1.5 else "Low",
          delta_color="normal" if wc["current_ratio"] >= 1.5 else "inverse")
k4.metric("WC % of Investment", f"{wc['wc_pct_of_investment']:.1f}%")

st.markdown("---")

# ── Detailed Breakdown ───────────────────────────────────────────────
st.subheader("Working Capital Components")

wc_rows = []
for item in wc["items"]:
    wc_rows.append({
        "Component": item["component"],
        "Days": item["days"],
        "Basis": item["basis"],
        "Amount ₹": format_inr(abs(item["amount"])),
        "Type": "Current Asset" if item["type"] == "asset" else "Current Liability",
    })
st.dataframe(pd.DataFrame(wc_rows), use_container_width=True, hide_index=True)

# Summary
st.markdown(f"""
| | Amount |
|---|---|
| **Total Current Assets** | **{format_inr(wc['total_current_assets'])}** |
| Less: Current Liabilities | -{format_inr(wc['total_current_liabilities'])} |
| **NET WORKING CAPITAL** | **{format_inr(wc['net_working_capital'])}** |
| Current Ratio | **{wc['current_ratio']:.2f}** |
""")

# ── Chart ────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    assets = [i for i in wc["items"] if i["type"] == "asset"]
    fig = go.Figure(data=[go.Bar(
        x=[i["component"] for i in assets],
        y=[i["amount"] for i in assets],
        marker_color=["#34d399", "#38bdf8", "#a78bfa", "#f59e0b", "#fb923c"],
    )])
    fig.update_layout(title="Current Assets Breakdown", template="plotly_white", height=350,
                      xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig2 = go.Figure(data=[go.Pie(
        labels=["Current Assets", "Current Liabilities"],
        values=[wc["total_current_assets"], wc["total_current_liabilities"]],
        hole=0.5,
        marker=dict(colors=["#34d399", "#ef4444"]),
    )])
    fig2.update_layout(title="Assets vs Liabilities", template="plotly_white", height=350)
    st.plotly_chart(fig2, use_container_width=True)

# ── Bank Requirement ─────────────────────────────────────────────────
st.markdown("---")
st.subheader("Bank Working Capital Facility")
margin_money = wc["net_working_capital"] * 0.25  # 25% margin
bank_limit = wc["net_working_capital"] * 0.75

st.markdown(f"""
| Parameter | Amount |
|---|---|
| Net Working Capital Requirement | {format_inr(wc['net_working_capital'])} |
| Margin Money (25%) | {format_inr(margin_money)} |
| **Bank CC/OD Limit Required** | **{format_inr(bank_limit)}** |
| Interest on CC @ 12% p.a. | {format_inr(bank_limit * 0.12)} per year |
""")

st.markdown("---")
if st.button("Print", key="prt_wc"):
    import streamlit.components.v1 as _stc
    _stc.html("<script>window.print();</script>", height=0)

st.caption(f"{COMPANY['name']} | Working Capital Calculator | Auto-linked to DPR Cost Sheet")
