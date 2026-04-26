"""
Seed pre-defined client projects into the database.
Run once: python seed_clients.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, seed_client_if_missing, save_client_config, get_all_customers

init_db()

# ══════════════════════════════════════════════════════════════════════
# CLIENT 1 — REX FUELS | Bahadurgarh, Haryana | 5 TPD PMB-40
# ══════════════════════════════════════════════════════════════════════
BAHADURGARH_CONFIG = {
    # Identity
    "client_name": "Rexy Ravindran Pallithara",
    "client_company": "REX FUELS MANAGEMENT PRIVATE LIMITED",
    "client_email": "rex.fuels@gmail.com",
    "client_phone": "+91 91672 79047",
    "client_gst": "27AADCR1932Q1ZY",
    "project_name": "Bahadurgarh 5 TPD PMB-40 Bio-Bitumen Plant",
    "project_id": "REX-BHD-001",
    "dpr_version": "v1.0",

    # Location
    "state": "Haryana",
    "location": "Bahadurgarh",
    "district": "Jhajjar",
    "site_address": "Bahadurgarh Industrial Area, Jhajjar District, Haryana — Delhi-NCR Gateway",
    "site_pincode": "124507",
    "site_district": "Jhajjar",
    "site_area_acres": 1.5,
    "site_ownership": "Lease (deed held by REX FUELS)",

    # Plant Config
    "capacity_tpd": 5.0,
    "working_days": 250,
    "process_id": 1,
    "product_model": "bitumen",
    "num_shifts": 2,
    "operating_hours": 16,

    # Product — PMB-40 specific
    "selling_price_per_mt": 52000,   # PMB-40 premium pricing
    "biochar_price_per_mt": 4500,
    "syngas_value_per_mt": 1200,
    "sale_bio_bitumen_vg30": 44000,
    "sale_bio_bitumen_vg40": 48000,
    "sale_biochar_agri": 26000,
    "sale_biochar_industrial": 32000,

    # Raw Material — Haryana rice straw / wheat straw
    "price_rice_straw_loose": 1200,
    "price_wheat_straw": 1700,
    "mix_rice_straw_loose": 0.50,
    "mix_wheat_straw": 0.30,
    "mix_rice_straw_baled": 0.10,
    "mix_other_agro_waste": 0.10,
    "mix_bagasse": 0.0,
    "mix_lignin": 0.0,

    # Process yields
    "bio_oil_yield_pct": 32,
    "bio_char_yield_pct": 28,
    "syngas_yield_pct": 22,
    "process_loss_pct": 18,
    "bio_blend_pct": 20,

    # Costs
    "electricity_rate": 6.5,     # Haryana industrial tariff
    "electricity_kwh_day": 350,  # 5 TPD scale
    "diesel_litres_day": 35,
    "labour_daily_cost": 6500,   # 10 staff lean crew
    "overheads_daily_cost": 4000,

    # Finance — Rs 6.50 Cr total
    "investment_cr": 6.50,
    "equity_ratio": 0.40,         # Rs 2.60 Cr equity
    "interest_rate": 0.115,
    "emi_tenure_months": 84,
    "moratorium_months": 6,
    "tax_rate": 0.25,
    "depreciation_rate": 0.10,

    # Site / Drawing
    "plot_length_m": 80,
    "plot_width_m": 60,
    "seismic_zone": "IV",        # Delhi-NCR zone
    "flood_prone": False,
    "build_type": "peb",
    "drawing_scale": "1:100",
    "paper_size": "A1",
    "pyrolysis_temp_C": 500,

    # Biomass
    "biomass_source": "FPO-sourced rice husk + wheat straw, Haryana / Punjab",
    "power_source": "DHBVN Grid 11kV + 175kVA DG backup",
    "water_source": "Borewell on-site",
}

BAHADURGARH_CUSTOMER = {
    "name": "Rexy Ravindran Pallithara",
    "company": "REX FUELS MANAGEMENT PRIVATE LIMITED",
    "email": "rex.fuels@gmail.com",
    "phone": "+91 91672 79047",
    "whatsapp": "+91 91672 79047",
    "state": "Haryana",
    "city": "Bahadurgarh",
    "interested_capacity": "5 TPD",
    "budget_cr": 6.50,
    "status": "Active",
    "notes": (
        "GSTIN: 27AADCR1932Q1ZY | DIN: 01801295\n"
        "Regd: 523/524, Midas, Sahar Plaza, Near Kohinoor Hotel, J B Nagar, "
        "M V Road, Andheri East, Mumbai 400059, Maharashtra\n"
        "Master CSIR-CRRI licence holder for bio-bitumen technology.\n"
        "Pan-India rollout: Bahadurgarh (Plant 1), Malkangiri Odisha (Plant 2).\n"
        "PMC: YUGA (PPS Anantams Corp Pvt Ltd) — Prince Pratap Shah +91 7795242424\n"
        "Haryana PADMA subsidy: Rs 48L | H-GUVY: Rs 17L/yr x 7 yrs\n"
        "Hard cap: Rs 7 Cr (overrun absorbed by PMC personally)\n"
        "Product: PMB-40 only (IS 15462:2019)"
    ),
}

# ══════════════════════════════════════════════════════════════════════
# CLIENT 2 — REX FUELS | Malkangiri, Odisha | 5 TPD (Plant 2)
# ══════════════════════════════════════════════════════════════════════
ODISHA_CONFIG = {
    **BAHADURGARH_CONFIG,  # Start from Bahadurgarh base
    "project_name": "Malkangiri 5 TPD Bio-Bitumen Plant (Plant 2)",
    "project_id": "REX-MLK-002",
    "state": "Odisha",
    "location": "Malkangiri",
    "district": "Malkangiri",
    "site_address": "Malkangiri Industrial Zone, Odisha",
    "site_pincode": "764045",
    "site_district": "Malkangiri",
    "electricity_rate": 7.0,  # Odisha TPCODL tariff
    # Odisha rice straw + bamboo biomass
    "mix_rice_straw_loose": 0.40,
    "mix_rice_straw_baled": 0.20,
    "mix_wheat_straw": 0.10,
    "mix_other_agro_waste": 0.30,
    "biomass_source": "Rice straw + bamboo biomass, Malkangiri / Koraput district",
    "power_source": "TPCODL Grid + 175kVA DG backup",
}

ODISHA_CUSTOMER = {
    **BAHADURGARH_CUSTOMER,
    "name": "Rexy Ravindran Pallithara (Plant 2)",
    "city": "Malkangiri",
    "state": "Odisha",
    "notes": BAHADURGARH_CUSTOMER["notes"] + "\nThis is Plant 2 — Malkangiri, Odisha location.",
}


def run_seed():
    print("Seeding client database...")

    # Check existing
    existing = get_all_customers()
    existing_companies = [c.get("company", "") for c in existing]

    # Seed Bahadurgarh
    if "REX FUELS MANAGEMENT PRIVATE LIMITED" not in existing_companies:
        cid1 = seed_client_if_missing(
            "Rexy Ravindran Pallithara",
            "REX FUELS MANAGEMENT PRIVATE LIMITED",
            BAHADURGARH_CONFIG,
            BAHADURGARH_CUSTOMER
        )
        print(f"  OK Bahadurgarh client seeded (ID: {cid1})")
    else:
        cid1 = next(c["id"] for c in existing if c.get("company") == "REX FUELS MANAGEMENT PRIVATE LIMITED")
        save_client_config(cid1, BAHADURGARH_CONFIG)
        print(f"  OK Bahadurgarh client config updated (ID: {cid1})")

    # Seed Odisha (Plant 2)
    if "Rexy Ravindran Pallithara (Plant 2)" not in [c.get("name","") for c in existing]:
        cid2 = seed_client_if_missing(
            "Rexy Ravindran Pallithara (Plant 2)",
            "REX FUELS — Malkangiri Plant",
            ODISHA_CONFIG,
            ODISHA_CUSTOMER
        )
        print(f"  OK Odisha (Malkangiri) client seeded (ID: {cid2})")
    else:
        print("  OK Odisha client already exists")

    print("\nDone! Both clients are now in the portal.")
    print("Open the portal > Client Manager page > Switch to load any client.")


if __name__ == "__main__":
    run_seed()
