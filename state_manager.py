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

    # Cost Inputs (EDITABLE)
    "raw_material_cost_per_mt": 8000,  # Rs/MT output
    "power_cost_per_mt": 4500,
    "labour_cost_per_mt": 3000,
    "chemical_cost_per_mt": 1500,
    "packaging_cost_per_mt": 500,
    "transport_cost_per_mt": 2000,
    "qc_cost_per_mt": 500,
    "misc_cost_per_mt": 1000,

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
    """Auto-generate Bill of Quantities based on plant capacity."""
    scale = tpd / 20  # 20 TPD as reference

    boq = [
        {"item": "Pyrolysis Reactor", "spec": f"{tpd:.0f} TPD Continuous", "qty": max(1, int(tpd/10)),
         "unit": "Nos", "rate_lac": round(35 * max(1, tpd/10), 1), "category": "Machinery"},
        {"item": "Biomass Shredder", "spec": "5-10 TPH Hammer Mill", "qty": max(1, int(scale)),
         "unit": "Nos", "rate_lac": round(8 * scale, 1), "category": "Machinery"},
        {"item": "Rotary Dryer", "spec": f"{tpd*1.5:.0f} kg/hr", "qty": 1,
         "unit": "Nos", "rate_lac": round(18 * scale, 1), "category": "Machinery"},
        {"item": "Bio-Oil Condenser", "spec": "Shell & Tube Type", "qty": max(1, int(tpd/15)),
         "unit": "Nos", "rate_lac": round(5 * scale, 1), "category": "Machinery"},
        {"item": "Bitumen Heating Tank", "spec": f"{tpd*2:.0f} MT capacity", "qty": 2,
         "unit": "Nos", "rate_lac": round(8 * scale, 1), "category": "Machinery"},
        {"item": "High Shear Mixer", "spec": "Bio-oil + VG30 blending", "qty": 1,
         "unit": "Nos", "rate_lac": round(12 * scale, 1), "category": "Machinery"},
        {"item": "Colloid Mill", "spec": "Fine dispersion unit", "qty": 1,
         "unit": "Nos", "rate_lac": round(6 * scale, 1), "category": "Machinery"},
        {"item": "Storage Tanks (Bitumen)", "spec": f"{tpd*3:.0f} MT heated", "qty": 2,
         "unit": "Nos", "rate_lac": round(10 * scale, 1), "category": "Storage"},
        {"item": "Bio-Oil Storage Tank", "spec": f"{tpd*2:.0f} KL", "qty": 2,
         "unit": "Nos", "rate_lac": round(5 * scale, 1), "category": "Storage"},
        {"item": "DG Set", "spec": f"{max(50, int(tpd*5))} kVA", "qty": 1,
         "unit": "Nos", "rate_lac": round(8 * scale, 1), "category": "Electrical"},
        {"item": "Electrical Panel + HT", "spec": "Complete distribution", "qty": 1,
         "unit": "Lot", "rate_lac": round(15 * scale, 1), "category": "Electrical"},
        {"item": "Weighbridge", "spec": "60 MT Electronic", "qty": 1,
         "unit": "Nos", "rate_lac": 6, "category": "Civil"},
        {"item": "Lab Equipment", "spec": "Complete QC Lab", "qty": 1,
         "unit": "Lot", "rate_lac": round(15 * scale, 1), "category": "Quality"},
        {"item": "Fire Safety System", "spec": "Hydrants + Extinguishers", "qty": 1,
         "unit": "Lot", "rate_lac": round(8 * scale, 1), "category": "Safety"},
        {"item": "Pollution Control", "spec": "Bag filter + Scrubber + Stack", "qty": 1,
         "unit": "Lot", "rate_lac": round(12 * scale, 1), "category": "Environment"},
        {"item": "Pipe Rack & Piping", "spec": "MS + SS piping complete", "qty": 1,
         "unit": "Lot", "rate_lac": round(10 * scale, 1), "category": "Piping"},
        {"item": "Civil & Building", "spec": f"{int(tpd*150)} sq ft PEB + RCC", "qty": 1,
         "unit": "Lot", "rate_lac": round(40 * scale, 1), "category": "Civil"},
        {"item": "Road & Compound Wall", "spec": "Internal roads + boundary", "qty": 1,
         "unit": "Lot", "rate_lac": round(8 * scale, 1), "category": "Civil"},
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
