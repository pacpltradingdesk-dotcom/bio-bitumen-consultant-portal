"""
Detailed Costing — Complete Cost-Per-Tonne Bifurcation
=======================================================
Landing cost, waste, packing, scrap, location multipliers, cost sheet.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from state_manager import get_config, init_state
from config import COMPANY
from engines.detailed_costing import (
    calculate_complete_cost_sheet, calculate_landing_cost,
    calculate_waste_costs, calculate_packing_costs,
    calculate_scrap_revenue, LOCATION_MULTIPLIERS, get_multiplier
)

st.set_page_config(page_title="Detailed Costing", page_icon="📊", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.title("Detailed Costing — Cost Per Tonne Bifurcation")
st.markdown(f"**Complete cost breakdown for {cfg['capacity_tpd']:.0f} TPD plant in {cfg.get('state', 'Maharashtra')}**")
st.markdown("---")

# Calculate everything
cs = calculate_complete_cost_sheet(cfg)

# ══════════════════════════════════════════════════════════════════════
# TOP KPIs
# ══════════════════════════════════════════════════════════════════════
k1, k2, k3, k4 = st.columns(4)
k1.metric("Net Cost/Tonne", f"₹{cs['net_cpt']:,}",
          help="All-in cost per tonne of bio-bitumen blend after by-product credits")
k2.metric("Sale Price/Tonne", f"₹{cs['sale_price_pt']:,}")
k3.metric("Margin/Tonne", f"₹{cs['margin_pt']:,}",
          delta=f"{cs['margin_pct']:.1f}%",
          delta_color="normal" if cs['margin_pt'] > 0 else "inverse")
k4.metric("Daily Revenue", f"₹{cs['total_rev_daily']:,}")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# 6 TABS
# ══════════════════════════════════════════════════════════════════════
tab_sheet, tab_landing, tab_waste, tab_packing, tab_scrap, tab_location = st.tabs([
    "📊 Cost Sheet", "🚛 Landing Cost", "♻️ Waste & Loss",
    "📦 Packing", "💰 Scrap Revenue", "📍 Location Multipliers"
])

# ── TAB: COST SHEET ──────────────────────────────────────────────────
with tab_sheet:
    st.subheader("Complete Cost Sheet — ₹ per Tonne of Bio-Bitumen Blend")
    st.caption(f"Location: {cs['state']} | Output: {cs['blend_total_tpd']} T/day blend | {cfg['capacity_tpd']:.0f} TPD feed")

    # Cost breakdown table
    rows = []
    for i, (head, daily_cost) in enumerate(cs["cost_heads"], 1):
        cpt = daily_cost / cs["blend_total_tpd"] if cs["blend_total_tpd"] > 0 else 0
        pct = cpt / (cs["gross_daily"] / cs["blend_total_tpd"]) * 100 if cs["gross_daily"] > 0 else 0
        rows.append({"#": i, "Cost Head": head, "Daily ₹": f"₹{daily_cost:,.0f}",
                      "₹/Tonne": f"₹{cpt:,.0f}", "% of Total": f"{pct:.1f}%"})

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    # Summary
    d = cs["blend_total_tpd"] if cs["blend_total_tpd"] > 0 else 1
    st.markdown(f"""
    | | Amount |
    |---|---|
    | **GROSS COST / Tonne** | **₹{cs['gross_daily']/d:,.0f}** |
    | Less: By-product Credits | -₹{cs['by_product_credit']/d:,.0f} |
    | Less: Scrap Income | -₹{cs['scrap_total']/d:,.0f} |
    | **NET COST / Tonne** | **₹{cs['net_cpt']:,}** |
    | Sale Price | ₹{cs['sale_price_pt']:,} |
    | **MARGIN / Tonne** | **₹{cs['margin_pt']:,} ({cs['margin_pct']:.1f}%)** |
    """)

    # Cost breakdown pie chart
    fig = go.Figure(data=[go.Pie(
        labels=[h for h, _ in cs["cost_heads"]],
        values=[c for _, c in cs["cost_heads"]],
        hole=0.4,
        marker=dict(colors=["#f59e0b", "#ef4444", "#38bdf8", "#a78bfa", "#34d399",
                             "#fb923c", "#64748b", "#f472b6", "#94a3b8", "#4ade80"]),
    )])
    fig.update_layout(title="Cost Breakdown", template="plotly_white", height=350)
    st.plotly_chart(fig, width="stretch")

# ── TAB: LANDING COST ────────────────────────────────────────────────
with tab_landing:
    st.subheader("Agro Waste Landing Cost — Farm Gate to Plant Gate")
    st.caption(f"Location: {cs['state']} | Transport multiplier: {cs['multiplier']['tr_in']:.2f}x")

    landing = cs["landing"]
    landing_rows = []
    for name, cost, editable in landing["items"]:
        landing_rows.append({"Component": name, "₹/Tonne Feed": f"₹{cost:,.0f}"})

    st.dataframe(pd.DataFrame(landing_rows), width="stretch", hide_index=True)
    st.metric("TOTAL Landing Cost", f"₹{landing['total']:,}/tonne", help="Per tonne of agro waste at plant gate")

# ── TAB: WASTE & LOSS ────────────────────────────────────────────────
with tab_waste:
    st.subheader("Waste, Rejection & Process Losses")

    waste = cs["waste"]
    waste_rows = []
    for name, stage, pct, tonnes, cost in waste["items"]:
        waste_rows.append({"Loss Type": name, "Stage": stage, "% of Input": f"{pct}%",
                            "T/day": f"{tonnes:.2f}", "Daily Cost ₹": f"₹{cost:,.0f}"})

    st.dataframe(pd.DataFrame(waste_rows), width="stretch", hide_index=True)
    st.metric("Total Waste Cost/Day", f"₹{waste['total']:,}")
    st.caption("These costs are absorbed into the product cost — they increase your effective cost per tonne")

# ── TAB: PACKING ─────────────────────────────────────────────────────
with tab_packing:
    st.subheader("Packing Cost Matrix — Net of Scrap Value")

    packing = cs["packing"]
    pack_rows = []
    for product, pack_type, cost, scrap, net, desc, units in packing["items"]:
        pack_rows.append({"Product": product, "Pack Type": pack_type,
                           "Pack Cost ₹": cost, "Scrap Value ₹": scrap,
                           "Net ₹/unit": net, "Units/day": units,
                           "Daily ₹": f"₹{net * units:,}"})

    st.dataframe(pd.DataFrame(pack_rows), width="stretch", hide_index=True)
    st.metric("Total Packing Cost/Day", f"₹{packing['total']:,}")

# ── TAB: SCRAP REVENUE ───────────────────────────────────────────────
with tab_scrap:
    st.subheader("Scrap & By-Product Revenue")
    st.caption("These credits REDUCE your effective cost of production")

    scrap = cs["scrap"]
    scrap_rows = []
    for item, qty, price, income, buyer in scrap["items"]:
        scrap_rows.append({"Item": item, "Qty/day": qty, "Rate ₹": f"₹{price:,}",
                            "Daily Income ₹": f"₹{income:,}", "Buyer": buyer})

    st.dataframe(pd.DataFrame(scrap_rows), width="stretch", hide_index=True)
    st.metric("Total Scrap Income/Day", f"₹{scrap['total']:,}")

# ── TAB: LOCATION MULTIPLIERS ───────────────────────────────────────
with tab_location:
    st.subheader("Location Cost Multipliers — 9 States")
    st.caption("Select different location to see cost impact across all parameters")

    loc_rows = []
    for state_name, mult in LOCATION_MULTIPLIERS.items():
        loc_rows.append({
            "State": state_name,
            "Raw Material": f"{mult['rm']:.2f}x",
            "Labour": f"{mult['lb']:.2f}x",
            "Transport In": f"{mult['tr_in']:.2f}x",
            "Transport Out": f"{mult['tr_out']:.2f}x",
            "Energy": f"{mult['energy']:.2f}x",
        })

    st.dataframe(pd.DataFrame(loc_rows), width="stretch", hide_index=True)

    # Current state highlight
    current_mult = cs["multiplier"]
    st.info(f"**Current: {cs['state']}** — RM: {current_mult['rm']:.2f}x | Labour: {current_mult['lb']:.2f}x | "
            f"Transport: {current_mult['tr_in']:.2f}x | Energy: {current_mult['energy']:.2f}x")

# ── Export + Print ───────────────────────────────────────────────────
st.markdown("---")
ex1, ex2 = st.columns(2)
with ex1:
    if st.button("Download Cost Sheet Excel", type="primary", key="dl_cost_xl"):
        import io
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Cost Sheet"
        ws.cell(row=1, column=1, value="Bio-Bitumen Cost Sheet")
        ws.cell(row=2, column=1, value=f"Capacity: {cfg['capacity_tpd']:.0f} TPD | State: {cs['state']}")
        for i, (head, cost) in enumerate(cs["cost_heads"], 4):
            ws.cell(row=i, column=1, value=head)
            ws.cell(row=i, column=2, value=round(cost))
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        st.download_button("Download", buf.getvalue(), "Detailed_Cost_Sheet.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_cs_xl")
with ex2:
    if st.button("Print", key="prt_cost"):
        import streamlit.components.v1 as _stc
        _stc.html("<script>window.print();</script>", height=0)

st.markdown("---")
st.caption(f"{COMPANY['name']} | Detailed Costing Engine | All values auto-update from project config")
