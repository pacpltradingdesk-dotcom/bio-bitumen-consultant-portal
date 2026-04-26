"""
Export Center — Centralized PDF/Excel/ZIP Export for All Dashboard Data
========================================================================
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import json
import io
import datetime
from state_manager import get_config, init_state
from database import init_db, get_all_customers, get_all_packages, get_all_communications
from document_index import build_index
from config import (COMPANY, NHAI_TENDERS, COMPETITORS, PPS_SWOT, RISK_REGISTRY,
                    ENVIRONMENTAL_FACTORS, INDUSTRY_NEWS, LICENSE_TYPES,
                    STATE_SCORES, LOCATION_WEIGHTS, STATES, STATE_COSTS)

st.set_page_config(page_title="Export Center", page_icon="📤", layout="wide")
init_db()
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass


st.title("Export Center")
st.markdown("**One-Click Export for All Dashboard Data — CSV, Excel, Text Reports**")
st.markdown("---")

now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# ══════════════════════════════════════════════════════════════════════
# EXPORT CATEGORIES
# ══════════════════════════════════════════════════════════════════════

tab_fin, tab_market, tab_crm, tab_compliance, tab_full, tab_master = st.tabs([
    "Financial Report", "Market & Tenders", "CRM Data", "Compliance",
    "Full Project Report", "🔗 Master Export"
])

# ── TAB 1: Financial Report ──────────────────────────────────────────
with tab_fin:
    st.subheader("Financial Model Export")

    fin_report = f"""BIO BITUMEN FINANCIAL MODEL — EXPORT REPORT
{'='*60}
Generated: {now_str}
Company: {COMPANY['name']}
Prepared by: {COMPANY['owner']}

PLANT CONFIGURATION
{'─'*40}
Capacity:           {cfg['capacity_tpd']:.0f} MT/Day
Working Days:       {cfg['working_days']}
Annual Output:      {cfg['capacity_tpd'] * cfg['working_days']:.0f} MT

INVESTMENT STRUCTURE
{'─'*40}
Total Investment:   Rs {cfg['investment_cr']:.2f} Crore
Loan Component:     Rs {cfg['loan_cr']:.2f} Crore
Equity Component:   Rs {cfg['equity_cr']:.2f} Crore
Interest Rate:      {cfg['interest_rate']*100:.1f}%
Monthly EMI:        Rs {cfg['emi_lac_mth']:.2f} Lakhs

KEY FINANCIAL METRICS
{'─'*40}
ROI:                {cfg['roi_pct']:.1f}%
IRR:                {cfg['irr_pct']:.1f}%
DSCR Year 3:        {cfg['dscr_yr3']:.2f}x
Break-Even:         {cfg['break_even_months']} months
Revenue Year 5:     Rs {cfg['revenue_yr5_lac']:.0f} Lakhs
Monthly Profit:     Rs {cfg['monthly_profit_lac']:.1f} Lakhs
Profit per MT:      Rs {cfg['profit_per_mt']:,.0f}

REVENUE BREAKDOWN (Year 5 @ 85% utilization)
{'─'*40}
Selling Price:      Rs {cfg['selling_price_per_mt']:,}/MT
Biochar Revenue:    Rs {cfg['biochar_price_per_mt']:,}/MT
Total Variable Cost: Rs {cfg['total_variable_cost_per_mt']:,}/MT
"""

    if cfg.get("roi_timeline"):
        fin_report += f"\n7-YEAR P&L PROJECTION\n{'─'*40}\n"
        fin_report += "Year | Revenue | Variable Cost | Fixed Cost | PAT | DSCR\n"
        for row in cfg["roi_timeline"]:
            fin_report += f"  {row['Year']}  | Rs {row['Revenue (Lac)']:.0f}L | Rs {row['Variable Cost (Lac)']:.0f}L | Rs {row['Fixed Cost (Lac)']:.0f}L | Rs {row['PAT (Lac)']:.0f}L | {row['DSCR']:.2f}x\n"

    fin_report += f"\n{'='*60}\n{COMPANY['name']} | {COMPANY['phone']}\n"

    st.text_area("Preview", fin_report, height=400)
    st.download_button("Download Financial Report (TXT)", fin_report,
                        f"Financial_Report_{cfg['capacity_tpd']:.0f}TPD.txt", "text/plain")

    # Excel export
    if st.button("Export P&L to Excel", key="fin_excel"):
        if cfg.get("roi_timeline"):
            pl_df = pd.DataFrame(cfg["roi_timeline"])
            buffer = io.BytesIO()
            pl_df.to_excel(buffer, index=False, sheet_name="P&L 7-Year")
            buffer.seek(0)
            st.download_button("Download Excel", buffer.getvalue(),
                                f"PL_{cfg['capacity_tpd']:.0f}TPD.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key="dl_fin_excel")

# ── TAB 2: Market & Tenders ──────────────────────────────────────────
with tab_market:
    st.subheader("Market Data & NHAI Tenders Export")

    # Tenders CSV
    tender_df = pd.DataFrame(NHAI_TENDERS)
    csv_tenders = tender_df.to_csv(index=False)
    st.download_button("Download NHAI Tenders (CSV)", csv_tenders, "nhai_tenders.csv", "text/csv")

    # Competitors CSV
    comp_df = pd.DataFrame(COMPETITORS)
    csv_comp = comp_df.to_csv(index=False)
    st.download_button("Download Competitors (CSV)", csv_comp, "competitors.csv", "text/csv")

    # State Analysis
    state_data = []
    for state in STATES:
        scores = STATE_SCORES.get(state, {})
        costs = STATE_COSTS.get(state, {})
        total = sum(scores.get(k, 50) * LOCATION_WEIGHTS[k] for k in LOCATION_WEIGHTS)
        state_data.append({"State": state, "Score": round(total, 1), **scores, **costs})
    state_df = pd.DataFrame(state_data)
    csv_states = state_df.to_csv(index=False)
    st.download_button("Download State Analysis (CSV)", csv_states, "state_analysis.csv", "text/csv")

    # Industry News
    news_df = pd.DataFrame(INDUSTRY_NEWS)
    csv_news = news_df.to_csv(index=False)
    st.download_button("Download Industry News (CSV)", csv_news, "industry_news.csv", "text/csv")

# ── TAB 3: CRM Data ─────────────────────────────────────────────────
with tab_crm:
    st.subheader("Customer & Communication Data Export")

    customers = get_all_customers()
    packages = get_all_packages()
    comms = get_all_communications()

    if customers:
        cust_df = pd.DataFrame(customers)
        st.download_button("Download Customers (CSV)", cust_df.to_csv(index=False),
                            "customers.csv", "text/csv")
        st.metric("Customers", len(customers))
    else:
        st.info("No customer data to export")

    if packages:
        pkg_df = pd.DataFrame(packages)
        st.download_button("Download Packages (CSV)", pkg_df.to_csv(index=False),
                            "packages.csv", "text/csv")

    if comms:
        comm_df = pd.DataFrame(comms)
        st.download_button("Download Communications (CSV)", comm_df.to_csv(index=False),
                            "communications.csv", "text/csv")

# ── TAB 4: Compliance ───────────────────────────────────────────────
with tab_compliance:
    st.subheader("License & Compliance Export")

    lic_df = pd.DataFrame(LICENSE_TYPES)
    st.download_button("Download License Master List (CSV)", lic_df.to_csv(index=False),
                        "license_types.csv", "text/csv")

    risk_df = pd.DataFrame(RISK_REGISTRY)
    risk_df["score"] = risk_df["probability"] * risk_df["impact"]
    st.download_button("Download Risk Register (CSV)", risk_df.to_csv(index=False),
                        "risk_register.csv", "text/csv")

# ── TAB 5: Full Project Report ──────────────────────────────────────
with tab_full:
    st.subheader("Complete Project Report (All-in-One)")

    full_report = f"""{'='*70}
BIO BITUMEN PROJECT — COMPLETE REPORT
{COMPANY['name']} | {COMPANY['owner']}
Generated: {now_str}
{'='*70}

1. COMPANY PROFILE
{'─'*50}
Name:          {COMPANY['name']}
Trade Name:    {COMPANY['trade_name']}
Owner:         {COMPANY['owner']}
Experience:    {COMPANY['experience']}
Phone:         {COMPANY['phone']}
Email:         {COMPANY['email']}
HQ:            {COMPANY['hq']}
GST:           {COMPANY['gst']}
CIN:           {COMPANY['cin']}

2. PLANT CONFIGURATION
{'─'*50}
Capacity:          {cfg['capacity_tpd']:.0f} MT/Day
Investment:        Rs {cfg['investment_cr']:.2f} Crore
ROI:               {cfg['roi_pct']:.1f}%
IRR:               {cfg['irr_pct']:.1f}%
Break-Even:        {cfg['break_even_months']} months
DSCR Yr3:          {cfg['dscr_yr3']:.2f}x
Monthly Profit:    Rs {cfg['monthly_profit_lac']:.1f} Lakhs

3. MARKET OPPORTUNITY
{'─'*50}
India Bitumen Consumption:  {ENVIRONMENTAL_FACTORS['india_annual_bitumen_consumption_mt']:,} MT/year
Import Dependency:          {ENVIRONMENTAL_FACTORS['india_import_dependency_pct']}%
Plants Needed (5-7 years):  130-216
NHAI Open Tenders:          {len([t for t in NHAI_TENDERS if t['status']=='Open'])}
Tender Value:               Rs {sum(t['budget_cr'] for t in NHAI_TENDERS if t['status']=='Open'):,} Crore

4. COMPETITIVE LANDSCAPE
{'─'*50}
Competitors Tracked:  {len(COMPETITORS)}
High Threat:          {len([c for c in COMPETITORS if c['threat_level']=='High'])}
PPS Advantage:        {COMPANY['usp']}

5. SWOT ANALYSIS
{'─'*50}
STRENGTHS:
"""
    for s in PPS_SWOT["strengths"]:
        full_report += f"  + {s}\n"
    full_report += "\nWEAKNESSES:\n"
    for w in PPS_SWOT["weaknesses"]:
        full_report += f"  - {w}\n"
    full_report += "\nOPPORTUNITIES:\n"
    for o in PPS_SWOT["opportunities"]:
        full_report += f"  * {o}\n"
    full_report += "\nTHREATS:\n"
    for t in PPS_SWOT["threats"]:
        full_report += f"  ! {t}\n"

    full_report += f"""
6. ENVIRONMENTAL IMPACT
{'─'*50}
CO2 Saved/Year:       {cfg['capacity_tpd'] * 300 * ENVIRONMENTAL_FACTORS['co2_saved_per_mt_bio_bitumen']:,.0f} tonnes
Carbon Credit Rev:    Rs {cfg['capacity_tpd'] * 300 * ENVIRONMENTAL_FACTORS['co2_saved_per_mt_bio_bitumen'] * ENVIRONMENTAL_FACTORS['carbon_credit_rate_usd'] * ENVIRONMENTAL_FACTORS['usd_inr_for_calc'] / 100000:.1f} Lac/year
Stubble Diverted:     {cfg['capacity_tpd'] * 300 * ENVIRONMENTAL_FACTORS['stubble_diverted_per_mt_output']:,.0f} MT/year

7. RISK SUMMARY
{'─'*50}
Total Risks:     {len(RISK_REGISTRY)}
High/Critical:   {len([r for r in RISK_REGISTRY if r['probability']*r['impact'] >= 12])}
Top Risk:        {max(RISK_REGISTRY, key=lambda r: r['probability']*r['impact'])['risk'][:60]}

8. CRM SUMMARY
{'─'*50}
Total Customers: {len(customers)}
Active Pipeline: {sum(1 for c in customers if c.get('status') not in ('Closed Won','Closed Lost'))}
Industry Network: {COMPANY['industry_contacts']:,} contacts

{'='*70}
Report prepared by {COMPANY['trade_name']} Bio Bitumen Consulting System
Contact: {COMPANY['phone']} | {COMPANY['email']}
{'='*70}
"""

    st.text_area("Preview Full Report", full_report, height=500)
    st.download_button("Download Full Project Report (TXT)", full_report,
                        f"Bio_Bitumen_Full_Report_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                        "text/plain")

# ── TAB 6: Master Export (all engines connected) ─────────────────────
with tab_master:
    st.subheader("Master Export — All Portal Data in One Click")
    st.caption("Pulls Financial + Carbon + Govt Schemes + Viability Rating into every export")

    mx1, mx2, mx3, mx4 = st.columns(4)
    mx1.metric("Revenue (Yr3)",   f"₹ {cfg.get('revenue_lac',0):.0f} Lac")
    mx2.metric("Net Profit (Yr3)",f"₹ {cfg.get('net_profit_lac',0):.0f} Lac")
    mx3.metric("Output TPD",      f"{cfg.get('output_tpd',0):.1f} TPD")
    mx4.metric("Biomass Cost",    f"₹ {cfg.get('biomass_price_per_mt',0):.0f}/MT")

    if st.button("🔗 Run All Engines & Build Master Export", type="primary", key="master_export_btn"):
        with st.spinner("Running carbon, scheme, rating engines…"):
            try:
                from engines.master_connector import get_full_project_data, save_full_snapshot
                full = get_full_project_data(cfg, run_engines=True)
                st.session_state["master_export_data"] = full
                snap_path = save_full_snapshot(cfg)
                st.success(
                    f"✅ All engines complete — "
                    f"CO₂: {full.get('total_co2_saved_tpa',0):,.0f} tCO₂e/yr  |  "
                    f"Schemes: {full.get('schemes_count',0)}  |  "
                    f"Grade: {full.get('viability_grade','—')}  |  "
                    f"Snapshot: {snap_path.name}"
                )
            except Exception as e:
                st.error(f"Master export error: {e}")

    full = st.session_state.get("master_export_data")
    if full:
        st.markdown("---")
        ecols = st.columns(3)

        # Export 1: Complete Summary TXT
        summary_lines = [
            f"BIO BITUMEN MASTER PROJECT EXPORT",
            f"Generated: {now_str}",
            f"{'='*60}",
            f"Project: {full.get('project_name','')}",
            f"Client:  {full.get('client_name','')}",
            f"Location:{full.get('location','')}, {full.get('state','')}",
            f"Capacity:{full.get('capacity_tpd',20)} TPD  |  Output: {full.get('output_tpd',0):.1f} TPD",
            f"",
            f"FINANCIALS",
            f"  Investment    : {full.get('fmt_investment','')}",
            f"  Revenue Yr3   : {full.get('fmt_revenue','')}",
            f"  Net Profit Yr3: {full.get('fmt_net_profit','')}",
            f"  Gross Profit  : {full.get('fmt_gross_profit','')}",
            f"  IRR           : {full.get('fmt_irr','')}",
            f"  ROI           : {full.get('fmt_roi','')}",
            f"  Break-even    : {full.get('break_even_str','')}",
            f"  Monthly EMI   : {full.get('fmt_emi','')}",
            f"  Biomass Cost  : ₹ {full.get('biomass_price_per_mt',0):.0f}/MT (weighted avg)",
            f"",
            f"CARBON PROFILE",
            f"  CO₂ Saved/yr  : {full.get('total_co2_saved_tpa',0):,.0f} tCO₂e",
            f"  Carbon Revenue: {full.get('fmt_carbon_rev','')}",
            f"  Best Scheme   : {full.get('best_carbon_scheme','')}",
            f"  Trees Equiv   : {full.get('trees_equivalent',0):,}",
            f"",
            f"GOVT SCHEMES",
            f"  Schemes Found : {full.get('schemes_count',0)}",
            f"  Total Benefit : {full.get('fmt_schemes_total','')}",
            f"",
            f"VIABILITY RATING",
            f"  Grade: {full.get('viability_grade','—')}  Score: {full.get('viability_score',0)}/100",
            f"  Label: {full.get('viability_label','')}",
        ]
        summary_txt = "\n".join(summary_lines)
        with ecols[0]:
            st.download_button(
                "⬇ Complete Summary TXT",
                summary_txt,
                f"master_summary_{datetime.datetime.now():%Y%m%d}.txt",
                "text/plain", key="dl_master_txt",
            )

        # Export 2: Full JSON snapshot
        import json as _json
        json_str = _json.dumps(
            {k: v for k, v in full.items()
             if not isinstance(v, (bytes, type(None))) and k not in ("carbon", "schemes", "rating")},
            indent=2, ensure_ascii=False, default=str
        )
        with ecols[1]:
            st.download_button(
                "⬇ Full JSON Snapshot",
                json_str,
                f"project_snapshot_{datetime.datetime.now():%Y%m%d}.json",
                "application/json", key="dl_master_json",
            )

        # Export 3: Schemes CSV
        if full.get("schemes"):
            schemes_df = pd.DataFrame([{
                "Scheme": s.get("name",""), "Type": s.get("type",""),
                "Category": s.get("category",""), "Ministry": s.get("ministry",""),
                "Benefit": s.get("benefit_type",""),
                "Rate %": s.get("benefit_pct",""),
                "Est Benefit Cr": s.get("est_benefit_cr",0),
                "Apply At": s.get("apply_at",""),
            } for s in full["schemes"]])
            with ecols[2]:
                st.download_button(
                    "⬇ Schemes + Subsidies CSV",
                    schemes_df.to_csv(index=False),
                    f"schemes_{cfg.get('state','')[:5]}_{datetime.datetime.now():%Y%m%d}.csv",
                    "text/csv", key="dl_master_schemes",
                )

st.markdown("---")
st.caption(f"{COMPANY['name']} | Export Center")


# ── AI Skill: Export Summary ──────────────────────────────────────
st.markdown("---")
try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("🤖 AI: Export Summary"):
            if st.button("Generate", type="primary", key="ai_67Expor"):
                with st.spinner("AI working..."):
                    _p = f"As a senior bio-bitumen consultant, generate: Export Summary. "
                    _p += f"Plant: {cfg.get('capacity_tpd',20):.0f} TPD, Investment: Rs {cfg.get('investment_cr',8):.2f} Cr, "
                    _p += f"Location: {cfg.get('location','')}, {cfg.get('state','')}. "
                    _p += "Be specific with numbers. Professional format."
                    _r, _pv = ask_ai(_p, "Senior industrial consultant.", 1000)
                if _r:
                    st.markdown(_r)
except Exception:
    pass

# Print
if st.sidebar.button("Print", key="prt_67Exp"):
    import streamlit.components.v1 as _stc
    _stc.html("<script>window.print();</script>", height=0)


# ── Next Steps Navigation ──
try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "62")
except Exception:
    pass
