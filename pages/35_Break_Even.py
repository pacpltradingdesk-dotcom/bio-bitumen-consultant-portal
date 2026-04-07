"""
Break-Even Analysis — DPR Module
==================================
Fixed vs Variable cost split, contribution margin, break-even tonnes/days/%,
price sensitivity scenarios, margin of safety.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from state_manager import get_config, init_state, format_inr
from config import COMPANY
from engines.detailed_costing import calculate_complete_cost_sheet
from engines.dpr_financial_engine import calculate_break_even

st.set_page_config(page_title="Break-Even Analysis", page_icon="⚖️", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.title("Break-Even Analysis")
st.markdown(f"**{cfg['capacity_tpd']:.0f} TPD plant | Fixed vs Variable cost split | "
            f"Contribution margin approach**")
st.markdown("---")

# Calculate
cs = calculate_complete_cost_sheet(cfg)
be = calculate_break_even(cfg, cs)

# ── KPIs ─────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Break-Even Tonnes/Year", f"{be['be_tonnes_annual']:,}",
          help="Annual production needed to cover all fixed costs")
k2.metric("Break-Even Days", f"{be['be_days']}",
          help="Operating days to reach break-even")
k3.metric("Break-Even %", f"{be['be_pct']:.1f}%",
          help="% of full capacity needed for break-even",
          delta="Viable" if be["be_pct"] < 80 else "Tight",
          delta_color="normal" if be["be_pct"] < 80 else "inverse")
k4.metric("Margin of Safety", f"{be['margin_of_safety']:.1f}%",
          delta="Strong" if be["margin_of_safety"] > 25 else "Weak",
          delta_color="normal" if be["margin_of_safety"] > 25 else "inverse")
k5.metric("Contribution/Tonne", f"₹{be['contribution_per_tonne']:,}")

st.info("**DPR Conservative Analysis:** This break-even uses full landed-cost method (conventional bitumen at "
        f"₹{cfg.get('price_conv_bitumen', 45750):,}/T + 18% GST + freight). The Financial Model page uses "
        "aggregated cost-per-MT method which shows a more favorable break-even. For bank presentations, "
        "present the Financial Model break-even alongside this DPR analysis for completeness.")
st.markdown("---")

tab_analysis, tab_scenarios, tab_chart = st.tabs([
    "📊 Cost Analysis", "📈 Price Scenarios", "📉 Break-Even Chart"
])

# ── TAB: COST ANALYSIS ──────────────────────────────────────────────
with tab_analysis:
    st.subheader("Fixed vs Variable Cost Split")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        | Parameter | Amount |
        |---|---|
        | **Fixed Costs (Annual)** | **{format_inr(be['fixed_costs_annual'])}** |
        | Variable Cost / Tonne | ₹{be['variable_per_tonne']:,} |
        | Effective Revenue / Tonne | ₹{be['effective_revenue_per_tonne']:,} |
        | **Contribution / Tonne** | **₹{be['contribution_per_tonne']:,}** |
        | Contribution Ratio | {be['contribution_ratio']:.3f} |
        """)

    with c2:
        st.markdown(f"""
        | Break-Even Metric | Value |
        |---|---|
        | BE Tonnes / Year | {be['be_tonnes_annual']:,} T |
        | BE Operating Days | {be['be_days']} days |
        | BE Capacity Utilization | {be['be_pct']:.1f}% |
        | Margin of Safety | {be['margin_of_safety']:.1f}% |
        | Min Selling Price | ₹{be['min_selling_price']:,}/T |
        | Full Cost / Tonne | ₹{be['total_cost_per_tonne']:,}/T |
        """)

    # Fixed vs Variable pie
    fig = go.Figure(data=[go.Pie(
        labels=["Fixed Costs", "Variable Costs"],
        values=[be["fixed_costs_annual"],
                be["variable_per_tonne"] * be["annual_output"]],
        hole=0.4,
        marker=dict(colors=["#ef4444", "#38bdf8"]),
    )])
    fig.update_layout(title="Annual Cost Structure — Fixed vs Variable",
                      template="plotly_white", height=300)
    st.plotly_chart(fig, use_container_width=True)

# ── TAB: PRICE SCENARIOS ────────────────────────────────────────────
with tab_scenarios:
    st.subheader("Break-Even at Different Selling Prices")
    st.caption("How break-even changes when selling price moves ±10% to ±20%")

    sc_rows = []
    for sc in be["price_scenarios"]:
        sc_rows.append({
            "Price Change": sc["price_change"],
            "Selling Price ₹/T": f"₹{sc['selling_price']:,}",
            "BE Tonnes/Year": f"{sc['be_tonnes']:,}",
            "BE Capacity %": f"{sc['be_pct']:.1f}%",
            "Viable?": "✅ Yes" if sc["viable"] else "❌ No",
        })
    st.dataframe(pd.DataFrame(sc_rows), use_container_width=True, hide_index=True)

    # Chart
    fig2 = go.Figure()
    viable_colors = ["#ef4444" if not s["viable"] else "#34d399" for s in be["price_scenarios"]]
    fig2.add_trace(go.Bar(
        x=[s["price_change"] for s in be["price_scenarios"]],
        y=[s["be_pct"] for s in be["price_scenarios"]],
        marker_color=viable_colors,
        text=[f"{s['be_pct']:.0f}%" for s in be["price_scenarios"]],
        textposition="outside",
    ))
    fig2.add_hline(y=100, line_dash="dash", line_color="red",
                   annotation_text="100% = Not Viable")
    fig2.update_layout(title="Break-Even % at Different Sale Prices",
                       xaxis_title="Price Change", yaxis_title="BE Capacity %",
                       template="plotly_white", height=350)
    st.plotly_chart(fig2, use_container_width=True)

# ── TAB: BREAK-EVEN CHART ───────────────────────────────────────────
with tab_chart:
    st.subheader("Break-Even Point — Revenue vs Cost")

    # Generate data points
    max_output = be["annual_output"] * 1.2
    x_vals = [i * max_output / 20 for i in range(21)]

    fixed = be["fixed_costs_annual"]
    var_per_t = be["variable_per_tonne"]
    rev_per_t = be["effective_revenue_per_tonne"]

    total_costs = [fixed + var_per_t * x for x in x_vals]
    total_revenue = [rev_per_t * x for x in x_vals]

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=x_vals, y=total_revenue, name="Total Revenue",
                              line=dict(color="#34d399", width=3)))
    fig3.add_trace(go.Scatter(x=x_vals, y=total_costs, name="Total Cost",
                              line=dict(color="#ef4444", width=3)))
    fig3.add_trace(go.Scatter(x=x_vals, y=[fixed] * len(x_vals), name="Fixed Cost",
                              line=dict(color="#f59e0b", width=2, dash="dot")))

    # Mark break-even point
    if be["be_tonnes_annual"] < max_output:
        be_rev = rev_per_t * be["be_tonnes_annual"]
        fig3.add_trace(go.Scatter(
            x=[be["be_tonnes_annual"]], y=[be_rev],
            mode="markers+text",
            marker=dict(size=15, color="#a78bfa", symbol="diamond"),
            text=[f"BE: {be['be_tonnes_annual']:,} T"],
            textposition="top right",
            name="Break-Even Point",
        ))

    fig3.update_layout(
        title="Break-Even Chart",
        xaxis_title="Annual Output (Tonnes)",
        yaxis_title="₹",
        template="plotly_white", height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
if st.button("Print", key="prt_be"):
    import streamlit.components.v1 as _stc
    _stc.html("<script>window.print();</script>", height=0)

st.caption(f"{COMPANY['name']} | Break-Even Analysis | Auto-linked to DPR Cost Sheet")


# ── Next Steps Navigation ──
try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "35")
except Exception:
    pass
