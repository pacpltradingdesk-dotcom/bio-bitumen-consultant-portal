"""
91 · Scenario Comparison — Side-by-Side Project Analysis
==========================================================
Compare up to 4 capacity scenarios: Pilot / Small / Medium / Large
Shows: IRR, ROI, Break-even, Investment, Revenue, Profit in radar + bar charts.
"""
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import init_state, get_config, DEFAULTS
from engines.scenario_engine import run_scenarios, load_scenarios, OUTPUT_KEYS, DEFAULT_SCENARIOS
from config import COMPANY

st.set_page_config(page_title="Scenario Compare · Bio Bitumen", page_icon="🔄", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#15130F;}
[data-testid="stSidebar"]{background:#1A1710;}
h1,h2,h3,h4,label,.stMarkdown p{color:#F0E6D3;}
[data-testid="stMetricValue"]{color:#E8B547 !important;}
[data-testid="stMetricLabel"]{color:#B09060 !important;}
.stButton>button{background:#E8B547;color:#15130F;font-weight:700;
  border:none;border-radius:6px;}
.stButton>button:hover{background:#F5C842;}
.best-tag{background:#1B3A25;color:#51CF66;padding:2px 10px;
  border-radius:10px;font-size:12px;font-weight:700;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="color:#E8B547;margin-bottom:2px;">🔄 Scenario Comparison</h1>
<p style="color:#9A8A6A;margin-top:0;">Compare Pilot / Small / Medium / Large — find the optimal capacity</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Custom scenario builder ───────────────────────────────────────────────
with st.expander("⚙️ Customise Scenarios (optional — defaults are 5/10/20/50 TPD)"):
    sc_cols = st.columns(4)
    custom_scenarios = []
    default_caps = [5, 10, 20, 50]
    default_labels = ["Pilot", "Small", "Medium", "Large"]
    colors = ["#74C0FC", "#A9E34B", "#E8B547", "#FF9999"]

    for i, col in enumerate(sc_cols):
        with col:
            lbl = st.text_input(f"Label {i+1}", value=default_labels[i], key=f"sc_lbl_{i}")
            cap = st.number_input(f"Capacity (TPD)", 1.0, 500.0,
                                   float(default_caps[i]), 1.0, key=f"sc_cap_{i}")
            price = st.number_input(f"Selling Price (₹/MT)", 20000, 80000,
                                     int(cfg.get("selling_price_per_mt", 35000)),
                                     1000, key=f"sc_price_{i}")
            custom_scenarios.append({
                "label": lbl, "capacity_tpd": cap,
                "selling_price_per_mt": price, "color": colors[i],
            })

# ── Run comparison ────────────────────────────────────────────────────────
run_col, _ = st.columns([1, 3])
with run_col:
    run_btn = st.button("▶ Run Comparison", type="primary", key="run_scenarios")

if run_btn:
    with st.spinner("Computing 4 scenarios…"):
        scenarios = run_scenarios(dict(cfg), custom_scenarios)
        st.session_state["scenario_results"] = scenarios
        st.success("Comparison ready!")

scenarios = st.session_state.get("scenario_results") or load_scenarios()

if not scenarios:
    st.info("Click **▶ Run Comparison** to analyse all scenarios.")
    st.stop()

st.markdown("---")

# ── Comparison table ──────────────────────────────────────────────────────
st.subheader("Side-by-Side Comparison")

labels = [s["label"] for s in scenarios]
table_rows = []
for key, display_name in OUTPUT_KEYS:
    row = {"Parameter": display_name}
    vals = [s.get(key, 0) for s in scenarios]
    best_idx = None
    if key in ("roi_pct", "irr_pct", "revenue_lac", "gross_profit_lac", "net_profit_lac", "output_tpd"):
        best_idx = vals.index(max(vals))
    elif key == "break_even_months":
        best_idx = vals.index(min(v for v in vals if v > 0))
    for i, s in enumerate(scenarios):
        v = s.get(key, 0)
        cell = f"{v:,.1f}" if isinstance(v, float) else str(v)
        if i == best_idx:
            cell += " ★"
        row[s["label"]] = cell
    table_rows.append(row)

df_table = pd.DataFrame(table_rows)
st.dataframe(df_table, use_container_width=True, hide_index=True)

# Best scenario badge
best_irr_idx = [s.get("irr_pct", 0) for s in scenarios].index(
    max(s.get("irr_pct", 0) for s in scenarios))
st.markdown(
    f'<p>★ Best IRR: <span class="best-tag">{scenarios[best_irr_idx]["label"]} — '
    f'{scenarios[best_irr_idx]["irr_pct"]:.1f}% IRR</span></p>',
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Charts ────────────────────────────────────────────────────────────────
ch1, ch2 = st.columns(2)

with ch1:
    st.markdown("**IRR & ROI Comparison**")
    fig_irr = go.Figure()
    fig_irr.add_trace(go.Bar(
        name="IRR (%)", x=labels,
        y=[s["irr_pct"] for s in scenarios],
        marker_color=[s["color"] for s in scenarios],
        text=[f"{s['irr_pct']:.1f}%" for s in scenarios],
        textposition="outside",
    ))
    fig_irr.add_trace(go.Bar(
        name="ROI (%)", x=labels,
        y=[s["roi_pct"] for s in scenarios],
        marker_color=[s["color"] for s in scenarios],
        opacity=0.5,
        text=[f"{s['roi_pct']:.1f}%" for s in scenarios],
        textposition="outside",
    ))
    fig_irr.update_layout(
        barmode="group", height=300, template="plotly_dark",
        paper_bgcolor="#1E1B14", plot_bgcolor="#1E1B14",
        font_color="#C8B88A", legend=dict(font=dict(color="#9A8A6A")),
        margin=dict(t=10, b=30),
    )
    st.plotly_chart(fig_irr, use_container_width=True)

with ch2:
    st.markdown("**Investment vs Revenue vs Profit (₹ Lac)**")
    fig_fin = go.Figure()
    for key, label_name, color in [
        ("investment_cr", "Investment (₹ Cr×10)", "#FF9999"),
        ("revenue_lac",   "Revenue (₹ Lac)",       "#E8B547"),
        ("net_profit_lac","Net Profit (₹ Lac)",     "#51CF66"),
    ]:
        mult = 10 if key == "investment_cr" else 1
        fig_fin.add_trace(go.Bar(
            name=label_name, x=labels,
            y=[s.get(key, 0) * mult for s in scenarios],
            marker_color=color, opacity=0.85,
        ))
    fig_fin.update_layout(
        barmode="group", height=300, template="plotly_dark",
        paper_bgcolor="#1E1B14", plot_bgcolor="#1E1B14",
        font_color="#C8B88A", legend=dict(font=dict(color="#9A8A6A")),
        margin=dict(t=10, b=30),
    )
    st.plotly_chart(fig_fin, use_container_width=True)

# Radar chart
st.markdown("**Multi-Dimension Radar**")
radar_metrics = ["IRR (%)", "ROI (%)", "Revenue Score", "Profit Margin", "Payback Score"]

def _normalize(scenarios, key, invert=False):
    vals = [s.get(key, 0) for s in scenarios]
    mx = max(vals) if max(vals) > 0 else 1
    if invert:
        mn = min(v for v in vals if v > 0)
        return [round((mx - s.get(key, mx)) / max(mx - mn, 1) * 100) for s in scenarios]
    return [round(v / mx * 100) for v in vals]

irr_n   = _normalize(scenarios, "irr_pct")
roi_n   = _normalize(scenarios, "roi_pct")
rev_n   = _normalize(scenarios, "revenue_lac")
prof_n  = _normalize(scenarios, "gross_profit_lac")
bev_n   = _normalize(scenarios, "break_even_months", invert=True)

fig_radar = go.Figure()
for i, s in enumerate(scenarios):
    fig_radar.add_trace(go.Scatterpolar(
        r=[irr_n[i], roi_n[i], rev_n[i], prof_n[i], bev_n[i]],
        theta=radar_metrics, fill="toself",
        name=s["label"], line_color=s["color"], opacity=0.7,
    ))
fig_radar.update_layout(
    polar=dict(
        bgcolor="#1E1B14",
        radialaxis=dict(visible=True, range=[0, 100], color="#9A8A6A"),
        angularaxis=dict(color="#C8B88A"),
    ),
    showlegend=True, height=380, template="plotly_dark",
    paper_bgcolor="#1E1B14", font_color="#C8B88A",
    legend=dict(font=dict(color="#9A8A6A")),
)
st.plotly_chart(fig_radar, use_container_width=True)

# ── Export ────────────────────────────────────────────────────────────────
st.markdown("---")
ex1, ex2 = st.columns(2)
with ex1:
    st.download_button(
        "⬇ Download Comparison CSV",
        df_table.to_csv(index=False),
        file_name=f"scenario_compare_{datetime.now():%Y%m%d}.csv",
        mime="text/csv", key="dl_sc_csv",
    )
with ex2:
    try:
        import io
        from openpyxl import Workbook
        wb = Workbook(); ws = wb.active; ws.title = "Scenario Comparison"
        ws.append(list(df_table.columns))
        for row in df_table.itertuples(index=False):
            ws.append(list(row))
        buf = io.BytesIO(); wb.save(buf)
        st.download_button(
            "Download Excel", buf.getvalue(),
            f"scenarios_{datetime.now():%Y%m%d}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_sc_xl", type="primary",
        )
    except Exception:
        pass

st.caption(f"{COMPANY['name']} | Scenario Comparison | {datetime.now().strftime('%d %B %Y')}")

try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "91")
except Exception:
    pass
