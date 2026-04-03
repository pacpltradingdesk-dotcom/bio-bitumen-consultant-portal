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
