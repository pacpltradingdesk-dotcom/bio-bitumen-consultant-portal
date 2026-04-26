"""
PROFILE_MASTER.py — Single source of truth for Prince Pratap Shah's profile.

All facts here are sourced from one of:
  [CV]    — PPS_Prince_Shah_Profile_Original.pdf
  [TIME]  — Year-by-year career timeline spreadsheet (shared April 2026)
  [AMT]   — AMT Techno Marketing & Sales Rep Authorization Certificate, Ref L-012 (2015-16), dated 25-09-2015
  [MCA]   — Ministry of Corporate Affairs public records (DIN / CIN)
  [WEB]   — Public records (zaubacorp, thecompanycheck, omnipotent.co.in, BSE filings)

DATE-ANCHORED: experience years auto-calculate from anchor dates so
numbers never go stale.  Update anchors, not counts.
"""
from datetime import date as _date

# ══════════════════════════════════════════════════════════════════════
# 1. DATE ANCHORS (single source for auto-calculated year counts)
# ══════════════════════════════════════════════════════════════════════
CAREER_START_YEAR          = 2001  # Arrkay (Feb) → Southern Asphalt (Aug) — bitumen career begins
BITUMEN_CAREER_START_YEAR  = 2001  # Southern Asphalt Mangalore, Aug 2001 [CV]
DIRECTOR_SINCE_YEAR        = 2009  # Mundra Oil Pvt Ltd (first MCA directorship) [MCA]
OMNIPOTENT_INCORP_YEAR     = 2016  # [MCA]
OMNIPOTENT_IPO_YEAR        = 2020  # IPO fully subscribed → BSE-listed [TIME]
PACPL_INCORP_YEAR          = 2019  # [MCA]
PACPL_OPERATIONAL_YEAR     = 2024  # Active operations began [TIME]

_CURRENT_YEAR          = _date.today().year
YEARS_EXPERIENCE       = _CURRENT_YEAR - CAREER_START_YEAR         # auto: 25 in 2026
YEARS_AS_DIRECTOR      = _CURRENT_YEAR - DIRECTOR_SINCE_YEAR       # auto: 17 in 2026
YEARS_SINCE_OMNI_IPO   = _CURRENT_YEAR - OMNIPOTENT_IPO_YEAR       # auto: 6 in 2026
AGE                    = _CURRENT_YEAR - 1982                      # auto: 44 in 2026 (DOB 11 Mar 1982)


# ══════════════════════════════════════════════════════════════════════
# 2. IDENTITY
# ══════════════════════════════════════════════════════════════════════
IDENTITY = {
    "full_name":          "Prince Pratap Shah",
    "short_name":         "Prince P. Shah",
    "dob":                "11 March 1982",
    "age":                AGE,                              # auto
    "nationality":        "Indian",
    "marital_status":     "Married",
    "languages_rws":      ["English", "Hindi", "Marathi", "Gujarati"],   # read/write/speak
    "languages_spoken":   ["Kannada", "Kutchi", "Tulu"],                 # spoken only
}


# ══════════════════════════════════════════════════════════════════════
# 3. CONTACT (all verified on letterheads and public records)
# ══════════════════════════════════════════════════════════════════════
CONTACT = {
    "phone_primary":     "+91 7795242424",                  # [CV][AMT][Omnipotent]
    "phone_secondary":   "+91 7506941655",                  # [AMT cert 2015]
    "landline_mumbai":   "022-25666680",                    # [AMT cert 2015]
    "email_personal":    "princepshah@gmail.com",           # [CV][AMT]
    "email_business":    "sales@princeshah.com",            # [AMT cert]
    "website":           "www.princeshah.com",              # [CV][AMT]
    "linkedin":          "https://www.linkedin.com/in/prince-shah-b781921b/",

    # Addresses — all same building, flat/spelling varies across documents.
    "address_registered": "1/13 Damji Nenshi Estate, Station Road, Behind Bikaner Sweets, Bhandup (West), Mumbai 400078, Maharashtra, India",  # [AMT 2015 — most authoritative signed doc]
    "address_operations": "Vadodara, Gujarat",               # Global Enterprises / Omnipotent Vadodara unit
}


# ══════════════════════════════════════════════════════════════════════
# 4. REGULATORY IDS (all publicly verifiable)
# ══════════════════════════════════════════════════════════════════════
REGULATORY = {
    "din":                "06680837",                        # [MCA] Director ID, active since 2009
    "pacpl_cin":          "U46632GJ2019PTC110676",           # [MCA] PPS Anantams Corp Pvt Ltd, 2019
    "pacpl_pan":          "AAHCV1611L",
    "pacpl_gst":          "24AAHCV1611L2ZD",                 # Gujarat
    "omnipotent_cin":     "L74999MH2016PLC285902",           # [MCA/BSE] "L" = Public-listed
    "omnipotent_ipo":     "2020 (fully subscribed)",         # [TIME]
}


# ══════════════════════════════════════════════════════════════════════
# 5. BUSINESS ENTITIES FOUNDED / OWNED
# ══════════════════════════════════════════════════════════════════════
ENTITIES = [
    {
        "name":       "Global Enterprises",
        "type":       "Proprietorship",
        "since":      2004,                                  # [CV]
        "status":     "Active",
        "role":       "Proprietor",
        "business":   "Bitumen & Bituminous Product & Related Machinery — Trading and Worldwide Representation",
        "branches":   "Mangalore (Karnataka), Hyderabad (Telangana), Coimbatore (Tamil Nadu), Mumbai (Maharashtra)",
        "highlight":  "Authorised Worldwide Marketing & Sales Representative for AMT Techno (ISO 9001 certified) from 2015-2017 [Ref L-012 (2015-16)]",
    },
    {
        "name":       "Krush Tar Industries Private Limited",
        "type":       "Private Limited Company",
        "since":      2013,
        "status":     "Historical (2013-2014)",
        "role":       "Chief Executive Officer",
        "business":   "Bitumen manufacturing + trading (40 KMT/annum), JV of 8 top transporters of Karnataka",
        "highlight":  "Plant commissioned in record 90 days of site fabrication; #1 in India for bulk bitumen purchase (2012); 1st fully automatic Emulsion Plant in Karnataka (2013, Hubli)",
    },
    {
        "name":       "Omnipotent Industries Limited",
        "type":       "BSE-LISTED Public Limited Company",
        "cin":        "L74999MH2016PLC285902",
        "since":      2016,
        "ipo_year":   2020,
        "status":     "Active (BSE-listed)",
        "role":       "Founder (Ex-Director / CFO / Managing Director)",
        "business":   "Bitumen import, distribution, manufacturing — 3 plants (Panvel 2016, Kandala 2018, Karjan/Vadodara 2019), warehousing (Kandla 2022), 11 Joint Ventures, 17-state network",
        "highlight":  "Initial Public Offering fully subscribed in 2020; 1st No. bitumen supplier in West & South India in drum bitumen (2019); sourced bulk oil from Petromina, Bepco, Hyundai Korea in 2020 (20,000 MT)",
    },
    {
        "name":       "PPS Anantams Corporation Private Limited",
        "type":       "Private Limited Company",
        "cin":        "U46632GJ2019PTC110676",
        "since":      2019,
        "operational_since": 2024,
        "status":     "Active",
        "role":       "Founder & Managing Director",
        "business":   "Bio-Modified Bitumen plant setup and PMC consulting; bitumen industry CRM + 150,000-contact database (125K petroleum verified + 25K bitumen-specific)",
        "highlight":  "Full digital CRM + WhatsApp automation + client-base indicator development (2024); Bio-Bitumen consulting launched 2026 (CSIR-CRRI KrishiBind technology)",
    },
    {
        "name":       "PS Enterprises",
        "type":       "Proprietorship",
        "since":      2023,
        "status":     "Active",
        "role":       "Proprietor",
        "business":   "International bitumen / petroleum product trading",
        "highlight":  "Signed 1.2 Lakh MT bitumen supply contract with UK-based company (2023)",
    },
]


# ══════════════════════════════════════════════════════════════════════
# 6. EMPLOYMENT HISTORY (pre-entrepreneur years)
# ══════════════════════════════════════════════════════════════════════
EMPLOYMENT = [
    {
        "period":     "Feb 2001 – Aug 2001",
        "company":    "Arrkay Computers, Mumbai",
        "role":       "Manager – Operations (Team Leader within 5 months)",
        "industry":   "Computer Hardware (Assembly, Server, Networking)",
        "notes":      "First point of contact for corporate complaints; managed entire assembled-computer stock and hardware planning.",
    },
    {
        "period":     "Aug 2001 – Apr 2006",
        "company":    "Southern Asphalt, Mangalore",
        "role":       "Production Manager → General Manager",
        "industry":   "Bitumen Emulsion Manufacturing",
        "notes":      "Set up new unit from scratch — land identification, licenses (PCB, factory, fire, explosive), manpower. Led day-to-day sales, dispatch, stock utilization; designed labour wage structure.",
    },
    {
        "period":     "Apr 2006 – Aug 2012",
        "company":    "Tiki Tar Industries (Baroda) Limited — Mangalore Unit",
        "role":       "General Manager → South India Regional Manager",
        "territory":  "Karnataka, North Kerala, Goa, West Tamil Nadu, East Andhra Pradesh",
        "industry":   "Bitumen Emulsion, Blown Bitumen, CRMB",
        "notes":      "Regional head from 2009; handled Sales Tax & Central Excise Audit + Income Tax investigation; tackled fire incident. Dealt with Central Excise, Service Tax, PCB, KIADB, DIC, Explosive Dept, etc.",
    },
]


# ══════════════════════════════════════════════════════════════════════
# 7. PLANTS ENGAGED (9 hands-on + consulting engagements)
# ══════════════════════════════════════════════════════════════════════
PLANTS_ENGAGED = [
    {"n": 1, "year": 2001, "plant": "Southern Asphalt, Mangalore",                "role": "Production Manager → General Manager",  "scope": "Unit establishment + full operations"},
    {"n": 2, "year": 2006, "plant": "Tiki Tar Industries — Mangalore Unit",       "role": "General Manager",                       "scope": "Plant operations + south India regional distribution"},
    {"n": 3, "year": 2013, "plant": "Krush Tar Industries, Hubli, Karnataka",     "role": "CEO (own venture)",                     "scope": "Greenfield — land ID to commissioning in 90 days (1st automatic Emulsion Plant in Karnataka)"},
    {"n": 4, "year": 2014, "plant": "Teknobit Vadodara — PMB+CRMB+Emulsion",      "role": "Consultant (via Global Enterprises)",   "scope": "Machinery procurement + drawings supply for 1st commercial order"},
    {"n": 5, "year": 2016, "plant": "Omnipotent Industries — Panvel Decanter",    "role": "Founder & MD",                          "scope": "1st decanter plant in Panvel — full commissioning"},
    {"n": 6, "year": 2018, "plant": "Omnipotent Industries — Kandala, Gujarat",   "role": "Founder & MD",                          "scope": "2nd plant — decanter + warehousing"},
    {"n": 7, "year": 2019, "plant": "Omnipotent Industries — Karjan, Vadodara",   "role": "Founder & MD (MOU with Aarya Infra)",   "scope": "3rd plant — decanter + warehousing for West India supply"},
    {"n": 8, "year": 2025, "plant": "Teknobit Chatta, Mathura",                   "role": "Consultant (via PPS Anantams)",          "scope": "Decanter + Emulsion plant — full installation"},
    {"n": 9, "year": 2026, "plant": "Teknobit Plant, Karnataka — Hubli",          "role": "Consultant (via PPS Anantams)",          "scope": "PMB plant setup"},
]


# ══════════════════════════════════════════════════════════════════════
# 8. DOCUMENTED PLANT INNOVATIONS (hands-on engineering record)
# ══════════════════════════════════════════════════════════════════════
INNOVATIONS = [
    {"year": 2001, "plant": "Southern Asphalt",     "innovation": "Redesigned emulsion refilling drum in-house using hydro-pneumatic technology — reduced packaging cost"},
    {"year": 2002, "plant": "Southern Asphalt",     "innovation": "Pre-heated all fuel to flash point — realised full calorific value with low smoke emission"},
    {"year": 2003, "plant": "Southern Asphalt",     "innovation": "Rebuilt coil heating line with 2× heating capacity — production increase within the same plant footprint"},
    {"year": 2004, "plant": "Southern Asphalt",     "innovation": "Added multi-level pulsation system + water softener — resolved hard-water production issues"},
    {"year": 2005, "plant": "Southern Asphalt",     "innovation": "Added water chillers to all condensers — full oil recovery, low smoke, improved pulsation efficiency"},
    {"year": 2006, "plant": "Tiki Tar Mangalore",   "innovation": "Opened retail-level sales of blown bitumen — developed 3,000-retailer network in South India (MFG-to-retailer direct channel)"},
    {"year": 2007, "plant": "Tiki Tar Mangalore",   "innovation": "Plant capacity expansion 3× at existing location"},
    {"year": 2008, "plant": "Tiki Tar Mangalore",   "innovation": "Obtained above-ground A/B/C class explosive-storage licence in coastal India — industry first"},
    {"year": 2010, "plant": "Tiki Tar Mangalore",   "innovation": "Summary: 9 total plant improvements across product, capacity, and process between 2002-2009; sold to all major South India traders — CRMB, PMB, Emulsion"},
]


# ══════════════════════════════════════════════════════════════════════
# 9. SIGNATURE ACHIEVEMENTS ("FIRSTS" — strong credibility signals)
# ══════════════════════════════════════════════════════════════════════
FIRSTS = [
    "#1 in India for bulk bitumen purchase in 2012 (via Krush Tar's JV of 8 top Karnataka transporters)",
    "1st fully automatic Emulsion Plant in Karnataka — commissioned at Hubli in 2013 (Krush Tar)",
    "Worldwide Authorised Marketing & Sales Representative for AMT Techno (2015-2017) — ISO 9001 certified supplier [Ref L-012 (2015-16)]",
    "1st decanter plant in Panvel, Maharashtra (2016, Omnipotent Industries)",
    "1st No. bitumen supplier in West & South India in drum bitumen (2019, Omnipotent Industries)",
    "Omnipotent Industries IPO — fully subscribed in 2020 → BSE-listed",
    "1.2 Lakh MT international bitumen supply contract signed with UK-based company (2023, PS Enterprises)",
    "125,000-contact pan-India verified petroleum product database + 25,000 bitumen-specific contacts (2024, PPS Anantams)",
    "Bio-Modified Bitumen PMC consulting launched (2026, PPS Anantams — CSIR-CRRI KrishiBind technology partner)",
]


# ══════════════════════════════════════════════════════════════════════
# 10. INDUSTRY NETWORK (verified database scale)
# ══════════════════════════════════════════════════════════════════════
NETWORK = {
    "petroleum_db_total":   125000,  # [TIME 2024] pan-India verified petroleum products database
    "bitumen_db":            25000,  # [TIME 2024] bitumen-specific (international + domestic)
    "total_database":       150000,
    # Curated deep-relationship subset (Omnipotent network, pre-2024):
    "curated_breakdown": {
        "contractors":     2758,
        "traders":          994,
        "importers":        360,
        "transporters":     206,
        "manufacturers":     84,
        "decanters":         50,
    },
    "curated_total":         4452,
    "states_covered":          17,
    "product_types":            5,   # Emulsion / Blown / CRMB / PMB / VG-30
    "int_import_capacity_mt_yr": 240000,  # 2.4 Lakh MT/yr VG-30 capacity (Iraq/USA)
    "uk_contract_mt":      120000,   # 1.2 Lakh MT UK contract 2023
}


# ══════════════════════════════════════════════════════════════════════
# 11. GLOBAL PARTNERSHIPS
# ══════════════════════════════════════════════════════════════════════
PARTNERSHIPS = [
    {
        "partner":   "AMT Techno (No. 8, Maruti Complex, GIDC, Ranoli, Vadodara-391350)",
        "period":    "25-Sep-2015 to 31-Mar-2017",
        "scope":     "Worldwide Authorised Marketing & Sales Representative",
        "territory": "Worldwide (via Global Enterprises)",
        "cert_ref":  "Ref L-012 (2015-16), dated 25-09-2015",
        "supplier_certifications": "ISO 9001 (BMQR), AIAO-BAR 5-star, ACCREDITED USA",
    },
    {
        "partner":   "Getka Energy Trading LLC (Tulsa, Oklahoma, USA)",
        "scope":     "VG-30 bitumen international supply",
        "capacity":  "up to 2.4 Lakh MT / year (Iraq / USA origin)",
        "signatories": ["Dariusz Cichocki (President, Getka)", "Prince Pratap Shah (MD, Omnipotent)"],
    },
    {
        "partner":   "UK-based bitumen company",
        "period":    "2023 onwards",
        "scope":     "1.2 Lakh MT bitumen supply contract",
        "via":       "PS Enterprises",
    },
    {
        "partner":   "Petromina, Bepco, Hyundai Korea",
        "period":    "2020",
        "scope":     "Bulk BS-Oil purchase (20,000 MT) + onward sale in Indonesia (Hai See)",
        "via":       "Omnipotent Industries",
    },
    {
        "partner":   "CSIR-CRRI & CSIR-IIP",
        "scope":     "Bio-Bitumen (KrishiBind) technology — Bio-Modified Bitumen PMC consulting",
        "via":       "PPS Anantams Corporation Pvt Ltd",
    },
]


# ══════════════════════════════════════════════════════════════════════
# 11B. PROFESSIONAL HEADLINE (from CV)
# ══════════════════════════════════════════════════════════════════════
PROFESSIONAL_HEADLINE = (
    "Senior-Level Commercial Operations / Human Resource / Bituminous Product "
    "Manufacturing Unit Consulting Professional"
)


# ══════════════════════════════════════════════════════════════════════
# 11C. CORE MANAGEMENT COMPETENCIES (from CV — 12 domains)
# ══════════════════════════════════════════════════════════════════════
MANAGEMENT_COMPETENCIES = [
    "Strategy Planning",
    "Commercial Operations",
    "Strategic Sourcing",
    "Process Improvement",
    "Resource Planning",
    "Human Resource Management",
    "Budgeting & MIS",
    "Contract Management",
    "Vendor Management",
    "General Administration",
    "Liaising & Coordination",
    "Legal & Corporate Affairs",
]


# ══════════════════════════════════════════════════════════════════════
# 11D. CORE-COMPETENCY DETAIL (from CV)
# ══════════════════════════════════════════════════════════════════════
COMPETENCY_DETAIL = {
    "Strategic Planning": [
        "Formulate strategies for achievement of goals and targets by identifying & developing new avenues for long-term growth.",
        "Develop long-term partnerships with suppliers; manage supplier performance to ensure service, cost, delivery and quality norms — including strategic sourcing strategy.",
        "Oversee preparation, control & monitoring of capital & operating budgets.",
        "Plan marketing schedule for the sales & business-development team.",
    ],
    "Commercial Operations & Coordination": [
        "Liaise with related departments for all project activities and obtain government orders / approvals for seamless operations.",
        "Handle all liaison activities — Central & State Government departments, including Central Excise, Service Tax, Sales Tax, Professional Tax, Pollution Control Board, KIADB, DIC, Explosive Department, etc.",
        "Manage administrative functions while ensuring optimum and effective utilisation of funds.",
        "Purchase & supply of raw material on time to production lines.",
    ],
    "General Administration": [
        "Handle overall forecasting, budgeting, procurement, distribution and consumption of resources.",
        "Develop and implement key procurement strategies / purchase schedules from vendors and ensure alignment with organisational objectives.",
        "Select and develop vendors to meet various facility requirements of the organisation.",
    ],
    "Human Resource Management": [
        "Manage the complete recruitment life-cycle — sourcing the best talent from diverse sources after identification of manpower requirements.",
        "Plan human-resource requirements in consultation with heads of different functional & operational areas and conduct selection interviews.",
        "Design labour wage structures (daily and monthly), payment aligned with skill and output.",
    ],
}


# ══════════════════════════════════════════════════════════════════════
# 11E. SIGNIFICANT COMMERCIAL & LEGAL ACCOMPLISHMENTS (from CV)
# ══════════════════════════════════════════════════════════════════════
SIGNIFICANT_ACCOMPLISHMENTS = [
    "Undertook Sales Tax Audit and Central Excise Audit; handled Income Tax Raid & Investigation Department at Tiki Tar Industries.",
    "Effectively tackled a fire incident at the plant without commercial loss.",
    "Set up Southern Asphalt Mangalore from scratch — land identification, licences (PCB, Factory, Fire, Explosive), permissions, documentation — and delivered plant commissioning on committed date.",
    "Commissioned the Krush Tar plant in a record 90 days of site fabrication — from drawing-board to commercial production — including identification of land, machinery, manpower, and procurement.",
    "Established Global Enterprises' multi-state branch network (Mangalore → Hyderabad → Coimbatore → Mumbai) for bitumen & bituminous product / machinery distribution pan-India.",
]


# ══════════════════════════════════════════════════════════════════════
# 12. TECHNICAL EXPERTISE (hands-on competence across the bitumen value chain)
# ══════════════════════════════════════════════════════════════════════
TECHNICAL_EXPERTISE = [
    "Bitumen Emulsion production & plant design (since 2001)",
    "Blown Bitumen production & plant design (since 2001)",
    "CRMB — Crumb Rubber Modified Bitumen (since 2008)",
    "PMB — Polymer Modified Bitumen (since 2014)",
    "VG-10 / VG-20 / VG-30 / VG-40 grade blending per IS 73",
    "Bulk bitumen import — terminal operations, drum packing, logistics (since 2012)",
    "Decanter plant operations — truck/tanker decanting (since 2016)",
    "Warehousing, weighbridge, canting line operations (since 2022)",
    "Plant hardware improvements — pre-heaters, coil heating lines, condensers, pulsation systems, water softening, flash-point fuel optimisation",
    "Bio-Modified Bitumen (Pyrolysis + VG-30 blending) — CSIR-CRRI KrishiBind technology (from 2026)",
    "Digital CRM, WhatsApp automation, client-indicator dashboards for petroleum customer management (since 2024)",
    "Regulatory & statutory: Central Excise, Service Tax, PCB, KIADB, DIC, Explosive Department, Factory License, Fire NOC, BIS — end-to-end navigation",
]


# ══════════════════════════════════════════════════════════════════════
# 13. PMC (Project Management Consultancy) — POSITIONING
# ══════════════════════════════════════════════════════════════════════
PMC_OFFER = {
    "positioning": f"Full-service Project Management Consultancy (PMC) for Bitumen, CRMB, PMB, Emulsion and Bio-Modified Bitumen plants — backed by {YEARS_EXPERIENCE} years of hands-on operations, {YEARS_AS_DIRECTOR}+ years as an MCA-registered director, and BSE-listed founder track record.",
    "why_pmc": [
        "Hands-on plant commissioning — not desk consultancy",
        "Personally engineered 9+ documented plant innovations across Southern Asphalt & Tiki Tar",
        "Founded and operated 5 business entities (1 BSE-listed public company + 1 Pvt Ltd + 1 defunct Pvt Ltd + 2 proprietorships)",
        "Set up 9 bitumen plants — Mangalore, Hubli, Vadodara, Panvel, Kandala, Karjan, Mathura",
        "Global partnerships: AMT Techno (worldwide rep), Getka USA, UK bitumen supplier, Petromina / Bepco / Hyundai Korea",
        "150,000-contact pan-India industry database — live, verified",
        "CSIR-CRRI & CSIR-IIP technology alignment for Bio-Bitumen (KrishiBind)",
    ],
    "scope_end_to_end": [
        "Feasibility Study + Detailed Project Report (DPR)",
        "Land identification, site selection, layout, soil testing",
        "Civil construction supervision & structural approvals",
        "Machinery procurement — verified OEM network, best-price negotiation",
        "Installation + commissioning + trial runs",
        "Quality lab setup & CSIR-CRRI / NHAI / BIS certification",
        "Regulatory clearances — PCB, Factory License, Fire NOC, Explosive Dept, BIS",
        "Staff recruitment + plant operator & lab technician training",
        "Market data — demand-supply mapping, pricing benchmarks, competitor intelligence",
        "Buyer network activation — 25,000 bitumen contacts",
        "Raw material sourcing — agro-waste aggregators / VG-30 international import",
        "Bank DPR + CMA data + financial model + loan facilitation",
        "Post-commissioning hand-holding for 6 months",
    ],
}


# ══════════════════════════════════════════════════════════════════════
# 14. EDUCATION
# ══════════════════════════════════════════════════════════════════════
EDUCATION = [
    {"degree": "MBA",     "specialisation": "Marketing & Finance",             "institute": "Dr. C.V. Raman University"},
    {"degree": "B.Com",   "specialisation": None,                              "institute": "Vinayaka Missions University"},
    {"degree": "Diploma", "specialisation": "Safety & Fire Management",         "institute": "Karnataka Fire & Emergency"},
    {"degree": "Diploma", "specialisation": "Computer Hardware Engineering",    "institute": "CMS Computers"},
    {"degree": "Diploma", "specialisation": "Computer Education (Tally)",       "institute": "Soft Link Master"},
]


# ══════════════════════════════════════════════════════════════════════
# 15. AWARDS
# ══════════════════════════════════════════════════════════════════════
AWARDS = [
    {"year": 2021, "award": "Pride of India Icon", "category": "Best Fast-Growing Business"},
]


# ══════════════════════════════════════════════════════════════════════
# 16. ASSOCIATIONS / INDUSTRY BODIES
# ══════════════════════════════════════════════════════════════════════
ASSOCIATIONS = [
    "Kanara Chamber of Commerce & Industry, Mangalore — Working Team Head, Power & Infrastructure Committee",
    "Rotary Club of Mangalore Hillside — Pulse Polio Director",
    "Karnad Small Scale Industries Association, Mangalore — Vice President",
    "Shree Gujarati Swetamber Murtipujak Jain Sangh, Mangalore — Trustee",
    "Shree Mangalore Gujarati Sangh Mahajan — Senior Chairperson",
    "Single Window Clearance Committee, Dakshina Kannada District — Round Table Member",
]


# ══════════════════════════════════════════════════════════════════════
# 17. ELEVATOR PITCH (one paragraph — use in every brochure opening)
# ══════════════════════════════════════════════════════════════════════
ELEVATOR_PITCH = (
    f"Prince Pratap Shah is a {YEARS_EXPERIENCE}-year bitumen-industry veteran (since {CAREER_START_YEAR}) "
    f"and {YEARS_AS_DIRECTOR}+ years MCA-registered Company Director (DIN 06680837, since {DIRECTOR_SINCE_YEAR}). "
    f"He is the Founder of Omnipotent Industries Limited (BSE-listed since the IPO of {OMNIPOTENT_IPO_YEAR}, "
    f"CIN L74999MH2016PLC285902, incorporated {OMNIPOTENT_INCORP_YEAR}) — operator of 3 bitumen plants, "
    f"11 Joint Ventures, 17-state distribution network, and a 1.2 Lakh MT UK supply contract (2023, via PS Enterprises). "
    f"Career start: Production Manager at Southern Asphalt Mangalore (2001), progressing to General Manager of "
    f"Tiki Tar Industries Baroda Ltd (Mangalore Unit, 2006–2012) with regional headship across 5 South Indian states, "
    f"then CEO of Krush Tar Industries (2013–14) where he commissioned Karnataka's 1st fully automatic emulsion plant "
    f"in a record 90 days. Global Enterprises, his flagship proprietorship since 2004, was the Worldwide Authorised "
    f"Marketing & Sales Representative for AMT Techno (ISO 9001, Ref L-012 dated 25-09-2015). PPS Anantams Corporation "
    f"Pvt Ltd (2019, CIN U46632GJ2019PTC110676) is his full-service PMC consultancy for Bitumen, CRMB, PMB, Emulsion, "
    f"and Bio-Modified Bitumen plants — backed by a 150,000-contact pan-India industry database "
    f"(125,000 petroleum + 25,000 bitumen-specific, verified) and CSIR-CRRI KrishiBind bio-bitumen technology alignment. "
    f"He has engineered 9+ documented plant innovations (2001–2010), commissioned 9 bitumen plants across India, and "
    f"received the Pride of India Icon 2021 award for Best Fast-Growing Business."
)


# ══════════════════════════════════════════════════════════════════════
# 18. ONE-LINE HEADLINES (by audience — use in slide corners / email signatures)
# ══════════════════════════════════════════════════════════════════════
HEADLINES = {
    "bank":     f"Prince P. Shah | {YEARS_EXPERIENCE} yrs Bitumen | DIN 06680837 | Founder — Omnipotent Industries Ltd (BSE-Listed IPO {OMNIPOTENT_IPO_YEAR}) & PACPL | 9 Plants Commissioned",
    "investor": f"Prince P. Shah | BSE-Listed Founder | {YEARS_EXPERIENCE}-yr Bitumen PMC | 1.2 Lakh MT UK Contract (2023) | 150,000-Contact Pan-India Database",
    "govt":     f"Prince P. Shah | DIN 06680837 | Founder PPS Anantams Corp Pvt Ltd (CIN U46632GJ2019PTC110676) | CSIR-CRRI KrishiBind Partner | Pride of India Icon 2021",
    "client":   f"Prince P. Shah | {YEARS_EXPERIENCE} Years Hands-On Bitumen PMC | 9 Plants Commissioned | Site → DPR → Plant → Production → Sales | 9+ Documented Innovations",
}
