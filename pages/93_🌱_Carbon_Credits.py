"""
93 · Carbon Credits & Sustainability
======================================
CO₂ savings, carbon credit revenue by scheme, CBAM assessment,
sustainability metrics — trees, cars, households.
"""
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import init_state, get_config
from engines.carbon_engine import calculate_carbon, load_carbon, cbam_assessment, CARBON_PRICES
from config import COMPANY

st.set_page_config(page_title="Carbon Credits · Bio Bitumen", page_icon="🌱", layout="wide")
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
.stat-box{background:#1E1B14;border:1px solid #3A3520;border-radius:10px;
  padding:16px;text-align:center;}
.stat-num{font-size:2.2rem;font-weight:900;color:#51CF66;}
.stat-lbl{font-size:11px;color:#9A8A6A;margin-top:2px;}
.credit-row{background:#1E1B14;padding:8px 12px;border-radius:6px;
  margin:3px 0;display:flex;align-items:center;gap:12px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="color:#51CF66;margin-bottom:2px;">🌱 Carbon Credits & Sustainability</h1>
<p style="color:#9A8A6A;margin-top:0;">
  CO₂ savings · Carbon credit revenue · CBAM export advantage · Sustainability metrics
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Live FX for carbon credit valuation ──────────────────────────────────
usd_inr = 84.0
try:
    from engines.free_apis import get_exchange_rates
    fx = get_exchange_rates()
    if "error" not in fx:
        usd_inr = fx.get("usd_inr", 84.0)
except Exception:
    pass

# ── Run calculation ───────────────────────────────────────────────────────
calc_col, _ = st.columns([1, 3])
with calc_col:
    if st.button("♻️ Calculate Carbon Profile", type="primary", key="calc_carbon"):
        with st.spinner("Calculating CO₂ savings and carbon credit revenue…"):
            result = calculate_carbon(cfg, usd_inr=usd_inr)
            st.session_state["carbon_result"] = result
        st.success("Carbon profile calculated!")

result = st.session_state.get("carbon_result") or load_carbon()

if not result:
    st.info("Click **Calculate Carbon Profile** to start.")
    st.stop()

# ── Hero metrics ──────────────────────────────────────────────────────────
h1, h2, h3, h4 = st.columns(4)
h1.metric("CO₂ Saved / Year", f"{result['total_co2_saved_tpa']:,.0f} tCO₂e")
h2.metric("Best Carbon Revenue", f"₹ {result['best_rev_lac']:.1f} Lac/yr",
          help=f"via {result['best_scheme']}")
h3.metric("Equiv. Trees Planted", f"{result['trees_equivalent']:,}")
h4.metric("USD/INR Used", f"₹ {result['usd_inr_used']:.2f}")

st.markdown("---")

# ── CO₂ breakdown ─────────────────────────────────────────────────────────
st.subheader("CO₂ Savings Breakdown")
br1, br2 = st.columns([1, 1])

with br1:
    breakdown_data = {
        "Bitumen Substitution": result["co2_from_bitumen_sub"],
        "Biochar Sequestration": result["co2_from_biochar"],
        "Syngas Substitution":   result["co2_from_syngas"],
    }
    fig_pie = px.pie(
        values=list(breakdown_data.values()),
        names=list(breakdown_data.keys()),
        color_discrete_sequence=["#51CF66", "#E8B547", "#74C0FC"],
        hole=0.45,
    )
    fig_pie.update_layout(
        height=280, paper_bgcolor="#1E1B14", plot_bgcolor="#1E1B14",
        font_color="#C8B88A", margin=dict(t=10, b=10),
        legend=dict(font=dict(color="#9A8A6A")),
        annotations=[dict(text=f"{result['total_co2_saved_tpa']:,.0f}<br>tCO₂e",
                          font=dict(size=13, color="#51CF66"), showarrow=False)]
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with br2:
    st.markdown("**Annual Production → CO₂ Impact**")
    prod_rows = [
        ["Annual Biomass Input",   f"{result['annual_biomass_mt']:,} MT"],
        ["Bio-Oil / Bitumen",      f"{result['annual_bio_oil_mt']:,} MT"],
        ["Biochar",                f"{result['annual_biochar_mt']:,} MT"],
        ["Syngas",                 f"{result['annual_syngas_mt']:,} MT"],
        ["CO₂ saved (bitumen sub).",f"{result['co2_from_bitumen_sub']:,.0f} tCO₂e"],
        ["CO₂ saved (biochar)",    f"{result['co2_from_biochar']:,.0f} tCO₂e"],
        ["CO₂ saved (syngas)",     f"{result['co2_from_syngas']:,.0f} tCO₂e"],
        ["TOTAL CO₂ Saved",        f"{result['total_co2_saved_tpa']:,.0f} tCO₂e"],
    ]
    df_prod = pd.DataFrame(prod_rows, columns=["Metric", "Value"])
    st.dataframe(df_prod, use_container_width=True, hide_index=True)

st.markdown("---")

# ── Carbon credit revenue by scheme ───────────────────────────────────────
st.subheader("Carbon Credit Revenue by Scheme")

credit_rows = []
for scheme, data in result["credit_revenues"].items():
    credit_rows.append({
        "Scheme": scheme,
        "Price (USD/tCO₂e)": data["price_usd"],
        "Revenue (USD)": f"$ {data['revenue_usd']:,.0f}",
        "Revenue (₹ Lac)": data["revenue_inr_lac"],
        "Best?": "★" if scheme == result["best_scheme"] else "",
    })
df_credits = pd.DataFrame(credit_rows)

cr1, cr2 = st.columns([2, 1])
with cr1:
    st.dataframe(df_credits, use_container_width=True, hide_index=True)
with cr2:
    fig_bar = go.Figure(go.Bar(
        y=[r["Scheme"] for r in credit_rows],
        x=[r["Revenue (₹ Lac)"] for r in credit_rows],
        orientation="h",
        marker_color=["#51CF66" if r["Best?"] == "★" else "#E8B547"
                      for r in credit_rows],
        text=[f"₹{r['Revenue (₹ Lac)']:.1f}L" for r in credit_rows],
        textposition="outside",
    ))
    fig_bar.update_layout(
        height=260, paper_bgcolor="#1E1B14", plot_bgcolor="#1E1B14",
        font_color="#C8B88A", margin=dict(t=10, b=10, l=120, r=50),
        xaxis_title="₹ Lac / year",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ── Sustainability badges ─────────────────────────────────────────────────
st.subheader("Sustainability Impact — Visual")
sb1, sb2, sb3 = st.columns(3)
for col, num, lbl, icon in [
    (sb1, result["trees_equivalent"], "Equivalent Trees Planted / Year", "🌳"),
    (sb2, result["cars_off_road"],    "Equivalent Cars Removed",          "🚗"),
    (sb3, result["households_equiv"], "Households' Annual Emissions",     "🏠"),
]:
    with col:
        st.markdown(
            f'<div class="stat-box">'
            f'<div style="font-size:2.5rem;">{icon}</div>'
            f'<div class="stat-num">{num:,.0f}</div>'
            f'<div class="stat-lbl">{lbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── CBAM assessment ───────────────────────────────────────────────────────
st.subheader("🇪🇺 EU CBAM Export Opportunity")
st.caption("Carbon Border Adjustment Mechanism — bio-bitumen exported to EU avoids the CBAM levy")

cbam = cbam_assessment(result["annual_bio_oil_mt"], usd_inr)
cb1, cb2, cb3 = st.columns(3)
cb1.metric("CBAM Saving / MT", f"€ {cbam['cbam_saving_per_mt_eur']:.2f}")
cb2.metric("Annual CBAM Saving", f"€ {cbam['annual_cbam_saving_eur']:,.0f}")
cb3.metric("Annual Saving (₹ Lac)", f"₹ {cbam['annual_cbam_saving_lac_inr']:.1f} Lac")
st.info(cbam["note"])

# ── Export ────────────────────────────────────────────────────────────────
st.markdown("---")
ex1, ex2 = st.columns(2)
with ex1:
    st.download_button(
        "⬇ Download Carbon Report CSV",
        df_credits.to_csv(index=False),
        file_name=f"carbon_{datetime.now():%Y%m%d}.csv",
        mime="text/csv", key="dl_cc_csv",
    )
with ex2:
    if st.button("Print", key="prt_93"):
        import streamlit.components.v1 as _stc
        _stc.html("<script>window.print();</script>", height=0)

try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("AI Assist — Carbon Credit Strategy"):
            if st.button("Generate Carbon Strategy", type="primary", key="ai_93"):
                p = (
                    f"Bio-bitumen plant: {cfg.get('capacity_tpd',20)} TPD, "
                    f"saves {result['total_co2_saved_tpa']:,.0f} tCO₂e/year. "
                    f"Best carbon revenue: ₹{result['best_rev_lac']:.1f} Lac/year via {result['best_scheme']}. "
                    "Give a step-by-step carbon credit monetisation strategy for India: "
                    "which registry, how to register, timeline, documentation needed. Concise."
                )
                with st.spinner("AI thinking…"):
                    resp, prov = ask_ai(p, "Carbon credit and ESG consultant, India.")
                if resp:
                    st.markdown(f"**via {prov.upper()}:**")
                    st.markdown(resp)
except Exception:
    pass

st.caption(f"{COMPANY['name']} | Carbon Credits | {datetime.now().strftime('%d %B %Y')}")

try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "93")
except Exception:
    pass
