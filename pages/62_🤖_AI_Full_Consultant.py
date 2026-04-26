"""
AI Full Consultant — 6 capability areas in one page
Tabs: Cross-Validate | Viability Check | Permissions | Layout | BOM | Free Chat
"""
import json
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from engines.ai_engine import (
    ask_ai, ai_cross_validate, ai_viability_check,
    ai_permissions_guide, ai_layout_guidance, ai_machine_bom,
    ai_financial_analysis, SYSTEM_PROMPT_BASE,
    load_ai_config, get_ai_provider_summary,
)

# ── page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Full Consultant | Bio-Bitumen",
    page_icon="🤖",
    layout="wide",
)

# ── shared styles ─────────────────────────────────────────────────────
st.markdown("""
<style>
.ai-badge {
    display:inline-block; padding:2px 10px; border-radius:12px;
    font-size:12px; font-weight:700; letter-spacing:.5px;
}
.badge-free  { background:#e8f5e9; color:#2e7d32; }
.badge-paid  { background:#fff3e0; color:#e65100; }
.badge-local { background:#e3f2fd; color:#0277bd; }
.badge-ok    { background:#e8f5e9; color:#2e7d32; }
.badge-warn  { background:#fff8e1; color:#f57f17; }
.badge-na    { background:#f5f5f5; color:#9e9e9e; }
.result-box {
    background:#f0f4f8; border-left:4px solid #1565c0;
    padding:16px 20px; border-radius:6px; margin-top:12px;
    white-space:pre-wrap; font-size:14px; line-height:1.6;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR — provider status + quick config
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🤖 AI Provider Status")
    providers = get_ai_provider_summary()
    for p in providers:
        tier_cls = {"FREE": "badge-free", "PAID": "badge-paid", "LOCAL": "badge-local"}.get(p["tier"], "badge-na")
        avail_cls = "badge-ok" if p["has_key"] else "badge-na"
        avail_txt = "KEY SET" if p["has_key"] else "no key"
        st.markdown(
            f'<span class="ai-badge {tier_cls}">{p["tier"]}</span> '
            f'**{p["display"]}** '
            f'<span class="ai-badge {avail_cls}">{avail_txt}</span>',
            unsafe_allow_html=True,
        )
    st.divider()
    st.markdown("**Tip:** Set API keys in ⚙️ Settings page for best results. Groq free key recommended.")
    st.divider()
    st.markdown("#### Quick Project Config")
    sb_cap = st.number_input("Capacity (TPD)", 1.0, 200.0, 5.0, 1.0, key="sb_cap")
    sb_inv = st.number_input("Investment (Rs Cr)", 0.5, 100.0, 6.5, 0.5, key="sb_inv")
    sb_state = st.selectbox("State", [
        "Haryana", "Maharashtra", "Gujarat", "Rajasthan", "Punjab",
        "Uttar Pradesh", "Madhya Pradesh", "Karnataka", "Odisha",
        "West Bengal", "Tamil Nadu", "Telangana", "Andhra Pradesh",
        "Jharkhand", "Bihar", "Chhattisgarh",
    ], key="sb_state")
    sb_city = st.text_input("City / Location", "Bahadurgarh", key="sb_city")

def _sidebar_cfg():
    return {
        "capacity_tpd": st.session_state.get("sb_cap", 5.0),
        "investment_cr": st.session_state.get("sb_inv", 6.5),
        "state": st.session_state.get("sb_state", "Haryana"),
        "location": st.session_state.get("sb_city", ""),
        "pm_cost_cr": round(st.session_state.get("sb_inv", 6.5) * 0.57, 2),
        "civil_cost_cr": round(st.session_state.get("sb_inv", 6.5) * 0.17, 2),
        "utility_cost_cr": round(st.session_state.get("sb_inv", 6.5) * 0.10, 2),
        "wc_cr": round(st.session_state.get("sb_inv", 6.5) * 0.12, 2),
        "preop_cr": round(st.session_state.get("sb_inv", 6.5) * 0.04, 2),
        "roi_pct": 22.0, "irr_pct": 26.0, "dscr_yr3": 1.35,
        "break_even_months": 28, "revenue_yr5_lac": 0,
        "util_yr1": 60,
    }


# ══════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════
st.title("🤖 AI Full Consultant")
st.caption("YUGA PMC — All-scope AI: Cross-validate · Viability · Permissions · Layout · BOM · Free Chat")
st.divider()

# ══════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════
(
    tab_xval, tab_viab, tab_perm,
    tab_layout, tab_bom, tab_fin, tab_chat,
) = st.tabs([
    "🔍 Cross-Validate",
    "✅ Viability Check",
    "📋 Permissions Guide",
    "📐 Layout Guidance",
    "⚙️ Machine BOM",
    "💰 Financial Analysis",
    "💬 Free Chat",
])


# ══════════════════════════════════════════════════════════════════════
# TAB 1 — CROSS-VALIDATE
# ══════════════════════════════════════════════════════════════════════
with tab_xval:
    st.subheader("🔍 Project Cross-Validation")
    st.markdown(
        "AI audits every number against engineering benchmarks and flags inconsistencies "
        "before you submit to a bank or investor."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        xv_cap  = st.number_input("Capacity (TPD)", 1.0, 200.0, float(sb_cap), 1.0, key="xv_cap")
        xv_inv  = st.number_input("Total Investment (Rs Cr)", 0.5, 200.0, float(sb_inv), 0.5, key="xv_inv")
        xv_pm   = st.number_input("P&M Cost (Rs Cr)", 0.0, 150.0, round(float(sb_inv)*0.57, 2), 0.1, key="xv_pm")
    with c2:
        xv_civ  = st.number_input("Civil Cost (Rs Cr)", 0.0, 50.0, round(float(sb_inv)*0.17, 2), 0.1, key="xv_civ")
        xv_util = st.number_input("Utility Cost (Rs Cr)", 0.0, 30.0, round(float(sb_inv)*0.10, 2), 0.1, key="xv_util")
        xv_wc   = st.number_input("Working Capital (Rs Cr)", 0.0, 30.0, round(float(sb_inv)*0.12, 2), 0.1, key="xv_wc")
    with c3:
        xv_roi  = st.number_input("ROI (%)", 0.0, 100.0, 22.0, 0.5, key="xv_roi")
        xv_irr  = st.number_input("IRR (%)", 0.0, 100.0, 26.0, 0.5, key="xv_irr")
        xv_dscr = st.number_input("DSCR Year 3", 0.0, 5.0, 1.35, 0.05, key="xv_dscr")
    c4, c5 = st.columns(2)
    with c4:
        xv_bev = st.number_input("Break-even (months)", 6, 120, 28, 1, key="xv_bev")
        xv_rev5 = st.number_input("Revenue Year 5 (Rs Lakhs)", 0, 50000, 0, 50, key="xv_rev5")
    with c5:
        xv_util1 = st.number_input("Capacity Utilisation Yr1 (%)", 0, 100, 60, 5, key="xv_util1")
        xv_state = st.selectbox("State", [
            "Haryana","Maharashtra","Gujarat","Rajasthan","Punjab","Uttar Pradesh",
            "Madhya Pradesh","Karnataka","Odisha","West Bengal","Tamil Nadu",
        ], key="xv_state")

    if st.button("🔍 Run Cross-Validation", type="primary", use_container_width=True, key="btn_xval"):
        cfg_xv = {
            "capacity_tpd": xv_cap, "investment_cr": xv_inv,
            "pm_cost_cr": xv_pm, "civil_cost_cr": xv_civ,
            "utility_cost_cr": xv_util, "wc_cr": xv_wc, "preop_cr": 0,
            "roi_pct": xv_roi, "irr_pct": xv_irr, "dscr_yr3": xv_dscr,
            "break_even_months": xv_bev, "revenue_yr5_lac": xv_rev5,
            "util_yr1": xv_util1, "state": xv_state,
        }
        with st.spinner("AI auditing all numbers …"):
            result, prov = ai_cross_validate(cfg_xv)
        st.success(f"Validated by **{prov}**")
        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
        st.download_button("⬇ Download Report", result,
                           file_name="cross_validation.txt", mime="text/plain")


# ══════════════════════════════════════════════════════════════════════
# TAB 2 — VIABILITY CHECK
# ══════════════════════════════════════════════════════════════════════
with tab_viab:
    st.subheader("✅ Commercial Viability Assessment")
    st.markdown(
        "AI scores your project across 5 dimensions and gives a Go/No-Go verdict "
        "— **PRACTICAL / MARGINAL / NOT VIABLE**."
    )
    c1, c2 = st.columns(2)
    with c1:
        vb_cap   = st.number_input("Capacity (TPD)", 1.0, 200.0, float(sb_cap), 1.0, key="vb_cap")
        vb_inv   = st.number_input("Investment (Rs Cr)", 0.5, 200.0, float(sb_inv), 0.5, key="vb_inv")
        vb_roi   = st.number_input("ROI (%)", 0.0, 100.0, 22.0, 0.5, key="vb_roi")
        vb_irr   = st.number_input("IRR (%)", 0.0, 100.0, 26.0, 0.5, key="vb_irr")
    with c2:
        vb_dscr  = st.number_input("DSCR Year 3", 0.0, 5.0, 1.35, 0.05, key="vb_dscr")
        vb_bev   = st.number_input("Break-even (months)", 6, 120, 28, 1, key="vb_bev")
        vb_rev5  = st.number_input("Revenue Year 5 (Rs Lakhs)", 0, 50000, 0, 50, key="vb_rev5")
        vb_state = st.selectbox("State", [
            "Haryana","Maharashtra","Gujarat","Rajasthan","Punjab","Uttar Pradesh",
            "Madhya Pradesh","Karnataka","Odisha","West Bengal","Tamil Nadu",
        ], key="vb_state")
    vb_city = st.text_input("City / Location", sb_city, key="vb_city")

    if st.button("✅ Run Viability Check", type="primary", use_container_width=True, key="btn_viab"):
        cfg_vb = {
            "capacity_tpd": vb_cap, "investment_cr": vb_inv,
            "roi_pct": vb_roi, "irr_pct": vb_irr, "dscr_yr3": vb_dscr,
            "break_even_months": vb_bev, "revenue_yr5_lac": vb_rev5,
            "state": vb_state, "location": vb_city,
        }
        with st.spinner("AI assessing viability across 5 dimensions …"):
            result, prov = ai_viability_check(cfg_vb)
        st.success(f"Assessed by **{prov}**")
        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
        st.download_button("⬇ Download Report", result,
                           file_name="viability_check.txt", mime="text/plain")


# ══════════════════════════════════════════════════════════════════════
# TAB 3 — PERMISSIONS GUIDE
# ══════════════════════════════════════════════════════════════════════
with tab_perm:
    st.subheader("📋 Permissions & Licences Guide")
    st.markdown(
        "AI generates a **complete state-specific checklist** with authority names, "
        "documents, timelines, fees, and the critical path."
    )
    c1, c2 = st.columns(2)
    with c1:
        pm_state = st.selectbox("State", [
            "Haryana","Maharashtra","Gujarat","Rajasthan","Punjab","Uttar Pradesh",
            "Madhya Pradesh","Karnataka","Odisha","West Bengal","Tamil Nadu",
            "Telangana","Andhra Pradesh","Jharkhand","Bihar","Chhattisgarh",
        ], key="pm_state")
        pm_cap = st.number_input("Capacity (TPD)", 1.0, 200.0, float(sb_cap), 1.0, key="pm_cap")
    with c2:
        st.info(
            "**What you'll get:**\n"
            "- 10 permission categories\n"
            "- Authority, docs, timeline, fee for each\n"
            "- Sequence / critical path\n"
            "- State-specific schemes (PADMA, H-GUVY, PSI…)"
        )

    if st.button("📋 Generate Permissions Guide", type="primary", use_container_width=True, key="btn_perm"):
        with st.spinner(f"AI building {pm_state} permission checklist …"):
            result, prov = ai_permissions_guide(pm_state, pm_cap)
        st.success(f"Generated by **{prov}**")
        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
        st.download_button("⬇ Download Checklist", result,
                           file_name=f"permissions_{pm_state.replace(' ','_')}.txt",
                           mime="text/plain")


# ══════════════════════════════════════════════════════════════════════
# TAB 4 — LAYOUT GUIDANCE
# ══════════════════════════════════════════════════════════════════════
with tab_layout:
    st.subheader("📐 Plant Layout Guidance")
    st.markdown(
        "AI designs the 15-zone area schedule, adjacency rules, fire safety layout, "
        "and dimensions for your specific capacity."
    )
    c1, c2 = st.columns(2)
    with c1:
        ly_cap   = st.number_input("Capacity (TPD)", 1.0, 200.0, float(sb_cap), 1.0, key="ly_cap")
        ly_state = st.selectbox("State", [
            "Haryana","Maharashtra","Gujarat","Rajasthan","Punjab","Uttar Pradesh",
            "Madhya Pradesh","Karnataka","Odisha","West Bengal","Tamil Nadu",
        ], key="ly_state")
    with c2:
        ly_plot = st.number_input("Available Plot Area (sqm) — 0 = estimate", 0, 100000, 0, 100, key="ly_plot")
        st.info(
            "**Zones A–O:** Gate · Admin · Raw Mat Store · Pre-processing · "
            "Pyrolysis · Condensation · Oil Upgrade · PMB Blending · Storage · "
            "QC Lab · Utility · ETP · Fire Point · Maintenance"
        )

    if st.button("📐 Generate Layout Guide", type="primary", use_container_width=True, key="btn_layout"):
        cfg_ly = {
            "capacity_tpd": ly_cap, "state": ly_state,
            "plot_area_sqm": ly_plot if ly_plot > 0 else 0,
        }
        with st.spinner("AI designing zone layout …"):
            result, prov = ai_layout_guidance(cfg_ly)
        st.success(f"Designed by **{prov}**")
        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
        st.download_button("⬇ Download Layout Guide", result,
                           file_name=f"layout_{int(ly_cap)}tpd.txt",
                           mime="text/plain")


# ══════════════════════════════════════════════════════════════════════
# TAB 5 — MACHINE BOM
# ══════════════════════════════════════════════════════════════════════
with tab_bom:
    st.subheader("⚙️ Plant & Machinery BOM")
    st.markdown(
        "AI generates the **complete Bill of Materials** across 15 equipment categories "
        "with specs, quantities, indicative costs, and make suggestions."
    )
    c1, c2 = st.columns(2)
    with c1:
        bm_cap   = st.number_input("Capacity (TPD)", 1.0, 200.0, float(sb_cap), 1.0, key="bm_cap")
        bm_state = st.selectbox("State", [
            "Haryana","Maharashtra","Gujarat","Rajasthan","Punjab","Uttar Pradesh",
            "Madhya Pradesh","Karnataka","Odisha","West Bengal","Tamil Nadu",
        ], key="bm_state")
    with c2:
        st.info(
            "**15 categories:**\n"
            "Biomass Handling · Pre-processing · Pyrolysis Reactor · "
            "Condensation · Gas Handling · Bio-oil Upgrade · PMB Blending · "
            "Bitumen Storage · Biochar Handling · Utilities · Electrical/SCADA · "
            "QC Lab · ETP · Fire & Safety · Civil Embedded"
        )

    if st.button("⚙️ Generate Full BOM", type="primary", use_container_width=True, key="btn_bom"):
        cfg_bm = {"capacity_tpd": bm_cap, "state": bm_state}
        with st.spinner(f"AI building {bm_cap:.0f} TPD BOM — this may take 30-60s …"):
            result, prov = ai_machine_bom(cfg_bm)
        st.success(f"BOM by **{prov}**")
        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
        st.download_button("⬇ Download BOM", result,
                           file_name=f"bom_{int(bm_cap)}tpd.txt",
                           mime="text/plain")


# ══════════════════════════════════════════════════════════════════════
# TAB 6 — FINANCIAL ANALYSIS
# ══════════════════════════════════════════════════════════════════════
with tab_fin:
    st.subheader("💰 AI Financial Analysis")
    st.markdown(
        "AI gives a **bankability score /10**, health assessment, strengths, risks, "
        "and specific recommendations."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        fn_cap  = st.number_input("Capacity (TPD)", 1.0, 200.0, float(sb_cap), 1.0, key="fn_cap")
        fn_inv  = st.number_input("Investment (Rs Cr)", 0.5, 200.0, float(sb_inv), 0.5, key="fn_inv")
        fn_roi  = st.number_input("ROI (%)", 0.0, 100.0, 22.0, 0.5, key="fn_roi")
    with c2:
        fn_irr  = st.number_input("IRR (%)", 0.0, 100.0, 26.0, 0.5, key="fn_irr")
        fn_dscr = st.number_input("DSCR Year 3", 0.0, 5.0, 1.35, 0.05, key="fn_dscr")
        fn_bev  = st.number_input("Break-even (months)", 6, 120, 28, 1, key="fn_bev")
    with c3:
        fn_rev5 = st.number_input("Revenue Year 5 (Rs Lakhs)", 0, 50000, 0, 50, key="fn_rev5")
        fn_state = st.selectbox("State", [
            "Haryana","Maharashtra","Gujarat","Rajasthan","Punjab","Uttar Pradesh",
            "Madhya Pradesh","Karnataka","Odisha","West Bengal","Tamil Nadu",
        ], key="fn_state")

    if st.button("💰 Run Financial Analysis", type="primary", use_container_width=True, key="btn_fin"):
        cfg_fn = {
            "capacity_tpd": fn_cap, "investment_cr": fn_inv,
            "roi_pct": fn_roi, "irr_pct": fn_irr, "dscr_yr3": fn_dscr,
            "break_even_months": fn_bev, "revenue_yr5_lac": fn_rev5,
            "state": fn_state, "roi_timeline": [],
        }
        with st.spinner("AI analysing financials …"):
            result, prov = ai_financial_analysis(cfg_fn)
        st.success(f"Analysed by **{prov}**")
        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
        st.download_button("⬇ Download Analysis", result,
                           file_name="financial_analysis.txt", mime="text/plain")


# ══════════════════════════════════════════════════════════════════════
# TAB 7 — FREE CHAT
# ══════════════════════════════════════════════════════════════════════
with tab_chat:
    st.subheader("💬 Free Chat with AI Consultant")
    st.markdown(
        "Ask anything — DPR, permissions, raw materials, prices, calculations, "
        "drawings, or vendor advice. Uses project context from the sidebar."
    )

    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    # Display history
    for msg in st.session_state.ai_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if user_input := st.chat_input("Ask YUGA PMC AI anything about your bio-bitumen project …"):
        st.session_state.ai_chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        cfg_ctx = _sidebar_cfg()
        context = (
            f"Project context: {cfg_ctx['capacity_tpd']:.0f} TPD, "
            f"Rs {cfg_ctx['investment_cr']:.2f} Cr, "
            f"{cfg_ctx['state']}, {cfg_ctx['location']}."
        )

        # Build history string
        history_str = ""
        for m in st.session_state.ai_chat_history[-8:]:
            role = "User" if m["role"] == "user" else "Consultant"
            history_str += f"{role}: {m['content'][:300]}\n"

        prompt = f"{context}\n\nConversation:\n{history_str}\nAnswer professionally with specific numbers and sources."

        with st.chat_message("assistant"):
            with st.spinner("YUGA PMC AI thinking …"):
                response, prov = ask_ai(prompt, SYSTEM_PROMPT_BASE, max_tokens=2000)
            st.markdown(response)
            st.caption(f"via **{prov}**")

        st.session_state.ai_chat_history.append({"role": "assistant", "content": response})

    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.ai_chat_history = []
            st.rerun()

    # Quick-start prompts
    st.divider()
    st.markdown("**Quick prompts:**")
    quick_prompts = [
        "What is the benchmark investment per TPD for a bio-bitumen plant?",
        "List the government subsidies available for bio-bitumen in Haryana.",
        "What permissions are needed before starting construction?",
        "Explain the PMB-40 manufacturing process step by step.",
        "What is the current price of VG-10 bitumen in India?",
        "What should DSCR Year 3 be for bank approval?",
    ]
    cols = st.columns(3)
    for i, qp in enumerate(quick_prompts):
        with cols[i % 3]:
            if st.button(qp[:45] + ("…" if len(qp) > 45 else ""), key=f"qp_{i}", use_container_width=True):
                st.session_state.ai_chat_history.append({"role": "user", "content": qp})
                cfg_ctx = _sidebar_cfg()
                context = f"Project: {cfg_ctx['capacity_tpd']:.0f} TPD, Rs {cfg_ctx['investment_cr']:.2f} Cr, {cfg_ctx['state']}."
                with st.spinner("Thinking …"):
                    response, prov = ask_ai(
                        f"{context}\n{qp}", SYSTEM_PROMPT_BASE, max_tokens=1500
                    )
                st.session_state.ai_chat_history.append({"role": "assistant", "content": response})
                st.rerun()
