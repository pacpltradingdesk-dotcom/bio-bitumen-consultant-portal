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

st.title("Engineering Drawings")
st.markdown(f"**{cfg['capacity_tpd']:.0f} TPD Plant — All drawings viewable & downloadable**")
st.markdown("---")

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
            st.image(d["path"], width="stretch")
        except Exception:
            st.error(f"Cannot display: {d['filename']}")

        col_info, col_dl = st.columns([3, 1])
        with col_info:
            st.caption(f"File: {d['filename']} | Size: {d['size_kb']:.0f} KB")
        with col_dl:
            with open(d["path"], "rb") as f:
                st.download_button("Download", f.read(), d["filename"],
                                    mime="image/png", key=f"dl_{i}")
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
