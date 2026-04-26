"""
Bio Bitumen Master Consulting System — Central Configuration
ALL PROFILE DATA FLOWS FROM: PROFILE_MASTER.py  (single source of truth — never edit here)
Update profile facts in PROFILE_MASTER.py only.
"""
from pathlib import Path
from PROFILE_MASTER import (
    CAREER_START_YEAR, DIRECTOR_SINCE_YEAR,
    OMNIPOTENT_INCORP_YEAR as OMNIPOTENT_FOUNDED,
    PACPL_INCORP_YEAR as PACPL_FOUNDED,
    OMNIPOTENT_IPO_YEAR,
    YEARS_EXPERIENCE, YEARS_AS_DIRECTOR,
    IDENTITY, CONTACT, REGULATORY, ENTITIES,
    PLANTS_ENGAGED as _PLANTS_DETAIL, INNOVATIONS, FIRSTS,
    NETWORK, PARTNERSHIPS, TECHNICAL_EXPERTISE, PMC_OFFER,
    EDUCATION as _EDUCATION_LIST, AWARDS as _AWARDS_LIST,
    ASSOCIATIONS as _ASSOCIATIONS, ELEVATOR_PITCH, HEADLINES,
)

# ── PATHS ─────────────────────────────────────────────────────────────
DOC_ROOT = Path(r"C:\Users\HP\Desktop\Bio Bitumen Full Working all document")
MASTER_DATA_PATH = DOC_ROOT / "13_Professional_Upgrade" / "MASTER_DATA_CORRECTED.py"
PORTAL_DIR = DOC_ROOT / "14_Consultant_Portal"
DB_PATH = PORTAL_DIR / "data" / "consultant_portal.db"
PACKAGE_OUTPUT_DIR = DOC_ROOT / "CUSTOMER_PACKAGES"
SUBMISSION_DIR = DOC_ROOT / "READY_FOR_SUBMISSION"
STATE_FORMS_DIR = DOC_ROOT / "STATE_WISE_APPLICATION_FORMS"

# ── CAPACITY KEYS ─────────────────────────────────────────────────────
CAPACITY_KEYS = ["05MT", "10MT", "15MT", "20MT", "25MT", "30MT", "40MT", "50MT"]

CAPACITY_LABELS = {
    "05MT": "5 MT/Day — INR 1.5 Cr",
    "10MT": "10 MT/Day — INR 3.0 Cr",
    "15MT": "15 MT/Day — INR 4.5 Cr",
    "20MT": "20 MT/Day — INR 8.0 Cr",
    "25MT": "25 MT/Day — INR 10.0 Cr",
    "30MT": "30 MT/Day — INR 12.0 Cr",
    "40MT": "40 MT/Day — INR 14.0 Cr",
    "50MT": "50 MT/Day — INR 16.0 Cr",
}

# ── SUBMISSION CATEGORIES (12 types) ──────────────────────────────────
SUBMISSION_CATEGORIES = {
    "01_FOR_BANK_LOAN": "Bank Loan",
    "02_FOR_INVESTOR": "Investor",
    "03_FOR_GOVERNMENT_OFFICER": "Government Officer",
    "04_FOR_ENGINEER_CONSULTANT": "Engineer / Consultant",
    "05_FOR_CONTRACTOR": "Contractor",
    "06_FOR_MACHINERY_SUPPLIER": "Machinery Supplier",
    "07_FOR_RAW_MATERIAL_SUPPLIER": "Raw Material Supplier",
    "08_FOR_BUYER_NHAI_PWD": "Buyer (NHAI / PWD)",
    "09_FOR_INSURANCE_COMPANY": "Insurance Company",
    "10_FOR_CA_AUDITOR": "CA / Auditor",
    "11_FOR_LEGAL_ADVISOR": "Legal Advisor",
    "12_FOR_POLLUTION_BOARD": "Pollution Board",
}

# ── DOCUMENT SECTIONS ─────────────────────────────────────────────────
DOCUMENT_SECTIONS = {
    "01_DPR": "Detailed Project Report",
    "02_Drawings": "Engineering Drawings",
    "03_Engineering": "Engineering & Technical",
    "04_BOQ": "Bill of Quantities",
    "05_Safety": "Safety & Environment",
    "05_FOR_CONTRACTOR": "Contractor Documents",
    "06_Approvals": "Approvals & Compliance",
    "06_FOR_MACHINERY_SUPPLIER": "Machinery Supplier Docs",
    "07_Execution": "Execution & Planning",
    "08_Financials": "Financial Documents",
    "09_Commercial": "Commercial & Sales",
    "09_Technical_Documents": "Technical Documents",
    "10_Bank_KYC_Documents": "Bank KYC",
    "11_Legal_Documents": "Legal Documents",
    "12_Regulatory_Documents": "Regulatory Documents",
    "13_Investor_Documents": "Investor Documents",
    "14_Govt_Scheme_Docs": "Govt Scheme Documents",
    "15_HR_Operations": "HR & Operations",
    "16_Commercial_Agreements": "Commercial Agreements",
    "PDF_Final": "Final PDFs",
}

# ── STATES (18 covered) ───────────────────────────────────────────────
STATES = [
    "Andhra Pradesh", "Assam", "Bihar", "Chhattisgarh", "Gujarat",
    "Haryana", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
    "Maharashtra", "Odisha", "Punjab", "Rajasthan", "Tamil Nadu",
    "Telangana", "Uttar Pradesh", "West Bengal",
]

# ── CUSTOMER STATUS PIPELINE ──────────────────────────────────────────
CUSTOMER_STATUSES = [
    "New", "Contacted", "Proposal Sent", "Follow-up",
    "Negotiation", "Closed Won", "Closed Lost",
]

# ══════════════════════════════════════════════════════════════════════
# COMPANY PROFILE — REAL DATA from Prince P. Shah PDFs
# ══════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════
# COMPANY — derived from PROFILE_MASTER.py (DO NOT hand-edit fields here)
# ══════════════════════════════════════════════════════════════════════
COMPANY = {
    # ── IDENTITY ──
    "name":         "PPS Anantams Corporation Private Limited",
    "short_name":   "PACPL",
    "trade_name":   "PPS Anantams",
    "owner":        IDENTITY["full_name"],
    "dob":          IDENTITY["dob"],

    # ── CONTACT ──
    "phone":        CONTACT["phone_primary"],
    "phone_secondary": CONTACT["phone_secondary"],
    "landline":     CONTACT["landline_mumbai"],
    "email":        CONTACT["email_personal"],
    "email_business": CONTACT["email_business"],
    "website":      CONTACT["website"],
    "linkedin":     CONTACT["linkedin"],

    # ── REGULATORY IDs ──
    "din":          REGULATORY["din"],
    "pan":          REGULATORY["pacpl_pan"],
    "gst":          REGULATORY["pacpl_gst"],
    "cin":          REGULATORY["pacpl_cin"],
    "omnipotent_cin": REGULATORY["omnipotent_cin"],

    # ── ADDRESSES ──
    "hq":                   f"{CONTACT['address_operations']} (Operations) | Mumbai (Registered)",
    "registered_address":   CONTACT["address_registered"],
    "operations_address":   CONTACT["address_operations"],

    # ── HEADLINE ──
    "experience":   (f"{YEARS_EXPERIENCE} Years in Bitumen Industry (since {CAREER_START_YEAR}) | "
                     f"{YEARS_AS_DIRECTOR}+ Years as MCA-Registered Director (since {DIRECTOR_SINCE_YEAR}) | "
                     f"Founder — Omnipotent Industries Ltd (BSE-Listed IPO {OMNIPOTENT_IPO_YEAR}) | "
                     f"9 Bitumen Plants Commissioned"),
    "tagline":      "Bio-Modified Bitumen + Conventional Bitumen — Complete Plant Setup & PMC Consulting",
    "usp":          (f"{YEARS_EXPERIENCE}-year bitumen industry veteran, founder of BSE-listed Omnipotent Industries Ltd (IPO {OMNIPOTENT_IPO_YEAR}), "
                     f"9 plants commissioned, 9+ documented plant innovations, {NETWORK['total_database']:,}-contact industry database — "
                     f"now offering full-service PMC for Bitumen, CRMB, PMB, Emulsion & Bio-Modified Bitumen plants via PACPL."),

    # ── CAREER ANCHORS ──
    "career_start_year":    CAREER_START_YEAR,
    "director_since_year":  DIRECTOR_SINCE_YEAR,
    "omnipotent_ipo_year":  OMNIPOTENT_IPO_YEAR,
    "years_experience":     YEARS_EXPERIENCE,
    "years_as_director":    YEARS_AS_DIRECTOR,

    # ── PLANT / PROJECT EXPOSURE ──
    "plants_engaged":       9,
    "plants_built":         9,   # alias
    "plants_breakdown":     "3 as GM, 1 as CEO, 3 as Founder/MD, 2 as Consultant",

    # ── BUSINESS SCALE ──
    "uk_contract_mt":       NETWORK["uk_contract_mt"],      # 1.2 Lakh MT UK contract 2023 via PS Enterprises
    "uk_contract_year":     2023,
    "joint_ventures":       11,
    "omnipotent_branches":  2,
    "intl_import_mt_yr":    NETWORK["int_import_capacity_mt_yr"],

    # ── NETWORK ──
    "industry_contacts":    NETWORK["total_database"],      # 150,000 total
    "petroleum_db":         NETWORK["petroleum_db_total"],  # 125,000 verified petroleum
    "bitumen_db":           NETWORK["bitumen_db"],          # 25,000 bitumen-specific
    "curated_contacts":     NETWORK["curated_total"],       # 4,452 curated / deeper relationships
    "contacts_framing":     (f"{NETWORK['total_database']:,}-Contact Pan-India Industry Database "
                             f"(verified: {NETWORK['petroleum_db_total']:,} petroleum + {NETWORK['bitumen_db']:,} bitumen-specific)"),
    "product_types":        NETWORK["product_types"],
    "states_network":       NETWORK["states_covered"],

    # ── EDUCATION / AWARDS / LANGUAGES / ASSOCIATIONS ──
    "education":    " | ".join(
        f"{e['degree']}" + (f" ({e['specialisation']})" if e.get('specialisation') else "") + f" — {e['institute']}"
        for e in _EDUCATION_LIST
    ),
    "awards":       " | ".join(f"{a['award']} {a['year']} — {a['category']}" for a in _AWARDS_LIST),
    "languages":    (f"{', '.join(IDENTITY['languages_rws'])} (Read/Write/Speak); "
                     f"{', '.join(IDENTITY['languages_spoken'])} (Speak)"),
    "associations": _ASSOCIATIONS,
}

# ── CONSULTANT CAREER TRACK RECORD ────────────────────────────────────
# MCA-verifiable milestones marked with [MCA] — rest from CV + Omnipotent public sources
CAREER_TRACK = [
    {"year": 2001, "company": "Southern Asphalt", "location": "Mangalore, Karnataka", "plant_type": "Bitumen Emulsion Plant", "role": "General Manager"},
    {"year": 2006, "company": "Tiki Tar Industries (Baroda) Ltd", "location": "Mangalore Unit — Karnataka, N.Kerala, Goa, W.Tamil Nadu, E.Andhra Pradesh", "plant_type": "Blown Bitumen + Regional Distribution", "role": "General Manager / Regional Head"},
    {"year": 2009, "company": "Mundra Oil Pvt Ltd [MCA]", "location": "India", "plant_type": "Oil / Petroleum Products", "role": "Additional Director (first directorship, DIN 06680837)"},
    {"year": 2013, "company": "Krush Tar Industries Pvt Ltd", "location": "India", "plant_type": "Manufacturing + Trading (40 KMT/yr) — commissioned in 90 days", "role": "CEO (Own Venture)"},
    {"year": 2016, "company": "Omnipotent Industries Limited [MCA / BSE-Listed]", "location": "Mumbai (Registered) + Pan-India operations", "plant_type": "Bitumen Import, Distribution, 11 Joint Ventures, 1.2 Lakh MT traded (FY2020-21)", "role": "Founder"},
    {"year": 2016, "company": "Teknobit Industries", "location": "Gujarat", "plant_type": "Bitumen Processing Plant", "role": "Consultant"},
    {"year": 2018, "company": "Omnipotent Industries — Panvel Unit", "location": "Panvel, Maharashtra", "plant_type": "Decanter + Warehousing", "role": "Founder & MD"},
    {"year": 2019, "company": "PPS Anantams Corporation Pvt Ltd [MCA]", "location": "Vadodara, Gujarat (CIN U46632GJ2019PTC110676)", "plant_type": "Bio-Bitumen Consulting + Plant Setup", "role": "Founder & Director"},
    {"year": 2019, "company": "Omnipotent Industries — Vadodara Unit", "location": "Vadodara, Gujarat", "plant_type": "Decanter + Warehousing", "role": "Founder & MD"},
    {"year": 2020, "company": "Omnipotent Industries — Kutch Unit", "location": "Kutch, Gujarat", "plant_type": "Decanter + Warehousing", "role": "Founder & MD"},
    {"year": 2024, "company": "Teknobit Industries", "location": "Mathura, UP", "plant_type": "Decanter Plant", "role": "Consultant"},
]

# ── LIVE INDUSTRY NETWORK ─────────────────────────────────────────────
INDUSTRY_NETWORK = {
    "contractors": 2758,
    "traders": 994,
    "importers": 360,
    "transporters": 206,
    "manufacturers": 84,
    "decanters": 50,
    "total": 4452,
}

# ── 4 STAGES OF BIO-BITUMEN (from Services PDF) ──────────────────────
FOUR_STAGES = [
    {
        "stage": 1, "name": "Raw Material Procurement & Pelletization",
        "description": "Collect agro-waste (rice straw, groundnut shells, cotton stalk, sugarcane bagasse) from farmers within 50-100 km radius. Process into uniform pellets.",
        "capex": "Rs 15-30 Lakh", "manpower": "8-12 people", "space": "5,000-10,000 sq ft",
    },
    {
        "stage": 2, "name": "Pyrolysis & Bio-Oil Extraction",
        "description": "Heat biomass pellets at 450-550°C in absence of oxygen. Produces bio-oil, bio-char & combustible gases. Bio-oil yield: 20-25% by weight.",
        "capex": "Rs 80L-1.5 Cr", "manpower": "10-15 people", "space": "10,000-20,000 sq ft",
    },
    {
        "stage": 3, "name": "Bio-Oil Refining & Blending",
        "description": "Refine & upgrade bio-oil through oxidation at 230-250°C. Blend 15-30% bio-oil with conventional VG-30 petroleum bitumen.",
        "capex": "Rs 40-80 Lakh", "manpower": "5-8 people", "space": "5,000-8,000 sq ft",
    },
    {
        "stage": 4, "name": "Bio-Bitumen Testing & Marketing",
        "description": "Quality testing: penetration, softening point, ductility, rheology, rutting, cracking. NHAI/MoRTH certification. Sell to road contractors, state PWDs, NHAI projects.",
        "capex": "Rs 20-40 Lakh", "manpower": "3-5 people", "network": "2,758 contractors",
    },
]

# ── 5 TARGET AUDIENCES ────────────────────────────────────────────────
TARGET_AUDIENCES = [
    {
        "type": "New Investor (No Industry Experience)", "stages": "ALL 4 STAGES",
        "investment": "Rs 2-6 Cr", "fee_dpr": "Rs 3-5L", "fee_setup": "Rs 15-25L", "fee_retainer": "Rs 1-2L/month",
        "key_services": ["Complete A-to-Z plant setup from SCRATCH", "Land identification & site selection", "All regulatory clearances", "Machinery procurement", "Hiring & training", "Sales support: 2,758 contractors + NHAI"],
    },
    {
        "type": "Existing Bitumen Company", "stages": "STAGE 1-2 (Client handles 3-4)",
        "investment": "Rs 80L-2 Cr (add-on)", "fee_dpr": "Rs 3-5L", "fee_setup": "Rs 10-15L", "fee_retainer": "Rs 1L/month",
        "key_services": ["Raw material sourcing: farmer aggregator network", "Pelletization unit design", "Pyrolysis reactor commissioning", "Blending ratio calibration (15-30%)", "CSIR-CRRI specification compliance"],
    },
    {
        "type": "Existing Pyrolysis Operator", "stages": "STAGE 3-4 (Client handles 1-2)",
        "investment": "Rs 40-80L", "fee_dpr": "Rs 2-3L", "fee_setup": "Rs 8-12L", "fee_retainer": "Rs 1-2L/month",
        "key_services": ["Bio-oil oxidation & upgrading (230-250°C)", "VG-30 supply for blending (int'l network)", "Blending unit setup", "NHAI specification compliance", "MARKET ACCESS: 2,758 contractors + 994 traders"],
    },
    {
        "type": "Existing Biomass Pellet Manufacturer", "stages": "STAGE 2-3-4 (Client handles 1)",
        "investment": "Rs 1-2 Cr", "fee_dpr": "Rs 3-5L", "fee_setup": "Rs 12-18L", "fee_retainer": "Rs 1-2L/month",
        "key_services": ["Pyrolysis reactor selection", "Bio-oil extraction & quality optimization", "Blending with VG-30", "NHAI/MoRTH certification", "COMPLETE MARKET LINKAGE: 2,758 contractors + 360 importers"],
    },
    {
        "type": "Agro-Processor / Farmer Cooperative / CSIR Licensee", "stages": "ALL 4 STAGES (with guidance)",
        "investment": "Rs 1.5-4 Cr", "fee_dpr": "Rs 3-5L", "fee_setup": "Rs 15-25L", "fee_retainer": "Rs 1-2L/month",
        "key_services": ["Raw material at zero/low cost — HIGHEST MARGIN", "Complete plant design: pelletization + pyrolysis + blending", "All regulatory clearances", "Government subsidy guidance (MNRE, Waste-to-Wealth)", "FULL SALES SUPPORT"],
    },
]

# ── CONSULTING SERVICES (at every stage) ──────────────────────────────
CONSULTING_SERVICES = {
    "Machinery": ["Verified vendor shortlisting", "Best pricing negotiation", "Procurement supervision", "Installation oversight", "Commissioning & trial run"],
    "Setup": ["Site selection & layout", "Civil & electrical planning", "Utility arrangements", "Safety & fire compliance", "Pollution Control Board NOC"],
    "Training": ["Plant operator training", "Quality testing procedures", "Bitumen grading knowledge", "Safety protocols", "Maintenance schedules"],
    "Market Data": ["Demand-supply analysis", "Pricing benchmarks", "Competitor mapping", "NHAI project pipeline", "State PWD tender info"],
    "Buyer/Seller": ["2,758 road contractors", "994 bitumen traders", "360 importers", "84 manufacturers", "NHAI/PWD direct links"],
    "Supply Chain": ["Agro-waste procurement", "Farmer aggregator setup", "VG-30 int'l supply", "Logistics optimization", "Seasonal planning"],
}

# ── KEY CREDENTIALS ───────────────────────────────────────────────────
KEY_CREDENTIALS = [
    "BSE-Listed Founder — Omnipotent Industries (1.2L MT, 11 JVs)",
    "Int'l Import Contracts — 2.4 Lakh MT/yr VG-30 (Iraq/USA)",
    "Proven Consultant — 2 paid projects (Teknobit 2016 & 2024)",
    "5 Product Types — Emulsion/Blown/CRMB/PMB/VG30",
    "17-State Distribution — PAN India network, first of its kind",
    "Pride of India Award — Best Fast-Growing Business 2021",
    "Iran Consulate — Direct meeting for bitumen sourcing",
    "Bitumen India Forum — Founder Member",
]

# ── GETKA CONTRACT DATA ───────────────────────────────────────────────
GETKA_CONTRACT = {
    "seller": "Getka Energy Trading, LLC (Tulsa, Oklahoma, USA)",
    "buyer": "Omnipotent Industries Ltd. (Mumbai, India)",
    "product": "Bitumen VG-30, embossed steel drums, 181 kg each",
    "origin": "Iraq (Erbil, Ex-Refinery)",
    "base_price": "USD 215/MT (Ex-Refinery, Ex-Works)",
    "trial_quantity": "9,600 MT",
    "annual_schedule_mt": 240000,
    "monthly_schedule": {
        "November": 9600, "December": 14400, "January": 21600,
        "February": 28800, "March": 40800, "April": 36000,
        "May": 28800, "June": 21600, "July": 16800,
        "August": 12000, "September": 7200, "October": 2400,
    },
    "pricing_review": "Bi-monthly (every 15 days)",
    "payment": "Letter of Credit (L/C), negotiable, 100% at sight",
    "quality": "SGS certificate for every shipment",
    "date_signed": "25 September 2024",
    "signatories": ["Dariusz Cichocki (President, Getka)", "Prince Pratap Shah (MD, Omnipotent)"],
}

# ── WHY NOW — MARKET OPPORTUNITY ──────────────────────────────────────
WHY_NOW = [
    "India became FIRST country to commercially produce bio-bitumen (Jan 2026, Min. Gadkari)",
    "CSIR-CRRI transferred technology to 14 companies on 7 Jan 2026",
    "15-30% conventional bitumen replaceable with bio-oil — saving Rs 4,500 Cr+ annually",
    "India imports 49% of bitumen (Rs 25,000 Cr/yr) — govt target: full replacement in 10 years",
    "130-216 plants needed in 5-7 years — most new entrants have ZERO bitumen expertise",
]

# ── FILE TYPES FOR FILTERING ──────────────────────────────────────────
FILE_TYPES = {
    "docx": "Word Document",
    "pdf": "PDF",
    "xlsx": "Excel Spreadsheet",
    "pptx": "PowerPoint",
    "png": "Image (PNG)",
    "jpg": "Image (JPG)",
}

# ── EXCLUDE FROM DOCUMENT INDEX ───────────────────────────────────────
EXCLUDED_DIRS = {
    "__pycache__", ".claude", "consultant_portal", "CUSTOMER_PACKAGES",
    "ARCHIVE_Output_100Cr_Original", "ARCHIVE_Output_Biomass_Original",
    "ARCHIVE_Output_Bio_Bitumen_Original",
}
EXCLUDED_EXTENSIONS = {".py", ".pyc", ".js", ".json", ".b64", ".html", ".txt", ".bat"}

# ── LICENSE REGISTRY (25 types) ───────────────────────────────────────
LICENSE_TYPES = [
    {"name": "GST Registration", "authority": "Central GST", "category": "Tax", "typical_days": 7, "mandatory": True},
    {"name": "Udyam (MSME) Registration", "authority": "MSME Ministry", "category": "Registration", "typical_days": 1, "mandatory": True},
    {"name": "Factory License", "authority": "State Factory Inspector", "category": "Operations", "typical_days": 30, "mandatory": True},
    {"name": "Consent to Establish (CTE)", "authority": "State PCB", "category": "Environment", "typical_days": 60, "mandatory": True},
    {"name": "Consent to Operate (CTO)", "authority": "State PCB", "category": "Environment", "typical_days": 45, "mandatory": True},
    {"name": "Fire NOC", "authority": "Fire Department", "category": "Safety", "typical_days": 30, "mandatory": True},
    {"name": "Building Plan Approval", "authority": "Municipal/Nagar Palika", "category": "Civil", "typical_days": 45, "mandatory": True},
    {"name": "Electricity HT Connection", "authority": "State DISCOM", "category": "Utility", "typical_days": 60, "mandatory": True},
    {"name": "Water Connection", "authority": "Municipal/PHED", "category": "Utility", "typical_days": 30, "mandatory": True},
    {"name": "PAN Card (Company)", "authority": "Income Tax Dept", "category": "Tax", "typical_days": 15, "mandatory": True},
    {"name": "TAN Registration", "authority": "Income Tax Dept", "category": "Tax", "typical_days": 7, "mandatory": True},
    {"name": "EPF Registration", "authority": "EPFO", "category": "Labour", "typical_days": 7, "mandatory": True},
    {"name": "ESI Registration", "authority": "ESIC", "category": "Labour", "typical_days": 7, "mandatory": True},
    {"name": "Professional Tax", "authority": "State Govt", "category": "Tax", "typical_days": 15, "mandatory": True},
    {"name": "Trade License", "authority": "Municipal Corporation", "category": "Operations", "typical_days": 15, "mandatory": True},
    {"name": "Labour License", "authority": "Labour Dept", "category": "Labour", "typical_days": 30, "mandatory": True},
    {"name": "Shops & Establishment", "authority": "Labour Dept", "category": "Registration", "typical_days": 15, "mandatory": True},
    {"name": "PESO License (Petroleum)", "authority": "PESO (Nagpur)", "category": "Safety", "typical_days": 90, "mandatory": True},
    {"name": "Environmental Clearance", "authority": "MoEFCC/SEIAA", "category": "Environment", "typical_days": 120, "mandatory": False},
    {"name": "BIS Certification", "authority": "Bureau of Indian Standards", "category": "Quality", "typical_days": 90, "mandatory": False},
    {"name": "NABL Accreditation", "authority": "NABL", "category": "Quality", "typical_days": 120, "mandatory": False},
    {"name": "Weighbridge License", "authority": "Legal Metrology", "category": "Operations", "typical_days": 30, "mandatory": False},
    {"name": "Insurance (Property)", "authority": "Insurance Company", "category": "Finance", "typical_days": 7, "mandatory": True},
    {"name": "Insurance (Liability)", "authority": "Insurance Company", "category": "Finance", "typical_days": 7, "mandatory": True},
    {"name": "CGTMSE Guarantee", "authority": "CGTMSE Trust", "category": "Finance", "typical_days": 30, "mandatory": False},
    # ── PRE-CONSTRUCTION (added from bank/govt research) ──
    {"name": "Land Use / NA Permission", "authority": "District Collector / Revenue Dept", "category": "Land", "typical_days": 60, "mandatory": True,
     "act": "State Land Revenue Code", "when": "Before construction", "validity": "Permanent", "docs": "7/12 extract, survey sketch, ownership docs"},
    {"name": "Structural Stability Certificate", "authority": "Licensed Structural Engineer", "category": "Civil", "typical_days": 15, "mandatory": True,
     "act": "Factories Act 1948", "when": "Before factory license", "docs": "Structural design, soil report"},
    {"name": "Soil Test Report", "authority": "Geotechnical Lab", "category": "Civil", "typical_days": 15, "mandatory": False,
     "act": "IS 1892/IS 2131", "when": "Before foundation design", "docs": "Site bore log samples"},
    # ── LABOUR LAW ──
    {"name": "Minimum Wages Act Compliance", "authority": "Labour Commissioner", "category": "Labour", "typical_days": 0, "mandatory": True,
     "act": "Minimum Wages Act 1948", "when": "Before hiring", "docs": "Wage register, attendance register"},
    {"name": "Contract Labour License", "authority": "Labour Dept", "category": "Labour", "typical_days": 30, "mandatory": True,
     "act": "Contract Labour Act 1970", "when": "If 20+ contract workers", "docs": "Principal employer registration"},
    {"name": "Workmen Compensation Insurance", "authority": "Insurance Company", "category": "Insurance", "typical_days": 7, "mandatory": True,
     "act": "Workmen Compensation Act 1923", "when": "Before hiring", "docs": "Employee list, salary details"},
    # ── SAFETY & ENVIRONMENT ──
    {"name": "Hazardous Waste Authorization", "authority": "State PCB", "category": "Environment", "typical_days": 60, "mandatory": True,
     "act": "Hazardous Waste Rules 2016", "when": "Before operations", "docs": "Waste inventory, disposal plan"},
    {"name": "Boiler Registration", "authority": "Chief Inspector of Boilers", "category": "Safety", "typical_days": 45, "mandatory": False,
     "act": "Indian Boilers Act 1923", "when": "If using boiler", "docs": "Boiler drawings, manufacturer cert"},
    {"name": "Electrical Installation Approval", "authority": "State Electrical Inspector", "category": "Safety", "typical_days": 30, "mandatory": True,
     "act": "Indian Electricity Act 2003", "when": "Before energizing", "docs": "SLD, earthing report, test results"},
    {"name": "Stability Certificate (Annual)", "authority": "Competent Person (IS 14489)", "category": "Safety", "typical_days": 7, "mandatory": True,
     "act": "Factories Act Sec 40", "when": "Annual renewal", "docs": "Structural inspection report"},
    # ── BUSINESS REGISTRATIONS ──
    {"name": "IEC (Import Export Code)", "authority": "DGFT", "category": "Registration", "typical_days": 3, "mandatory": False,
     "act": "Foreign Trade Policy", "when": "If importing/exporting", "docs": "PAN, bank certificate, entity docs"},
    {"name": "GeM Portal Registration", "authority": "gem.gov.in", "category": "Registration", "typical_days": 5, "mandatory": False,
     "act": "GFR 2017 Rule 149", "when": "For govt supply", "docs": "GST, PAN, bank details, product catalog"},
    {"name": "NSIC Registration", "authority": "NSIC", "category": "Registration", "typical_days": 15, "mandatory": False,
     "act": "MSME Support", "when": "For tender preference", "docs": "Udyam, financial statements, factory license"},
    {"name": "ISO 9001:2015 Certification", "authority": "Accredited Certifying Body", "category": "Quality", "typical_days": 90, "mandatory": False,
     "act": "Voluntary but bank-preferred", "when": "Within 1 year", "docs": "QMS documentation, internal audit"},
    {"name": "ZED Certification", "authority": "QCI (Quality Council of India)", "category": "Quality", "typical_days": 60, "mandatory": False,
     "act": "MSME ZED Scheme", "when": "Optional for subsidy", "docs": "Online assessment + physical audit"},
    # ── STATE-SPECIFIC ──
    {"name": "State Industrial Policy Registration", "authority": "State Industries Dept / SLBC", "category": "Registration", "typical_days": 30, "mandatory": True,
     "act": "State Industrial Policy", "when": "For state subsidy", "docs": "DPR, Udyam, land docs, investment proof"},
    {"name": "GIDC/MIDC/SIPCOT Allotment", "authority": "State Industrial Dev Corp", "category": "Land", "typical_days": 60, "mandatory": False,
     "act": "If in industrial estate", "when": "Before construction", "docs": "Application, DPR, company docs"},
    {"name": "Pollution Under Control (PUC) for Vehicles", "authority": "Transport Dept", "category": "Transport", "typical_days": 1, "mandatory": True,
     "act": "Motor Vehicles Act", "when": "For plant vehicles", "docs": "RC of vehicle"},
    # ── NHAI / MoRTH SPECIFIC ──
    {"name": "MoRTH Specification Compliance", "authority": "MoRTH / CSIR-CRRI", "category": "Quality", "typical_days": 30, "mandatory": True,
     "act": "MoRTH Spec 2026 Sec 519", "when": "For road bitumen supply", "docs": "IS:73 test reports, CSIR-CRRI letter"},
    {"name": "NHAI Vendor Empanelment", "authority": "NHAI", "category": "Registration", "typical_days": 30, "mandatory": False,
     "act": "NHAI procurement policy", "when": "For direct NHAI supply", "docs": "Company profile, test reports, financials"},
    # ── INSURANCE (ADDITIONAL) ──
    {"name": "Marine Transit Insurance", "authority": "Insurance Company", "category": "Insurance", "typical_days": 3, "mandatory": True,
     "act": "Bank requirement", "when": "For imported machinery", "docs": "Invoice, bill of lading"},
    {"name": "Keyman Insurance", "authority": "Life Insurance Company", "category": "Insurance", "typical_days": 15, "mandatory": False,
     "act": "Bank may require", "when": "At loan disbursement", "docs": "Promoter medical, bank nomination"},
    {"name": "Public Liability Insurance", "authority": "Insurance Company", "category": "Insurance", "typical_days": 7, "mandatory": True,
     "act": "Public Liability Insurance Act 1991", "when": "For hazardous operations", "docs": "Factory license, CTO, PESO license"},
]

# ── LOCATION SCORING DATA (18 states) ─────────────────────────────────
STATE_SCORES = {
    "Andhra Pradesh":   {"biomass": 70, "subsidy": 65, "logistics": 70, "power": 75, "land_cost": 60, "season": 75},
    "Assam":            {"biomass": 60, "subsidy": 70, "logistics": 40, "power": 50, "land_cost": 85, "season": 55},
    "Bihar":            {"biomass": 80, "subsidy": 60, "logistics": 50, "power": 45, "land_cost": 80, "season": 60},
    "Chhattisgarh":     {"biomass": 75, "subsidy": 70, "logistics": 55, "power": 65, "land_cost": 80, "season": 70},
    "Gujarat":          {"biomass": 65, "subsidy": 80, "logistics": 85, "power": 80, "land_cost": 45, "season": 80},
    "Haryana":          {"biomass": 85, "subsidy": 65, "logistics": 80, "power": 75, "land_cost": 35, "season": 70},
    "Jharkhand":        {"biomass": 65, "subsidy": 65, "logistics": 50, "power": 55, "land_cost": 75, "season": 65},
    "Karnataka":        {"biomass": 70, "subsidy": 75, "logistics": 75, "power": 70, "land_cost": 50, "season": 80},
    "Kerala":           {"biomass": 50, "subsidy": 60, "logistics": 65, "power": 70, "land_cost": 30, "season": 60},
    "Madhya Pradesh":   {"biomass": 85, "subsidy": 75, "logistics": 65, "power": 70, "land_cost": 75, "season": 70},
    "Maharashtra":      {"biomass": 75, "subsidy": 70, "logistics": 85, "power": 75, "land_cost": 40, "season": 75},
    "Odisha":           {"biomass": 70, "subsidy": 70, "logistics": 55, "power": 60, "land_cost": 80, "season": 60},
    "Punjab":           {"biomass": 90, "subsidy": 70, "logistics": 80, "power": 70, "land_cost": 40, "season": 65},
    "Rajasthan":        {"biomass": 60, "subsidy": 75, "logistics": 70, "power": 75, "land_cost": 70, "season": 85},
    "Tamil Nadu":       {"biomass": 65, "subsidy": 70, "logistics": 80, "power": 75, "land_cost": 45, "season": 75},
    "Telangana":        {"biomass": 70, "subsidy": 80, "logistics": 75, "power": 75, "land_cost": 50, "season": 80},
    "Uttar Pradesh":    {"biomass": 90, "subsidy": 75, "logistics": 75, "power": 65, "land_cost": 70, "season": 65},
    "West Bengal":      {"biomass": 75, "subsidy": 60, "logistics": 60, "power": 55, "land_cost": 65, "season": 55},
}

LOCATION_WEIGHTS = {
    "biomass": 0.25, "subsidy": 0.20, "logistics": 0.20,
    "power": 0.15, "land_cost": 0.10, "season": 0.10,
}

# ── STATE-WISE COST DATA (for financial profitability analysis) ───────
# Sources: State DISCOM tariffs 2025-26, Labor Bureau, IBEF, State Industrial Policy
STATE_COSTS = {
    "Andhra Pradesh":   {"power_rate": 7.20, "labor_daily": 450, "land_lac_acre": 15, "water_kl": 12, "transport_per_km": 5.5, "subsidy_pct": 15, "biomass_cost_mt": 2200, "refinery_dist_km": 400, "port_dist_km": 100, "bitumen_demand_mt": 180000},
    "Assam":            {"power_rate": 6.80, "labor_daily": 350, "land_lac_acre": 5, "water_kl": 8, "transport_per_km": 6.5, "subsidy_pct": 25, "biomass_cost_mt": 1800, "refinery_dist_km": 200, "port_dist_km": 500, "bitumen_demand_mt": 80000},
    "Bihar":            {"power_rate": 7.50, "labor_daily": 350, "land_lac_acre": 6, "water_kl": 10, "transport_per_km": 5.5, "subsidy_pct": 20, "biomass_cost_mt": 1500, "refinery_dist_km": 500, "port_dist_km": 800, "bitumen_demand_mt": 150000},
    "Chhattisgarh":     {"power_rate": 6.50, "labor_daily": 380, "land_lac_acre": 5, "water_kl": 8, "transport_per_km": 5.0, "subsidy_pct": 20, "biomass_cost_mt": 1800, "refinery_dist_km": 600, "port_dist_km": 700, "bitumen_demand_mt": 100000},
    "Gujarat":          {"power_rate": 7.00, "labor_daily": 500, "land_lac_acre": 25, "water_kl": 15, "transport_per_km": 5.0, "subsidy_pct": 20, "biomass_cost_mt": 2500, "refinery_dist_km": 50, "port_dist_km": 50, "bitumen_demand_mt": 300000},
    "Haryana":          {"power_rate": 7.80, "labor_daily": 500, "land_lac_acre": 30, "water_kl": 15, "transport_per_km": 5.5, "subsidy_pct": 15, "biomass_cost_mt": 2000, "refinery_dist_km": 150, "port_dist_km": 600, "bitumen_demand_mt": 200000},
    "Jharkhand":        {"power_rate": 6.50, "labor_daily": 380, "land_lac_acre": 6, "water_kl": 8, "transport_per_km": 5.5, "subsidy_pct": 20, "biomass_cost_mt": 2000, "refinery_dist_km": 400, "port_dist_km": 500, "bitumen_demand_mt": 90000},
    "Karnataka":        {"power_rate": 7.50, "labor_daily": 480, "land_lac_acre": 18, "water_kl": 12, "transport_per_km": 5.5, "subsidy_pct": 15, "biomass_cost_mt": 2300, "refinery_dist_km": 100, "port_dist_km": 100, "bitumen_demand_mt": 250000},
    "Kerala":           {"power_rate": 7.20, "labor_daily": 600, "land_lac_acre": 40, "water_kl": 10, "transport_per_km": 6.0, "subsidy_pct": 10, "biomass_cost_mt": 3000, "refinery_dist_km": 200, "port_dist_km": 50, "bitumen_demand_mt": 120000},
    "Madhya Pradesh":   {"power_rate": 6.80, "labor_daily": 400, "land_lac_acre": 8, "water_kl": 10, "transport_per_km": 5.0, "subsidy_pct": 25, "biomass_cost_mt": 1600, "refinery_dist_km": 500, "port_dist_km": 700, "bitumen_demand_mt": 200000},
    "Maharashtra":      {"power_rate": 8.00, "labor_daily": 550, "land_lac_acre": 30, "water_kl": 15, "transport_per_km": 5.5, "subsidy_pct": 15, "biomass_cost_mt": 2200, "refinery_dist_km": 50, "port_dist_km": 50, "bitumen_demand_mt": 400000},
    "Odisha":           {"power_rate": 6.20, "labor_daily": 380, "land_lac_acre": 5, "water_kl": 8, "transport_per_km": 5.5, "subsidy_pct": 20, "biomass_cost_mt": 1800, "refinery_dist_km": 300, "port_dist_km": 100, "bitumen_demand_mt": 120000},
    "Punjab":           {"power_rate": 7.50, "labor_daily": 500, "land_lac_acre": 25, "water_kl": 12, "transport_per_km": 5.5, "subsidy_pct": 15, "biomass_cost_mt": 1500, "refinery_dist_km": 300, "port_dist_km": 700, "bitumen_demand_mt": 200000},
    "Rajasthan":        {"power_rate": 7.00, "labor_daily": 420, "land_lac_acre": 8, "water_kl": 18, "transport_per_km": 5.0, "subsidy_pct": 25, "biomass_cost_mt": 2200, "refinery_dist_km": 200, "port_dist_km": 500, "bitumen_demand_mt": 250000},
    "Tamil Nadu":       {"power_rate": 7.00, "labor_daily": 480, "land_lac_acre": 20, "water_kl": 12, "transport_per_km": 5.5, "subsidy_pct": 15, "biomass_cost_mt": 2200, "refinery_dist_km": 100, "port_dist_km": 50, "bitumen_demand_mt": 280000},
    "Telangana":        {"power_rate": 7.20, "labor_daily": 450, "land_lac_acre": 15, "water_kl": 12, "transport_per_km": 5.5, "subsidy_pct": 20, "biomass_cost_mt": 2000, "refinery_dist_km": 300, "port_dist_km": 300, "bitumen_demand_mt": 200000},
    "Uttar Pradesh":    {"power_rate": 7.50, "labor_daily": 400, "land_lac_acre": 10, "water_kl": 10, "transport_per_km": 5.0, "subsidy_pct": 20, "biomass_cost_mt": 1500, "refinery_dist_km": 400, "port_dist_km": 800, "bitumen_demand_mt": 350000},
    "West Bengal":      {"power_rate": 7.80, "labor_daily": 400, "land_lac_acre": 12, "water_kl": 10, "transport_per_km": 5.5, "subsidy_pct": 15, "biomass_cost_mt": 1800, "refinery_dist_km": 300, "port_dist_km": 100, "bitumen_demand_mt": 180000},
}
# Data sources: DISCOM tariff orders 2025-26, Labour Bureau Min Wages, State Industrial Policy docs
# biomass_cost_mt = delivered farm-gate price for rice straw/bagasse
# refinery_dist_km = distance to nearest IOCL/BPCL/HPCL refinery
# port_dist_km = distance to nearest major port
# bitumen_demand_mt = annual state road construction bitumen consumption

# ══════════════════════════════════════════════════════════════════════
# NHAI / GOVERNMENT TENDER DATABASE (curated, representative data)
# ══════════════════════════════════════════════════════════════════════
NHAI_TENDERS = [
    {"id": "NHAI-2026-0401", "project": "NH-44 Bangalore-Chitradurga 6-Laning", "authority": "NHAI", "state": "Karnataka", "budget_cr": 3200, "bitumen_mt": 45000, "deadline": "2026-05-15", "status": "Open", "type": "EPC"},
    {"id": "NHAI-2026-0392", "project": "NH-48 Udaipur-Ahmedabad Widening", "authority": "NHAI", "state": "Rajasthan", "budget_cr": 2800, "bitumen_mt": 38000, "deadline": "2026-04-30", "status": "Open", "type": "HAM"},
    {"id": "NHAI-2026-0385", "project": "NH-2 Varanasi-Allahabad Resurfacing", "authority": "NHAI", "state": "Uttar Pradesh", "budget_cr": 1500, "bitumen_mt": 22000, "deadline": "2026-05-20", "status": "Open", "type": "EPC"},
    {"id": "PWD-MH-2026-112", "project": "Pune-Nashik State Highway Strengthening", "authority": "Maharashtra PWD", "state": "Maharashtra", "budget_cr": 850, "bitumen_mt": 12000, "deadline": "2026-04-25", "status": "Open", "type": "Item Rate"},
    {"id": "NHAI-2026-0378", "project": "NH-8 Baroda-Mumbai Expressway Maintenance", "authority": "NHAI", "state": "Gujarat", "budget_cr": 1200, "bitumen_mt": 18000, "deadline": "2026-06-10", "status": "Open", "type": "EPC"},
    {"id": "PWD-MP-2026-089", "project": "Bhopal-Indore State Highway Overlay", "authority": "MP PWD", "state": "Madhya Pradesh", "budget_cr": 620, "bitumen_mt": 9500, "deadline": "2026-05-05", "status": "Open", "type": "Item Rate"},
    {"id": "NHAI-2026-0371", "project": "NH-66 Mangalore-Goa Coastal Highway", "authority": "NHAI", "state": "Karnataka", "budget_cr": 4500, "bitumen_mt": 55000, "deadline": "2026-06-30", "status": "Open", "type": "BOT"},
    {"id": "NHAI-2026-0365", "project": "Delhi-Jaipur Expressway Phase 2", "authority": "NHAI", "state": "Rajasthan", "budget_cr": 5200, "bitumen_mt": 62000, "deadline": "2026-07-15", "status": "Upcoming", "type": "EPC"},
    {"id": "PWD-GJ-2026-045", "project": "Rajkot-Jamnagar District Roads", "authority": "Gujarat PWD", "state": "Gujarat", "budget_cr": 380, "bitumen_mt": 5500, "deadline": "2026-04-20", "status": "Open", "type": "Item Rate"},
    {"id": "NHAI-2026-0358", "project": "NH-30 Lucknow-Gorakhpur 4-Laning", "authority": "NHAI", "state": "Uttar Pradesh", "budget_cr": 2200, "bitumen_mt": 32000, "deadline": "2026-05-28", "status": "Open", "type": "HAM"},
    {"id": "BRO-2026-NE-012", "project": "Arunachal Border Road Connectivity", "authority": "BRO", "state": "Assam", "budget_cr": 1800, "bitumen_mt": 25000, "deadline": "2026-06-15", "status": "Open", "type": "EPC"},
    {"id": "PWD-TN-2026-078", "project": "Chennai-Madurai Highway Resurfacing", "authority": "Tamil Nadu PWD", "state": "Tamil Nadu", "budget_cr": 950, "bitumen_mt": 14000, "deadline": "2026-05-10", "status": "Open", "type": "Item Rate"},
    {"id": "NHAI-2026-0351", "project": "NH-16 Visakhapatnam-Vijayawada Expansion", "authority": "NHAI", "state": "Andhra Pradesh", "budget_cr": 3800, "bitumen_mt": 48000, "deadline": "2026-07-01", "status": "Upcoming", "type": "HAM"},
    {"id": "PWD-RJ-2026-056", "project": "Jodhpur-Jaisalmer Desert Highway", "authority": "Rajasthan PWD", "state": "Rajasthan", "budget_cr": 720, "bitumen_mt": 11000, "deadline": "2026-05-25", "status": "Open", "type": "EPC"},
    {"id": "NHAI-2026-0344", "project": "NH-53 Raipur-Bilaspur Corridor", "authority": "NHAI", "state": "Chhattisgarh", "budget_cr": 1600, "bitumen_mt": 21000, "deadline": "2026-06-20", "status": "Open", "type": "EPC"},
    {"id": "PWD-HR-2026-034", "project": "Gurugram-Rewari State Highway", "authority": "Haryana PWD", "state": "Haryana", "budget_cr": 450, "bitumen_mt": 6800, "deadline": "2026-04-28", "status": "Open", "type": "Item Rate"},
    {"id": "NHAI-2026-0337", "project": "Patna Ring Road Construction", "authority": "NHAI", "state": "Bihar", "budget_cr": 2100, "bitumen_mt": 28000, "deadline": "2026-06-05", "status": "Open", "type": "EPC"},
    {"id": "NHAI-2026-0330", "project": "NH-6 Kolkata-Dhanbad Mining Corridor", "authority": "NHAI", "state": "West Bengal", "budget_cr": 1900, "bitumen_mt": 26000, "deadline": "2026-06-25", "status": "Open", "type": "HAM"},
    {"id": "PWD-PB-2026-023", "project": "Amritsar-Jalandhar State Highway", "authority": "Punjab PWD", "state": "Punjab", "budget_cr": 580, "bitumen_mt": 8500, "deadline": "2026-05-12", "status": "Open", "type": "Item Rate"},
    {"id": "NHAI-2026-0323", "project": "NH-65 Hyderabad-Vijayawada Expressway", "authority": "NHAI", "state": "Telangana", "budget_cr": 4100, "bitumen_mt": 52000, "deadline": "2026-07-20", "status": "Upcoming", "type": "EPC"},
    {"id": "PWD-OD-2026-067", "project": "Bhubaneswar-Puri Coastal Road", "authority": "Odisha PWD", "state": "Odisha", "budget_cr": 680, "bitumen_mt": 9800, "deadline": "2026-05-18", "status": "Open", "type": "Item Rate"},
    {"id": "NHAI-2026-0316", "project": "NH-7 Nagpur-Hyderabad 6-Laning", "authority": "NHAI", "state": "Maharashtra", "budget_cr": 3600, "bitumen_mt": 44000, "deadline": "2026-06-28", "status": "Open", "type": "EPC"},
    {"id": "PWD-KL-2026-019", "project": "Kochi-Thrissur State Highway Upgrade", "authority": "Kerala PWD", "state": "Kerala", "budget_cr": 520, "bitumen_mt": 7200, "deadline": "2026-05-30", "status": "Open", "type": "Item Rate"},
    {"id": "NHAI-2026-0309", "project": "Ranchi-Jamshedpur Industrial Corridor", "authority": "NHAI", "state": "Jharkhand", "budget_cr": 1400, "bitumen_mt": 19000, "deadline": "2026-06-12", "status": "Open", "type": "HAM"},
    {"id": "NHAI-2026-0302", "project": "Bharatmala Phase II — Western Corridor", "authority": "NHAI", "state": "Gujarat", "budget_cr": 8500, "bitumen_mt": 95000, "deadline": "2026-08-15", "status": "Upcoming", "type": "EPC"},
    {"id": "PWD-BR-2026-041", "project": "Patna-Gaya State Highway Widening", "authority": "Bihar PWD", "state": "Bihar", "budget_cr": 420, "bitumen_mt": 6200, "deadline": "2026-05-22", "status": "Open", "type": "Item Rate"},
    {"id": "NHAI-2026-0295", "project": "NH-27 East-West Corridor — UP Section", "authority": "NHAI", "state": "Uttar Pradesh", "budget_cr": 2800, "bitumen_mt": 36000, "deadline": "2026-07-10", "status": "Open", "type": "EPC"},
    {"id": "NHAI-2026-0288", "project": "Bengaluru-Mysuru Expressway Extension", "authority": "NHAI", "state": "Karnataka", "budget_cr": 3400, "bitumen_mt": 42000, "deadline": "2026-07-25", "status": "Upcoming", "type": "HAM"},
    {"id": "PWD-CG-2026-015", "project": "Raipur-Jagdalpur Tribal Area Road", "authority": "Chhattisgarh PWD", "state": "Chhattisgarh", "budget_cr": 350, "bitumen_mt": 5000, "deadline": "2026-05-08", "status": "Open", "type": "Item Rate"},
    {"id": "NHAI-2026-0281", "project": "NH-52 Guwahati-Shillong Highway Upgrade", "authority": "NHAI", "state": "Assam", "budget_cr": 1100, "bitumen_mt": 15000, "deadline": "2026-06-18", "status": "Open", "type": "EPC"},
    {"id": "PMGSY-2026-BATCH7", "project": "PMGSY Phase VII Rural Roads — MP", "authority": "PMGSY / NRRDA", "state": "Madhya Pradesh", "budget_cr": 280, "bitumen_mt": 4200, "deadline": "2026-04-22", "status": "Open", "type": "Item Rate"},
    {"id": "NHAI-2026-0274", "project": "Sagarmala Port-Highway Connectivity", "authority": "NHAI / Sagarmala", "state": "Tamil Nadu", "budget_cr": 2600, "bitumen_mt": 34000, "deadline": "2026-08-01", "status": "Upcoming", "type": "EPC"},
]

# ══════════════════════════════════════════════════════════════════════
# COMPETITOR DATABASE
# ══════════════════════════════════════════════════════════════════════
COMPETITORS = [
    {"name": "Rex Fuels Management Pvt Ltd", "location": "Delhi NCR", "capacity_tpd": 20, "technology": "CSIR-CRRI License", "year_started": 2026, "product": "Bio-Bitumen VG30", "strengths": "First CSIR licensee, strong R&D backing", "weaknesses": "No commercial production yet, no industry network", "threat_level": "High"},
    {"name": "Hindustan Colas Ltd", "location": "Pune, Maharashtra", "capacity_tpd": 0, "technology": "Conventional Bitumen", "year_started": 1990, "product": "Emulsion/PMB/CRMB", "strengths": "50+ year legacy, nationwide presence, strong brand", "weaknesses": "No bio-bitumen capability, slow to innovate", "threat_level": "Medium"},
    {"name": "Agarwal Industrial Corporation", "location": "Hyderabad", "capacity_tpd": 30, "technology": "Conventional + Trial Bio", "year_started": 2005, "product": "VG30/PMB", "strengths": "Large refinery, established distribution", "weaknesses": "Bio-bitumen in trial phase only, no pyrolysis setup", "threat_level": "Medium"},
    {"name": "KGN Industries", "location": "Ahmedabad, Gujarat", "capacity_tpd": 15, "technology": "Pyrolysis Equipment OEM", "year_started": 2010, "product": "Pyrolysis machinery", "strengths": "Equipment manufacturer, low-cost reactors", "weaknesses": "Machinery only — no bitumen expertise, no buyer network", "threat_level": "Low"},
    {"name": "Tiki Tar Industries", "location": "Mangalore, Karnataka", "capacity_tpd": 25, "technology": "Conventional", "year_started": 1995, "product": "Blown Bitumen/Emulsion", "strengths": "Southern India stronghold, port proximity", "weaknesses": "No bio-bitumen, aging infrastructure", "threat_level": "Low"},
    {"name": "Indian Oil Corporation (Bitumen Div)", "location": "Pan India", "capacity_tpd": 500, "technology": "Refinery-grade", "year_started": 1959, "product": "VG10/VG30/VG40", "strengths": "Largest producer, govt backing, refinery integration", "weaknesses": "Bureaucratic, no bio-bitumen program, slow innovation", "threat_level": "Low"},
    {"name": "Bharat Petroleum (Bitumen)", "location": "Pan India", "capacity_tpd": 300, "technology": "Refinery-grade", "year_started": 1976, "product": "VG30/PMB", "strengths": "Strong brand, refinery integration", "weaknesses": "No bio-bitumen focus, petroleum-only strategy", "threat_level": "Low"},
    {"name": "Green Asphalt Technologies", "location": "Noida, UP", "capacity_tpd": 10, "technology": "Waste Plastic Modified", "year_started": 2022, "product": "Plastic-modified bitumen", "strengths": "Green narrative, NHAI pilot projects", "weaknesses": "Different technology (plastic not bio), small scale, limited track record", "threat_level": "Medium"},
    {"name": "BioRoads India Pvt Ltd", "location": "Chennai", "capacity_tpd": 5, "technology": "Bio-oil blending (trial)", "year_started": 2025, "product": "Bio-modified trial batches", "strengths": "Early mover in south India, academic partnerships", "weaknesses": "Tiny scale, no buyer network, no proven commercial model", "threat_level": "Medium"},
    {"name": "Teknobit Industries", "location": "Mathura, UP", "capacity_tpd": 20, "technology": "Decanter + Processing", "year_started": 2016, "product": "VG30/Bitumen Processing", "strengths": "PPS Anantams consulting client, northern India presence", "weaknesses": "No in-house bio capability, depends on consultants", "threat_level": "Low"},
]

# PPS Anantams competitive advantages for SWOT
PPS_SWOT = {
    "strengths": [
        f"{YEARS_EXPERIENCE} years in bitumen industry (since {CAREER_START_YEAR}) — 9 plants engaged (3 as GM, 1 as CEO, 3 as Founder/MD, 2 as Consultant)",
        f"{YEARS_AS_DIRECTOR}+ years as MCA-registered Company Director (DIN 06680837, since {DIRECTOR_SINCE_YEAR})",
        "Founder of BSE-LISTED Omnipotent Industries Limited (CIN L74999MH2016PLC285902) — 1.2 Lakh MT bitumen traded FY2020-21, 11 Joint Ventures across India",
        "4,452-contact industry database (contractors, traders, importers, transporters, manufacturers) — built through Omnipotent Industries since 2016",
        "International VG-30 import capacity — up to 2.4 Lakh MT/yr (Iraq/USA)",
        "Only consultant offering end-to-end: site selection to sales network",
        "5 product types expertise (Emulsion / Blown / CRMB / PMB / VG30)",
        "17-state distribution network",
    ],
    "weaknesses": [
        "Small team — relies heavily on founder expertise",
        "No own CSIR-CRRI license (clients must obtain independently)",
        "No in-house lab for quality testing",
        "Limited digital marketing presence",
    ],
    "opportunities": [
        "India's first bio-bitumen commercial production announced Jan 2026",
        "130-216 new plants needed in 5-7 years",
        "Government mandate for green alternatives in road construction",
        "49% bitumen import dependency — massive replacement market",
        "Carbon credit potential for bio-bitumen production",
        "MNRE / Waste-to-Wealth subsidy schemes",
    ],
    "threats": [
        "CSIR-CRRI may license more competitors",
        "Large oil companies (IOCL/BPCL) may enter bio-bitumen",
        "Technology risk — bio-bitumen performance needs long-term field validation",
        "Crude oil price drops could reduce bio-bitumen cost advantage",
        "Regulatory changes or delays in NHAI green mandates",
    ],
}

# ══════════════════════════════════════════════════════════════════════
# RISK REGISTRY — Bio-Bitumen Project Risks
# ══════════════════════════════════════════════════════════════════════
RISK_REGISTRY = [
    {"category": "Market", "risk": "Crude oil price drops below $50 — reduces bio-bitumen cost advantage", "probability": 3, "impact": 4, "mitigation": "Diversify revenue: sell bio-oil + bio-char separately. Lock long-term contracts with NHAI/PWD."},
    {"category": "Market", "risk": "Low buyer adoption — contractors prefer conventional bitumen", "probability": 3, "impact": 4, "mitigation": "Leverage 2,758 contractor network. Offer trial batches free. Get NHAI pilot approval."},
    {"category": "Market", "risk": "Competition from large oil companies entering bio-bitumen", "probability": 2, "impact": 5, "mitigation": "First-mover advantage. Build brand. Lock consulting contracts before competition scales."},
    {"category": "Technical", "risk": "Pyrolysis reactor failure or low bio-oil yield", "probability": 2, "impact": 4, "mitigation": "Use proven reactor designs. Maintain 5% spare capacity. Vendor warranty + AMC contracts."},
    {"category": "Technical", "risk": "Bio-bitumen fails field performance tests (rutting, cracking)", "probability": 2, "impact": 5, "mitigation": "Follow CSIR-CRRI validated formulations. Conduct accelerated lab testing before field trials."},
    {"category": "Technical", "risk": "Inconsistent bio-oil quality from variable biomass feedstock", "probability": 3, "impact": 3, "mitigation": "Standardize feedstock (rice straw). Pelletize before pyrolysis. Install quality testing at intake."},
    {"category": "Financial", "risk": "Bank loan rejection or delayed sanction", "probability": 3, "impact": 4, "mitigation": "Prepare bankable DPR. Apply to 3+ banks simultaneously. Use CGTMSE guarantee for collateral-free loan."},
    {"category": "Financial", "risk": "Cost overrun during plant construction (>20% of estimate)", "probability": 3, "impact": 3, "mitigation": "Fixed-price EPC contracts. 10% contingency in budget. Phased construction approach."},
    {"category": "Financial", "risk": "Working capital shortage during ramp-up period", "probability": 3, "impact": 3, "mitigation": "Secure CC/OD facility from bank. Collect advance payments from buyers. Start with smaller batches."},
    {"category": "Regulatory", "risk": "Consent to Establish (CTE) delayed >6 months", "probability": 3, "impact": 4, "mitigation": "Apply simultaneously for all clearances. Hire environmental consultant. Choose green-zone industrial area."},
    {"category": "Regulatory", "risk": "PESO license delay blocks bitumen storage", "probability": 2, "impact": 3, "mitigation": "Apply early (12 weeks lead time). Use consultant with PESO experience. Start with smaller tank capacity."},
    {"category": "Regulatory", "risk": "Environmental clearance complications", "probability": 2, "impact": 4, "mitigation": "Bio-bitumen is green technology — leverage govt green mandates. Prepare strong EIA report."},
    {"category": "Supply Chain", "risk": "Biomass supply disruption during off-season", "probability": 3, "impact": 3, "mitigation": "Build 90-day biomass inventory. Contract with 3+ farmer cooperatives. Pelletize and store."},
    {"category": "Supply Chain", "risk": "VG-30 import price spike due to geopolitical disruption", "probability": 2, "impact": 4, "mitigation": "Diversify VG-30 sources (Iraq + Iran + domestic). Hedge with forward contracts. Maintain 30-day inventory."},
    {"category": "Supply Chain", "risk": "Key equipment delivery delayed >8 weeks", "probability": 3, "impact": 3, "mitigation": "Order critical equipment first. Use 2+ vendors for redundancy. Penalty clauses in purchase orders."},
    {"category": "Operational", "risk": "Plant fire or explosion (pyrolysis involves high temperatures)", "probability": 1, "impact": 5, "mitigation": "Follow IS safety standards. Fire NOC compliance. Install fire detection + suppression. Regular drills."},
    {"category": "Operational", "risk": "Skilled operator unavailability in rural locations", "probability": 3, "impact": 3, "mitigation": "Train local workers (2-week program). Offer competitive salary + housing. Retain through incentives."},
    {"category": "Operational", "risk": "Power supply interruption affecting production", "probability": 3, "impact": 2, "mitigation": "Install DG backup (100% capacity). Apply for dedicated HT line. Consider solar power supplement."},
    {"category": "Legal", "risk": "Land ownership dispute or title issue", "probability": 2, "impact": 4, "mitigation": "Thorough title search. Legal due diligence. Prefer GIDC/MIDC industrial plots with clear titles."},
    {"category": "Legal", "risk": "Contract dispute with equipment vendor or buyer", "probability": 2, "impact": 3, "mitigation": "Clear contracts with arbitration clause. Use standard industry terms. Legal review before signing."},
]

# ══════════════════════════════════════════════════════════════════════
# ENVIRONMENTAL IMPACT FACTORS
# ══════════════════════════════════════════════════════════════════════
ENVIRONMENTAL_FACTORS = {
    "co2_saved_per_mt_bio_bitumen": 0.35,       # tonnes CO2 saved per MT of bio-bitumen vs conventional
    "stubble_diverted_per_mt_output": 2.5,       # MT of crop residue used per MT bio-bitumen output
    "carbon_credit_rate_usd": 12.0,              # USD per tonne CO2 (voluntary market, 2026)
    "usd_inr_for_calc": 84.0,                    # reference FX rate
    "water_saved_pct_vs_conventional": 15,        # % less water usage
    "energy_efficiency_improvement_pct": 10,      # % better energy use vs conventional
    "nhai_green_mandate_replacement_pct": 15,     # NHAI target: 15% bio-bitumen in new projects by 2030
    "india_annual_bitumen_consumption_mt": 8500000,  # 85 lakh MT
    "india_import_dependency_pct": 49,
    "annual_stubble_burning_india_mt": 150000000,  # 15 crore MT crop residue burned annually
    "bio_bitumen_can_use_pct_of_stubble": 2,       # realistic utilization potential
}

# ══════════════════════════════════════════════════════════════════════
# INDUSTRY NEWS — Curated Updates (static, admin-editable)
# ══════════════════════════════════════════════════════════════════════
INDUSTRY_NEWS = [
    {"date": "2026-03-28", "category": "Government", "title": "NHAI mandates 15% bio-bitumen in all new NH projects by 2030", "summary": "Ministry of Road Transport issues circular requiring bio-modified bitumen usage in all new NHAI contracts starting FY2027-28.", "source": "MoRTH Circular"},
    {"date": "2026-03-15", "category": "Technology", "title": "CSIR-CRRI completes 3-year field trial of KrishiBind bio-bitumen", "summary": "Field sections on NH-44 show 22% less rutting and 18% better fatigue life compared to conventional VG30.", "source": "CSIR-CRRI Report"},
    {"date": "2026-03-10", "category": "Market", "title": "India bitumen imports hit record Rs 28,000 Cr in FY2025-26", "summary": "Import dependency rises to 51% as domestic refinery output lags road construction demand.", "source": "IBEF"},
    {"date": "2026-02-28", "category": "Policy", "title": "MNRE adds bio-bitumen to Waste-to-Wealth Mission subsidy list", "summary": "Bio-bitumen plants now eligible for 25% capital subsidy under Waste-to-Wealth Mission.", "source": "MNRE Notification"},
    {"date": "2026-02-20", "category": "Industry", "title": "First commercial bio-bitumen batch sold to L&T Construction", "summary": "100 MT trial batch of bio-modified VG30 supplied for Mumbai-Pune Expressway maintenance.", "source": "Industry Report"},
    {"date": "2026-02-15", "category": "Price", "title": "VG30 bitumen price crosses Rs 40,000/MT — 3-year high", "summary": "Rising crude oil prices and strong road construction demand push VG30 prices to Rs 40,200/MT.", "source": "Market Data"},
    {"date": "2026-02-10", "category": "Government", "title": "Bharatmala Phase II approved — Rs 6.5 Lakh Cr for 12,000 km", "summary": "Cabinet approves second phase of Bharatmala with focus on economic corridors and port connectivity.", "source": "PIB"},
    {"date": "2026-02-01", "category": "Technology", "title": "IIT Roorkee publishes bio-bitumen durability study", "summary": "Dr. Manoranjan Parida's team confirms bio-bitumen meets all MoRTH specifications for use in tropical climates.", "source": "IIT Roorkee"},
    {"date": "2026-01-25", "category": "Industry", "title": "3 new CSIR-CRRI technology licensees announced", "summary": "Total licensees now 17. New entrants from Gujarat, Maharashtra, and Tamil Nadu.", "source": "CSIR"},
    {"date": "2026-01-15", "category": "Price", "title": "Brent Crude at $82/barrel — stable for road construction season", "summary": "Moderate crude prices support steady bitumen pricing. Peak construction season Q1-Q2 2026.", "source": "Reuters"},
    {"date": "2026-01-07", "category": "Government", "title": "India becomes FIRST country to commercially produce bio-bitumen", "summary": "Minister Gadkari announces at CSIR-CRRI event. Technology transferred to 14 companies.", "source": "MoRTH Press Release"},
    {"date": "2025-12-20", "category": "Market", "title": "NHAI awards Rs 1.8 Lakh Cr in road contracts in FY2025-26", "summary": "Highest ever annual contract awards. Bitumen demand expected to grow 12% in FY2026-27.", "source": "NHAI Annual Report"},
    {"date": "2025-12-10", "category": "Policy", "title": "Carbon credit framework for green construction materials notified", "summary": "MoEFCC notifies rules allowing carbon credit trading for bio-based construction materials including bio-bitumen.", "source": "MoEFCC Gazette"},
    {"date": "2025-11-28", "category": "Industry", "title": "Bitumen India Forum 2025 — PPS Anantams keynote on bio-bitumen", "summary": "Prince P. Shah presents bio-bitumen consulting model at annual industry conference in Mumbai.", "source": "BIF 2025"},
    {"date": "2025-11-15", "category": "Technology", "title": "Agro-waste pelletization technology costs drop 30% in 2 years", "summary": "Chinese and Indian machinery manufacturers bring pelletizer costs down to Rs 8-12 Lakh.", "source": "IndiaMART Research"},
]

# ══════════════════════════════════════════════════════════════════════
# EMI / LOAN PRESETS
# ══════════════════════════════════════════════════════════════════════
EMI_PRESETS = [
    {"name": "SBI MSME Term Loan", "interest_pct": 11.5, "tenure_months": 84, "processing_fee_pct": 0.5, "collateral": "Plant + Machinery", "max_loan_cr": 10},
    {"name": "MUDRA Loan (Tarun)", "interest_pct": 10.0, "tenure_months": 60, "processing_fee_pct": 0.0, "collateral": "None (up to 10L)", "max_loan_cr": 0.10},
    {"name": "CGTMSE Collateral-Free", "interest_pct": 12.0, "tenure_months": 84, "processing_fee_pct": 1.5, "collateral": "CGTMSE Guarantee", "max_loan_cr": 5},
    {"name": "Bank of Baroda MSME", "interest_pct": 11.0, "tenure_months": 84, "processing_fee_pct": 0.5, "collateral": "Property/Fixed Assets", "max_loan_cr": 25},
    {"name": "SIDBI Direct Lending", "interest_pct": 10.5, "tenure_months": 72, "processing_fee_pct": 1.0, "collateral": "Plant + Machinery", "max_loan_cr": 15},
    {"name": "State Subsidy + Loan Combo", "interest_pct": 9.0, "tenure_months": 84, "processing_fee_pct": 0.5, "collateral": "Land + Building", "max_loan_cr": 20},
]

# ══════════════════════════════════════════════════════════════════════
# TRAINING MODULES
# ══════════════════════════════════════════════════════════════════════
TRAINING_MODULES = [
    {"module": "Plant Safety & Fire Prevention", "category": "Safety", "duration_hrs": 8, "audience": "All Staff",
     "topics": ["Fire hazard zones in pyrolysis plants", "PPE requirements (helmet, gloves, safety shoes, goggles)", "Emergency evacuation procedures", "Fire extinguisher types and usage", "First aid basics", "PESO safety compliance", "Hot bitumen handling safety"]},
    {"module": "Pyrolysis Reactor Operations", "category": "Operations", "duration_hrs": 16, "audience": "Operators",
     "topics": ["Reactor startup and shutdown procedures", "Temperature control (450-550C range)", "Feed rate optimization", "Bio-oil condensation monitoring", "Gas handling and flaring", "Maintenance schedules", "Troubleshooting common issues"]},
    {"module": "Quality Testing & Lab Procedures", "category": "Quality", "duration_hrs": 12, "audience": "Lab Technicians",
     "topics": ["Penetration test (IS 1203)", "Softening point (IS 1205)", "Ductility test (IS 1208)", "Flash point (IS 1209)", "Viscosity measurement (IS 1206)", "Sample collection procedures", "Calibration of equipment"]},
    {"module": "Bio-Bitumen Blending Operations", "category": "Operations", "duration_hrs": 8, "audience": "Operators",
     "topics": ["Bio-oil to VG30 blending ratios (15-30%)", "High shear mixing procedures", "Temperature control during blending (230-250C)", "Quality checks during blending", "Batch record keeping", "Additive dosing"]},
    {"module": "Raw Material Management", "category": "Supply Chain", "duration_hrs": 4, "audience": "Store/Procurement",
     "topics": ["Biomass receiving and inspection", "Moisture content testing", "Storage and inventory management", "Pelletization process", "Supplier management", "Seasonal procurement planning"]},
    {"module": "Sales & Customer Management", "category": "Commercial", "duration_hrs": 8, "audience": "Sales Team",
     "topics": ["Understanding NHAI/PWD tender process", "Product specification presentation", "Pricing strategy and negotiation", "Customer relationship management", "Order processing and dispatch", "Payment collection"]},
    {"module": "Environmental Compliance", "category": "Regulatory", "duration_hrs": 4, "audience": "Management",
     "topics": ["Pollution Control Board requirements", "Emission monitoring and reporting", "Waste management protocols", "Water recycling systems", "Noise level compliance", "Annual environmental audit preparation"]},
    {"module": "Financial Management for Plant Managers", "category": "Finance", "duration_hrs": 6, "audience": "Management",
     "topics": ["Daily production cost tracking", "Break-even analysis understanding", "Working capital management", "GST compliance for bitumen sales", "Bank reporting requirements", "Subsidy claim procedures"]},
]
