"""
Bio Bitumen Master Consulting System — AI Advisor (UPGRADED)
==============================================================
100+ Q&A patterns covering subsidies, loans, insurance, HR, safety,
carbon credits, exports, market data, and more.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from state_manager import get_config, init_state
from interpolation_engine import get_all_known_plants
from config import (STATES, STATE_SCORES, LOCATION_WEIGHTS, LICENSE_TYPES, COMPANY,
                    NHAI_TENDERS, COMPETITORS, RISK_REGISTRY, ENVIRONMENTAL_FACTORS,
                    EMI_PRESETS, TRAINING_MODULES, INDUSTRY_NEWS, STATE_COSTS,
                    FOUR_STAGES, TARGET_AUDIENCES, CONSULTING_SERVICES,
                    KEY_CREDENTIALS, GETKA_CONTRACT, WHY_NOW, PPS_SWOT)

st.set_page_config(page_title="AI Advisor", page_icon="🤖", layout="wide")
init_state()
st.title("AI Business Advisor")
st.markdown("**100+ Topics | Bio-Bitumen Plant Setup | Financial, Technical, Legal, Market Intelligence**")
st.markdown("---")

cfg = get_config()
plants = get_all_known_plants()

# ══════════════════════════════════════════════════════════════════════
# EXPANDED KNOWLEDGE BASE — 100+ Patterns
# ══════════════════════════════════════════════════════════════════════
def answer_question(query):
    q = query.lower().strip()

    # ── 1. Capacity/Investment ───────────────────────────────────────
    if any(w in q for w in ["capacity", "how much", "investment", "cost", "budget"]):
        for tpd_str in ["5", "10", "15", "20", "30", "40", "50"]:
            if tpd_str in q and (f"{tpd_str} mt" in q or f"{tpd_str}mt" in q or f"{tpd_str} tpd" in q):
                key = f"{int(tpd_str):02d}MT"
                if key in plants:
                    p = plants[key]
                    return (f"**{p.get('label', key)} Plant:**\n"
                            f"- Investment: Rs {p['inv_cr']} Crore\n"
                            f"- Loan: Rs {p['loan_cr']} Cr | Equity: Rs {p['equity_cr']} Cr\n"
                            f"- Revenue Yr5: Rs {p['rev_yr5_cr']} Cr\n"
                            f"- Staff: {p['staff']} | Power: {p['power_kw']} kW\n"
                            f"- IRR: {p['irr_pct']}% | DSCR Yr3: {p['dscr_yr3']}x\n\n"
                            f"*Use ROI Quick Calculator for interactive analysis.*")

        for amount in [1, 2, 3, 4, 5, 8, 10, 12, 14, 15, 16, 20, 30]:
            if f"{amount} cr" in q or f"{amount} crore" in q:
                best = None
                for key, p in plants.items():
                    if p["inv_cr"] <= amount:
                        best = p
                if best:
                    return (f"For Rs {amount} Crore budget, best option: **{best.get('label', '')}**\n"
                            f"- Investment: Rs {best['inv_cr']} Cr | IRR: {best['irr_pct']}%\n"
                            f"- Revenue Yr5: Rs {best['rev_yr5_cr']} Cr\n\n"
                            f"*See Capacity Compare tool for side-by-side analysis.*")

        lines = ["**Available Plant Capacities:**\n"]
        for key, p in plants.items():
            lines.append(f"- {p.get('label', key)}: Rs {p['inv_cr']} Cr | Rev Yr5: Rs {p['rev_yr5_cr']} Cr | IRR: {p['irr_pct']}%")
        return "\n".join(lines)

    # ── 2. Location ──────────────────────────────────────────────────
    if any(w in q for w in ["location", "state", "where", "best place", "which state", "site selection"]):
        for state in STATES:
            if state.lower() in q:
                s = STATE_SCORES.get(state, {})
                sc = STATE_COSTS.get(state, {})
                total = sum(s.get(k, 50) * LOCATION_WEIGHTS[k] for k in LOCATION_WEIGHTS)
                return (f"**{state} Feasibility Analysis:**\n"
                        f"- Overall Score: **{total:.1f}/100**\n"
                        f"- Biomass: {s.get('biomass', 50)}/100 | Subsidy: {s.get('subsidy', 50)}/100\n"
                        f"- Logistics: {s.get('logistics', 50)}/100 | Power: {s.get('power', 50)}/100\n\n"
                        f"**Cost Factors:**\n"
                        f"- Power Rate: Rs {sc.get('power_rate', 7)}/kWh\n"
                        f"- Labor: Rs {sc.get('labor_daily', 400)}/day\n"
                        f"- Land: Rs {sc.get('land_lac_acre', 10)} Lac/acre\n"
                        f"- Biomass: Rs {sc.get('biomass_cost_mt', 2000)}/MT\n"
                        f"- Subsidy: {sc.get('subsidy_pct', 15)}%\n"
                        f"- Nearest Refinery: {sc.get('refinery_dist_km', 300)} km\n"
                        f"- Bitumen Demand: {sc.get('bitumen_demand_mt', 0):,} MT/yr")

        scores = [(s, sum(STATE_SCORES.get(s, {}).get(k, 50) * LOCATION_WEIGHTS[k] for k in LOCATION_WEIGHTS)) for s in STATES]
        scores.sort(key=lambda x: -x[1])
        lines = ["**Top 5 States for Bio-Bitumen Plant:**\n"]
        for state, score in scores[:5]:
            lines.append(f"- **{state}**: Score {score:.1f}/100")
        lines.append("\n*Use Location Analysis page for detailed comparison.*")
        return "\n".join(lines)

    # ── 3. Licenses & Compliance ─────────────────────────────────────
    if any(w in q for w in ["license", "compliance", "approval", "permit", "noc", "gst", "registration",
                              "peso", "factory", "pollution", "consent", "cte", "cto"]):
        if "peso" in q:
            return ("**PESO License (Petroleum & Explosives Safety Organisation):**\n"
                    "- Authority: PESO, Nagpur\n- Timeline: ~90 days\n- Mandatory for bitumen storage >1000 liters\n"
                    "- Requirements: Site plan, safety equipment list, fire NOC, insurance\n"
                    "- Apply at: peso.gov.in\n- Consultant fee: Rs 50,000-1,00,000")
        if "cte" in q or "consent to establish" in q:
            return ("**Consent to Establish (CTE):**\n"
                    "- Authority: State Pollution Control Board\n- Timeline: ~60 days\n"
                    "- Apply BEFORE construction starts\n- Documents: Site plan, EIA, process flow, emission data\n"
                    "- Fee: Rs 25,000-1,00,000 (varies by state)\n- Validity: 5 years")
        if "fire" in q:
            return ("**Fire NOC:**\n"
                    "- Authority: State Fire Department\n- Timeline: ~30 days\n"
                    "- Requirements: Fire safety plan, equipment list, escape routes, water storage\n"
                    "- Annual renewal required\n- Fee: Rs 5,000-25,000")

        mandatory = [lt for lt in LICENSE_TYPES if lt.get("mandatory")]
        lines = [f"**{len(mandatory)} Mandatory Licenses Required:**\n"]
        for lt in mandatory[:15]:
            lines.append(f"- **{lt['name']}** — {lt['authority']} (~{lt['typical_days']} days)")
        if len(mandatory) > 15:
            lines.append(f"\n...and {len(mandatory)-15} more.")
        lines.append("\n*See Compliance Tracker for full tracking per customer.*")
        return "\n".join(lines)

    # ── 4. Financial / ROI / IRR ─────────────────────────────────────
    if any(w in q for w in ["revenue", "profit", "return", "roi", "irr", "dscr", "break even", "payback"]):
        return (f"**Current Configuration — Financial Summary:**\n"
                f"- Capacity: {cfg['capacity_tpd']:.0f} MT/Day\n"
                f"- Investment: Rs {cfg['investment_cr']:.2f} Cr\n"
                f"- ROI: {cfg['roi_pct']:.1f}% | IRR: {cfg['irr_pct']:.1f}%\n"
                f"- Revenue Yr5: Rs {cfg['revenue_yr5_lac']:.0f} Lac\n"
                f"- Monthly Profit: Rs {cfg['monthly_profit_lac']:.1f} Lac\n"
                f"- EMI: Rs {cfg['emi_lac_mth']:.2f} Lac/month\n"
                f"- DSCR Yr3: {cfg['dscr_yr3']:.2f}x\n"
                f"- Break-Even: Month {cfg['break_even_month']}\n\n"
                f"*Use Financial Model page to edit inputs and see live updates.*\n"
                f"*Use ROI Quick Calculator for instant projector demos.*")

    # ── 5. Compare ───────────────────────────────────────────────────
    if "compare" in q:
        lines = ["**All 7 Capacities Comparison:**\n"]
        lines.append("| Capacity | Investment | Revenue Yr5 | IRR | DSCR |")
        lines.append("|----------|-----------|-------------|-----|------|")
        for key, p in plants.items():
            lines.append(f"| {p.get('label', key)} | Rs {p['inv_cr']} Cr | Rs {p['rev_yr5_cr']} Cr | {p['irr_pct']}% | {p['dscr_yr3']}x |")
        lines.append("\n*Use Capacity Compare tool for detailed side-by-side analysis.*")
        return "\n".join(lines)

    # ── 6. Raw Material / Biomass ────────────────────────────────────
    if any(w in q for w in ["raw material", "biomass", "feedstock", "agro waste", "rice straw",
                              "pellet", "farmer", "stubble"]):
        return ("**Raw Material (Biomass) Details:**\n"
                "- **Types:** Rice straw, sugarcane bagasse, cotton stalk, groundnut shell, wheat straw\n"
                f"- **Cost:** Rs {cfg.get('biomass_cost_per_mt', 2000):,}/MT delivered\n"
                "- **Source:** Farmer cooperatives within 50-100 km radius\n"
                "- **Availability:** Year-round (seasonal peaks: Oct-Dec for rice, Mar-May for wheat)\n"
                f"- **Daily Requirement:** {cfg.get('biomass_mt_day', 20):.0f} MT/day for {cfg['capacity_tpd']:.0f} TPD\n"
                "- **Storage:** 90-day buffer recommended (pelletized form)\n"
                "- **Top Biomass States:** Punjab (90), UP (90), Haryana (85), MP (85), Bihar (80)\n\n"
                "**India burns 15 Crore MT of crop residue annually — huge opportunity!**")

    # ── 7. Process / Technology ──────────────────────────────────────
    if any(w in q for w in ["process", "technology", "how it works", "pyrolysis", "bio-oil",
                              "temperature", "vg30", "blending", "krishibind"]):
        return ("**Bio-Modified Bitumen Technology (CSIR-CRRI Licensed):**\n\n"
                "**4 Stages:**\n"
                "1. **Raw Material Procurement & Pelletization** — Collect agro-waste, process into pellets\n"
                "2. **Pyrolysis & Bio-Oil Extraction** — Heat at 450-550C in oxygen-free reactor\n"
                "   - Yields: Bio-Oil 40% | Biochar 30% | Syngas 25% | Loss 5%\n"
                "3. **Bio-Oil Refining & Blending** — Oxidize at 230-250C, blend 15-30% with VG-30\n"
                "4. **Testing & Marketing** — IS:73 compliance testing, sell to NHAI/PWD contractors\n\n"
                "**Key Product: KrishiBind** — CSIR-CRRI validated bio-binder\n"
                "- 22% less rutting vs conventional | 18% better fatigue life\n"
                "- Meets all MoRTH 2026 specifications")

    # ── 8. Subsidy / Government Schemes ──────────────────────────────
    if any(w in q for w in ["subsidy", "scheme", "mnre", "waste to wealth", "government help",
                              "grant", "incentive", "capital subsidy"]):
        return ("**Government Subsidies & Schemes for Bio-Bitumen:**\n\n"
                "1. **MNRE Waste-to-Wealth Mission** — 25% capital subsidy\n"
                "   - Eligible: All bio-bitumen plants using agro-waste\n"
                "   - Apply through: mnre.gov.in\n\n"
                "2. **State MSME Subsidies** — 15-25% (varies by state)\n"
                "   - Gujarat: 20% | MP: 25% | Rajasthan: 25% | UP: 20%\n\n"
                "3. **CGTMSE** — Collateral-free loan guarantee up to Rs 5 Cr\n\n"
                "4. **Pradhan Mantri MUDRA Yojana** — Up to Rs 10 Lakh (micro units)\n\n"
                "5. **Technology Development Board** — Up to 50% for new technology\n\n"
                "6. **BIRAC/DBT** — Bio-technology innovation grants\n\n"
                "7. **Carbon Credits** — Rs 1,000-1,500/tonne CO2 saved\n\n"
                "**Total potential subsidy: 25-40% of project cost!**")

    # ── 9. Loan / Bank / EMI ─────────────────────────────────────────
    if any(w in q for w in ["loan", "bank", "emi", "finance", "cgtmse", "mudra", "interest",
                              "collateral", "sanction", "disbursement"]):
        if "cgtmse" in q:
            return ("**CGTMSE (Credit Guarantee Fund Trust):**\n"
                    "- Collateral-free loans up to Rs 5 Crore\n"
                    "- Annual guarantee fee: 1.5% of loan amount\n"
                    "- Available at all scheduled banks\n"
                    "- Processing: 15-30 days after bank sanction\n"
                    "- Covers both term loan and working capital\n\n"
                    "*Use Loan EMI Calculator for detailed computation.*")
        lines = ["**Bank Loan Options:**\n"]
        for preset in EMI_PRESETS:
            lines.append(f"- **{preset['name']}** — {preset['interest_pct']}% | {preset['tenure_months']} months | Max Rs {preset['max_loan_cr']} Cr | Collateral: {preset['collateral']}")
        lines.append(f"\n**For {cfg['capacity_tpd']:.0f} TPD plant:**")
        lines.append(f"- Total Investment: Rs {cfg['investment_cr']:.2f} Cr")
        lines.append(f"- Recommended Loan: Rs {cfg['investment_cr']*0.7:.2f} Cr (70%)")
        lines.append(f"- Current EMI: Rs {cfg['emi_lac_mth']:.2f} Lac/month")
        lines.append("\n*Use Loan EMI Calculator for detailed amortization.*")
        return "\n".join(lines)

    # ── 10. Insurance ────────────────────────────────────────────────
    if any(w in q for w in ["insurance", "risk cover", "fire insurance", "liability"]):
        return ("**Insurance Requirements for Bio-Bitumen Plant:**\n\n"
                "1. **Property Insurance** — Covers plant, machinery, building\n"
                "   - Premium: ~0.5% of asset value/year\n"
                "   - Mandatory for bank loan\n\n"
                "2. **Public Liability Insurance** — Covers third-party injury/damage\n"
                "   - Premium: Rs 50,000-2,00,000/year\n"
                "   - Mandatory under Public Liability Insurance Act\n\n"
                "3. **Fire Insurance** — Covers fire, explosion, lightning\n"
                "   - Critical for pyrolysis plants (high-temp operations)\n\n"
                "4. **Workers Compensation** — Covers employee injuries\n"
                "   - Mandatory under Workmen's Compensation Act\n\n"
                "5. **Marine Insurance** — For VG-30 import shipments\n\n"
                f"**Estimated annual premium for {cfg['capacity_tpd']:.0f} TPD: Rs 3-8 Lac**")

    # ── 11. HR / Manpower / Staffing ─────────────────────────────────
    if any(w in q for w in ["staff", "employee", "manpower", "hiring", "salary", "hr",
                              "worker", "operator", "team"]):
        return (f"**Manpower Requirements ({cfg['capacity_tpd']:.0f} TPD Plant):**\n\n"
                "| Role | Count | Monthly Salary |\n"
                "|------|-------|----------------|\n"
                "| Plant Manager | 1 | Rs 60,000-80,000 |\n"
                "| Shift Supervisor | 2 | Rs 30,000-40,000 |\n"
                "| Reactor Operators | 4-6 | Rs 18,000-25,000 |\n"
                "| Lab Technician | 1-2 | Rs 20,000-30,000 |\n"
                "| Electrician | 1 | Rs 20,000-25,000 |\n"
                "| Helpers/Loaders | 6-10 | Rs 12,000-15,000 |\n"
                "| Drivers | 2-3 | Rs 15,000-20,000 |\n"
                "| Office/Accounts | 2 | Rs 20,000-30,000 |\n"
                "| Security | 2-3 | Rs 12,000-15,000 |\n\n"
                f"**Total Staff: 20-30 people**\n"
                f"**Monthly Salary Bill: Rs 4-8 Lac**\n\n"
                "*Training modules available in Training & Knowledge Base page.*")

    # ── 12. Safety ───────────────────────────────────────────────────
    if any(w in q for w in ["safety", "fire", "ppe", "hazard", "emergency", "explosion"]):
        return ("**Safety Requirements for Bio-Bitumen Plant:**\n\n"
                "1. **Fire Safety:**\n"
                "   - 5-meter safety zone around pyrolysis reactor\n"
                "   - Fire extinguishers (CO2 + DCP) at every section\n"
                "   - Fire hydrant system with dedicated water storage\n"
                "   - Fire alarm system + smoke detectors\n\n"
                "2. **PPE Requirements:**\n"
                "   - Safety helmets, goggles, heat-resistant gloves\n"
                "   - Safety shoes (steel toe), fire-retardant clothing\n"
                "   - Ear protection (near crusher/shredder)\n\n"
                "3. **Emergency Systems:**\n"
                "   - Emergency shutdown system for reactor\n"
                "   - Gas leak detection (syngas monitoring)\n"
                "   - Eye wash stations, first aid rooms\n"
                "   - Evacuation plan with assembly point\n\n"
                "4. **Compliance:**\n"
                "   - PESO license for petroleum storage\n"
                "   - Fire NOC from State Fire Department\n"
                "   - Annual safety audit required")

    # ── 13. Carbon Credits / ESG / Environmental ─────────────────────
    if any(w in q for w in ["carbon", "esg", "environment", "green", "emission", "co2",
                              "sustainable", "stubble", "pollution"]):
        ef = ENVIRONMENTAL_FACTORS
        return (f"**Environmental Impact & Carbon Credits:**\n\n"
                f"**CO2 Savings:**\n"
                f"- {ef['co2_saved_per_mt_bio_bitumen']} tonnes CO2 saved per MT bio-bitumen\n"
                f"- For {cfg['capacity_tpd']:.0f} TPD plant (300 days): "
                f"**{cfg['capacity_tpd'] * 300 * ef['co2_saved_per_mt_bio_bitumen']:.0f} tonnes CO2/year**\n\n"
                f"**Carbon Credit Revenue:**\n"
                f"- Rate: ${ef['carbon_credit_rate_usd']}/tonne CO2 (voluntary market)\n"
                f"- Annual revenue: Rs {cfg['capacity_tpd'] * 300 * ef['co2_saved_per_mt_bio_bitumen'] * ef['carbon_credit_rate_usd'] * ef['usd_inr_for_calc'] / 100000:.1f} Lac/year\n\n"
                f"**Stubble Burning Impact:**\n"
                f"- {ef['stubble_diverted_per_mt_output']} MT crop residue used per MT output\n"
                f"- India burns {ef['annual_stubble_burning_india_mt']/10000000:.0f} Crore MT annually\n"
                f"- Bio-bitumen can utilize {ef['bio_bitumen_can_use_pct_of_stubble']}% of this waste\n\n"
                f"**NHAI Green Mandate:** {ef['nhai_green_mandate_replacement_pct']}% bio-bitumen in new projects by 2030\n\n"
                f"*See Environmental Impact Dashboard for detailed analysis.*")

    # ── 14. Export / International ───────────────────────────────────
    if any(w in q for w in ["export", "international", "import", "getka", "iraq", "vg-30 supply"]):
        gc = GETKA_CONTRACT
        return (f"**International Import/Export:**\n\n"
                f"**VG-30 Import Contract (Active):**\n"
                f"- Seller: {gc['seller']}\n"
                f"- Product: {gc['product']}\n"
                f"- Origin: {gc['origin']}\n"
                f"- Base Price: {gc['base_price']}\n"
                f"- Annual Schedule: {gc['annual_schedule_mt']:,} MT\n"
                f"- Payment: {gc['payment']}\n"
                f"- Quality: {gc['quality']}\n"
                f"- Signed: {gc['date_signed']}\n\n"
                f"**Export Potential:**\n"
                f"- Bio-bitumen demand growing in SE Asia, Africa, Middle East\n"
                f"- India can become net exporter with bio-bitumen replacing imports\n"
                f"- Current import dependency: {ENVIRONMENTAL_FACTORS['india_import_dependency_pct']}%")

    # ── 15. Competitors ──────────────────────────────────────────────
    if any(w in q for w in ["competitor", "competition", "market player", "who else", "rival"]):
        lines = ["**Bio-Bitumen Market Competitors:**\n"]
        for c in COMPETITORS:
            lines.append(f"- **{c['name']}** ({c['location']}) — {c['capacity_tpd']} TPD | "
                         f"Threat: {c['threat_level']} | {c['strengths'][:50]}...")
        lines.append(f"\n**PPS Anantams Advantage:** {COMPANY['usp']}")
        lines.append("\n*See Competitor Intelligence page for full SWOT analysis.*")
        return "\n".join(lines)

    # ── 16. NHAI Tenders ─────────────────────────────────────────────
    if any(w in q for w in ["tender", "nhai", "pwd", "bro", "road project", "bharatmala",
                              "pmgsy", "sagarmala"]):
        open_tenders = [t for t in NHAI_TENDERS if t["status"] == "Open"]
        total_budget = sum(t["budget_cr"] for t in open_tenders)
        total_bitumen = sum(t["bitumen_mt"] for t in open_tenders)
        lines = [f"**{len(open_tenders)} Open Tenders | Total: Rs {total_budget:,} Cr | Bitumen: {total_bitumen:,} MT**\n"]
        for t in open_tenders[:8]:
            lines.append(f"- **{t['id']}** — {t['project'][:50]} | {t['state']} | Rs {t['budget_cr']} Cr | {t['bitumen_mt']:,} MT | Deadline: {t['deadline']}")
        lines.append(f"\n*See NHAI Tender Tracker for full list with filters.*")
        return "\n".join(lines)

    # ── 17. Risk Assessment ──────────────────────────────────────────
    if any(w in q for w in ["risk", "danger", "threat", "challenge", "problem", "issue"]):
        high_risks = [r for r in RISK_REGISTRY if r["probability"] * r["impact"] >= 12]
        lines = ["**Top Risks for Bio-Bitumen Project:**\n"]
        for r in high_risks[:8]:
            score = r["probability"] * r["impact"]
            lines.append(f"- **{r['category']}** ({score}/25): {r['risk']}\n  *Mitigation: {r['mitigation'][:80]}...*")
        lines.append("\n*See Risk Matrix page for full heatmap analysis.*")
        return "\n".join(lines)

    # ── 18. Training / SOP ───────────────────────────────────────────
    if any(w in q for w in ["training", "sop", "learn", "course", "skill", "knowledge"]):
        lines = ["**Training Modules Available:**\n"]
        for tm in TRAINING_MODULES:
            lines.append(f"- **{tm['module']}** — {tm['category']} | {tm['duration_hrs']} hrs | For: {tm['audience']}")
        lines.append("\n*See Training & Knowledge Base for detailed content.*")
        return "\n".join(lines)

    # ── 19. News / Market Updates ────────────────────────────────────
    if any(w in q for w in ["news", "update", "latest", "recent", "what's new", "market update"]):
        lines = ["**Latest Industry News:**\n"]
        for n in INDUSTRY_NEWS[:8]:
            lines.append(f"- **[{n['date']}]** {n['title']}\n  *{n['summary'][:80]}...*")
        lines.append("\n*See News Feed page for full updates.*")
        return "\n".join(lines)

    # ── 20. About PPS / Consultant ───────────────────────────────────
    if any(w in q for w in ["who are you", "about", "consultant", "prince", "pps", "anantams",
                              "experience", "credential", "why you"]):
        lines = [f"**{COMPANY['trade_name']} — {COMPANY['tagline']}**\n"]
        lines.append(f"**Owner:** {COMPANY['owner']} | {COMPANY['experience']}\n")
        lines.append(f"**USP:** {COMPANY['usp']}\n\n")
        lines.append("**Key Credentials:**")
        for cred in KEY_CREDENTIALS:
            lines.append(f"- {cred}")
        lines.append(f"\n**SWOT Strengths:** {', '.join(PPS_SWOT['strengths'][:3])}")
        lines.append(f"\n**Contact:** {COMPANY['phone']} | {COMPANY['email']}")
        return "\n".join(lines)

    # ── 21. Why Now / Market Opportunity ─────────────────────────────
    if any(w in q for w in ["why now", "opportunity", "market size", "demand", "future",
                              "potential", "growth"]):
        lines = ["**Why Bio-Bitumen NOW?**\n"]
        for w in WHY_NOW:
            lines.append(f"- {w}")
        lines.append(f"\n**Market Size:** India consumes {ENVIRONMENTAL_FACTORS['india_annual_bitumen_consumption_mt']/100000:.0f} Lakh MT bitumen/year")
        lines.append(f"**Import Dependency:** {ENVIRONMENTAL_FACTORS['india_import_dependency_pct']}% — Rs 25,000+ Cr/year")
        lines.append("**Plants Needed:** 130-216 new plants in 5-7 years")
        return "\n".join(lines)

    # ── 22. Water / Power / Utilities ────────────────────────────────
    if any(w in q for w in ["water", "power", "electricity", "utility", "dg set", "diesel"]):
        return (f"**Utility Requirements ({cfg['capacity_tpd']:.0f} TPD):**\n\n"
                f"**Power:**\n"
                f"- Connected Load: {cfg.get('power_kw', 150)} kW\n"
                "- HT Connection required (>100 kW)\n"
                "- DG Set backup: 100% load capacity recommended\n"
                "- Annual power cost: Rs 15-30 Lac (depends on state tariff)\n\n"
                "**Water:**\n"
                "- Daily requirement: 20-50 KL (cooling, dust suppression, domestic)\n"
                "- Bore well + tanker backup\n"
                "- Recycling system reduces consumption 30%\n\n"
                "**Fuel (Syngas):**\n"
                "- Pyrolysis syngas used as captive fuel (saves Rs 5-10 Lac/year)")

    # ── 23. Land / Area Requirements ─────────────────────────────────
    if any(w in q for w in ["land", "area", "plot", "acre", "square feet", "layout"]):
        return (f"**Land Requirements ({cfg['capacity_tpd']:.0f} TPD Plant):**\n\n"
                "| Capacity | Land (Acres) | Built-Up (sq ft) |\n"
                "|----------|-------------|------------------|\n"
                "| 5 TPD | 0.5-1 | 5,000-8,000 |\n"
                "| 10 TPD | 1-1.5 | 10,000-15,000 |\n"
                "| 20 TPD | 2-3 | 20,000-30,000 |\n"
                "| 30 TPD | 3-4 | 30,000-45,000 |\n"
                "| 50 TPD | 5-7 | 50,000-70,000 |\n\n"
                "**Preferred Location:**\n"
                "- GIDC/MIDC/RIICO industrial area (clear titles)\n"
                "- Within 50 km of biomass source\n"
                "- Near NH/SH for logistics\n"
                "- Minimum 5 km from residential area\n\n"
                "*Use Plant Design page for detailed layout.*")

    # ── 24. Timeline / How Long ──────────────────────────────────────
    if any(w in q for w in ["timeline", "how long", "duration", "time", "months", "when ready"]):
        return ("**Project Timeline:**\n\n"
                "| Phase | Duration | Activities |\n"
                "|-------|----------|------------|\n"
                "| Pre-Feasibility | 1 month | Site selection, DPR |\n"
                "| Company Setup | 1 month | ROC, GST, PAN |\n"
                "| Land & Approvals | 3 months | Land, CTE, Fire NOC |\n"
                "| Bank Loan | 3 months | DPR submission, sanction |\n"
                "| Engineering | 3 months | Design, P&ID, SLD |\n"
                "| Procurement | 4 months | Equipment ordering |\n"
                "| Construction | 5 months | Civil, electrical, piping |\n"
                "| Commissioning | 3 months | Installation, trial run |\n"
                "| Commercial Prod | 6 months | Ramp-up 40% to 85% |\n\n"
                "**Total: 12-18 months** (new plant from scratch)\n"
                "**Upgrade existing: 30-90 days**\n\n"
                "*Use Project Gantt page for customer-specific tracking.*")

    # ── 25. Consulting Fees / Services ───────────────────────────────
    if any(w in q for w in ["fee", "consulting", "charge", "pricing", "service cost", "how much you charge"]):
        lines = ["**PPS Anantams Consulting Fee Structure:**\n"]
        for ta in TARGET_AUDIENCES:
            lines.append(f"\n**{ta['type']}:**")
            lines.append(f"- DPR Fee: {ta['fee_dpr']} | Setup Fee: {ta['fee_setup']} | Retainer: {ta['fee_retainer']}")
            lines.append(f"- Investment: {ta['investment']} | Stages: {ta['stages']}")
        return "\n".join(lines)

    # ── DOCUMENT SEARCH ──────────────────────────────────────────────
    if any(w in q for w in ["document", "file", "find", "search", "dpr", "report", "drawing",
                              "form", "boq", "hazop", "salary", "agreement"]):
        try:
            from engines.deep_extractor import load_deep_scan
            deep = load_deep_scan()
            stop_words = {"find", "search", "show", "me", "the", "a", "for", "document", "file",
                          "about", "related", "to", "any", "do", "you", "have", "i", "need",
                          "want", "get", "give", "what", "is", "in", "of"}
            search_terms = [w for w in q.split() if w not in stop_words and len(w) > 2]

            if search_terms:
                matches = []
                for path, entry in deep.items():
                    text = (entry.get("summary", "") + " " + entry.get("filename", "")).lower()
                    score = sum(1 for term in search_terms if term in text)
                    if score > 0:
                        matches.append((score, path, entry))
                matches.sort(key=lambda x: -x[0])
                if matches:
                    lines = [f"**Found {len(matches)} files matching:**\n"]
                    for score, path, entry in matches[:10]:
                        preview = entry.get("summary", "")[:80].replace("\n", " ")
                        lines.append(f"- **{entry['filename']}** ({entry.get('capacity', '')})")
                        if preview:
                            lines.append(f"  *{preview}...*")
                    return "\n".join(lines)
        except Exception:
            pass

        try:
            from document_index import build_index, search_index
            doc_df = build_index()
            search_terms = [w for w in q.split() if len(w) > 2]
            search_str = " ".join(search_terms) if search_terms else q
            results = search_index(doc_df, query=search_str)
            if not results.empty:
                lines = [f"**Found {len(results)} documents matching '{search_str}':**\n"]
                for _, row in results.head(8).iterrows():
                    lines.append(f"- **{row['filename']}** ({row.get('capacity', 'General')}) — {row['size_display']}")
                return "\n".join(lines)
        except Exception:
            pass

    # ── 26. Vendor / Equipment ───────────────────────────────────────
    if any(w in q for w in ["vendor", "supplier", "machinery", "equipment", "buy", "purchase",
                              "reactor", "shredder", "dryer", "condenser"]):
        return ("**Equipment & Vendor Information:**\n"
                "- **Pyrolysis Reactor 10T:** Rs 45-75 Lac (IndiaMART/Proctech)\n"
                "- **Pyrolysis Reactor 20T:** Rs 3.5 Cr (Custom/KGN)\n"
                "- **Biomass Shredder:** Rs 8-12 Lac (Laxmi Eng)\n"
                "- **Rotary Dryer:** Rs 18-25 Lac (Techno Therm)\n"
                "- **Condenser:** Rs 5-8 Lac (MAAN Global)\n"
                "- **DG Set 100kVA:** Rs 8-12 Lac (Kirloskar/Cummins)\n"
                "- **Weighbridge 60T:** Rs 6-8 Lac (Essae)\n"
                "- **Blending Tank:** Rs 5-10 Lac (custom fabrication)\n"
                "- **Lab Equipment:** Rs 15-25 Lac (full QC lab)\n\n"
                "*See Procurement page for full vendor database with contacts.*")

    # ── DEFAULT RESPONSE ─────────────────────────────────────────────
    return ("I can help with **25+ topic areas:**\n\n"
            "**Business:** Plant capacity, investment, ROI, compare capacities\n"
            "**Finance:** Bank loans, EMI, CGTMSE, subsidies, insurance\n"
            "**Technical:** Process, technology, raw materials, equipment, safety\n"
            "**Legal:** Licenses (25 types), compliance, PESO, CTE/CTO\n"
            "**Market:** NHAI tenders, competitors, news, pricing\n"
            "**HR:** Staffing, salaries, training modules\n"
            "**Green:** Carbon credits, ESG, stubble burning impact\n"
            "**Location:** 18-state analysis with cost breakdown\n"
            "**International:** Export, VG-30 import, Getka contract\n"
            "**Consulting:** Fees, services, why PPS Anantams\n"
            "**Documents:** Search 3,085+ files\n\n"
            "**Try asking:**\n"
            "- *'What subsidy can I get?'*\n"
            "- *'Compare all capacities'*\n"
            "- *'NHAI tenders in Gujarat'*\n"
            "- *'Who are the competitors?'*\n"
            "- *'How much staff for 20 TPD?'*\n"
            "- *'Carbon credit revenue?'*\n"
            "- *'Best state for bio-bitumen?'*")


# ══════════════════════════════════════════════════════════════════════
# CHAT INTERFACE
# ══════════════════════════════════════════════════════════════════════
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Quick Question Buttons (expanded)
st.subheader("Quick Questions")
row1 = st.columns(4)
row2 = st.columns(4)

quick_qs_row1 = [
    "Compare all 7 capacities",
    "Best state for bio-bitumen?",
    "What licenses do I need?",
    "What subsidies are available?",
]
quick_qs_row2 = [
    "NHAI open tenders?",
    "Who are the competitors?",
    "Carbon credit revenue?",
    "What staff do I need?",
]

for i, qq in enumerate(quick_qs_row1):
    if row1[i].button(qq, key=f"qq1_{i}"):
        st.session_state["chat_history"].append({"role": "user", "content": qq})
        st.session_state["chat_history"].append({"role": "assistant", "content": answer_question(qq)})
        st.rerun()

for i, qq in enumerate(quick_qs_row2):
    if row2[i].button(qq, key=f"qq2_{i}"):
        st.session_state["chat_history"].append({"role": "user", "content": qq})
        st.session_state["chat_history"].append({"role": "assistant", "content": answer_question(qq)})
        st.rerun()

st.markdown("---")

# Chat display
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about bio-bitumen plant setup, subsidies, loans, safety, carbon credits..."):
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = answer_question(prompt)
    st.session_state["chat_history"].append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# Controls
ctrl1, ctrl2 = st.columns(2)
with ctrl1:
    if st.button("Clear Chat", key="clear_chat"):
        st.session_state["chat_history"] = []
        st.rerun()
with ctrl2:
    if st.button("Export Chat", key="export_chat"):
        if st.session_state["chat_history"]:
            export_text = "\n\n".join([f"{'User' if m['role']=='user' else 'Advisor'}: {m['content']}"
                                        for m in st.session_state["chat_history"]])
            st.download_button("Download Chat Log", export_text, "chat_log.txt", key="dl_chat")
        else:
            st.info("No chat history to export.")

st.markdown("---")
st.caption(f"{COMPANY['name']} | {COMPANY['owner']} | {COMPANY['phone']}")
