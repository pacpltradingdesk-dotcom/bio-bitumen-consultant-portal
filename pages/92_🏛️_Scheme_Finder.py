"""
92 · Government Scheme Finder
================================
Find all applicable central + state subsidies for this bio-bitumen project.
30+ schemes database — filters by state, capacity, project type.
"""
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import init_state, get_config
from engines.scheme_finder_engine import find_schemes, save_schemes, load_schemes, total_benefit
from config import COMPANY

st.set_page_config(page_title="Scheme Finder · Bio Bitumen", page_icon="🏛️", layout="wide")
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
.scheme-card{background:#1E1B14;border-left:4px solid #E8B547;
  border-radius:0 10px 10px 0;padding:12px 16px;margin:5px 0;}
.scheme-card.state{border-left-color:#74C0FC;}
.scheme-card.finance{border-left-color:#51CF66;}
.scheme-card.market{border-left-color:#FF9999;}
.badge{display:inline-block;padding:2px 10px;border-radius:10px;
  font-size:11px;font-weight:600;margin:2px;}
.badge-central{background:#3A2E00;color:#E8B547;}
.badge-state  {background:#1E3A5F;color:#74C0FC;}
.badge-finance{background:#1B3A25;color:#51CF66;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="color:#E8B547;margin-bottom:2px;">🏛️ Government Scheme Finder</h1>
<p style="color:#9A8A6A;margin-top:0;">
  Find all central + state subsidies applicable to your bio-bitumen project
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Project context ───────────────────────────────────────────────────────
pc1, pc2, pc3, pc4 = st.columns(4)
pc1.metric("State", cfg.get("state", "—"))
pc2.metric("Capacity", f"{cfg.get('capacity_tpd',20)} TPD")
pc3.metric("Investment", f"₹ {cfg.get('investment_cr',0):.2f} Cr")
pc4.metric("Location", cfg.get("location", "—")[:15])

st.markdown("---")

# ── Run finder ────────────────────────────────────────────────────────────
run_col, _ = st.columns([1, 3])
with run_col:
    if st.button("🔍 Find All Applicable Schemes", type="primary", key="find_schemes"):
        with st.spinner("Scanning 30+ central and state schemes…"):
            schemes = find_schemes(cfg)
            save_schemes(schemes)
            st.session_state["found_schemes"] = schemes
        st.success(f"Found {len(schemes)} applicable schemes!")

schemes = st.session_state.get("found_schemes") or load_schemes()

if not schemes:
    st.info("Click **Find All Applicable Schemes** to start.")

    # Show database count
    from engines.scheme_finder_engine import SCHEMES
    st.markdown(f"Database: **{len(SCHEMES)} schemes** — central + 10 states")
    st.stop()

# ── Summary metrics ───────────────────────────────────────────────────────
total_cr = total_benefit(schemes)
central  = [s for s in schemes if s["type"] == "Central"]
state_s  = [s for s in schemes if s["type"] == "State"]

sm1, sm2, sm3, sm4 = st.columns(4)
sm1.metric("Total Schemes Found", len(schemes))
sm2.metric("Central Schemes", len(central))
sm3.metric("State Schemes", len(state_s))
sm4.metric("Est. Total Benefit", f"₹ {total_cr:.2f} Cr")

st.markdown("---")

# ── Filter ────────────────────────────────────────────────────────────────
fl1, fl2, fl3 = st.columns(3)
with fl1:
    ftype = st.selectbox("Filter by Type", ["All", "Central", "State"], key="sf_type")
with fl2:
    fcats = ["All"] + sorted(set(s["category"] for s in schemes))
    fcat  = st.selectbox("Filter by Category", fcats, key="sf_cat")
with fl3:
    fsort = st.selectbox("Sort By", ["Est. Benefit ↓", "Name A-Z", "Type"], key="sf_sort")

filtered = schemes
if ftype != "All":
    filtered = [s for s in filtered if s["type"] == ftype]
if fcat != "All":
    filtered = [s for s in filtered if s["category"] == fcat]
if fsort == "Name A-Z":
    filtered.sort(key=lambda s: s["name"])
elif fsort == "Type":
    filtered.sort(key=lambda s: s["type"])

st.markdown(f"**Showing {len(filtered)} schemes**")
st.markdown("---")

# ── Scheme cards ─────────────────────────────────────────────────────────
tab_cards, tab_table = st.tabs(["📋 Cards View", "📊 Table View"])

with tab_cards:
    for s in filtered:
        t_class = "state" if s["type"] == "State" else (
            "finance" if s["category"] == "Finance" else (
            "market" if s["category"] == "Market" else ""))
        badge_cls = "badge-state" if s["type"] == "State" else "badge-central"
        benefit_str = f"₹ {s['est_benefit_cr']:.2f} Cr est." if s["est_benefit_cr"] > 0 else "Non-financial benefit"

        st.markdown(
            f'<div class="scheme-card {t_class}">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
            f'<b style="color:#E8B547;font-size:14px;">{s["name"]}</b>'
            f'<span style="color:#51CF66;font-weight:700;font-size:13px;">{benefit_str}</span>'
            f'</div>'
            f'<div style="margin:4px 0;">'
            f'<span class="badge {badge_cls}">{s["type"]}</span>'
            f'<span class="badge badge-finance">{s["category"]}</span>'
            f'<span style="font-size:12px;color:#9A8A6A;margin-left:8px;">{s["ministry"]}</span>'
            f'</div>'
            f'<p style="color:#C8B88A;font-size:12px;margin:4px 0;">{s["benefit_note"]}</p>'
            f'<p style="color:#7A6A4A;font-size:11px;margin:2px 0;">'
            f'Apply at: <b>{s["apply_at"]}</b></p>'
            f'</div>',
            unsafe_allow_html=True,
        )

with tab_table:
    tbl_rows = [{
        "Scheme": s["name"][:50],
        "Ministry": s["ministry"][:30],
        "Type": s["type"],
        "Benefit": s["benefit_type"],
        "Rate": f"{s['benefit_pct']}%" if s["benefit_pct"] else "—",
        "Est. Benefit (₹ Cr)": s["est_benefit_cr"],
        "Apply At": s["apply_at"],
    } for s in filtered]
    df_schemes = pd.DataFrame(tbl_rows)
    st.dataframe(df_schemes, use_container_width=True, hide_index=True)

# ── Export ────────────────────────────────────────────────────────────────
st.markdown("---")
ex1, ex2 = st.columns(2)
with ex1:
    st.download_button(
        "⬇ Download Schemes CSV",
        pd.DataFrame(tbl_rows).to_csv(index=False) if schemes else "",
        file_name=f"schemes_{cfg.get('state','')[:5]}_{datetime.now():%Y%m%d}.csv",
        mime="text/csv", key="dl_sch_csv",
    )
with ex2:
    if st.button("Print", key="prt_92"):
        import streamlit.components.v1 as _stc
        _stc.html("<script>window.print();</script>", height=0)

try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("AI Assist — Scheme Application Strategy"):
            if st.button("Generate Application Strategy", type="primary", key="ai_92"):
                top = schemes[:5]
                names = ", ".join(s["name"] for s in top)
                p = (
                    f"For a {cfg.get('capacity_tpd',20)} TPD bio-bitumen plant in {cfg.get('state')}, "
                    f"top applicable schemes are: {names}. "
                    "Give a step-by-step application strategy: which to apply first, required documents, "
                    "timeline, and how to maximise total subsidy. Concise bullet points."
                )
                with st.spinner("AI thinking…"):
                    resp, prov = ask_ai(p, "Government scheme expert, India MSME sector.")
                if resp:
                    st.markdown(f"**via {prov.upper()}:**")
                    st.markdown(resp)
except Exception:
    pass

st.caption(f"{COMPANY['name']} | Scheme Finder | {datetime.now().strftime('%d %B %Y')}")

try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "92")
except Exception:
    pass
