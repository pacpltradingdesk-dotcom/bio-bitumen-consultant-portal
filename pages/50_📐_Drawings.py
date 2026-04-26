"""
Engineering Drawings — ALL 117 drawings in one view
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from state_manager import get_config, init_state
# Note: CAPACITY_KEYS/LABELS available via config if needed

st.set_page_config(page_title="Engineering Drawings", page_icon="📐", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass


st.sidebar.markdown("---")
if st.sidebar.button("Print This Page", key="print_page"):
    import streamlit.components.v1 as _stc; _stc.html('<script>window.print();</script>', height=0)

st.title("Engineering Drawings")
st.markdown(f"**{cfg['capacity_tpd']:.0f} TPD Plant — All drawings viewable & downloadable**")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# CLIENT DRAWINGS — Real project-specific drawings per active client
# ══════════════════════════════════════════════════════════════════════
CLIENT_DRAWINGS_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "client_drawings")

# Map customer_id to folder name
CLIENT_FOLDER_MAP = {
    1: "REX_FUELS_BAHADURGARH",
    2: "REX_FUELS_BAHADURGARH",   # fallback — same base project
}

# Also map by company name snippet
CLIENT_FOLDER_BY_NAME = {
    "REX FUELS": "REX_FUELS_BAHADURGARH",
    "BAHADURGARH": "REX_FUELS_BAHADURGARH",
    "ODISHA": "REX_FUELS_ODISHA",
    "MALKANGIRI": "REX_FUELS_ODISHA",
}

DRAWING_TYPE_LABELS = {
    "DRG_A01": "Site Layout Plan",
    "DRG_A02": "Plant Layout Detail",
    "DRG_B01": "Foundation Plan",
    "DRG_B02": "Section & Elevation",
    "DRG_C01": "Electrical SLD",
    "DRG_C02": "Fire Safety Layout",
    "DRG_D01": "Process Flow Diagram",
    "DRG_D02": "Material Flow Diagram",
    "DRG_E01": "Utility Layout",
    "DRG_F01": "3D Isometric View",
    "DRG_F02": "Reactor Detail",
    "DRG_G01": "Condenser Detail",
    "DRG_Legacy_3D": "3D Plant Isometric (Legacy)",
    "DRG_Legacy_Break": "Break-Even Chart",
    "DRG_Legacy_Capex": "CAPEX Breakdown",
    "DRG_Legacy_Condenser": "Condenser Detail (Legacy)",
    "DRG_Legacy_Electrical": "Electrical SLD (Legacy)",
    "DRG_Legacy_Equipment": "Equipment Diagram",
    "DRG_Legacy_Fire": "Fire Safety Plan (Legacy)",
    "DRG_Legacy_Manpower": "Manpower Organisation",
    "DRG_Legacy_Piping": "Piping Layout",
    "DRG_Legacy_Plant": "Plant Layout (Legacy)",
    "DRG_Legacy_Plumbing": "Plumbing & Water",
    "DRG_Legacy_Process": "Process Flow (Legacy)",
    "DRG_Legacy_Reactor": "Reactor Detail (Legacy)",
    "DRG_Legacy_Revenue": "Revenue Projection",
    "DRG_Legacy_Road": "Road Access & Site",
    "DRG_Legacy_Structural_Elev": "Structural Elevation",
    "DRG_Legacy_Structural_Found": "Structural Foundation",
    "Chart_Cost": "Cost Per MT Chart",
    "Chart_DSCR": "DSCR Trend Chart",
    "Chart_ROI": "ROI & Payback Chart",
    "43_00_01": "Break-Even Chart",
    "43_00_02": "Capacity Comparison",
    "43_00_03": "CAPEX Breakdown",
    "43_00_08": "DSCR Trend",
    "43_00_09": "ESG Impact",
    "43_00_10": "India Expansion Map",
    "43_00_11": "Investment vs Returns",
    "43_00_12": "Market Comparison",
    "43_00_13": "Process Flow",
    "43_00_16": "5-Year Revenue",
    "43_00_17": "Revenue Streams",
    "43_00_18": "ROI Comparison",
}

def _get_drawing_label(fname):
    for key, label in DRAWING_TYPE_LABELS.items():
        if key in fname:
            return label
    return fname.replace("_", " ").replace(".png", "")

def _get_client_drawings_folder():
    """Get client drawings folder for the active client."""
    try:
        from state_manager import get_active_client_id
        from database import get_customer
        cid = get_active_client_id()
        if cid:
            c = get_customer(cid)
            if c:
                name = (c.get("name","") + " " + c.get("company","") + " " + c.get("city","")).upper()
                for key, folder in CLIENT_FOLDER_BY_NAME.items():
                    if key in name:
                        return os.path.join(CLIENT_DRAWINGS_ROOT, folder)
            folder = CLIENT_FOLDER_MAP.get(cid)
            if folder:
                return os.path.join(CLIENT_DRAWINGS_ROOT, folder)
    except Exception:
        pass
    return None

client_drw_folder = _get_client_drawings_folder()

if client_drw_folder and os.path.exists(client_drw_folder):
    client_files = sorted([f for f in os.listdir(client_drw_folder) if f.endswith(".png")])

    # Separate drawings vs charts
    drg_files = [f for f in client_files if "DRG_" in f]
    chart_files = [f for f in client_files if "Chart_" in f or "43_00_" in f]

    active_name = cfg.get("client_company", cfg.get("client_name", "This Client"))
    st.success(f"**{len(client_files)} Real Project Drawings** available for {active_name} "
               f"({len(drg_files)} Engineering + {len(chart_files)} Charts)")

    tab_eng, tab_charts, tab_generic = st.tabs([
        f"Engineering Drawings ({len(drg_files)})",
        f"Financial Charts ({len(chart_files)})",
        "Generic Library"
    ])

    with tab_eng:
        st.subheader(f"Engineering Drawings — {active_name}")
        st.caption("Actual project drawings — 5 TPD, Bahadurgarh/Odisha specific")
        if drg_files:
            cols = st.columns(2)
            for i, fname in enumerate(drg_files):
                fpath = os.path.join(client_drw_folder, fname)
                label = _get_drawing_label(fname)
                with cols[i % 2]:
                    st.markdown(f"**{label}**")
                    st.image(fpath, use_container_width=True)
                    with open(fpath, "rb") as f:
                        st.download_button(f"Download — {label}", f.read(), fname,
                                           key=f"dl_cdrg_{i}")
                    st.markdown("---")
        else:
            st.info("No engineering drawings found.")

    with tab_charts:
        st.subheader(f"Financial Charts — {active_name}")
        st.caption("Revenue projections, DSCR, ROI, CAPEX breakdown — actual project data")
        if chart_files:
            cols = st.columns(2)
            for i, fname in enumerate(chart_files):
                fpath = os.path.join(client_drw_folder, fname)
                label = _get_drawing_label(fname)
                with cols[i % 2]:
                    st.markdown(f"**{label}**")
                    st.image(fpath, use_container_width=True)
                    with open(fpath, "rb") as f:
                        st.download_button(f"Download — {label}", f.read(), fname,
                                           key=f"dl_cchart_{i}")
                    st.markdown("---")
        else:
            st.info("No charts found.")

    with tab_generic:
        st.caption("Generic library drawings (all capacities)")

else:
    if client_drw_folder:
        st.info("No client-specific drawings found. Showing generic library below.")
    else:
        st.info("Select a client from the sidebar to see their project drawings.")

ALL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "all_drawings")

# ── Build drawing list ────────────────────────────────────────────────
CAPACITIES = ["5", "10", "15", "20", "30", "40", "50", "75", "100"]

TYPE_MAP = {
    "Layout_TopView": "Plant Layout (Top View)",
    "SITE_LAYOUT": "Site Layout (Professional)",
    "CAD_Site_Layout": "Site Layout (CAD-Grade)",
    "PFD": "Process Flow Diagram",
    "Electrical_SLD": "Electrical Single Line Diagram",
    "Fire_Layout": "Fire Safety Layout",
    "Civil_Foundation": "Civil Foundation",
    "Water_Layout": "Water & Drainage Layout",
    "Piping_Cable": "Piping & Cable Routing",
    "Earthing_Layout": "Earthing & Lightning",
    "ETP_Layout": "ETP Layout (Effluent Treatment)",
    "Tank_Farm": "Tank Farm Layout (PESO)",
    "Machinery_Layout": "Machinery Layout (Factory)",
}

drawings = []
if os.path.exists(ALL_DIR):
    for fname in sorted(os.listdir(ALL_DIR)):
        if not fname.endswith('.png'):
            continue
        fpath = os.path.join(ALL_DIR, fname)

        # Detect capacity
        cap = "Unknown"
        for c in sorted(CAPACITIES, key=lambda x: -len(x)):  # longest first
            if f"{c}TPD" in fname:
                cap = f"{c} TPD"
                break

        # Detect type
        dtype = "Other"
        for key, label in TYPE_MAP.items():
            if key in fname:
                dtype = label
                break

        drawings.append({
            "filename": fname,
            "path": fpath,
            "capacity": cap,
            "type": dtype,
            "size_kb": os.path.getsize(fpath) / 1024,
        })

# ── Metrics ───────────────────────────────────────────────────────────
total = len(drawings)
types = sorted(set(d["type"] for d in drawings))
caps = sorted(set(d["capacity"] for d in drawings), key=lambda x: int(x.replace(" TPD", "")) if x != "Unknown" else 0)

m1, m2, m3 = st.columns(3)
m1.metric("Total Drawings", total)
m2.metric("Drawing Types", len(types))
m3.metric("Capacities", len(caps))

st.markdown("---")

# ── Filters ───────────────────────────────────────────────────────────
f1, f2 = st.columns(2)

with f1:
    # Default to nearest capacity
    nearest = min(caps, key=lambda x: abs(int(x.replace(" TPD", "")) - cfg["capacity_tpd"]) if x != "Unknown" else 999)
    default_idx = caps.index(nearest) + 1 if nearest in caps else 0
    sel_cap = st.selectbox("Capacity", ["ALL"] + caps, index=default_idx)

with f2:
    sel_type = st.selectbox("Drawing Type", ["ALL"] + types)

# Filter
filtered = drawings
if sel_cap != "ALL":
    filtered = [d for d in filtered if d["capacity"] == sel_cap]
if sel_type != "ALL":
    filtered = [d for d in filtered if d["type"] == sel_type]

st.markdown(f"### Showing {len(filtered)} of {total} drawings")

if not filtered:
    st.warning("No drawings for this combination. Select 'ALL' in one filter to see available drawings.")

    # Show what IS available for selected capacity
    if sel_cap != "ALL":
        avail = [d for d in drawings if d["capacity"] == sel_cap]
        if avail:
            st.info(f"Available types for {sel_cap}: {', '.join(sorted(set(d['type'] for d in avail)))}")
    if sel_type != "ALL":
        avail = [d for d in drawings if d["type"] == sel_type]
        if avail:
            st.info(f"Available capacities for {sel_type}: {', '.join(sorted(set(d['capacity'] for d in avail)))}")
else:
    for i, d in enumerate(filtered):
        st.markdown(f"### {d['type']} — {d['capacity']}")
        try:
            import os as _os
            if _os.path.exists(d["path"]):
                st.image(d["path"], width="stretch")
            else:
                st.warning(f"Drawing file not found: {d['filename']}")
        except Exception:
            st.warning(f"Cannot display: {d['filename']}")

        col_info, col_dl = st.columns([3, 1])
        with col_info:
            st.caption(f"File: {d['filename']} | Size: {d['size_kb']:.0f} KB")
        with col_dl:
            try:
                if os.path.exists(d["path"]):
                    with open(d["path"], "rb") as f:
                        file_bytes = f.read()
                    st.download_button("⬇️ Download", file_bytes, d["filename"],
                                        mime="image/png", key=f"dl_{i}")
                else:
                    st.error("File missing")
            except Exception as e:
                st.error(f"Error: {e}")
        st.markdown("---")

# ── Complete Register ─────────────────────────────────────────────────
st.subheader("Drawing Register")
if drawings:
    reg_df = pd.DataFrame([{
        "Type": d["type"], "Capacity": d["capacity"],
        "Size (KB)": f"{d['size_kb']:.0f}", "File": d["filename"],
    } for d in drawings])
    st.dataframe(reg_df, width="stretch", hide_index=True)

# ── Coverage Matrix ───────────────────────────────────────────────────
st.subheader("Coverage Matrix — Which drawings exist for which capacity")
matrix = {}
for d in drawings:
    if d["type"] not in matrix:
        matrix[d["type"]] = set()
    matrix[d["type"]].add(d["capacity"])

matrix_rows = []
for dtype in sorted(matrix.keys()):
    row = {"Drawing Type": dtype}
    for c in caps:
        row[c] = "YES" if c in matrix[dtype] else "—"
    matrix_rows.append(row)

if matrix_rows:
    st.dataframe(pd.DataFrame(matrix_rows), width="stretch", hide_index=True)

st.caption("Change capacity in Plant Design → auto-selects nearest available drawings here")

# ── Download ALL as ZIP ──────────────────────────────────────────────
st.markdown("---")
st.subheader("Bulk Download")
if filtered:
    if st.button("Download All Filtered Drawings as ZIP", type="primary", key="dl_zip_draw"):
        import zipfile, io
        zip_buf = io.BytesIO()
        file_count = 0
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for d in filtered:
                if os.path.exists(d["path"]):
                    zf.write(d["path"], d["filename"])
                    file_count += 1
        zip_buf.seek(0)
        cap_label = sel_cap if sel_cap != "ALL" else f"{cfg['capacity_tpd']:.0f}TPD"
        st.download_button(f"Download ZIP ({file_count} files)", zip_buf.getvalue(),
                            f"Drawings_{cap_label}.zip", "application/zip", key="dl_zip_draw_btn")

# ── AI Skill: Drawing Checklist ──────────────────────────────────────
st.markdown("---")
try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("🤖 AI: Drawing Checklist"):
            if st.button("Generate", type="primary", key="ai_08📐Dra"):
                with st.spinner("AI working..."):
                    _p = f"As a senior bio-bitumen consultant, generate: Drawing Checklist. "
                    _p += f"Plant: {cfg.get('capacity_tpd',20):.0f} TPD, Investment: Rs {cfg.get('investment_cr',8):.2f} Cr, "
                    _p += f"Location: {cfg.get('location','')}, {cfg.get('state','')}. "
                    _p += "Be specific with numbers. Professional format."
                    _r, _pv = ask_ai(_p, "Senior industrial consultant.", 1000)
                if _r:
                    st.markdown(_r)
except Exception:
    pass


# ── Next Steps Navigation ──
try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "50")
except Exception:
    pass
