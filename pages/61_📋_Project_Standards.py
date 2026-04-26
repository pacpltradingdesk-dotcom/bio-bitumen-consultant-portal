"""
Project Standards — YUGA PMC locked numbers, document map, submission protocol
Source: _PROJECT_STANDARDS.md | _YUGA_BRAND_SHEET.md | VENDOR_ENQUIRY_PACK
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from state_manager import init_state, get_config

st.set_page_config(page_title="Project Standards", page_icon="📋", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.sidebar.markdown("---")
if st.sidebar.button("Print This Page", key="print_page"):
    import streamlit.components.v1 as _c; _c.html('<script>window.print();</script>', height=0)

st.title("Project Standards & Reference")
st.markdown("**YUGA PMC Playbook — REX FUELS 5 TPD PMB-40, Bahadurgarh**")
st.markdown("---")

TAB_NUMBERS, TAB_DOCS, TAB_BRAND, TAB_REDFLAGS, TAB_PROTOCOL = st.tabs([
    "Locked Numbers",
    "Document Map",
    "YUGA Brand & Entity",
    "Red Flags",
    "Submission Protocol",
])

# ══════════════════════════════════════════════════════════════════════
# TAB 1 — LOCKED NUMBERS
# ══════════════════════════════════════════════════════════════════════
with TAB_NUMBERS:
    st.subheader("Locked Financial Numbers — Source of Truth")
    st.caption("These numbers are authoritative from 02_MASTER_FINANCIAL_MODEL.xlsx → LOCKED_NUMBERS sheet.")
    st.warning("Never change a number in one doc without propagating to ALL documents.")

    locked = [
        ("Total project cost",        "Rs 6.50 Cr",          "LOCKED_NUMBERS row 3"),
        ("Fixed CAPEX",               "Rs 5.30 Cr",          "LOCKED_NUMBERS row 4"),
        ("Working capital",           "Rs 1.20 Cr",          "LOCKED_NUMBERS row 5"),
        ("Hard cap (PMC undertaking)","Rs 7.00 Cr",          "LOCKED_NUMBERS row 6"),
        ("Capacity",                  "5 TPD = 1,250 MT/yr @ 250 days @ 100%", "row 7"),
        ("Husk dose",                 "1,400 kg/MT PMB gross (Correction B)",  "row 14"),
        ("Husk price — Base",         "Rs 6,000/MT landed",  "row 13"),
        ("Husk price — Bull",         "Rs 3,500/MT (FPO MoU required)", "—"),
        ("VG-10 price",               "Rs 48,000/MT ex-decanter",       "row 15"),
        ("VG-10 dose",                "700 kg/MT (3.5 MT/day)",         "row 16"),
        ("SBS price",                 "Rs 2,50,000/MT",                 "row 17"),
        ("SBS dose",                  "35 kg/MT Y1, 34 kg/MT Y2+",      "row 18"),
        ("PMB price Y1",              "Rs 72,000/MT (needs customer LOI)","row 20"),
        ("Y1 revenue (post-COD)",     "Rs 6.60 Cr (post-audit base)",   "row 21"),
        ("Y2 EBITDA Base",            "Rs 1.57 Cr",          "row 24"),
        ("Y3 EBITDA Base",            "Rs 2.52 Cr",          "row 25"),
        ("Tax rate",                  "25.17% interim (NOT 115BAB — ineligible)", "row 30"),
        ("Base payback",              "~35 months",          "row 28"),
        ("Base IRR",                  "18-22% post-subsidy", "Doc 12"),
        ("Connected load",            "147 kW",              "row 31"),
        ("Transformer",               "125 kVA",             "row 34"),
        ("PMC fee",                   "Rs 63.6 L (12% of Rs 5.30 Cr)", "row 12"),
        ("Staff",                     "12 in-house + outsourced security", "row 13"),
        ("Haryana PADMA subsidy",     "Rs 48 L",             "Doc 22"),
        ("H-GUVY subsidy",            "Rs 17 L/yr x 7 yrs", "Doc 22"),
    ]

    import pandas as pd
    df = pd.DataFrame(locked, columns=["Metric", "Value", "Source"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Process Parameters")
    proc = [
        ("Plant capacity",            "5 TPD (5 MT/day output)"),
        ("Working days",              "250 days/year"),
        ("Process",                   "Slow pyrolysis 480 deg C + PMB-40 blending"),
        ("Pyrolysis temp",            "480 deg C nominal, 500 deg C design"),
        ("Product",                   "PMB-40 per IS 15462:2019"),
        ("Bio-oil yield",             "~22% of husk feed"),
        ("Biochar yield",             "~35% of husk feed"),
        ("Syngas yield",              "~43% of husk feed (self-fuel)"),
        ("Husk moisture target",      "10-12%, 16% ash"),
        ("Reactor shell",             "SS 316, 12 mm min, refractory 150 mm"),
        ("Heating",                   "Indirect external burner (LPG/PNG/oil)"),
        ("Seismic zone",              "Zone IV (Delhi-NCR)"),
        ("Plot size",                 "644 sqm (80m x 60m plot, 1.5 acres site)"),
        ("Power source",              "DHBVN Grid 11kV + 175 kVA DG backup"),
        ("Water source",              "Borewell on-site"),
    ]
    df2 = pd.DataFrame(proc, columns=["Parameter", "Value"])
    st.dataframe(df2, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Subsidy Overview")
    sub_data = [
        ("PADMA (Haryana)", "Rs 48 L one-time capital subsidy", "DIC Jhajjar + HSIIDC"),
        ("H-GUVY", "Rs 17 L/year x 7 years = Rs 1.19 Cr", "HSIIDC energy benefit"),
        ("CLCSS (Central)", "~Rs 15 L on qualifying plant assets", "MSME via SIDBI"),
        ("GST ITC", "Rs 112 L build-up on CAPEX (Rs 58 L identified + Rs 54 L pending)", "CA M/s Agarwal"),
    ]
    df3 = pd.DataFrame(sub_data, columns=["Scheme", "Benefit", "Agency"])
    st.dataframe(df3, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════
# TAB 2 — DOCUMENT MAP
# ══════════════════════════════════════════════════════════════════════
with TAB_DOCS:
    st.subheader("Document Numbering Map — Reading Order")
    st.caption("Main numbered sequence tells the reading story. Never reorder.")

    doc_map = [
        ("00", "CLIENT_SUBMISSION_INDEX",          "Doc map",                     "All"),
        ("01", "MASTER_INDEX_Folder_Map",           "Folder navigation",           "All"),
        ("02", "MASTER_FINANCIAL_MODEL.xlsx",       "AUTHORITATIVE numbers",       "CA, Bank, Investor"),
        ("03", "EXECUTIVE_SUMMARY",                 "1-pager — send first",        "All — especially CEO"),
        ("04", "RAW_MATERIAL_OVERVIEW",             "Feedstock plan",              "Tech + Commercial"),
        ("05", "AGRO_SURPLUS_AVAILABILITY",         "Biomass supply",              "Tech"),
        ("06", "PROCESS_OPTIONS",                   "Pyrolysis route analysis",    "Tech"),
        ("07A","PROCESS_ENGINEERING",               "Mass + energy balance",       "Engineer"),
        ("07B","PROCESS_CHEMISTRY",                 "Reaction mechanisms",         "Chemist + CSIR"),
        ("08", "BYPRODUCTS_REVENUE_STREAMS",        "Biochar + wood vinegar",      "Commercial"),
        ("09", "PLANT_MACHINERY_INFRASTRUCTURE",    "11-line BOM",                 "Engineer + Procurement"),
        ("10", "DETAILED_PROJECT_COSTING",          "CAPEX Rs 5.30 Cr breakdown",  "CA + Bank"),
        ("11", "12MONTH_EARLY_REVENUE",             "Month-by-month ramp",         "Bank (DSCR)"),
        ("12", "FINANCIAL_PROJECTIONS",             "Y1-Y5 P&L + IRR",             "Bank + Investor"),
        ("13", "PLANT_OPERATIONS",                  "SOP",                         "Engineer + Operator"),
        ("14", "SOURCE_LIST_PROCUREMENT",           "Vendor shortlist",            "Procurement"),
        ("15", "PROJECT_TIMELINE_GANTT",            "12-month plan",               "PMC + Client"),
        ("16", "RISK_ANALYSIS",                     "Risk register",               "Bank + Investor"),
        ("17", "CONSULTANCY_SOW_FEES",              "YUGA fees + scope",           "Client"),
        ("18", "TECHNOLOGY_RELIABILITY_RESEARCH",   "CSIR-CRRI validation",        "Tech + Investor"),
        ("19", "INVESTOR_COUNTER_ISSUES",           "Hard Q&A",                    "Investor"),
        ("20", "MASTER_QA_BANK",                    "Top 50 Q&A",                  "All"),
        ("21", "REALITY_CHECK_LEARNING",            "Lessons from similar plants", "Tech"),
        ("22", "SUBSIDIES_COMPLIANCE",              "PADMA + CLCSS + H-GUVY",      "CA + DIC"),
        ("23", "FULL_CHEMISTRY_MSDS",               "MSDS library",                "PCB + Factory Act"),
        ("24", "AREA_LAND_UTILIZATION",             "644 sqm layout",              "Civil + Factory Inspector"),
        ("25", "ELECTRICITY_POWER_SIZING",          "125 kVA load",                "Electrical Consultant"),
        ("26", "PREMIUM_BYPRODUCTS",                "Byproduct upgrade plan",      "Commercial"),
        ("29", "BULL_CASE_24_MONTH_PAYBACK",        "Upside scenario",             "Investor"),
        ("35", "YUGA_BRAND_SHEET",                  "Entity + bank details",       "Procurement"),
        ("36", "PMC_AGREEMENT",                     "Contract draft",              "Legal"),
    ]
    df_docs = pd.DataFrame(doc_map, columns=["#", "Document", "Purpose", "Audience"])
    st.dataframe(df_docs, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Meeting-by-Meeting Release Plan")
    meetings = [
        ("1st (Intro)",      "00, 03, 04 + README.pdf",          "Anything else"),
        ("2nd (Financial)",  "Above + 10, 11, 12, 17, 22",       "02 Excel"),
        ("3rd (Technical)",  "Above + 06, 07A, 07B, 09, 13, 15", "2nd-tier ref library"),
        ("Bank appraisal",   "00, 03, 10, 12, 16, 22, 35 + 02 Excel + Audit reports", "—"),
        ("Investor pitch",   "Pitch Decks + 03, 29, 19",          "Detailed costing"),
        ("Govt officer",     "23, 24, 25, 22 + forms",            "Financial docs"),
        ("CSIR-CRRI",        "07A, 07B, 18, 23, 28",              "Financial docs"),
    ]
    df_m = pd.DataFrame(meetings, columns=["Meeting", "Send", "Do NOT Send"])
    st.dataframe(df_m, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════
# TAB 3 — YUGA BRAND & ENTITY
# ══════════════════════════════════════════════════════════════════════
with TAB_BRAND:
    st.subheader("YUGA PMC — Entity & Brand Details")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Legal Entity**")
        entity = [
            ("Brand (client-facing)",   "YUGA (Vision · Strategy · Execution)"),
            ("Legal entity",            "PPS Anantams Corporation Pvt. Ltd."),
            ("CIN",                     "U46632GJ2019PTC110676"),
            ("GSTIN",                   "24AAHCV1611L2ZD"),
            ("PAN",                     "AAHCV1611L"),
            ("State",                   "Gujarat, Code 24"),
            ("Reg. Office",             "04 Signet Plaza Tower-B, Kunal Cross Rd, Gotri, Vadodara 390021"),
            ("Mumbai Ops",              "1/12 D.N. Estate, Station Rd, Bhandup (W), Mumbai 400078"),
            ("Corporate phone",         "+91 94482 81224"),
            ("Corporate email",         "sales.ppsanantams@gmail.com"),
            ("Lead Consultant",         "Prince Pratap Shah"),
            ("Lead mobile",             "+91 7795242424"),
        ]
        st.table(pd.DataFrame(entity, columns=["Field", "Detail"]))

    with c2:
        st.markdown("**Bank Details (PMC Fee Payment)**")
        bank = [
            ("Beneficiary",    "PPS Anantams Corporation Pvt. Ltd."),
            ("Bank",           "ICICI Bank Ltd."),
            ("Account No.",    "184105001402"),
            ("IFSC",           "ICIC0001841"),
            ("Branch",         "Branch 1841"),
            ("GSTIN",          "24AAHCV1611L2ZD"),
            ("PAN",            "AAHCV1611L"),
        ]
        st.table(pd.DataFrame(bank, columns=["Field", "Value"]))

        st.markdown("**PMC Commercial Terms**")
        terms = [
            ("PMC fee",        "12% of fixed CAPEX"),
            ("Payment",        "7 milestones, 5% retention per milestone"),
            ("Hard cap",       "Overrun absorbed personally by Prince Pratap Shah"),
            ("Penalties",      "Schedule 1%/month | Revenue shortfall 20% | QC 15%"),
            ("Invoicing",      "By PPS Anantams Corp Pvt Ltd, Vadodara GSTIN"),
        ]
        st.table(pd.DataFrame(terms, columns=["Term", "Detail"]))

    st.markdown("---")
    st.subheader("Active Projects")
    projects = [
        (1, "5 TPD PMB-40 Bio-Bitumen",  "Bahadurgarh, Jhajjar, Haryana", "ACTIVE — bank-ready",  "BIO_BITUMEN_5TPD_BAHADURGARH_V1/"),
        (2, "5 TPD PMB-40 Bio-Bitumen",  "Malkangiri, Odisha (Zone-A tribal)", "TEMPLATE — localizing", "BIO_BITUMEN_5TPD_WEST_ODISHA_V1/"),
        (3, "12 TPD PMB (abandoned)",    "—",                              "SUPERSEDED — do not use", "_OLD_12TPD_Archive/"),
    ]
    df_p = pd.DataFrame(projects, columns=["#", "Project", "Location", "Status", "Folder"])
    st.dataframe(df_p, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════
# TAB 4 — RED FLAGS
# ══════════════════════════════════════════════════════════════════════
with TAB_REDFLAGS:
    st.subheader("Red Flags — Do NOT Submit to Bank Without Resolving")
    st.error("All 6 items below must be resolved before bank loan submission.")

    flags = [
        ("1", "PMB-40 Rs 72,000/MT",
         "Needs 3 customer LOIs. Web wholesale caps at Rs 70k. Not supportable without LOI.",
         "Procurement — get LOI from NHAI / state PWD contractor"),
        ("2", "Section 115BAB 17% tax",
         "CONFIRMED INELIGIBLE — window closed 31 Mar 2024. Remove from ALL documents.",
         "CA M/s Agarwal — replace with 25.17% in every doc"),
        ("3", "Land title",
         "Required for any bank loan. Term loan cannot be processed without land collateral.",
         "Client — provide lease deed / title deed to HDFC / SIDBI"),
        ("4", "Excel vs Doc 12 Y4/Y5 gap",
         "Rs 56 L EBITDA mismatch between Excel and Doc 12 Y4/Y5. One must be corrected.",
         "CA M/s Agarwal — reconcile before bank review"),
        ("5", "CA opinion on 80-IAC + GST ITC",
         "Written opinion from M/s Agarwal & Co. pending on Rs 112 L ITC reconciliation.",
         "Trigger: send RFQ Sr 69 (M/s Agarwal) — this is deliverable G-38"),
        ("6", "FPO MoU for Bull Case husk Rs 3,500/MT",
         "Bull Case relies on Rs 3,500/MT husk via FPO. No signed MoU yet.",
         "Procurement — engage Haryana FPO (Kaithal / Kurukshetra region)"),
    ]

    for num, title, issue, action in flags:
        with st.expander(f"Flag {num}: {title}", expanded=True):
            st.markdown(f"**Issue:** {issue}")
            st.markdown(f"**Action:** {action}")


# ══════════════════════════════════════════════════════════════════════
# TAB 5 — SUBMISSION PROTOCOL
# ══════════════════════════════════════════════════════════════════════
with TAB_PROTOCOL:
    st.subheader("30-Second Pre-Send Checklist")
    st.markdown("""
Before sending ANY client pack, confirm all 7 items:

| # | Check | Status |
|---|-------|--------|
| 1 | Is this a 1st meeting, 2nd, bank, or investor? Open the right meeting folder. | ☐ |
| 2 | NDA signed (required before 2nd-tier docs)? | ☐ |
| 3 | Did I re-render today (build date in footer = today)? | ☐ |
| 4 | Did I include README.pdf at the top of the pack? | ☐ |
| 5 | Are all 6 red flags resolved (if going to bank)? | ☐ |
| 6 | No `[CORRECTION X]` editor tags visible in any doc? | ☐ |
| 7 | Zip filename: `YUGA_REX_FUELS_5TPD_<Purpose>_YYYYMMDD.zip`? | ☐ |
    """)

    st.markdown("---")
    st.subheader("Forbidden Patterns")
    forbidden = [
        ("₹ rupee symbol",        "Mojibake in some viewers",         'Use "Rs" prefix'),
        ("en-dash – between digits", "Mojibake (32–38% → 32338%)",    "Use hyphen -"),
        ("Georgia font",           "Synthetic-bold ghost text",        "Helvetica only"),
        ("115BAB 17%",             "Law ineligibility confirmed",      "Use 25.17% or 80-IAC"),
        ('"Rs 72k PMB" without LOI', "Unsupported price claim",         "Require LOI first"),
        ("PACPL in client slides", "Confusing brand name",             'Use "YUGA PMC"'),
        ('"Revolutionary technology"', "No credibility with banks",      '"CSIR-CRRI validated"'),
        ("Multiple footer stamps", "Overlap garbage text",             "Single pass only"),
    ]
    df_f = pd.DataFrame(forbidden, columns=["Forbidden Pattern", "Why", "Use Instead"])
    st.dataframe(df_f, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Document Naming Convention")
    st.markdown("""
- **Main docs:** `NN_TOPIC.md` / `NN_TOPIC.pdf` (e.g. `10_DETAILED_PROJECT_COSTING.pdf`)
- **Subfolder pattern:** `41_SS_NN_Name.ext`
- **Internal/audit:** `_UPPERCASE` prefix (not sent to client)
- **Zip archive:** `YUGA_REX_FUELS_5TPD_<PurposeTag>_YYYYMMDD.zip`
- **Date format:** DD/MM/YYYY in headers; "DD Month YYYY" in footer stamps
    """)

try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "61")
except Exception:
    pass
