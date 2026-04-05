"""
Bio Bitumen Master Consulting System — Location & Feasibility Module
====================================================================
State-wise feasibility scoring, subsidy tracking, logistics analysis.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
from config import STATES, STATE_SCORES, LOCATION_WEIGHTS
from state_manager import get_config, update_field, init_state

st.set_page_config(page_title="Location & Feasibility", page_icon="📍", layout="wide")
init_state()
try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass
st.sidebar.markdown("---")
if st.sidebar.button("Print This Page", key="print_page"):
    import streamlit.components.v1 as _stc; _stc.html('<script>window.print();</script>', height=0)

st.title("Location & Feasibility Analysis")
st.markdown("**Pan-India state-wise scoring for Bio-Bitumen plant setup**")
st.markdown("---")

# ── Calculate Scores ──────────────────────────────────────────────────
state_data = []
for state in STATES:
    scores = STATE_SCORES.get(state, {})
    total = sum(scores.get(k, 50) * LOCATION_WEIGHTS[k] for k in LOCATION_WEIGHTS)
    state_data.append({
        "State": state,
        "Biomass (25%)": scores.get("biomass", 50),
        "Subsidy (20%)": scores.get("subsidy", 50),
        "Logistics (20%)": scores.get("logistics", 50),
        "Power (15%)": scores.get("power", 50),
        "Land Cost (10%)": scores.get("land_cost", 50),
        "Season (10%)": scores.get("season", 50),
        "Total Score": round(total, 1),
        "Rating": "Excellent" if total >= 75 else "Good" if total >= 65 else "Fair" if total >= 55 else "Below Avg",
    })

df = pd.DataFrame(state_data).sort_values("Total Score", ascending=False)

# ── Top Metrics ───────────────────────────────────────────────────────
top3 = df.head(3)
c1, c2, c3 = st.columns(3)
for i, (_, row) in enumerate(top3.iterrows()):
    medals = ["1st", "2nd", "3rd"]
    with [c1, c2, c3][i]:
        st.metric(f"{medals[i]} Best State", row["State"], f"Score: {row['Total Score']}/100")

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────
tab_rank, tab_detail, tab_compare = st.tabs(["State Rankings", "State Detail", "Factor Analysis"])

with tab_rank:
    st.subheader("All 18 States — Ranked by Feasibility Score")

    # Color-coded bar chart
    fig = px.bar(df, x="State", y="Total Score", color="Rating",
                  color_discrete_map={"Excellent": "#006400", "Good": "#228B22", "Fair": "#FFA500", "Below Avg": "#CC3333"},
                  title="State-wise Feasibility Score (0-100)")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, width="stretch")

    # Full table
    st.dataframe(df, width="stretch", hide_index=True)

with tab_detail:
    st.subheader("State Detail View")
    selected_state = st.selectbox("Select State", options=STATES,
                                   index=STATES.index(get_config()["state"]) if get_config()["state"] in STATES else 0)

    state_row = df[df["State"] == selected_state].iloc[0] if not df[df["State"] == selected_state].empty else None
    if state_row is not None:
        st.markdown(f"### {selected_state} — Score: **{state_row['Total Score']}/100** ({state_row['Rating']})")

        d1, d2, d3 = st.columns(3)
        d1.metric("Biomass Availability", f"{state_row['Biomass (25%)']}/100")
        d2.metric("Govt Subsidy", f"{state_row['Subsidy (20%)']}/100")
        d3.metric("Logistics", f"{state_row['Logistics (20%)']}/100")

        d4, d5, d6 = st.columns(3)
        d4.metric("Power Availability", f"{state_row['Power (15%)']}/100")
        d5.metric("Land Cost (lower=better)", f"{state_row['Land Cost (10%)']}/100")
        d6.metric("Season Favorability", f"{state_row['Season (10%)']}/100")

        # Radar chart
        categories = ["Biomass", "Subsidy", "Logistics", "Power", "Land Cost", "Season"]
        values = [state_row[f"Biomass (25%)"], state_row[f"Subsidy (20%)"],
                  state_row[f"Logistics (20%)"], state_row[f"Power (15%)"],
                  state_row[f"Land Cost (10%)"], state_row[f"Season (10%)"]]
        fig_radar = px.line_polar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            title=f"{selected_state} — Factor Profile",
        )
        fig_radar.update_traces(fill="toself", fillcolor="rgba(0,51,102,0.2)", line_color="#003366")
        st.plotly_chart(fig_radar, width="stretch")

        if st.button(f"Set {selected_state} as project location"):
            update_field("state", selected_state)
            st.success(f"Project location set to {selected_state}")

with tab_compare:
    st.subheader("Factor-wise Comparison")

    factor = st.selectbox("Select Factor", ["Biomass (25%)", "Subsidy (20%)", "Logistics (20%)",
                                              "Power (15%)", "Land Cost (10%)", "Season (10%)"])
    fig_factor = px.bar(df.sort_values(factor, ascending=False), x="State", y=factor,
                         color=factor, color_continuous_scale="Greens",
                         title=f"{factor} — State Comparison")
    fig_factor.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_factor, width="stretch")

# ── Export Section ────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Export")
_ex1, _ex2 = st.columns(2)
with _ex1:
    try:
        import io as _io
        from openpyxl import Workbook as _Wb
        _wb = _Wb()
        _ws = _wb.active
        _ws.title = "Export"
        _ws.cell(row=1, column=1, value="Bio Bitumen Export")
        _ws.cell(row=2, column=1, value=f"Capacity: {cfg.get('capacity_tpd',20):.0f} TPD")
        _ws.cell(row=3, column=1, value=f"Investment: Rs {cfg.get('investment_cr',8):.2f} Cr")
        _ws.cell(row=4, column=1, value=f"ROI: {cfg.get('roi_pct',0):.1f}%")
        _buf = _io.BytesIO()
        _wb.save(_buf)
        _xl_data = _buf.getvalue()
    except Exception:
        _xl_data = None
    if _xl_data:
        st.download_button("Download Excel", _xl_data, "export.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_xl_05_📍_L", type="primary")
with _ex2:
    if st.button("Print Page", key="exp_print_analysis"):
        import streamlit.components.v1 as _stc
        _stc.html("<script>window.print();</script>", height=0)


# ── AI Skill: Site Selection Advice ──────────────────────────────────────
st.markdown("---")
try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("🤖 AI: Site Selection Advice"):
            if st.button("Generate", type="primary", key="ai_05📍Loc"):
                with st.spinner("AI working..."):
                    _p = f"As a senior bio-bitumen consultant, generate: Site Selection Advice. "
                    _p += f"Plant: {cfg.get('capacity_tpd',20):.0f} TPD, Investment: Rs {cfg.get('investment_cr',8):.2f} Cr, "
                    _p += f"Location: {cfg.get('location','')}, {cfg.get('state','')}. "
                    _p += "Be specific with numbers. Professional format."
                    _r, _pv = ask_ai(_p, "Senior industrial consultant.", 1000)
                if _r:
                    st.markdown(_r)
except Exception:
    pass
