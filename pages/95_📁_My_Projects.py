"""
95 · My Projects — Multi-Project Manager
==========================================
Save / load / duplicate / delete named project configurations.
Switch active project, compare metrics, export/import JSON.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import init_state, get_config, update_fields
from engines.project_manager import (
    list_projects, save_project, load_project,
    delete_project, duplicate_project, export_project, import_project,
)
from config import COMPANY

st.set_page_config(page_title="My Projects · Bio Bitumen", page_icon="📁", layout="wide")
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
.proj-card{background:#1E1B14;border:1px solid #3A3520;border-radius:10px;
  padding:14px 18px;margin:6px 0;}
.proj-card.active{border-color:#E8B547;border-width:2px;}
.proj-name{color:#E8B547;font-size:15px;font-weight:700;}
.proj-meta{color:#9A8A6A;font-size:12px;margin-top:3px;}
.active-badge{background:#3A2E00;color:#E8B547;padding:2px 8px;
  border-radius:10px;font-size:11px;font-weight:600;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="color:#E8B547;margin-bottom:2px;">📁 My Projects</h1>
<p style="color:#9A8A6A;margin-top:0;">
  Save · Load · Duplicate · Compare · Export / Import project configurations
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Active project banner ─────────────────────────────────────────────────
active_name = cfg.get("project_name", "Untitled Project")
ac1, ac2, ac3, ac4 = st.columns(4)
ac1.metric("Active Project", active_name[:20])
ac2.metric("Capacity", f"{cfg.get('capacity_tpd', 20)} TPD")
ac3.metric("State", cfg.get("state", "—"))
ac4.metric("IRR", f"{cfg.get('irr_pct', 0):.1f}%")

st.markdown("---")

# ── Save current project ──────────────────────────────────────────────────
st.subheader("Save Current Project")
sv1, sv2 = st.columns([2, 1])
with sv1:
    save_name = st.text_input(
        "Project Name",
        value=active_name,
        placeholder="e.g. Pune 20TPD Phase-1",
        key="save_proj_name",
    )
with sv2:
    st.write("")
    st.write("")
    if st.button("💾 Save Project", type="primary", key="btn_save_proj"):
        if save_name.strip():
            save_project(save_name.strip(), dict(cfg))
            st.success(f"Saved: {save_name.strip()}")
            st.rerun()
        else:
            st.warning("Enter a project name.")

st.markdown("---")

# ── Project list ──────────────────────────────────────────────────────────
st.subheader("Saved Projects")
projects = list_projects()

if not projects:
    st.info("No saved projects yet. Save the current configuration above.")
else:
    # Summary metrics
    pm1, pm2 = st.columns(2)
    pm1.metric("Total Projects", len(projects))
    pm2.metric("Slots Used", f"{len(projects)} / 20")

    # Tabs: Cards + Compare table
    tab_cards, tab_compare = st.tabs(["📋 Project Cards", "📊 Compare"])

    with tab_cards:
        for proj in projects:
            is_active = proj["name"] == active_name
            card_cls = "proj-card active" if is_active else "proj-card"
            badge = '<span class="active-badge">ACTIVE</span>' if is_active else ""

            irr = proj.get("irr_pct", 0)
            cap = proj.get("capacity_tpd", 0)
            state = proj.get("state", "—")
            saved_at = proj.get("_saved_at", "")[:10]

            st.markdown(
                f'<div class="{card_cls}">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<span class="proj-name">{proj["name"]}</span>{badge}'
                f'</div>'
                f'<div class="proj-meta">'
                f'📍 {state} &nbsp;|&nbsp; ⚙️ {cap} TPD &nbsp;|&nbsp; '
                f'📈 IRR {irr:.1f}% &nbsp;|&nbsp; 🗓 {saved_at}'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            pa, pb, pc, pd_ = st.columns(4)
            with pa:
                if st.button("Load", key=f"load_{proj['slug']}"):
                    loaded = load_project(proj["name"])
                    if loaded:
                        update_fields(loaded)
                        st.success(f"Loaded: {proj['name']}")
                        st.rerun()
            with pb:
                if st.button("Duplicate", key=f"dup_{proj['slug']}"):
                    new_name = duplicate_project(proj["name"])
                    if new_name:
                        st.success(f"Duplicated as: {new_name}")
                        st.rerun()
            with pc:
                dl_bytes = export_project(proj["name"])
                if dl_bytes:
                    st.download_button(
                        "Export JSON",
                        dl_bytes,
                        file_name=f"{proj['slug']}.json",
                        mime="application/json",
                        key=f"exp_{proj['slug']}",
                    )
            with pd_:
                if not is_active:
                    if st.button("🗑 Delete", key=f"del_{proj['slug']}"):
                        delete_project(proj["name"])
                        st.success(f"Deleted: {proj['name']}")
                        st.rerun()

    with tab_compare:
        if len(projects) >= 2:
            compare_rows = []
            for p in projects:
                compare_rows.append({
                    "Project": p["name"][:25],
                    "State": p.get("state", "—"),
                    "Capacity (TPD)": p.get("capacity_tpd", 0),
                    "Investment (₹ Cr)": round(p.get("investment_cr", 0), 2),
                    "IRR (%)": round(p.get("irr_pct", 0), 1),
                    "ROI (%)": round(p.get("roi_pct", 0), 1),
                    "Break-even (mo)": p.get("break_even_months", 0),
                    "Saved": p.get("_saved_at", "")[:10],
                })
            df_cmp = pd.DataFrame(compare_rows)
            st.dataframe(df_cmp, use_container_width=True, hide_index=True)

            st.download_button(
                "⬇ Download Comparison CSV",
                df_cmp.to_csv(index=False),
                file_name=f"projects_compare_{datetime.now():%Y%m%d}.csv",
                mime="text/csv",
                key="dl_proj_cmp",
            )
        else:
            st.info("Save at least 2 projects to compare them here.")

st.markdown("---")

# ── Import project ────────────────────────────────────────────────────────
st.subheader("Import Project from JSON")
uploaded = st.file_uploader(
    "Upload a project JSON file (exported from this portal)",
    type=["json"],
    key="import_proj_file",
)
if uploaded:
    imp1, _ = st.columns([1, 3])
    with imp1:
        if st.button("Import Project", key="btn_import"):
            result = import_project(uploaded.read())
            if result:
                st.success(f"Imported: {result}")
                st.rerun()
            else:
                st.error("Import failed — check file format.")

st.markdown("---")

# ── Bulk export all ───────────────────────────────────────────────────────
if projects:
    st.subheader("Bulk Export")
    all_data = [load_project(p["name"]) for p in projects]
    all_data = [d for d in all_data if d]
    bulk_json = json.dumps(all_data, indent=2, ensure_ascii=False)
    st.download_button(
        "⬇ Export All Projects (JSON)",
        bulk_json,
        file_name=f"all_projects_{datetime.now():%Y%m%d}.json",
        mime="application/json",
        key="dl_all_proj",
    )

st.markdown("---")
st.caption(f"{COMPANY['name']} | My Projects | {datetime.now().strftime('%d %B %Y')}")

try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "95")
except Exception:
    pass
