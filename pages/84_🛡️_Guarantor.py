"""
Guarantor — Master Cross-Validation System
9 Specialist Workers + 20 Mathematical Rules + AI Deep Audit
🟢 All clear → DPR Export unlocked
🔴 Any red → DPR Export BLOCKED until fixed
"""
import sys
import json
import streamlit as st
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import init_state, get_config
from engines.guarantor_engine import (
    load_gs, save_gs, run_all_rules, get_module_health, health_score,
    can_export_dpr, get_rules_for_module, ai_deep_audit,
    MODULES, MODULE_NAMES, MODULE_RULES, STATUS_ICON, WORKER_DESCRIPTIONS,
    GS_DEFAULTS,
)

# ── page ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Guarantor | YUGA PMC",
    page_icon="🛡️",
    layout="wide",
)
init_state()
cfg = get_config()

# ── styles ────────────────────────────────────────────────────────────
st.markdown("""
<style>
.health-card {
    padding:18px 16px; border-radius:10px; text-align:center;
    border:2px solid; margin:4px;
}
.hc-green  { background:#e8f5e9; border-color:#2e7d32; }
.hc-yellow { background:#fff8e1; border-color:#f57f17; }
.hc-red    { background:#ffebee; border-color:#c62828; }
.hc-grey   { background:#f5f5f5; border-color:#9e9e9e; }
.block-bar {
    background:#ffebee; border-left:5px solid #c62828;
    padding:14px 20px; border-radius:6px; margin-bottom:12px;
}
.clear-bar {
    background:#e8f5e9; border-left:5px solid #2e7d32;
    padding:14px 20px; border-radius:6px; margin-bottom:12px;
}
.rule-row-red    { background:#fff5f5; }
.rule-row-yellow { background:#fffff0; }
.score-big { font-size:48px; font-weight:900; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# LOAD + RUN RULES
# ══════════════════════════════════════════════════════════════════════
data = load_gs()

# Auto-run on page load
results = run_all_rules(data)
module_health = get_module_health(results)
score = health_score(results)
can_export, blocking = can_export_dpr(data)

# ── Header ────────────────────────────────────────────────────────────
col_title, col_score = st.columns([3, 1])
with col_title:
    st.title("🛡️ GUARANTOR — Master Cross-Validation")
    st.caption(
        f"Project: **{data.get('project_name', '—')}** | "
        f"{data.get('capacity_tpd', 0):.0f} TPD | {data.get('state', '—')} | "
        f"Investment: Rs {data.get('investment_cr', 0):.2f} Cr"
    )
with col_score:
    ov_color = {"green": "#2e7d32", "yellow": "#f57f17", "red": "#c62828", "grey": "#9e9e9e"}
    ov = score["overall"]
    ov_c = ov_color.get(ov, "#333")
    ov_icon = STATUS_ICON.get(ov, "⚪")
    ov_label = "ALL CLEAR" if ov == "green" else ("WARNINGS" if ov == "yellow" else "RED FLAGS")
    st.markdown(
        f'<div style="text-align:center; padding:10px;">'
        f'<div class="score-big" style="color:{ov_c};">'
        f'{score["score"]}<span style="font-size:24px;">/{score["total"]}</span></div>'
        f'<div style="font-size:14px; color:#555;">Rules Passing</div>'
        f'<div style="font-size:20px;">{ov_icon} {ov_label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── DPR Block / Clear banner ──────────────────────────────────────────
if not can_export:
    st.markdown(
        f'<div class="block-bar">🔴 <strong>DPR EXPORT BLOCKED</strong> — '
        f'{len(blocking)} red flag(s) must be resolved before exporting to bank / investor.<br>'
        f'<small>{" | ".join([b[:80] for b in blocking[:3]])}</small></div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="clear-bar">🟢 <strong>ALL CLEAR — DPR EXPORT UNLOCKED</strong> '
        '— No red flags. Project numbers are self-consistent.</div>',
        unsafe_allow_html=True,
    )

st.divider()

# ══════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════
(
    tab_overview, tab_data, tab_finance,
    tab_eng, tab_market, tab_comply,
    tab_ai, tab_dpr,
) = st.tabs([
    "🏠 Overview",
    "📊 Project Data",
    "💰 Finance Audit",
    "🏭 Engineering Audit",
    "📊 Market Audit",
    "📜 Compliance Audit",
    "🤖 AI Deep Audit",
    "📤 DPR Readiness",
])


# ══════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════
with tab_overview:
    st.subheader("System Health Matrix")
    st.markdown("*9 Specialist AI Workers | 20 Mathematical Rules | Auto-updates every audit run*")

    # Health cards — one per module
    cols = st.columns(len(MODULES))
    css_cls = {"green": "hc-green", "yellow": "hc-yellow", "red": "hc-red", "grey": "hc-grey"}
    for i, m in enumerate(MODULES):
        h = module_health[m]
        cls = css_cls.get(h["status"], "hc-grey")
        icon = STATUS_ICON.get(h["status"], "⚪")
        total = h["total"]
        passed = h["pass"]
        with cols[i]:
            st.markdown(
                f'<div class="health-card {cls}">'
                f'<div style="font-size:22px">{icon}</div>'
                f'<div style="font-weight:700;font-size:13px">{MODULE_NAMES[m]}</div>'
                f'<div style="font-size:26px;font-weight:900">{passed}/{total}</div>'
                f'<div style="font-size:11px;color:#666">{WORKER_DESCRIPTIONS[m][:50]}…</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # Count summary
    c = score["counts"]
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("🟢 Passing", c["green"])
    mc2.metric("🟡 Warnings", c["yellow"])
    mc3.metric("🔴 Red Flags", c["red"])
    mc4.metric("⚪ No Data", c["grey"])

    # Full rules table
    st.subheader("All 20 Rules")
    rows = []
    for r in results:
        rows.append({
            "#": r["id"],
            "Rule": r["name"],
            "Status": STATUS_ICON.get(r["status"], "⚪") + " " + r["status"].upper(),
            "Audit Message": r["message"],
            "Workers": ", ".join(r["modules"]),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=500,
                 column_config={"#": st.column_config.NumberColumn(width=40)})

    if st.button("🔄 Re-run Full Audit", type="primary", key="btn_rerun_overview"):
        st.rerun()


# ══════════════════════════════════════════════════════════════════════
# TAB 2 — PROJECT DATA (editable single source of truth)
# ══════════════════════════════════════════════════════════════════════
with tab_data:
    st.subheader("Project Data — Single Source of Truth")
    st.markdown("Edit any value here → click **Save & Re-audit** → all 20 rules re-run automatically.")

    with st.form("guarantor_data_form"):
        st.markdown("#### Identity")
        c1, c2 = st.columns(2)
        f_client  = c1.text_input("Client Name", data.get("client_name", ""))
        f_project = c2.text_input("Project Name", data.get("project_name", ""))
        f_loc     = c1.text_input("Location", data.get("location", ""))
        f_state   = c2.selectbox("State", [
            "Haryana", "Maharashtra", "Gujarat", "Rajasthan", "Punjab",
            "Uttar Pradesh", "Madhya Pradesh", "Karnataka", "Odisha",
            "West Bengal", "Tamil Nadu", "Telangana", "Andhra Pradesh",
            "Jharkhand", "Bihar", "Chhattisgarh",
        ], index=0 if data.get("state") not in ["Haryana"] else 0)

        st.markdown("#### Capacity & Working Days")
        c1, c2, c3 = st.columns(3)
        f_tpd   = c1.number_input("Capacity (TPD)", 1.0, 500.0, float(data.get("capacity_tpd", 5)), 1.0)
        f_wdays = c2.number_input("Working Days/Year", 100, 365, int(data.get("working_days", 300)))
        f_ut1   = c3.number_input("Utilisation Yr1 (%)", 10.0, 100.0, float(data.get("util_yr1", 60)), 5.0)

        st.markdown("#### Investment Breakdown (Rs Crore)")
        c1, c2, c3 = st.columns(3)
        f_inv   = c1.number_input("Total Investment", 0.1, 500.0, float(data.get("investment_cr", 6.5)), 0.1)
        f_land  = c1.number_input("Land Cost", 0.0, 100.0, float(data.get("land_cost_cr", 0)), 0.05)
        f_civil = c2.number_input("Civil & Structural", 0.0, 100.0, float(data.get("civil_cost_cr", 1.10)), 0.05)
        f_pm    = c2.number_input("Plant & Machinery", 0.0, 300.0, float(data.get("pm_cost_cr", 3.71)), 0.05)
        f_util  = c3.number_input("Utility & Electrical", 0.0, 100.0, float(data.get("utility_cost_cr", 0.65)), 0.05)
        f_preop = c3.number_input("Pre-operative", 0.0, 50.0, float(data.get("preop_cr", 0.26)), 0.02)
        f_wc    = c3.number_input("Working Capital", 0.0, 100.0, float(data.get("wc_cr", 0.78)), 0.05)

        st.markdown("#### Revenue & Raw Material (Rs/MT)")
        c1, c2, c3 = st.columns(3)
        f_pmb_sell = c1.number_input("Selling Price PMB/MT", 10000, 200000, int(data.get("selling_price_pmb_per_mt", 72000)), 500)
        f_vg10     = c1.number_input("VG-10 Price/MT", 10000, 200000, int(data.get("vg10_price_per_mt", 48000)), 500)
        f_husk_pr  = c2.number_input("Husk Price (Rs/MT)", 500, 10000, int(data.get("rm_husk_price_per_mt", 3000)), 100)
        f_husk_rat = c2.number_input("Husk Ratio (MT husk/MT output)", 0.8, 3.0, float(data.get("husk_per_mt_output", 1.4)), 0.05)
        f_vg10_rat = c3.number_input("VG-10 Ratio in PMB blend", 0.3, 0.9, float(data.get("vg10_per_mt_pmb", 0.70)), 0.05)
        f_pmb_pct  = c3.number_input("PMB as % of total output", 0.3, 1.0, float(data.get("pmb_output_pct", 0.70)), 0.05)

        st.markdown("#### Operating & Loan")
        c1, c2, c3 = st.columns(3)
        f_pwr_kw   = c1.number_input("Power Load (kW)", 10, 5000, int(data.get("power_load_kw", 135)), 5)
        f_pwr_rate = c1.number_input("Power Rate (Rs/kWh)", 2.0, 20.0, float(data.get("power_rate_rs_per_kwh", 7.5)), 0.25)
        f_pwr_hrs  = c2.number_input("Power Hours/Day", 8, 24, int(data.get("power_hours_per_day", 20)))
        f_loan     = c2.number_input("Loan Amount (Rs Cr)", 0.0, 400.0, float(data.get("loan_amount_cr", 4.22)), 0.1)
        f_rate     = c3.number_input("Loan Rate (%)", 6.0, 24.0, float(data.get("loan_rate_pct", 11.5)), 0.25)
        f_tenure   = c3.number_input("Loan Tenure (Years)", 1, 15, int(data.get("loan_tenure_yr", 7)))

        st.markdown("#### Key Financial Metrics")
        c1, c2, c3 = st.columns(3)
        f_roi   = c1.number_input("ROI (%)", 0.0, 100.0, float(data.get("roi_pct", 22)), 0.5)
        f_irr   = c1.number_input("IRR (%)", 0.0, 100.0, float(data.get("irr_pct", 26)), 0.5)
        f_dscr  = c2.number_input("DSCR Year 3", 0.0, 10.0, float(data.get("dscr_yr3", 1.35)), 0.05)
        f_bev_m = c2.number_input("Break-even (Months)", 1, 120, int(data.get("break_even_months", 28)))
        f_bev_p = c3.number_input("Break-even (%)", 0.0, 100.0, float(data.get("break_even_pct", 58)), 1.0)

        st.markdown("#### Engineering & Compliance")
        c1, c2, c3 = st.columns(3)
        f_plot    = c1.number_input("Plot Area (sqm)", 100, 500000, int(data.get("plot_area_sqm", 3000)), 100)
        f_builtup = c1.number_input("Built-up Area (sqm)", 100, 200000, int(data.get("built_up_sqm", 800)), 50)
        f_water   = c2.number_input("Water Demand (LPD)", 100, 500000, int(data.get("water_demand_lpd", 5000)), 100)
        f_noc_kw  = c2.number_input("Electricity NOC (kW)", 10, 50000, int(data.get("electricity_noc_kw", 135)), 5)
        f_pol_cat = c3.selectbox("Pollution Category", ["Green", "Orange", "Red"],
                                 index=["Green","Orange","Red"].index(data.get("pollution_category","Orange")))
        f_workers = c3.number_input("Factory Workers", 1, 500, int(data.get("factory_workers", 12)))

        submitted = st.form_submit_button("💾 Save & Re-audit", type="primary", use_container_width=True)

    if submitted:
        new_data = {
            "client_name": f_client, "project_name": f_project,
            "location": f_loc, "state": f_state,
            "capacity_tpd": f_tpd, "working_days": f_wdays, "util_yr1": f_ut1,
            "investment_cr": f_inv, "land_cost_cr": f_land, "civil_cost_cr": f_civil,
            "pm_cost_cr": f_pm, "utility_cost_cr": f_util, "preop_cr": f_preop, "wc_cr": f_wc,
            "selling_price_pmb_per_mt": f_pmb_sell, "vg10_price_per_mt": f_vg10,
            "rm_husk_price_per_mt": f_husk_pr, "husk_per_mt_output": f_husk_rat,
            "vg10_per_mt_pmb": f_vg10_rat, "pmb_output_pct": f_pmb_pct,
            "power_load_kw": f_pwr_kw, "power_rate_rs_per_kwh": f_pwr_rate,
            "power_hours_per_day": f_pwr_hrs,
            "loan_amount_cr": f_loan, "loan_rate_pct": f_rate, "loan_tenure_yr": f_tenure,
            "roi_pct": f_roi, "irr_pct": f_irr, "dscr_yr3": f_dscr,
            "break_even_months": f_bev_m, "break_even_pct": f_bev_p,
            "plot_area_sqm": f_plot, "built_up_sqm": f_builtup, "water_demand_lpd": f_water,
            "electricity_noc_kw": f_noc_kw, "pollution_category": f_pol_cat,
            "factory_workers": f_workers,
        }
        save_gs(new_data)
        st.success("Saved! Re-running audit…")
        st.rerun()

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("♻️ Reset to Bahadurgarh Defaults", use_container_width=True):
            save_gs(dict(GS_DEFAULTS))
            st.success("Reset to locked numbers.")
            st.rerun()
    with col_r2:
        st.download_button(
            "⬇ Download State JSON", json.dumps(data, indent=2),
            file_name="guarantor_state.json", mime="application/json",
        )


# ══════════════════════════════════════════════════════════════════════
# HELPER: render rules for a module
# ══════════════════════════════════════════════════════════════════════
def _render_module_rules(module_key, results):
    mh = module_health[module_key]
    icon = STATUS_ICON.get(mh["status"], "⚪")
    st.info(f"{icon} **{MODULE_NAMES[module_key]}** — {mh['pass']}/{mh['total']} rules passing | {WORKER_DESCRIPTIONS[module_key]}")

    module_results = get_rules_for_module(module_key, results)
    for r in module_results:
        s = r["status"]
        icon_r = STATUS_ICON.get(s, "⚪")
        bg = {"red": "#ffebee", "yellow": "#fff8e1", "green": "#f1f8e9", "grey": "#fafafa"}.get(s, "#fafafa")
        with st.expander(f"{icon_r} R{r['id']} — {r['name']}", expanded=(s in ("red", "yellow"))):
            st.markdown(
                f'<div style="background:{bg};padding:10px;border-radius:6px;">'
                f'<strong>Status:</strong> {s.upper()}<br>'
                f'<strong>Audit:</strong> {r["message"]}'
                f'</div>',
                unsafe_allow_html=True,
            )
            if r["details"]:
                det_df = pd.DataFrame([r["details"]])
                st.dataframe(det_df, use_container_width=True, hide_index=True)
            if s in ("red", "yellow"):
                st.markdown("**Fix:** Update the relevant field in the 📊 Project Data tab and re-audit.")


# ══════════════════════════════════════════════════════════════════════
# TAB 3 — FINANCE AUDIT
# ══════════════════════════════════════════════════════════════════════
with tab_finance:
    st.subheader("💰 Finance Auditor — Rules 1-2, 7, 9-19")
    _render_module_rules("finance", results)


# ══════════════════════════════════════════════════════════════════════
# TAB 4 — ENGINEERING AUDIT
# ══════════════════════════════════════════════════════════════════════
with tab_eng:
    st.subheader("🏭 Engineering Auditor — Rules 3-6")
    _render_module_rules("engineering", results)


# ══════════════════════════════════════════════════════════════════════
# TAB 5 — MARKET AUDIT
# ══════════════════════════════════════════════════════════════════════
with tab_market:
    st.subheader("📊 Market Auditor — Rules 4, 7, 8, 19")
    _render_module_rules("market", results)


# ══════════════════════════════════════════════════════════════════════
# TAB 6 — COMPLIANCE AUDIT
# ══════════════════════════════════════════════════════════════════════
with tab_comply:
    st.subheader("📜 Compliance Auditor — Rules 5, 20")
    _render_module_rules("compliance", results)

    st.divider()
    st.markdown("#### Layout Auditor — Rule 6")
    _render_module_rules("layout", results)


# ══════════════════════════════════════════════════════════════════════
# TAB 7 — AI DEEP AUDIT
# ══════════════════════════════════════════════════════════════════════
with tab_ai:
    st.subheader("🤖 AI Deep Audit — Comprehensive Narrative Analysis")
    st.markdown(
        "The GUARANTOR master AI synthesises all 20 rule results + project numbers into a "
        "plain-English verdict, risk analysis, and ranked action plan. "
        "Uses best available LLM (Groq free key recommended)."
    )

    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("**Current rule status:**")
        for s_key, label in [("red","🔴 Red Flags"), ("yellow","🟡 Warnings"), ("green","🟢 Passing")]:
            n = score["counts"][s_key]
            if n > 0:
                st.markdown(f"- {label}: **{n}**")

    with col_b:
        if "ai_audit_result" in st.session_state:
            st.success(f"Last audit by: **{st.session_state.get('ai_audit_provider', '—')}**")

    if st.button("🤖 Run AI Deep Audit", type="primary", use_container_width=True, key="btn_ai_audit"):
        with st.spinner("GUARANTOR AI analysing all 20 rules + project numbers — 30-60s…"):
            result, prov = ai_deep_audit(data)
        st.session_state["ai_audit_result"] = result
        st.session_state["ai_audit_provider"] = prov
        st.rerun()

    if "ai_audit_result" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state["ai_audit_result"])
        st.download_button(
            "⬇ Download AI Audit Report",
            st.session_state["ai_audit_result"],
            file_name="guarantor_ai_audit.txt",
            mime="text/plain",
        )


# ══════════════════════════════════════════════════════════════════════
# TAB 8 — DPR READINESS
# ══════════════════════════════════════════════════════════════════════
with tab_dpr:
    st.subheader("📤 DPR Export Readiness")

    if can_export:
        st.success("🟢 ALL 20 RULES PASSING — DPR is ready for export")
        st.markdown("""
**What this means:**
- All financial numbers are internally consistent
- Plant capacity matches investment benchmark
- DSCR, ROI, IRR, break-even all within bank norms
- Pollution category correctly classified
- Power load and NOC are aligned

**Next steps:**
1. Go to **DPR Generator** page → export bank / investor / government DPR
2. Go to **Export Center** → download full submission package
3. Go to **Meeting Copilot** → prepare for bank presentation
        """)
    else:
        st.error(f"🔴 DPR EXPORT BLOCKED — {len(blocking)} red flag(s) to resolve")
        st.markdown("**Blocking issues (fix these first):**")
        for i, issue in enumerate(blocking, 1):
            st.markdown(
                f'<div class="block-bar">{i}. {issue}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("**How to fix:**")
        st.markdown("1. Go to **📊 Project Data** tab → update the flagged values")
        st.markdown("2. Click **💾 Save & Re-audit**")
        st.markdown("3. Return here — once all reds clear, DPR export unlocks")

    st.divider()
    st.subheader("20-Rule Quick Summary")
    rows = []
    for r in results:
        rows.append({
            "Rule": f"R{r['id']} — {r['name']}",
            "Status": STATUS_ICON.get(r["status"], "⚪"),
            "Message": r["message"][:100] + ("…" if len(r["message"]) > 100 else ""),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=550)

    st.download_button(
        "⬇ Download Readiness Report (JSON)",
        json.dumps({
            "project": data.get("project_name"),
            "audit_date": str(__import__("datetime").date.today()),
            "can_export_dpr": can_export,
            "score": score,
            "blocking_issues": blocking,
            "rules": [{"id": r["id"], "name": r["name"], "status": r["status"],
                        "message": r["message"]} for r in results],
        }, indent=2),
        file_name="dpr_readiness_report.json",
        mime="application/json",
    )
