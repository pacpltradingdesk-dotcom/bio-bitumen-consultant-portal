"""
Bio Bitumen Master Consulting System — FULL AUTO-UPDATE STATE MANAGER
=====================================================================
Change ANY input → ALL financials, charts, reports auto-update everywhere.
Editable Financial Model with complete P&L, ROI, Break-even, IRR.
"""
import streamlit as st
import numpy as np


# ── DEFAULT EDITABLE INPUTS ──────────────────────────────────────────
DEFAULTS = {
    # Plant Configuration
    "capacity_tpd": 20.0,
    "working_days": 300,
    "product_model": "bitumen",  # bitumen / oilchar

    # Revenue Inputs (EDITABLE)
    "selling_price_per_mt": 35000,    # Bio-Bitumen Rs/MT
    "biochar_price_per_mt": 4000,
    "syngas_value_per_mt": 1250,
    "oil_price_per_litre": 38,
    "char_price_per_kg": 10,

    # ── DPR SALE PRICES — Multiple Products (₹/tonne) ──
    "sale_bio_bitumen_vg30": 44000,   # Blended bio-bitumen VG30
    "sale_bio_bitumen_vg40": 48000,   # Blended bio-bitumen VG40
    "sale_biochar_agri": 26000,       # Soil amendment grade
    "sale_biochar_industrial": 32000, # Water filtration / sequestration
    "sale_bio_oil_fuel": 22000,       # Surplus bio-oil as industrial fuel
    "sale_biomass_pellets": 9000,     # 6-8mm pellets for co-firing
    "sale_empty_drum": 280,           # Per drum return value
    "sale_carbon_credit": 12500,      # Per voluntary credit unit ₹

    # Cost Inputs (EDITABLE — legacy per-MT aggregates)
    "raw_material_cost_per_mt": 8000,  # Rs/MT output
    "power_cost_per_mt": 4500,
    "labour_cost_per_mt": 3000,
    "chemical_cost_per_mt": 1500,
    "packaging_cost_per_mt": 500,
    "transport_cost_per_mt": 2000,
    "qc_cost_per_mt": 500,
    "misc_cost_per_mt": 1000,

    # ── DPR RAW MATERIAL PRICES — Individual Feedstock (₹/tonne farm gate) ──
    "price_rice_straw_loose": 1200,   # Punjab/Haryana loose
    "price_rice_straw_baled": 2700,   # Compressed bale
    "price_wheat_straw": 1700,        # UP/MP/Haryana
    "price_bagasse": 1000,            # Ex-sugar mill Maharashtra/TN
    "price_lignin": 4000,             # Kraft lignin from paper mills
    "price_other_agro_waste": 900,    # Groundnut shells, mustard straw
    "price_conv_bitumen": 45750,      # ₹/T ex-IOCL/BPCL VG30 bulk

    # ── DPR FEEDSTOCK MIX WEIGHTS (must sum to 1.0) ──
    "mix_rice_straw_loose": 0.35,
    "mix_rice_straw_baled": 0.20,
    "mix_wheat_straw": 0.15,
    "mix_bagasse": 0.10,
    "mix_lignin": 0.05,
    "mix_other_agro_waste": 0.15,

    # ── DPR PROCESS YIELD PARAMETERS (%) ──
    "bio_oil_yield_pct": 32,          # % of feed → bio-oil (range 20-40, typical 32)
    "bio_char_yield_pct": 28,         # % of feed → bio-char (range 20-38, typical 28)
    "syngas_yield_pct": 22,           # % → syngas, internal fuel (range 10-30, typical 22)
    "process_loss_pct": 18,           # % lost as moisture/flue gas (range 5-25, typical 18)

    # ── DPR LANDING COST COMPONENTS (₹/tonne of agro waste) ──
    "landing_baling": 350,            # Baling + compressing at source
    "landing_primary_transport": 250, # Farm→collection depot (tractor)
    "landing_depot_storage": 300,     # Semi-open storage at depot
    "landing_long_haul": 480,         # Depot→plant long-distance truck
    "landing_load_unload": 140,       # Loading + unloading combined
    "landing_testing_misc": 65,       # Weighbridge, QC testing, misc
    "bitumen_transport": 650,         # ₹/T for bitumen road/rail freight

    # ── DPR PRODUCTION COST PARAMETERS (daily) ──
    "electricity_rate": 7.5,          # ₹/kWh (varies by state 6.8-9.0)
    "electricity_kwh_day": 1200,      # kWh consumed per day
    "diesel_rate": 92,                # ₹/litre market price
    "diesel_litres_day": 120,         # Litres used per day
    "labour_daily_cost": 18000,       # ₹/day total all categories
    "overheads_daily_cost": 12000,    # Plant overheads, admin, security, insurance
    "chemicals_daily_cost": 2500,     # Catalysts, solvents, chemicals
    "waste_loss_factor": 5,           # % added on top of production cost

    # Finance Inputs (EDITABLE)
    "interest_rate": 0.115,
    "equity_ratio": 0.40,
    "emi_tenure_months": 84,
    "tax_rate": 0.25,
    "depreciation_rate": 0.10,
    "insurance_pct": 0.01,
    "admin_pct": 0.02,
    "maintenance_pct": 0.03,

    # NEW — Advanced Financial Inputs
    "land_cost_per_acre": 15,          # Rs Lakhs per acre
    "inflation_rate": 0.05,            # 5% annual inflation
    "revenue_growth_rate": 0.03,       # 3% annual price escalation
    "working_capital_months": 3,       # Months of WC needed
    "moratorium_months": 6,            # Bank moratorium before EMI starts
    "salvage_value_pct": 0.10,         # 10% of asset value at end of life
    "bio_blend_pct": 20,               # 20% bio-oil in bitumen blend
    "num_shifts": 2,                   # 1/2/3 shifts per day
    "carbon_credit_rate_usd": 12,      # USD per tonne CO2

    # ── SITE & DRAWING SETTINGS ──
    "plot_length_m": 120,              # Plot length in metres
    "plot_width_m": 80,                # Plot width in metres
    "seismic_zone": "III",             # IS 1893: II, III, IV, V
    "flood_prone": False,              # True = raise plinths +600mm
    "build_type": "peb",               # peb (PEB sheds) or rcc (full RCC)
    "operating_hours": 16,             # Hours per day (2 shifts = 16)
    "drawing_scale": "1:100",          # Default drawing scale
    "paper_size": "A1",                # A0, A1, A2, A3
    "pyrolysis_temp_C": 500,           # Operating temperature

    # ── DPR PROJECT IDENTITY ──
    "dpr_version": "v1.0",
    "prepared_by": "",
    "report_date": "",

    # Location
    "state": "Uttar Pradesh",
    "location": "Lucknow",
    "district": "",

    # Client & Project Info (flows into ALL documents)
    "client_name": "",
    "client_company": "",
    "client_email": "",
    "client_phone": "",
    "client_gst": "",
    "project_name": "",
    "project_id": "",
    "site_address": "",
    "site_pincode": "",
    "site_district": "",
    "site_area_acres": 0,
    "site_ownership": "",
    "project_start_date": "",
    "project_completion_target": "",
    "site_contact_person": "",
    "site_contact_phone": "",
    "biomass_source": "",
    "power_source": "",
    "water_source": "",
}

# Utilization schedule
UTIL = {1: 0.40, 2: 0.55, 3: 0.70, 4: 0.80, 5: 0.85, 6: 0.90, 7: 0.90}
OIL_YIELD = 0.40
CHAR_YIELD = 0.30


# ══════════════════════════════════════════════════════════════════════
# INDIAN NUMBER FORMATTING — Single function used everywhere
# ══════════════════════════════════════════════════════════════════════
def format_inr(amount, unit="rs"):
    """Format number in Indian system.
    unit='rs': raw rupees → auto-detect Cr/Lac/Rs
    unit='lac': amount is already in Lakhs
    unit='cr': amount is already in Crores
    """
    if amount is None or amount == 0:
        return "₹ 0"
    neg = "-" if amount < 0 else ""
    a = abs(amount)

    if unit == "cr":
        return f"{neg}₹ {a:.2f} Cr"
    if unit == "lac":
        if a >= 100:
            return f"{neg}₹ {a/100:.2f} Cr"
        return f"{neg}₹ {a:.1f} Lac"

    # unit == "rs" — raw rupees, auto-detect scale
    if a >= 10000000:  # 1 Cr = 1,00,00,000
        return f"{neg}₹ {a/10000000:.2f} Cr"
    if a >= 100000:  # 1 Lac = 1,00,000
        return f"{neg}₹ {a/100000:.1f} Lac"
    if a >= 1000:
        # Indian comma format: 1,23,456
        s = str(int(a))
        if len(s) > 3:
            last3 = s[-3:]
            rest = s[:-3]
            parts = []
            while len(rest) > 2:
                parts.insert(0, rest[-2:])
                rest = rest[:-2]
            if rest:
                parts.insert(0, rest)
            return f"{neg}₹ {','.join(parts)},{last3}"
        return f"{neg}₹ {s}"
    return f"{neg}₹ {a:.0f}"


def format_inr_lac(lac_amount):
    """Format Lac amount: ₹ 23.7 Lac or ₹ 6.40 Cr"""
    if lac_amount >= 100:
        return f"₹ {lac_amount/100:.2f} Cr"
    return f"₹ {lac_amount:.1f} Lac"


# ══════════════════════════════════════════════════════════════════════
# BOQ AUTO-CALCULATOR — Generates equipment list from capacity
# ══════════════════════════════════════════════════════════════════════
def calculate_boq(tpd):
    """Auto-generate comprehensive Bill of Quantities based on plant capacity.
    Covers EVERYTHING: gate to gate — unloading, processing, packing, office, lab,
    weighbridge, compound wall, store, parking, roads, utilities, safety, admin.
    65+ items across 15 zones, auto-scaled from capacity.
    """
    s = tpd / 20  # Scale factor (20 TPD = 1.0x reference)

    boq = [
        # ══════════════════════════════════════════════════════════════
        # ZONE 1 — GATE, SECURITY & WEIGHBRIDGE
        # ══════════════════════════════════════════════════════════════
        {"item": "Main Gate (MS Sliding)", "spec": f"{max(6,int(tpd/3))}m wide motorized", "qty": 1,
         "unit": "Nos", "rate_lac": round(2.5 * max(1, s*0.6), 1), "category": "A. Gate & Security"},
        {"item": "Security Guard Booth", "spec": "Prefab cabin with AC", "qty": 1,
         "unit": "Nos", "rate_lac": 1.5, "category": "A. Gate & Security"},
        {"item": "Boom Barrier", "spec": "Automatic with sensor", "qty": 2,
         "unit": "Nos", "rate_lac": 0.8, "category": "A. Gate & Security"},
        {"item": "CCTV System", "spec": f"{max(8, int(tpd/2))} cameras + DVR + monitor", "qty": 1,
         "unit": "Lot", "rate_lac": round(2.5 * max(1, s*0.7), 1), "category": "A. Gate & Security"},
        {"item": "Weighbridge", "spec": "60 MT Electronic (ESSAE/Avery)", "qty": 1,
         "unit": "Nos", "rate_lac": 6.0, "category": "A. Gate & Security"},
        {"item": "Weighbridge Cabin + Software", "spec": "With printer & ticket system", "qty": 1,
         "unit": "Nos", "rate_lac": 1.5, "category": "A. Gate & Security"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 2 — RAW MATERIAL RECEIVING & STORAGE
        # ══════════════════════════════════════════════════════════════
        {"item": "Unloading Ramp/Platform", "spec": f"RCC platform for {max(2,int(tpd/5))} trucks", "qty": 1,
         "unit": "Nos", "rate_lac": round(3 * s, 1), "category": "B. RM Receiving"},
        {"item": "RM Storage Shed (Open)", "spec": f"{int(tpd*100)} sq ft covered semi-open", "qty": 1,
         "unit": "Lot", "rate_lac": round(5 * s, 1), "category": "B. RM Receiving"},
        {"item": "RM Storage Shed (Closed)", "spec": f"{int(tpd*50)} sq ft closed godown", "qty": 1,
         "unit": "Lot", "rate_lac": round(4 * s, 1), "category": "B. RM Receiving"},
        {"item": "Belt Conveyor (RM to Shredder)", "spec": f"{max(10, int(tpd*1.5))}m, 5 TPH", "qty": 1,
         "unit": "Nos", "rate_lac": round(3.5 * s, 1), "category": "B. RM Receiving"},
        {"item": "Front-End Loader", "spec": "1.5 T capacity wheel loader", "qty": max(1, int(s)),
         "unit": "Nos", "rate_lac": round(8 * max(1, s*0.7), 1), "category": "B. RM Receiving"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 3 — PRE-PROCESSING
        # ══════════════════════════════════════════════════════════════
        {"item": "Biomass Shredder", "spec": f"{max(3, int(tpd/4))} TPH Hammer Mill", "qty": max(1, int(s)),
         "unit": "Nos", "rate_lac": round(8 * max(1, s), 1), "category": "C. Pre-Processing"},
        {"item": "Rotary Dryer", "spec": f"{int(tpd*60)} kg/hr capacity", "qty": 1,
         "unit": "Nos", "rate_lac": round(18 * s, 1), "category": "C. Pre-Processing"},
        {"item": "Pelletizer / Briquette Press", "spec": f"{max(2, int(tpd/5))} TPH", "qty": max(1, int(s*0.8)),
         "unit": "Nos", "rate_lac": round(6 * max(1, s*0.8), 1), "category": "C. Pre-Processing"},
        {"item": "Magnetic Separator", "spec": "Remove metal contaminants", "qty": 1,
         "unit": "Nos", "rate_lac": round(1.5 * max(1, s*0.5), 1), "category": "C. Pre-Processing"},
        {"item": "Screw Conveyor (to Reactor)", "spec": f"{max(8, int(tpd))}m enclosed", "qty": 1,
         "unit": "Nos", "rate_lac": round(2.5 * s, 1), "category": "C. Pre-Processing"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 4 — PYROLYSIS REACTOR
        # ══════════════════════════════════════════════════════════════
        {"item": "Pyrolysis Reactor", "spec": f"{tpd:.0f} TPD Continuous Rotary", "qty": max(1, int(tpd/10)),
         "unit": "Nos", "rate_lac": round(35 * max(1, tpd/10), 1), "category": "D. Reactor Zone"},
        {"item": "Reactor Feed Hopper", "spec": f"{int(tpd*2)} MT capacity", "qty": max(1, int(tpd/10)),
         "unit": "Nos", "rate_lac": round(2 * max(1, s*0.6), 1), "category": "D. Reactor Zone"},
        {"item": "Char Discharge System", "spec": "Water-sealed screw cooler", "qty": max(1, int(tpd/10)),
         "unit": "Nos", "rate_lac": round(3 * max(1, s*0.7), 1), "category": "D. Reactor Zone"},
        {"item": "Syngas Burner + Flare", "spec": "For process heat recovery", "qty": 1,
         "unit": "Nos", "rate_lac": round(4 * s, 1), "category": "D. Reactor Zone"},
        {"item": "Temperature Control Panel", "spec": "PLC + HMI for reactor", "qty": 1,
         "unit": "Nos", "rate_lac": round(5 * max(1, s*0.8), 1), "category": "D. Reactor Zone"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 5 — CONDENSATION & OIL RECOVERY
        # ══════════════════════════════════════════════════════════════
        {"item": "Bio-Oil Condenser", "spec": "Shell & Tube Type SS304", "qty": max(1, int(tpd/15)),
         "unit": "Nos", "rate_lac": round(5 * s, 1), "category": "E. Oil Recovery"},
        {"item": "Cooling Tower", "spec": f"{max(10, int(tpd*2))} TR capacity", "qty": 1,
         "unit": "Nos", "rate_lac": round(4 * s, 1), "category": "E. Oil Recovery"},
        {"item": "Oil-Water Separator", "spec": "Gravity + coalescer type", "qty": 1,
         "unit": "Nos", "rate_lac": round(3 * max(1, s*0.7), 1), "category": "E. Oil Recovery"},
        {"item": "Bio-Oil Collection Tank", "spec": f"{int(tpd*3)} KL SS tank", "qty": 2,
         "unit": "Nos", "rate_lac": round(3 * s, 1), "category": "E. Oil Recovery"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 6 — BLENDING SECTION (Bio-Oil + Bitumen)
        # ══════════════════════════════════════════════════════════════
        {"item": "Bitumen Heating Tank", "spec": f"{int(tpd*2)} MT heated to 160°C", "qty": 2,
         "unit": "Nos", "rate_lac": round(8 * s, 1), "category": "F. Blending"},
        {"item": "High Shear Mixer", "spec": "Bio-oil + VG30 inline blending", "qty": 1,
         "unit": "Nos", "rate_lac": round(12 * s, 1), "category": "F. Blending"},
        {"item": "Colloid Mill", "spec": "Fine dispersion 0.1 micron", "qty": 1,
         "unit": "Nos", "rate_lac": round(6 * s, 1), "category": "F. Blending"},
        {"item": "Bitumen Transfer Pump", "spec": "Gear pump 160°C rated", "qty": 2,
         "unit": "Nos", "rate_lac": round(2 * max(1, s*0.7), 1), "category": "F. Blending"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 7 — STORAGE TANKS
        # ══════════════════════════════════════════════════════════════
        {"item": "Finished Bitumen Tank (Heated)", "spec": f"{int(tpd*3)} MT with heating coils", "qty": 2,
         "unit": "Nos", "rate_lac": round(10 * s, 1), "category": "G. Storage"},
        {"item": "Bio-Oil Bulk Storage", "spec": f"{int(tpd*5)} KL MS tank", "qty": 2,
         "unit": "Nos", "rate_lac": round(5 * s, 1), "category": "G. Storage"},
        {"item": "Bio-Char Storage Silo", "spec": f"{int(tpd*4)} MT capacity", "qty": 1,
         "unit": "Nos", "rate_lac": round(4 * s, 1), "category": "G. Storage"},
        {"item": "Diesel Storage Tank", "spec": "5 KL underground + dispensing", "qty": 1,
         "unit": "Nos", "rate_lac": 3.0, "category": "G. Storage"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 8 — PACKING & DISPATCH
        # ══════════════════════════════════════════════════════════════
        {"item": "Bitumen Drum Filling Machine", "spec": "180 kg MS drum auto-fill", "qty": 1,
         "unit": "Nos", "rate_lac": round(4 * max(1, s*0.7), 1), "category": "H. Packing & Dispatch"},
        {"item": "Bio-Char Bagging Machine", "spec": "50 kg HDPE bag filler + sealer", "qty": 1,
         "unit": "Nos", "rate_lac": round(3 * max(1, s*0.6), 1), "category": "H. Packing & Dispatch"},
        {"item": "Tanker Loading Arm", "spec": "Bottom loading for bulk bitumen", "qty": 1,
         "unit": "Nos", "rate_lac": round(5 * max(1, s*0.7), 1), "category": "H. Packing & Dispatch"},
        {"item": "Loading Bay / Dispatch Area", "spec": f"RCC platform for {max(2, int(tpd/8))} trucks", "qty": 1,
         "unit": "Lot", "rate_lac": round(4 * s, 1), "category": "H. Packing & Dispatch"},
        {"item": "Forklift", "spec": "3T diesel/electric", "qty": max(1, int(s)),
         "unit": "Nos", "rate_lac": round(6 * max(1, s*0.7), 1), "category": "H. Packing & Dispatch"},
        {"item": "Parking Area (Truck/Visitor)", "spec": f"For {max(5, int(tpd/2))} vehicles", "qty": 1,
         "unit": "Lot", "rate_lac": round(3 * s, 1), "category": "H. Packing & Dispatch"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 9 — ELECTRICAL & POWER
        # ══════════════════════════════════════════════════════════════
        {"item": "HT/LT Transformer", "spec": f"{max(100, int(tpd*8))} kVA", "qty": 1,
         "unit": "Nos", "rate_lac": round(8 * s, 1), "category": "I. Electrical"},
        {"item": "DG Set (Standby)", "spec": f"{max(50, int(tpd*5))} kVA Kirloskar/Cummins", "qty": 1,
         "unit": "Nos", "rate_lac": round(8 * s, 1), "category": "I. Electrical"},
        {"item": "MCC + PCC Panels", "spec": "Motor control + power control", "qty": 1,
         "unit": "Lot", "rate_lac": round(8 * s, 1), "category": "I. Electrical"},
        {"item": "Electrical Cabling & Earthing", "spec": "HT/LT cables + earthing grid", "qty": 1,
         "unit": "Lot", "rate_lac": round(7 * s, 1), "category": "I. Electrical"},
        {"item": "Street Lighting (Plant)", "spec": f"{max(10, int(tpd))} LED high-mast lights", "qty": 1,
         "unit": "Lot", "rate_lac": round(2 * max(1, s*0.6), 1), "category": "I. Electrical"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 10 — UTILITIES
        # ══════════════════════════════════════════════════════════════
        {"item": "Pipe Rack & Process Piping", "spec": "MS + SS piping complete", "qty": 1,
         "unit": "Lot", "rate_lac": round(10 * s, 1), "category": "J. Utilities"},
        {"item": "Compressed Air System", "spec": f"{max(5, int(tpd/3))} HP screw compressor + dryer", "qty": 1,
         "unit": "Nos", "rate_lac": round(3 * max(1, s*0.7), 1), "category": "J. Utilities"},
        {"item": "Water Supply System", "spec": "Borewell + OHT + distribution", "qty": 1,
         "unit": "Lot", "rate_lac": round(4 * s, 1), "category": "J. Utilities"},
        {"item": "ETP (Effluent Treatment)", "spec": f"{max(5, int(tpd/2))} KLD capacity", "qty": 1,
         "unit": "Nos", "rate_lac": round(5 * s, 1), "category": "J. Utilities"},
        {"item": "Sewage & Septic System", "spec": "Septic tank + soak pit", "qty": 1,
         "unit": "Lot", "rate_lac": 2.0, "category": "J. Utilities"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 11 — LAB & QUALITY CONTROL
        # ══════════════════════════════════════════════════════════════
        {"item": "Penetration Tester (IS:1203)", "spec": "Bitumen penetration 0-300", "qty": 1,
         "unit": "Nos", "rate_lac": 1.2, "category": "K. Laboratory"},
        {"item": "Softening Point Apparatus", "spec": "Ring & Ball (IS:1205)", "qty": 1,
         "unit": "Nos", "rate_lac": 0.8, "category": "K. Laboratory"},
        {"item": "Viscosity Bath", "spec": "Kinematic viscosity (IS:1206)", "qty": 1,
         "unit": "Nos", "rate_lac": 1.5, "category": "K. Laboratory"},
        {"item": "Ductility Tester", "spec": "IS:1208 standard", "qty": 1,
         "unit": "Nos", "rate_lac": 1.0, "category": "K. Laboratory"},
        {"item": "Flash Point Apparatus", "spec": "Cleveland Open Cup (IS:1209)", "qty": 1,
         "unit": "Nos", "rate_lac": 0.8, "category": "K. Laboratory"},
        {"item": "Moisture Oven & Balance", "spec": "Hot air oven + precision balance", "qty": 1,
         "unit": "Nos", "rate_lac": 0.6, "category": "K. Laboratory"},
        {"item": "Marshall Stability Tester", "spec": "For bitumen mix design", "qty": 1,
         "unit": "Nos", "rate_lac": 2.5, "category": "K. Laboratory"},
        {"item": "Lab Furniture & Glassware", "spec": "Benches, fume hood, glassware set", "qty": 1,
         "unit": "Lot", "rate_lac": 3.0, "category": "K. Laboratory"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 12 — SAFETY & ENVIRONMENT
        # ══════════════════════════════════════════════════════════════
        {"item": "Fire Fighting System", "spec": "Hydrant network + hose reels", "qty": 1,
         "unit": "Lot", "rate_lac": round(6 * s, 1), "category": "L. Safety & Environment"},
        {"item": "Fire Extinguishers", "spec": "ABC/CO2/Foam (as per NBC)", "qty": max(10, int(tpd)),
         "unit": "Nos", "rate_lac": round(0.03 * max(10, tpd), 1), "category": "L. Safety & Environment"},
        {"item": "Pollution Control (Bag Filter)", "spec": "Pulse jet bag filter + ID fan", "qty": 1,
         "unit": "Nos", "rate_lac": round(6 * s, 1), "category": "L. Safety & Environment"},
        {"item": "Scrubber + Stack", "spec": f"Wet scrubber + {max(15, int(tpd))}m chimney stack", "qty": 1,
         "unit": "Nos", "rate_lac": round(5 * s, 1), "category": "L. Safety & Environment"},
        {"item": "Gas Detection System", "spec": "H2S, CO, LEL sensors + alarm", "qty": 1,
         "unit": "Lot", "rate_lac": round(2 * max(1, s*0.6), 1), "category": "L. Safety & Environment"},
        {"item": "Emergency Eyewash + Shower", "spec": "SS gravity-fed stations", "qty": max(2, int(s*2)),
         "unit": "Nos", "rate_lac": round(0.3 * max(2, s*2), 1), "category": "L. Safety & Environment"},
        {"item": "PPE Kit (Initial Stock)", "spec": "Helmets, gloves, boots, goggles, vests", "qty": max(15, int(tpd*1.2)),
         "unit": "Sets", "rate_lac": round(0.05 * max(15, tpd*1.2), 1), "category": "L. Safety & Environment"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 13 — CIVIL & BUILDING WORKS
        # ══════════════════════════════════════════════════════════════
        {"item": "Main Plant Building (PEB)", "spec": f"{int(tpd*80)} sq ft pre-engineered", "qty": 1,
         "unit": "Lot", "rate_lac": round(25 * s, 1), "category": "M. Civil Works"},
        {"item": "Office Building (RCC)", "spec": f"{max(400, int(tpd*20))} sq ft 2-floor", "qty": 1,
         "unit": "Lot", "rate_lac": round(8 * max(1, s*0.7), 1), "category": "M. Civil Works"},
        {"item": "Lab Building", "spec": f"{max(300, int(tpd*15))} sq ft", "qty": 1,
         "unit": "Lot", "rate_lac": round(4 * max(1, s*0.6), 1), "category": "M. Civil Works"},
        {"item": "Control Room", "spec": f"{max(200, int(tpd*10))} sq ft AC room", "qty": 1,
         "unit": "Lot", "rate_lac": round(3 * max(1, s*0.6), 1), "category": "M. Civil Works"},
        {"item": "Canteen & Rest Room", "spec": f"For {max(15, int(tpd*1.2))} workers", "qty": 1,
         "unit": "Lot", "rate_lac": round(3 * max(1, s*0.6), 1), "category": "M. Civil Works"},
        {"item": "Toilet Block (M/F)", "spec": "As per Factory Act", "qty": 1,
         "unit": "Lot", "rate_lac": round(2.5 * max(1, s*0.5), 1), "category": "M. Civil Works"},
        {"item": "Compound Wall", "spec": f"{int(max(200, tpd*30))} RFT RCC/brick", "qty": 1,
         "unit": "Lot", "rate_lac": round(6 * s, 1), "category": "M. Civil Works"},
        {"item": "Internal Roads (CC/Bitumen)", "spec": f"{int(max(300, tpd*25))} sqm", "qty": 1,
         "unit": "Lot", "rate_lac": round(5 * s, 1), "category": "M. Civil Works"},
        {"item": "Drainage & Storm Water", "spec": "RCC channel + catch pits", "qty": 1,
         "unit": "Lot", "rate_lac": round(2.5 * s, 1), "category": "M. Civil Works"},
        {"item": "Green Belt / Landscaping", "spec": f"{int(max(500, tpd*40))} sqm plantation", "qty": 1,
         "unit": "Lot", "rate_lac": round(1.5 * max(1, s*0.5), 1), "category": "M. Civil Works"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 14 — OFFICE & ADMIN
        # ══════════════════════════════════════════════════════════════
        {"item": "Office Furniture", "spec": "Desks, chairs, cabinets, meeting table", "qty": 1,
         "unit": "Lot", "rate_lac": round(3 * max(1, s*0.6), 1), "category": "N. Office & Admin"},
        {"item": "IT Equipment", "spec": "Computers, printer, scanner, UPS, LAN", "qty": 1,
         "unit": "Lot", "rate_lac": round(3 * max(1, s*0.5), 1), "category": "N. Office & Admin"},
        {"item": "Air Conditioning (Office+Lab)", "spec": f"{max(3, int(tpd/5))} split units", "qty": 1,
         "unit": "Lot", "rate_lac": round(2 * max(1, s*0.5), 1), "category": "N. Office & Admin"},
        {"item": "Signage & Safety Boards", "spec": "Plant signs, safety notices, directions", "qty": 1,
         "unit": "Lot", "rate_lac": 0.5, "category": "N. Office & Admin"},
        {"item": "Worker Lockers & Benches", "spec": f"For {max(15, int(tpd*1.2))} staff", "qty": 1,
         "unit": "Lot", "rate_lac": round(1 * max(1, s*0.5), 1), "category": "N. Office & Admin"},

        # ══════════════════════════════════════════════════════════════
        # ZONE 15 — MAINTENANCE WORKSHOP
        # ══════════════════════════════════════════════════════════════
        {"item": "Workshop Tools & Equipment", "spec": "Welding, grinding, cutting, hand tools", "qty": 1,
         "unit": "Lot", "rate_lac": round(3 * max(1, s*0.6), 1), "category": "O. Maintenance"},
        {"item": "Spare Parts Store", "spec": f"{max(100, int(tpd*8))} sq ft with racks", "qty": 1,
         "unit": "Lot", "rate_lac": round(2 * max(1, s*0.5), 1), "category": "O. Maintenance"},
        {"item": "Overhead Crane / Hoist", "spec": f"{max(2, int(tpd/5))} T capacity", "qty": 1,
         "unit": "Nos", "rate_lac": round(4 * max(1, s*0.7), 1), "category": "O. Maintenance"},
    ]

    for item in boq:
        item["amount_lac"] = round(item["qty"] * item["rate_lac"], 1)

    return boq


# Print helper — inject JS for browser print
PRINT_BUTTON_JS = """
<script>
function printPage() { window.print(); }
</script>
"""


def _full_default():
    """Return full config with defaults + empty derived fields."""
    cfg = dict(DEFAULTS)
    cfg.update({
        # Derived — auto-calculated
        "capacity_key": "20MT",
        "plant_data": {},
        "investment_cr": 0, "investment_lac": 0,
        "loan_cr": 0, "equity_cr": 0,
        "annual_production_mt": 0,
        "total_revenue_per_mt": 0,
        "total_variable_cost_per_mt": 0,
        "revenue_yr1_lac": 0, "revenue_yr5_lac": 0,
        "revenue_yr1_cr": 0, "revenue_yr5_cr": 0,
        "profit_per_mt": 0, "monthly_profit_lac": 0,
        "emi_lac_mth": 0, "irr_pct": 0, "dscr_yr3": 0,
        "roi_pct": 0, "break_even_months": 0,
        "staff": 0, "power_kw": 0, "biomass_mt_day": 0,
        "oil_ltr_day": 0, "char_kg_day": 0,
        "payroll_lac_yr": 0,
        "roi_timeline": [], "sensitivity_matrix": [],
        "monthly_pnl": {},
        "boq": [],  # Auto-calculated Bill of Quantities
        "display_mode": False,  # Meeting presentation mode

        # NEW — Advanced Financial Outputs (auto-calculated)
        "land_cost_lac": 0,
        "working_capital_lac": 0,
        "npv_lac": 0,              # Net Present Value
        "current_ratio": 0,
        "debt_equity_ratio": 0,
        "net_worth_yr5_lac": 0,
        "carbon_credit_annual_lac": 0,
        "total_investment_with_land": 0,
        "dscr_schedule": [],       # DSCR for all 7 years
        "cash_flow_statement": [],  # Operating + Investing + Financing
        "balance_sheet": [],        # Assets = Liabilities + Equity
    })
    return cfg


def _load_saved_config():
    """Try to load last saved config from database."""
    try:
        from database import get_configurations
        configs = get_configurations()
        if configs:
            saved = configs[0].get("config_json", {})
            if saved and saved.get("capacity_tpd"):
                return saved
    except Exception:
        pass
    return None


def save_config_to_db():
    """Save current config to database for persistence across refreshes."""
    try:
        from database import save_configuration
        cfg = st.session_state.get("master_config", {})
        # Save only editable inputs (not derived values)
        inputs_only = {k: v for k, v in cfg.items()
                       if k in DEFAULTS or k in ("capacity_key",)}
        save_configuration(None, "auto_save", inputs_only)
    except Exception:
        pass


def init_state():
    """Initialize state. Load from DB if available, else use defaults."""
    if "master_config" not in st.session_state:
        saved = _load_saved_config()
        if saved:
            cfg = _full_default()
            # Merge saved inputs into defaults
            for k, v in saved.items():
                if k in cfg:
                    cfg[k] = v
            st.session_state["master_config"] = cfg
        else:
            st.session_state["master_config"] = _full_default()
        recalculate()


def get_config():
    """Get current config (auto-init if needed)."""
    init_state()
    return st.session_state["master_config"]


def update_field(field, value):
    """Update one field, recalculate everything, auto-save, and sync documents."""
    init_state()
    st.session_state["master_config"][field] = value
    if field == "capacity_tpd":
        _sync_capacity_key(value)
    recalculate()
    save_config_to_db()
    _auto_sync_docs()


def update_fields(updates: dict):
    """Update multiple fields, recalculate once, auto-save, and sync documents."""
    init_state()
    for k, v in updates.items():
        st.session_state["master_config"][k] = v
    if "capacity_tpd" in updates:
        _sync_capacity_key(updates["capacity_tpd"])
    recalculate()
    save_config_to_db()
    _auto_sync_docs()


def _auto_sync_docs():
    """Auto-regenerate all documents when config changes."""
    try:
        from engines.auto_doc_sync import sync_all_documents
        from config import COMPANY
        cfg = st.session_state.get("master_config", {})
        if cfg.get("investment_cr", 0) > 0:
            sync_all_documents(cfg, COMPANY)
    except Exception:
        pass  # Don't block UI if sync fails


def _sync_capacity_key(tpd):
    presets = [5, 10, 15, 20, 30, 40, 50]
    nearest = min(presets, key=lambda x: abs(x - tpd))
    st.session_state["master_config"]["capacity_key"] = f"{nearest:02d}MT"


def recalculate():
    """FULL RECALCULATION — triggered on ANY input change."""
    cfg = st.session_state["master_config"]
    tpd = cfg["capacity_tpd"]
    days = cfg["working_days"]

    # ── Interpolate plant parameters ──────────────────────────────
    try:
        from interpolation_engine import interpolate_all
        plant = interpolate_all(tpd)
    except Exception:
        plant = {"inv_cr": tpd * 0.32, "staff": int(tpd * 0.9), "power_kw": tpd * 5,
                 "oil_ltr_day": tpd * 400, "char_kg_day": tpd * 300,
                 "mach_lac": tpd * 18, "civil_lac": tpd * 3}

    cfg["plant_data"] = plant
    cfg["biomass_mt_day"] = tpd
    cfg["staff"] = int(plant.get("staff", tpd * 0.9))
    cfg["power_kw"] = round(plant.get("power_kw", tpd * 5))
    cfg["oil_ltr_day"] = round(plant.get("oil_ltr_day", tpd * 400))
    cfg["char_kg_day"] = round(plant.get("char_kg_day", tpd * 300))
    cfg["payroll_lac_yr"] = round(plant.get("payroll_lac_yr", cfg["staff"] * 2.5), 1)

    # ── Investment ────────────────────────────────────────────────
    inv_cr = plant.get("inv_cr", tpd * 0.32)
    cfg["investment_cr"] = round(inv_cr, 2)
    cfg["investment_lac"] = round(inv_cr * 100, 2)
    cfg["loan_cr"] = round(inv_cr * (1 - cfg["equity_ratio"]), 2)
    cfg["equity_cr"] = round(inv_cr * cfg["equity_ratio"], 2)

    # ── Production ────────────────────────────────────────────────
    output_per_day = tpd * OIL_YIELD  # MT output/day
    annual_output_full = output_per_day * days  # at 100% util
    cfg["annual_production_mt"] = round(annual_output_full, 0)

    # ── Revenue per MT ────────────────────────────────────────────
    if cfg["product_model"] == "bitumen":
        rev_per_mt = cfg["selling_price_per_mt"] + cfg["biochar_price_per_mt"] + cfg["syngas_value_per_mt"]
    else:
        # Oil+char model: convert to per-MT-output equivalent
        rev_per_mt = (cfg["oil_price_per_litre"] * 1000 * OIL_YIELD +
                      cfg["char_price_per_kg"] * 1000 * CHAR_YIELD) / OIL_YIELD
    cfg["total_revenue_per_mt"] = round(rev_per_mt, 0)

    # ── Variable cost per MT ──────────────────────────────────────
    var_per_mt = (cfg["raw_material_cost_per_mt"] + cfg["power_cost_per_mt"] +
                  cfg["labour_cost_per_mt"] + cfg["chemical_cost_per_mt"] +
                  cfg["packaging_cost_per_mt"] + cfg["transport_cost_per_mt"] +
                  cfg["qc_cost_per_mt"] + cfg["misc_cost_per_mt"])
    cfg["total_variable_cost_per_mt"] = round(var_per_mt, 0)

    # ── Profit per MT ─────────────────────────────────────────────
    cfg["profit_per_mt"] = round(rev_per_mt - var_per_mt, 0)

    # ── EMI ───────────────────────────────────────────────────────
    loan_lac = cfg["loan_cr"] * 100
    r = cfg["interest_rate"] / 12
    n = cfg["emi_tenure_months"]
    if r > 0 and n > 0 and loan_lac > 0:
        cfg["emi_lac_mth"] = round(loan_lac * r * (1 + r)**n / ((1 + r)**n - 1), 2)
    else:
        cfg["emi_lac_mth"] = 0

    # ── 7-Year P&L Timeline ──────────────────────────────────────
    inv_lac = cfg["investment_lac"]
    timeline = []
    for yr in range(1, 8):
        util = UTIL.get(yr, 0.90)
        prod_mt = annual_output_full * util
        rev_lac = prod_mt * rev_per_mt / 1e5
        var_lac = prod_mt * var_per_mt / 1e5

        # Fixed costs
        insurance = inv_lac * cfg["insurance_pct"]
        admin = inv_lac * cfg["admin_pct"]
        maint = plant.get("mach_lac", inv_lac * 0.4) * cfg["maintenance_pct"]
        fixed_lac = insurance + admin + maint

        ebitda = rev_lac - var_lac - fixed_lac
        depr = inv_lac * cfg["depreciation_rate"]
        interest = cfg["loan_cr"] * 100 * cfg["interest_rate"]
        pbt = ebitda - depr - interest
        tax = max(0, pbt * cfg["tax_rate"])
        pat = pbt - tax
        cash_accrual = pat + depr
        debt_service = cfg["emi_lac_mth"] * 12
        dscr = cash_accrual / debt_service if debt_service > 0 else 0

        timeline.append({
            "Year": yr, "Utilization": f"{util:.0%}",
            "Production (MT)": round(prod_mt, 0),
            "Revenue (Lac)": round(rev_lac, 2),
            "Variable Cost (Lac)": round(var_lac, 2),
            "Fixed Cost (Lac)": round(fixed_lac, 2),
            "EBITDA (Lac)": round(ebitda, 2),
            "Depreciation (Lac)": round(depr, 2),
            "Interest (Lac)": round(interest, 2),
            "PBT (Lac)": round(pbt, 2),
            "Tax (Lac)": round(tax, 2),
            "PAT (Lac)": round(pat, 2),
            "Cash Accrual (Lac)": round(cash_accrual, 2),
            "DSCR": round(dscr, 2),
        })

    cfg["roi_timeline"] = timeline

    # Extract key metrics from Year 3 and Year 5
    if len(timeline) >= 5:
        cfg["revenue_yr1_lac"] = timeline[0]["Revenue (Lac)"]
        cfg["revenue_yr5_lac"] = timeline[4]["Revenue (Lac)"]
        cfg["revenue_yr1_cr"] = round(cfg["revenue_yr1_lac"] / 100, 2)
        cfg["revenue_yr5_cr"] = round(cfg["revenue_yr5_lac"] / 100, 2)
        cfg["dscr_yr3"] = timeline[2]["DSCR"]
        cfg["monthly_profit_lac"] = round(timeline[4]["PAT (Lac)"] / 12, 2)

    # ── ROI ───────────────────────────────────────────────────────
    if inv_lac > 0 and len(timeline) >= 5:
        annual_profit = timeline[4]["PAT (Lac)"]
        cfg["roi_pct"] = round(annual_profit / inv_lac * 100, 1)
    else:
        cfg["roi_pct"] = 0

    # ── Break-Even ────────────────────────────────────────────────
    if len(timeline) > 0:
        avg_monthly = sum(t["PAT (Lac)"] for t in timeline[:5]) / 60  # avg monthly over 5 yrs
        if avg_monthly > 0:
            cfg["break_even_months"] = int(np.ceil(inv_lac / (avg_monthly + timeline[0].get("Depreciation (Lac)", 0) / 12)))
        else:
            cfg["break_even_months"] = 0
    else:
        cfg["break_even_months"] = 0

    # ── IRR (Newton-Raphson) ──────────────────────────────────────
    equity_lac = cfg["equity_cr"] * 100
    cash_flows = [-equity_lac]
    for t in timeline:
        cash_flows.append(t["Cash Accrual (Lac)"] - cfg["emi_lac_mth"] * 12 * 0.5)  # approx principal
    try:
        irr = 0.20
        for _ in range(100):
            npv = sum(cf / (1 + irr)**i for i, cf in enumerate(cash_flows))
            dnpv = sum(-i * cf / (1 + irr)**(i + 1) for i, cf in enumerate(cash_flows))
            if abs(dnpv) < 1e-10:
                break
            irr = irr - npv / dnpv
        cfg["irr_pct"] = round(max(0, min(irr * 100, 200)), 1)
    except Exception:
        cfg["irr_pct"] = 0

    # ── Sensitivity Matrix (3x3) ──────────────────────────────────
    sell_variants = [cfg["selling_price_per_mt"] * 0.85, cfg["selling_price_per_mt"], cfg["selling_price_per_mt"] * 1.15]
    cost_variants = [var_per_mt * 0.80, var_per_mt, var_per_mt * 1.20]
    sensitivity = []
    for vc in cost_variants:
        row = []
        for sp in sell_variants:
            prod = annual_output_full * 0.85  # Yr5 util
            rev = prod * sp / 1e5
            var = prod * vc / 1e5
            ebitda = rev - var - (inv_lac * 0.06)
            row.append(round(ebitda, 1))
        sensitivity.append(row)
    cfg["sensitivity_matrix"] = sensitivity

    # ── Monthly P&L (for Year 5 steady state) ────────────────────
    if len(timeline) >= 5:
        yr5 = timeline[4]
        cfg["monthly_pnl"] = {
            "Revenue": round(yr5["Revenue (Lac)"] / 12, 2),
            "Variable Cost": round(yr5["Variable Cost (Lac)"] / 12, 2),
            "Fixed Cost": round(yr5["Fixed Cost (Lac)"] / 12, 2),
            "EBITDA": round(yr5["EBITDA (Lac)"] / 12, 2),
            "EMI": cfg["emi_lac_mth"],
            "Net Surplus": round((yr5["PAT (Lac)"] + yr5["Depreciation (Lac)"]) / 12 - cfg["emi_lac_mth"], 2),
        }

    # ── BOQ Auto-Calculation (from capacity) ─────────────────────
    cfg["boq"] = calculate_boq(tpd)

    # ── Break-even month alias ───────────────────────────────────
    cfg["break_even_month"] = cfg["break_even_months"]

    # ── Capacity key ─────────────────────────────────────────────
    cfg["capacity_key"] = f"{int(tpd):02d}MT"

    # ══════════════════════════════════════════════════════════════
    # NEW — ADVANCED FINANCIAL CALCULATIONS (CA-Grade)
    # ══════════════════════════════════════════════════════════════

    # 1. Land cost
    cfg["land_cost_lac"] = round(cfg["site_area_acres"] * cfg["land_cost_per_acre"], 1)

    # 2. Working capital
    monthly_cost = (var_per_mt * annual_output_full * 0.85 / 12) / 1e5  # Monthly cost in Lac at 85% util
    cfg["working_capital_lac"] = round(monthly_cost * cfg["working_capital_months"], 1)

    # 3. Total investment including land
    cfg["total_investment_with_land"] = round(cfg["investment_cr"] + cfg["land_cost_lac"] / 100, 2)

    # 4. Carbon credit revenue
    co2_saved = tpd * days * 0.85 * 0.35  # At 85% util, 0.35 tCO2/MT
    usd_inr = 84  # Default FX
    try:
        from engines.free_apis import get_exchange_rates
        fx = get_exchange_rates()
        if "error" not in fx:
            usd_inr = fx.get("usd_inr", 84)
    except Exception:
        pass
    cfg["carbon_credit_annual_lac"] = round(co2_saved * cfg["carbon_credit_rate_usd"] * usd_inr / 1e5, 1)

    # 5. DSCR Schedule (all 7 years)
    cfg["dscr_schedule"] = [round(t["DSCR"], 2) for t in timeline] if timeline else []

    # 6. NPV (Net Present Value at cost of equity = 15%)
    cost_of_equity = 0.15
    npv = -equity_lac
    for i, t in enumerate(timeline, 1):
        npv += t["Cash Accrual (Lac)"] / (1 + cost_of_equity) ** i
    cfg["npv_lac"] = round(npv, 1)

    # 7. Debt-Equity Ratio (Year 1)
    cfg["debt_equity_ratio"] = round(cfg["loan_cr"] / cfg["equity_cr"], 2) if cfg["equity_cr"] > 0 else 0

    # 8. Current Ratio (simplified: current assets / current liabilities)
    # Current assets = WC + 3 months receivables
    current_assets = cfg["working_capital_lac"] + (cfg.get("revenue_yr5_lac", 0) / 12 * 3)
    current_liabilities = cfg["emi_lac_mth"] * 12 + (inv_lac * 0.06)  # Annual EMI + fixed costs
    cfg["current_ratio"] = round(current_assets / current_liabilities, 2) if current_liabilities > 0 else 0

    # 9. Net Worth Year 5
    retained_earnings = sum(t["PAT (Lac)"] for t in timeline[:5]) if len(timeline) >= 5 else 0
    cfg["net_worth_yr5_lac"] = round(equity_lac + retained_earnings, 1)

    # 10. Cash Flow Statement (7 years)
    cash_flow = []
    outstanding_loan = loan_lac
    for yr_idx, t in enumerate(timeline):
        # Apply inflation to revenue from year 2 onwards
        inflation_factor = (1 + cfg["inflation_rate"]) ** yr_idx
        revenue_growth_factor = (1 + cfg["revenue_growth_rate"]) ** yr_idx

        operating = t["Cash Accrual (Lac)"]
        investing = -inv_lac * 0.05 if yr_idx == 0 else 0  # Capex maintenance
        emi_annual = cfg["emi_lac_mth"] * 12
        # Moratorium: no EMI for first N months
        if yr_idx == 0 and cfg["moratorium_months"] > 0:
            emi_annual = cfg["emi_lac_mth"] * max(0, 12 - cfg["moratorium_months"])
        principal_paid = emi_annual - (outstanding_loan * cfg["interest_rate"])
        outstanding_loan = max(0, outstanding_loan - max(0, principal_paid))

        financing = -emi_annual
        net_cash = operating + investing + financing

        cash_flow.append({
            "Year": t["Year"],
            "Operating (Lac)": round(operating, 1),
            "Investing (Lac)": round(investing, 1),
            "Financing (Lac)": round(financing, 1),
            "Net Cash (Lac)": round(net_cash, 1),
            "Loan Outstanding (Lac)": round(outstanding_loan, 1),
        })
    cfg["cash_flow_statement"] = cash_flow

    # 11. Balance Sheet Summary (simplified, Year 5)
    if len(timeline) >= 5:
        total_assets = inv_lac * (1 - cfg["depreciation_rate"] * 5) + cfg["working_capital_lac"] + \
                       sum(cf["Net Cash (Lac)"] for cf in cash_flow[:5])
        loan_yr5 = cash_flow[4]["Loan Outstanding (Lac)"] if len(cash_flow) >= 5 else 0
        equity_yr5 = cfg["net_worth_yr5_lac"]
        cfg["balance_sheet"] = [
            {"Item": "Fixed Assets (Net)", "Amount (Lac)": round(inv_lac * (1 - cfg["depreciation_rate"] * 5), 1)},
            {"Item": "Working Capital", "Amount (Lac)": cfg["working_capital_lac"]},
            {"Item": "Cash & Bank", "Amount (Lac)": round(sum(cf["Net Cash (Lac)"] for cf in cash_flow[:5]), 1)},
            {"Item": "TOTAL ASSETS", "Amount (Lac)": round(total_assets, 1)},
            {"Item": "---", "Amount (Lac)": 0},
            {"Item": "Term Loan Outstanding", "Amount (Lac)": round(loan_yr5, 1)},
            {"Item": "Net Worth (Equity + Retained)", "Amount (Lac)": round(equity_yr5, 1)},
            {"Item": "TOTAL LIABILITIES", "Amount (Lac)": round(loan_yr5 + equity_yr5, 1)},
        ]
