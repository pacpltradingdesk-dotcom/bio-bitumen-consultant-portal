"""
5-Year Cash Flow & Sensitivity — DPR Module
=============================================
Capacity ramp-up (60→95%), annual P&L projection, cumulative cash flow,
payback tracking, and 6-variable sensitivity stress test.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from state_manager import get_config, init_state, format_inr
from config import COMPANY
from engines.detailed_costing import calculate_complete_cost_sheet
from engines.dpr_financial_engine import calculate_5year_cashflow, calculate_sensitivity

st.set_page_config(page_title="5-Year Cash Flow & Sensitivity", page_icon="📉", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.title("5-Year Cash Flow Projection & Sensitivity Analysis")
st.markdown(f"**{cfg['capacity_tpd']:.0f} TPD | Capacity Ramp-Up: 60% → 75% → 85% → 90% → 95%**")
st.markdown("---")

# Calculate
cs = calculate_complete_cost_sheet(cfg)
cf = calculate_5year_cashflow(cfg, cs)

# ── KPIs ─────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Investment", f"₹ {cf['total_investment_cr']:.2f} Cr")
k2.metric("Payback Year", f"Year {cf['payback_year']}")
k3.metric("5-Year Total PAT", f"₹ {cf['total_pat_5yr_cr']:.2f} Cr")
k4.metric("Avg Annual ROI", f"{cf['avg_annual_roi']:.1f}%")
k5.metric("Year 5 PAT", f"₹ {cf['year5_pat_cr']:.2f} Cr")

st.markdown("---")

tab_cf, tab_sensitivity = st.tabs(["📊 5-Year Cash Flow", "🔬 Sensitivity Analysis"])

# ── TAB: 5-YEAR CASH FLOW ───────────────────────────────────────────
with tab_cf:
    st.subheader("Year-wise P&L with Capacity Ramp-Up")

    cf_rows = []
    for yr in cf["years"]:
        cf_rows.append({
            "Year": yr["year"],
            "Utilization": yr["utilization_pct"],
            "Revenue (Cr)": f"₹ {yr['revenue_cr']:.2f}",
            "EBITDA (Cr)": f"₹ {yr['ebitda_cr']:.2f}",
            "PAT (Cr)": f"₹ {yr['pat_cr']:.2f}",
            "Free CF (Cr)": f"₹ {yr['free_cf']/1e7:.2f}",
            "Cumulative CF (Cr)": f"₹ {yr['cumulative_cf_cr']:.2f}",
        })
    st.dataframe(pd.DataFrame(cf_rows), use_container_width=True, hide_index=True)

    # Detailed P&L table
    with st.expander("Detailed Year-wise P&L"):
        detail_rows = []
        for yr in cf["years"]:
            detail_rows.append({
                "Year": yr["year"],
                "Util %": yr["utilization_pct"],
                "Revenue": format_inr(yr["revenue"]),
                "Total Cost": format_inr(yr["total_cost"]),
                "Gross Profit": format_inr(yr["gross_profit"]),
                "Gross %": f"{yr['gross_margin_pct']:.1f}%",
                "Depreciation": format_inr(yr["depreciation"]),
                "Interest": format_inr(yr["interest"]),
                "EBT": format_inr(yr["ebt"]),
                "Tax": format_inr(yr["tax"]),
                "PAT": format_inr(yr["pat"]),
            })
        st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        years_x = [f"Year {y['year']}" for y in cf["years"]]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=years_x, y=[y["revenue_cr"] for y in cf["years"]],
                             name="Revenue", marker_color="#38bdf8"))
        fig.add_trace(go.Bar(x=years_x, y=[y["ebitda_cr"] for y in cf["years"]],
                             name="EBITDA", marker_color="#34d399"))
        fig.add_trace(go.Bar(x=years_x, y=[y["pat_cr"] for y in cf["years"]],
                             name="PAT", marker_color="#a78bfa"))
        fig.update_layout(title="5-Year Revenue, EBITDA & PAT (₹ Cr)",
                          template="plotly_white", height=350, barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=years_x, y=[y["cumulative_cf_cr"] for y in cf["years"]],
            mode="lines+markers+text",
            line=dict(color="#f59e0b", width=3),
            marker=dict(size=10),
            text=[f"₹{y['cumulative_cf_cr']:.1f}Cr" for y in cf["years"]],
            textposition="top center",
            name="Cumulative CF",
        ))
        fig2.add_hline(y=0, line_dash="dash", line_color="red",
                       annotation_text="Break-Even Line")
        fig2.update_layout(title="Cumulative Cash Flow (₹ Cr)",
                           template="plotly_white", height=350)
        st.plotly_chart(fig2, use_container_width=True)

    # Capacity ramp-up chart
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=years_x,
        y=[y["utilization"] * 100 for y in cf["years"]],
        marker_color=["#fbbf24", "#f59e0b", "#34d399", "#22c55e", "#16a34a"],
        text=[y["utilization_pct"] for y in cf["years"]],
        textposition="inside",
    ))
    fig3.update_layout(title="Capacity Utilization Ramp-Up",
                       yaxis_title="%", template="plotly_white", height=250,
                       yaxis=dict(range=[0, 110]))
    st.plotly_chart(fig3, use_container_width=True)

# ── TAB: SENSITIVITY ANALYSIS ───────────────────────────────────────
with tab_sensitivity:
    st.subheader("6-Variable Sensitivity Stress Test (±10%, ±20%, ±30%)")
    st.caption("Impact on Annual Net Profit when each variable changes independently")

    with st.spinner("Running sensitivity analysis (6 variables × 6 stress levels)..."):
        sens = calculate_sensitivity(cfg, cs)

    st.markdown(f"**Base Case:** Net Profit = {format_inr(sens['base_profit'])} | "
                f"Cost/Tonne = ₹{sens['base_cpt']:,} | Margin = {sens['base_margin']:.1f}%")
    st.markdown("---")

    for var in sens["variables"]:
        st.markdown(f"**{var['variable']}** (Base: ₹{var['base_value']:,})")

        sc_rows = []
        for sc in var["scenarios"]:
            color = "🟢" if sc["better"] else "🔴"
            sc_rows.append({
                "Stress": f"{sc['stress_pct']:+d}%",
                "Value": f"₹{sc['stressed_value']:,}",
                "Net Profit": format_inr(sc["net_profit"]),
                "Change": f"{sc['profit_change_pct']:+.1f}%",
                "Impact": color,
                "Cost/T": f"₹{sc['cost_per_tonne']:,}",
                "Margin": f"{sc['margin_pct']:.1f}%",
            })
        st.dataframe(pd.DataFrame(sc_rows), use_container_width=True, hide_index=True)

    # Tornado chart (impact at ±30%)
    st.markdown("---")
    st.subheader("Tornado Chart — Impact at ±30% Change")

    tornado_data = []
    for var in sens["variables"]:
        neg30 = next((s for s in var["scenarios"] if s["stress_pct"] == -30), None)
        pos30 = next((s for s in var["scenarios"] if s["stress_pct"] == 30), None)
        if neg30 and pos30:
            tornado_data.append({
                "variable": var["variable"],
                "low": neg30["profit_change"],
                "high": pos30["profit_change"],
                "range": abs(pos30["profit_change"] - neg30["profit_change"]),
            })

    tornado_data.sort(key=lambda x: x["range"], reverse=True)

    fig4 = go.Figure()
    labels = [t["variable"] for t in tornado_data]
    fig4.add_trace(go.Bar(
        y=labels, x=[t["low"] for t in tornado_data],
        orientation="h", name="-30%", marker_color="#ef4444",
    ))
    fig4.add_trace(go.Bar(
        y=labels, x=[t["high"] for t in tornado_data],
        orientation="h", name="+30%", marker_color="#34d399",
    ))
    fig4.update_layout(
        title="Tornado Chart — Profit Impact at ±30%",
        xaxis_title="Change in Net Profit (₹)",
        template="plotly_white", height=400, barmode="relative",
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
if st.button("Print", key="prt_cf"):
    import streamlit.components.v1 as _stc
    _stc.html("<script>window.print();</script>", height=0)

st.caption(f"{COMPANY['name']} | 5-Year Cash Flow & Sensitivity | Auto-linked to DPR Cost Sheet")
