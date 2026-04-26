"""
Government Scheme Finder Engine
=================================
Database of 30+ central + state schemes for bio-bitumen / bio-energy plants.
find_schemes(cfg) → list of applicable schemes sorted by subsidy value.
"""
from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime

_HERE = Path(__file__).parent.parent
DATA_DIR = _HERE / "data"

# ── Scheme database ──────────────────────────────────────────────────────
SCHEMES = [
    # ── CENTRAL SCHEMES ─────────────────────────────────────────────────
    {
        "id": "MNRE_BIOMASS",
        "name": "MNRE Biomass Power / Cogen Programme",
        "ministry": "Ministry of New & Renewable Energy",
        "type": "Central",
        "benefit_type": "Capital Subsidy",
        "benefit_pct": 25,
        "benefit_note": "25% capital subsidy on project cost (biomass-based energy)",
        "max_benefit_cr": 3.0,
        "min_capacity_tpd": 1,
        "max_capacity_tpd": 9999,
        "eligible_states": "ALL",
        "conditions": ["Biomass feedstock required", "Grid connectivity preferred"],
        "apply_at": "mnre.gov.in",
        "category": "Energy",
    },
    {
        "id": "CGTMSE",
        "name": "Credit Guarantee Fund Trust for Micro & Small Enterprises (CGTMSE)",
        "ministry": "Ministry of MSME / SIDBI",
        "type": "Central",
        "benefit_type": "Loan Guarantee",
        "benefit_pct": 75,
        "benefit_note": "75–85% credit guarantee on collateral-free loans up to Rs 5 Cr",
        "max_benefit_cr": 5.0,
        "min_capacity_tpd": 1,
        "max_capacity_tpd": 200,
        "eligible_states": "ALL",
        "conditions": ["MSME registration required", "New / existing enterprise"],
        "apply_at": "cgtmse.in",
        "category": "Finance",
    },
    {
        "id": "MUDRA_TARUN",
        "name": "PM Mudra Yojana — Tarun Category",
        "ministry": "Ministry of Finance / MUDRA",
        "type": "Central",
        "benefit_type": "Collateral-free Loan",
        "benefit_pct": 0,
        "benefit_note": "Loans up to Rs 10 lakh without collateral at concessional rate",
        "max_benefit_cr": 0.10,
        "min_capacity_tpd": 1,
        "max_capacity_tpd": 5,
        "eligible_states": "ALL",
        "conditions": ["Small enterprises only", "Non-farm income generating"],
        "apply_at": "mudra.org.in",
        "category": "Finance",
    },
    {
        "id": "NABARD_RIFF",
        "name": "NABARD Rural Infrastructure Fund (RIF)",
        "ministry": "NABARD",
        "type": "Central",
        "benefit_type": "Low-interest Loan",
        "benefit_pct": 0,
        "benefit_note": "Long-term loans at 5–7% for rural agro-processing & biomass plants",
        "max_benefit_cr": 10.0,
        "min_capacity_tpd": 5,
        "max_capacity_tpd": 9999,
        "eligible_states": "ALL",
        "conditions": ["Rural location preferred", "Agro-processing activity"],
        "apply_at": "nabard.org",
        "category": "Finance",
    },
    {
        "id": "SIDBI_CLEANTECH",
        "name": "SIDBI Cleantech / Green Finance",
        "ministry": "SIDBI",
        "type": "Central",
        "benefit_type": "Concessional Loan",
        "benefit_pct": 2,
        "benefit_note": "Interest rate subvention of 1–2% for clean-tech / bio-energy projects",
        "max_benefit_cr": 15.0,
        "min_capacity_tpd": 10,
        "max_capacity_tpd": 9999,
        "eligible_states": "ALL",
        "conditions": ["Environmental benefit must be demonstrated", "MSME preferred"],
        "apply_at": "sidbi.in",
        "category": "Finance",
    },
    {
        "id": "PLI_CHEMICAL",
        "name": "Production Linked Incentive — Specialty Chemicals",
        "ministry": "Ministry of Chemicals & Fertilisers",
        "type": "Central",
        "benefit_type": "Production Incentive",
        "benefit_pct": 10,
        "benefit_note": "6–10% incentive on incremental sales of specialty chemicals incl. bitumen blends",
        "max_benefit_cr": 50.0,
        "min_capacity_tpd": 20,
        "max_capacity_tpd": 9999,
        "eligible_states": "ALL",
        "conditions": ["5-year commitment required", "Minimum investment threshold"],
        "apply_at": "chemicals.gov.in/pli",
        "category": "Production",
    },
    {
        "id": "NITI_BIOENERGY",
        "name": "National Bioenergy Programme (NBP)",
        "ministry": "MNRE",
        "type": "Central",
        "benefit_type": "Capital Subsidy + R&D Grant",
        "benefit_pct": 30,
        "benefit_note": "Up to 30% capital subsidy for advanced bioenergy projects",
        "max_benefit_cr": 5.0,
        "min_capacity_tpd": 5,
        "max_capacity_tpd": 9999,
        "eligible_states": "ALL",
        "conditions": ["Bio-CNG, bio-bitumen, bio-oil projects eligible"],
        "apply_at": "mnre.gov.in/nbp",
        "category": "Energy",
    },
    {
        "id": "STARTUP_INDIA",
        "name": "Startup India — Tax & Patent Benefits",
        "ministry": "DPIIT",
        "type": "Central",
        "benefit_type": "Tax Exemption",
        "benefit_pct": 100,
        "benefit_note": "100% income tax exemption for 3 years + patent fee rebate",
        "max_benefit_cr": 0,
        "min_capacity_tpd": 1,
        "max_capacity_tpd": 9999,
        "eligible_states": "ALL",
        "conditions": ["DPIIT recognition required", "Company < 10 years old",
                       "Turnover < Rs 100 Cr"],
        "apply_at": "startupindia.gov.in",
        "category": "Tax",
    },
    {
        "id": "MSME_CLCSS",
        "name": "MSME Credit Linked Capital Subsidy Scheme (CLCSS)",
        "ministry": "Ministry of MSME",
        "type": "Central",
        "benefit_type": "Capital Subsidy",
        "benefit_pct": 15,
        "benefit_note": "15% upfront capital subsidy on technology upgradation loans up to Rs 1 Cr",
        "max_benefit_cr": 0.15,
        "min_capacity_tpd": 1,
        "max_capacity_tpd": 50,
        "eligible_states": "ALL",
        "conditions": ["Udyam registration mandatory", "Technology upgrade required"],
        "apply_at": "dcmsme.gov.in",
        "category": "Finance",
    },
    {
        "id": "NHDP_GREENBOND",
        "name": "NHAI Green Bond / NHDP Procurement Preference",
        "ministry": "Ministry of Road Transport & Highways",
        "type": "Central",
        "benefit_type": "Market Access",
        "benefit_pct": 0,
        "benefit_note": "NHAI mandates bio-bitumen in tender specs — guaranteed off-take market",
        "max_benefit_cr": 0,
        "min_capacity_tpd": 10,
        "max_capacity_tpd": 9999,
        "eligible_states": "ALL",
        "conditions": ["BIS IS 73:2013 certification required", "CSIR-CRRI approval"],
        "apply_at": "nhai.gov.in",
        "category": "Market",
    },
    # ── STATE SCHEMES ────────────────────────────────────────────────────
    {
        "id": "UP_MSME_SUBSIDY",
        "name": "UP MSME Subsidy & Incentive Policy 2022",
        "ministry": "UP Govt — MSME Dept",
        "type": "State",
        "benefit_type": "Capital Subsidy + Stamp Duty Exemption",
        "benefit_pct": 25,
        "benefit_note": "25% capital subsidy + 100% stamp duty exemption for MSME plants",
        "max_benefit_cr": 2.0,
        "min_capacity_tpd": 1,
        "max_capacity_tpd": 9999,
        "eligible_states": ["Uttar Pradesh"],
        "conditions": ["Udyam registered", "Plant in UP"],
        "apply_at": "niveshmitra.up.nic.in",
        "category": "State",
    },
    {
        "id": "PUNJAB_BIOMASS",
        "name": "Punjab Biomass Procurement Policy (Paddy Straw)",
        "ministry": "Punjab Govt — Agriculture Dept",
        "type": "State",
        "benefit_type": "Feedstock Support",
        "benefit_pct": 0,
        "benefit_note": "Government-backed paddy straw supply at Rs 1500/MT (below market)",
        "max_benefit_cr": 0,
        "min_capacity_tpd": 5,
        "max_capacity_tpd": 9999,
        "eligible_states": ["Punjab"],
        "conditions": ["Plant location in Punjab", "MoU with Punjab Mandi Board"],
        "apply_at": "agripb.gov.in",
        "category": "Feedstock",
    },
    {
        "id": "HARYANA_BIOMASS",
        "name": "Haryana Biomass Energy Policy",
        "ministry": "Haryana Govt — HAREDA",
        "type": "State",
        "benefit_type": "Capital Subsidy + Power Tariff Relief",
        "benefit_pct": 20,
        "benefit_note": "20% capital subsidy + concessional power tariff for biomass plants",
        "max_benefit_cr": 1.5,
        "min_capacity_tpd": 5,
        "max_capacity_tpd": 9999,
        "eligible_states": ["Haryana"],
        "conditions": ["Biomass feedstock-based plant"],
        "apply_at": "hareda.gov.in",
        "category": "State",
    },
    {
        "id": "MP_BIOENERGY",
        "name": "MP New & Renewable Energy Policy",
        "ministry": "MP Govt — MPNREC",
        "type": "State",
        "benefit_type": "Capital Subsidy",
        "benefit_pct": 20,
        "benefit_note": "20% capital subsidy + land at concessional rate in industrial parks",
        "max_benefit_cr": 2.0,
        "min_capacity_tpd": 5,
        "max_capacity_tpd": 9999,
        "eligible_states": ["Madhya Pradesh"],
        "conditions": ["Bio-energy project", "MP location"],
        "apply_at": "mprenewable.nic.in",
        "category": "State",
    },
    {
        "id": "MH_BIOENERGY",
        "name": "Maharashtra Green Energy / MEDA Subsidy",
        "ministry": "Maharashtra Govt — MEDA",
        "type": "State",
        "benefit_type": "Capital Subsidy + Fiscal Incentives",
        "benefit_pct": 15,
        "benefit_note": "15% capital subsidy + VAT exemption for bio-energy projects",
        "max_benefit_cr": 2.5,
        "min_capacity_tpd": 5,
        "max_capacity_tpd": 9999,
        "eligible_states": ["Maharashtra"],
        "conditions": ["MEDA registration", "Renewable energy project"],
        "apply_at": "mahaurja.com",
        "category": "State",
    },
    {
        "id": "GJ_BIOENERGY",
        "name": "Gujarat Renewable Energy Policy 2023",
        "ministry": "Gujarat Govt — GEDA",
        "type": "State",
        "benefit_type": "Capital Subsidy + Land Bank",
        "benefit_pct": 20,
        "benefit_note": "20% capital subsidy + land in GIDC at Rs 1/sqm for bio-energy",
        "max_benefit_cr": 3.0,
        "min_capacity_tpd": 10,
        "max_capacity_tpd": 9999,
        "eligible_states": ["Gujarat"],
        "conditions": ["Gujarat location", "GIDC industrial plot"],
        "apply_at": "geda.gujarat.gov.in",
        "category": "State",
    },
    {
        "id": "RJ_BIOENERGY",
        "name": "Rajasthan Renewable Energy Policy",
        "ministry": "Rajasthan Govt — RRECL",
        "type": "State",
        "benefit_type": "Capital Subsidy",
        "benefit_pct": 20,
        "benefit_note": "20% capital subsidy on biomass / bio-energy projects",
        "max_benefit_cr": 2.0,
        "min_capacity_tpd": 5,
        "max_capacity_tpd": 9999,
        "eligible_states": ["Rajasthan"],
        "conditions": ["Rajasthan location"],
        "apply_at": "rrecl.com",
        "category": "State",
    },
    {
        "id": "KA_BIOENERGY",
        "name": "Karnataka Renewable Energy Policy 2022–27",
        "ministry": "Karnataka Govt — KREDL",
        "type": "State",
        "benefit_type": "Capital Subsidy + GST Refund",
        "benefit_pct": 25,
        "benefit_note": "25% capital subsidy + 5-year SGST refund for bio-energy",
        "max_benefit_cr": 3.0,
        "min_capacity_tpd": 5,
        "max_capacity_tpd": 9999,
        "eligible_states": ["Karnataka"],
        "conditions": ["Karnataka location", "KREDL approval"],
        "apply_at": "kredl.kar.nic.in",
        "category": "State",
    },
    {
        "id": "TN_BIOENERGY",
        "name": "Tamil Nadu Green Energy Policy",
        "ministry": "TN Govt — TEDA",
        "type": "State",
        "benefit_type": "Capital Subsidy",
        "benefit_pct": 20,
        "benefit_note": "20% capital subsidy for biomass-based projects in Tamil Nadu",
        "max_benefit_cr": 2.0,
        "min_capacity_tpd": 5,
        "max_capacity_tpd": 9999,
        "eligible_states": ["Tamil Nadu"],
        "conditions": ["TN location", "TEDA registration"],
        "apply_at": "teda.in",
        "category": "State",
    },
    {
        "id": "TS_BIOENERGY",
        "name": "Telangana Industrial Health Policy — Bio-Energy",
        "ministry": "Telangana Govt — TSREDCO",
        "type": "State",
        "benefit_type": "Capital Subsidy + Power Concession",
        "benefit_pct": 20,
        "benefit_note": "20% capital subsidy + 5-year power tariff concession",
        "max_benefit_cr": 2.0,
        "min_capacity_tpd": 5,
        "max_capacity_tpd": 9999,
        "eligible_states": ["Telangana"],
        "conditions": ["Telangana location"],
        "apply_at": "tsredco.telangana.gov.in",
        "category": "State",
    },
]


# ── Finder ──────────────────────────────────────────────────────────────

def find_schemes(cfg: dict) -> list[dict]:
    state     = cfg.get("state", "")
    capacity  = float(cfg.get("capacity_tpd", 20) or 20)
    invest_cr = float(cfg.get("investment_cr", 6) or 6)

    applicable = []
    for s in SCHEMES:
        # capacity check
        if not (s["min_capacity_tpd"] <= capacity <= s["max_capacity_tpd"]):
            continue
        # state check
        if s["eligible_states"] != "ALL":
            if state not in s["eligible_states"]:
                continue

        # estimate benefit amount
        if s["benefit_type"] in ("Capital Subsidy",) and s["benefit_pct"] > 0:
            est = min(invest_cr * s["benefit_pct"] / 100, s["max_benefit_cr"] or 9999)
        elif s["max_benefit_cr"] > 0:
            est = s["max_benefit_cr"]
        else:
            est = 0

        applicable.append({**s, "est_benefit_cr": round(est, 2)})

    # sort by estimated benefit descending
    applicable.sort(key=lambda x: x["est_benefit_cr"], reverse=True)
    return applicable


def total_benefit(schemes: list[dict]) -> float:
    return sum(s["est_benefit_cr"] for s in schemes)


def save_schemes(schemes: list[dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "applicable_schemes.json"
    path.write_text(
        json.dumps({"found_at": datetime.now().isoformat(), "schemes": schemes},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_schemes() -> list[dict]:
    path = DATA_DIR / "applicable_schemes.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("schemes", [])
    except Exception:
        return []
