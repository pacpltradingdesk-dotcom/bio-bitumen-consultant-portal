"""
Plant Design — Capacity selector, auto area calculation, layout view, section breakup
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from state_manager import get_config, update_field, init_state

st.set_page_config(page_title="Plant Design", page_icon="⚙️", layout="wide")
init_state()
st.sidebar.markdown("---")
if st.sidebar.button("Print This Page", key="print_page"):
    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

st.title("Plant Design & Layout")
st.markdown("**Capacity selector (5-100 TPD) | Auto area calculation | Section planning**")
st.markdown("---")

cfg = get_config()

# ── Capacity Selector ─────────────────────────────────────────────────
st.subheader("Select Plant Capacity")
preset_options = [5, 10, 15, 20, 30, 40, 50, 100]
col_cap, col_custom = st.columns(2)

with col_cap:
    preset = st.selectbox("Standard Capacities (TPD)", preset_options,
                           index=preset_options.index(int(cfg["capacity_tpd"])) if int(cfg["capacity_tpd"]) in preset_options else 3)
    if preset != cfg["capacity_tpd"]:
        update_field("capacity_tpd", float(preset))
        cfg = get_config()

with col_custom:
    custom = st.number_input("Or enter custom TPD", min_value=3.0, max_value=100.0,
                              value=float(cfg["capacity_tpd"]), step=5.0)
    if custom != cfg["capacity_tpd"]:
        update_field("capacity_tpd", custom)
        cfg = get_config()

st.markdown("---")

# ── Auto Area Calculation ─────────────────────────────────────────────
tpd = cfg["capacity_tpd"]

# Area calculations based on capacity (industry standards)
sections = {
    "Raw Material Yard": round(tpd * 100, 0),      # 100 sqft per TPD
    "Reactor Building": round(tpd * 60, 0),          # 60 sqft per TPD
    "Condenser & Oil Section": round(tpd * 40, 0),   # 40 sqft per TPD
    "Tank Farm (Oil Storage)": round(tpd * 50, 0),   # 50 sqft per TPD
    "Char Storage": round(tpd * 30, 0),              # 30 sqft per TPD
    "Utility Area (Power, Water)": round(tpd * 35, 0),
    "Lab & QC": round(max(300, tpd * 10), 0),
    "Admin & Office": round(max(400, tpd * 8), 0),
    "Parking & Loading": round(tpd * 40, 0),
    "Green Belt & Buffer": round(tpd * 25, 0),
    "Internal Roads": round(tpd * 30, 0),
    "Future Expansion": round(tpd * 50, 0),
}
total_sqft = sum(sections.values())
total_acres = total_sqft / 43560

st.subheader(f"Plant Layout — {tpd:.0f} TPD")

la1, la2, la3 = st.columns(3)
la1.metric("Total Area Required", f"{total_sqft:,.0f} sq ft")
la2.metric("In Acres", f"{total_acres:.2f} acres")
la3.metric("In Sq Meters", f"{total_sqft * 0.093:.0f} sqm")

# ── Section Breakup Table + Chart ─────────────────────────────────────
sec_df = pd.DataFrame([{"Section": k, "Area (sq ft)": v, "% of Total": round(v/total_sqft*100, 1)}
                        for k, v in sections.items()])

col_table, col_chart = st.columns([1, 1])

with col_table:
    st.markdown("**Section-wise Area Breakup**")
    st.dataframe(sec_df, width="stretch", hide_index=True)

with col_chart:
    fig_area = px.pie(sec_df, names="Section", values="Area (sq ft)",
                       title="Area Distribution",
                       color_discrete_sequence=px.colors.qualitative.Set3)
    fig_area.update_traces(textposition="inside", textinfo="percent+label")
    fig_area.update_layout(height=450, template="plotly_white")
    st.plotly_chart(fig_area, width="stretch")

st.markdown("---")

# ── Visual Layout (Treemap) ───────────────────────────────────────────
st.subheader("Plant Layout Visualization")
fig_layout = px.treemap(sec_df, path=["Section"], values="Area (sq ft)",
                          color="Area (sq ft)", color_continuous_scale="Blues",
                          title=f"Plant Layout — {tpd:.0f} TPD ({total_sqft:,.0f} sq ft total)")
fig_layout.update_layout(height=500)
st.plotly_chart(fig_layout, width="stretch")

st.markdown("---")

# ── Process Flow ──────────────────────────────────────────────────────
st.subheader("Process Flow: Biomass → Bio-Modified Bitumen")
st.markdown("""
```
                    PROCESS FLOW DIAGRAM
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │   BIOMASS     SHREDDER     DRYER      PYROLYSIS         │
    │   INPUT   →   (Size     →  (Moisture →  REACTOR         │
    │   (Agro      Reduction)    <15%)     (400-600°C)        │
    │    Waste)                              │                 │
    │                                        ├─→ BIO-OIL (40%)│
    │                                        │   → Blend with │
    │                                        │     Bitumen    │
    │                                        │   → BIO-MOD    │
    │                                        │     BITUMEN    │
    │                                        │                │
    │                                        ├─→ BIOCHAR (30%)│
    │                                        │   → Soil Amend │
    │                                        │   → Carbon Blk │
    │                                        │                │
    │                                        └─→ SYNGAS (25%) │
    │                                            → Captive    │
    │                                              Fuel       │
    │                                                         │
    │   Storage → Quality Testing → Dispatch to NHAI/PWD      │
    └─────────────────────────────────────────────────────────┘
```
""")

st.markdown("---")

# ── Key Equipment for Selected Capacity ───────────────────────────────
st.subheader(f"Equipment Required — {tpd:.0f} TPD")

# Scale equipment based on capacity
reactors = max(1, int(tpd / 10))
shredders = max(1, int(tpd / 15))
dryers = max(1, int(tpd / 20))
condensers = max(1, int(tpd / 10))

equipment = [
    {"Equipment": "Pyrolysis Reactor", "Quantity": reactors, "Specification": f"{min(10, tpd/reactors):.0f} MT each, Continuous"},
    {"Equipment": "Biomass Shredder", "Quantity": shredders, "Specification": f"{tpd/shredders:.0f} TPH Hammer Mill"},
    {"Equipment": "Rotary Dryer", "Quantity": dryers, "Specification": f"{tpd/dryers:.0f} TPH capacity"},
    {"Equipment": "Condenser/Heat Exchanger", "Quantity": condensers, "Specification": "Shell & Tube type"},
    {"Equipment": "Bio-Oil Storage Tank", "Quantity": max(2, int(tpd/10)), "Specification": f"{max(10, tpd*2):.0f} KL each"},
    {"Equipment": "Vacuum Distillation Unit", "Quantity": 1, "Specification": "For oil refining"},
    {"Equipment": "Pollution Control Scrubber", "Quantity": 1, "Specification": "As per PCB norms"},
    {"Equipment": "DG Set", "Quantity": 1, "Specification": f"{max(250, int(cfg['power_kw']*1.2))} kVA"},
    {"Equipment": "HT/LT Transformer", "Quantity": 1, "Specification": f"{int(cfg['power_kw'])} kW rated"},
    {"Equipment": "Weighbridge", "Quantity": 1, "Specification": "60 MT electronic"},
    {"Equipment": "Lab Equipment", "Quantity": 1, "Specification": "BIS testing lab"},
    {"Equipment": "Fire Fighting System", "Quantity": 1, "Specification": "As per Fire NOC"},
    {"Equipment": "Material Handling", "Quantity": 1, "Specification": "Conveyors, loaders"},
]
st.dataframe(pd.DataFrame(equipment), width="stretch", hide_index=True)

# ── Utility Requirements ──────────────────────────────────────────────
st.markdown("---")
st.subheader("Utility Requirements")
uc1, uc2, uc3, uc4 = st.columns(4)
uc1.metric("Power", f"{cfg['power_kw']:.0f} kW")
uc2.metric("Water", f"{max(5, int(tpd * 1)):,} KLD")
uc3.metric("Compressed Air", f"{max(50, int(tpd * 5)):,} CFM")
uc4.metric("Steam", f"{max(100, int(tpd * 50)):,} Kg/hr")

st.caption("All values auto-calculated based on selected capacity. Source: Industry standards for pyrolysis plants.")

# ── Related Documents from File System ────────────────────────────────
st.markdown("---")
st.subheader("Related Project Documents")
try:
    from engines.content_extractor import get_documents_for_module
    cap_key = cfg.get("capacity_key", "20MT")
    plant_folder = f"PLANT_{cap_key}_Day"
    docs = get_documents_for_module("plant_design")
    matching = [d for d in docs if cap_key in d.get("capacity", "")]
    if matching:
        st.markdown(f"**{len(matching)} documents** available for {cfg['capacity_tpd']:.0f} TPD:")
        for d in matching[:15]:
            st.markdown(f"- **{d['filename']}** ({d['section']}) — {d.get('extension', '')} — `{d['path']}`")
        if len(matching) > 15:
            st.caption(f"...and {len(matching)-15} more. See Document Library for full list.")
    else:
        st.info("Select a standard capacity (5-50 MT) to see related documents.")
except Exception:
    pass
