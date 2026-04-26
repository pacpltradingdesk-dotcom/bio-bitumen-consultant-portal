"""
Bio Bitumen Consultant Portal — Master Data Loader
Imports MASTER_DATA_CORRECTED.py from 13_Professional_Upgrade/ and exposes helper functions.
Falls back to embedded defaults if the file is missing, so the portal never crashes.
"""
import importlib.util
import pandas as pd
from config import MASTER_DATA_PATH

_FALLBACK_PLANTS = {
    "05MT": {"label": "5 MT/Day", "inv_cr": 1.5, "loan_cr": 1.05, "equity_cr": 0.45,
             "rev_yr1_cr": 1.2, "rev_yr5_cr": 2.1, "emi_lac_mth": 1.5, "staff": 8,
             "payroll_lac_yr": 24, "power_kw": 15, "biomass_mt_yr": 1500,
             "oil_ltr_day": 1500, "char_kg_day": 750, "dscr_yr3": 1.6, "irr_pct": 28,
             "location": "Vadodara", "state": "Gujarat",
             "civil_lac": 25, "mach_lac": 80, "gst_mach_lac": 14.4,
             "wc_lac": 12, "idc_lac": 6, "preop_lac": 5, "cont_lac": 5, "sec_lac": 2.6},
    "10MT": {"label": "10 MT/Day", "inv_cr": 3.0, "loan_cr": 2.1, "equity_cr": 0.9,
             "rev_yr1_cr": 2.4, "rev_yr5_cr": 4.2, "emi_lac_mth": 3.0, "staff": 12,
             "payroll_lac_yr": 40, "power_kw": 25, "biomass_mt_yr": 3000,
             "oil_ltr_day": 3000, "char_kg_day": 1500, "dscr_yr3": 1.7, "irr_pct": 30,
             "location": "Vadodara", "state": "Gujarat",
             "civil_lac": 45, "mach_lac": 160, "gst_mach_lac": 28.8,
             "wc_lac": 24, "idc_lac": 10, "preop_lac": 8, "cont_lac": 10, "sec_lac": 4.2},
    "20MT": {"label": "20 MT/Day", "inv_cr": 8.0, "loan_cr": 5.6, "equity_cr": 2.4,
             "rev_yr1_cr": 5.5, "rev_yr5_cr": 9.5, "emi_lac_mth": 7.0, "staff": 18,
             "payroll_lac_yr": 72, "power_kw": 45, "biomass_mt_yr": 6000,
             "oil_ltr_day": 6000, "char_kg_day": 3000, "dscr_yr3": 1.8, "irr_pct": 32,
             "location": "Vadodara", "state": "Gujarat",
             "civil_lac": 100, "mach_lac": 380, "gst_mach_lac": 68.4,
             "wc_lac": 60, "idc_lac": 25, "preop_lac": 20, "cont_lac": 25, "sec_lac": 21.6},
}

_md = None
_load_error = None

try:
    if MASTER_DATA_PATH.exists():
        _spec = importlib.util.spec_from_file_location("MASTER_DATA", str(MASTER_DATA_PATH))
        _md = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_md)
    else:
        _load_error = f"Master data file not found: {MASTER_DATA_PATH}"
except Exception as _e:
    _load_error = str(_e)

if _md is not None:
    PLANTS      = _md.PLANTS
    OIL_PRICE   = _md.OIL_PRICE
    CHAR_PRICE  = _md.CHAR_PRICE
    BIOMASS_COST = _md.BIOMASS_COST
    INT_RATE    = _md.INT_RATE
    EMI_TENURE  = _md.EMI_TENURE
    TAX_RATE    = _md.TAX_RATE
    WORKING_DAYS = _md.WORKING_DAYS
    RAMP        = _md.RAMP
    STEADY_STATE = _md.STEADY_STATE
    OIL_YIELD   = _md.OIL_YIELD
    CHAR_YIELD  = _md.CHAR_YIELD
    get_annual_rev       = _md.get_annual_rev
    get_var_cost_per_day = _md.get_var_cost_per_day
    get_monthly_fixed    = _md.get_monthly_fixed
else:
    PLANTS       = _FALLBACK_PLANTS
    OIL_PRICE    = {"base": 55.0, "low": 45.0, "high": 65.0}
    CHAR_PRICE   = {"base": 8.0,  "low": 6.0,  "high": 10.0}
    BIOMASS_COST = {"base": 2500, "low": 2000, "high": 3000}
    INT_RATE     = 0.12
    EMI_TENURE   = 84
    TAX_RATE     = 0.25
    WORKING_DAYS = 300
    RAMP         = {1: 0.50, 2: 0.60, 3: 0.70, 4: 0.75, 5: 0.80, 6: 0.85,
                    7: 0.85, 8: 0.85, 9: 0.85, 10: 0.90, 11: 0.90, 12: 0.90}
    STEADY_STATE = 0.90
    OIL_YIELD    = 0.60
    CHAR_YIELD   = 0.25

    def get_annual_rev(plant, utilization):
        return round(plant["rev_yr5_cr"] * utilization / 0.9, 2)

    def get_var_cost_per_day(plant, utilization):
        biomass_day = plant["biomass_mt_yr"] / WORKING_DAYS * utilization
        return biomass_day * BIOMASS_COST["base"]

    def get_monthly_fixed(plant):
        return plant["payroll_lac_yr"] / 12 * 1e5


def get_plants():
    """Return all plants dict."""
    return PLANTS


def get_plant(key):
    """Return a single plant dict by capacity key (e.g. '20MT').
    If key not in PLANTS (e.g. '25MT'), interpolate from nearest neighbors."""
    if key in PLANTS:
        return PLANTS[key]

    # Interpolate for missing capacities (e.g. 25MT between 20MT and 30MT)
    try:
        tpd = int(key.replace("MT", ""))
        sorted_keys = sorted(PLANTS.keys(), key=lambda k: int(k.replace("MT", "")))
        sorted_tpds = [int(k.replace("MT", "")) for k in sorted_keys]

        # Find bracketing capacities
        lower_key, upper_key = sorted_keys[0], sorted_keys[-1]
        for i, t in enumerate(sorted_tpds):
            if t <= tpd:
                lower_key = sorted_keys[i]
            if t >= tpd:
                upper_key = sorted_keys[i]
                break

        lower = PLANTS[lower_key]
        upper = PLANTS[upper_key]
        lower_tpd = int(lower_key.replace("MT", ""))
        upper_tpd = int(upper_key.replace("MT", ""))

        if lower_tpd == upper_tpd:
            return dict(lower)

        # Linear interpolation factor
        f = (tpd - lower_tpd) / (upper_tpd - lower_tpd)

        interpolated = {}
        for k in lower:
            lv, uv = lower[k], upper[k]
            if isinstance(lv, (int, float)) and isinstance(uv, (int, float)):
                val = lv + (uv - lv) * f
                interpolated[k] = round(val, 2) if isinstance(lv, float) else int(round(val))
            else:
                interpolated[k] = lv  # Use lower for non-numeric (strings)

        interpolated["label"] = f"{tpd} MT/Day"
        return interpolated
    except Exception:
        # Fallback to 20MT
        return PLANTS.get("20MT", list(PLANTS.values())[0])


def get_comparison_df():
    """Return a DataFrame comparing all 7 plant capacities."""
    rows = []
    for key, p in PLANTS.items():
        rows.append({
            "Capacity": p["label"],
            "Key": key,
            "Investment (Cr)": p["inv_cr"],
            "Loan (Cr)": p["loan_cr"],
            "Equity (Cr)": p["equity_cr"],
            "Revenue Yr1 (Cr)": p["rev_yr1_cr"],
            "Revenue Yr5 (Cr)": p["rev_yr5_cr"],
            "EMI (Lac/month)": p["emi_lac_mth"],
            "Staff": p["staff"],
            "Payroll (Lac/yr)": p["payroll_lac_yr"],
            "Power (kW)": p["power_kw"],
            "Biomass (MT/yr)": p["biomass_mt_yr"],
            "Oil (Ltr/day)": p["oil_ltr_day"],
            "Char (Kg/day)": p["char_kg_day"],
            "DSCR Yr3": p["dscr_yr3"],
            "IRR (%)": p["irr_pct"],
            "Location": p["location"],
            "State": p["state"],
        })
    return pd.DataFrame(rows)


def get_investment_breakdown(key):
    """Return investment cost breakdown for a plant capacity."""
    p = PLANTS[key]
    return {
        "Civil & Building": p["civil_lac"],
        "Machinery": p["mach_lac"],
        "GST on Machinery": p["gst_mach_lac"],
        "Working Capital": p["wc_lac"],
        "Interest During Construction": p["idc_lac"],
        "Pre-operative Expenses": p["preop_lac"],
        "Contingency": p["cont_lac"],
        "Security Deposit": p["sec_lac"],
    }


def calculate_emi(loan_cr, rate=None, tenure_months=None):
    """Calculate monthly EMI in Lakhs."""
    rate = rate or INT_RATE
    tenure_months = tenure_months or EMI_TENURE
    principal = loan_cr * 100  # Convert Cr to Lakhs
    r = rate / 12
    emi = principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
    return round(emi, 2)


def calculate_break_even_month(key):
    """Estimate break-even month using ramp-up schedule."""
    p = PLANTS[key]
    cumulative_profit = 0
    total_investment = p["inv_cr"] * 1e7  # in rupees

    for month in range(1, 61):  # up to 5 years
        if month in RAMP:
            util = RAMP[month]
        else:
            util = STEADY_STATE

        if util == 0:
            continue

        daily_rev = (p["oil_ltr_day"] * util * OIL_PRICE["base"] +
                     p["char_kg_day"] * util * CHAR_PRICE["base"])
        monthly_rev = daily_rev * 25  # 25 working days/month

        daily_var = get_var_cost_per_day(p, util)
        monthly_var = daily_var * 25
        monthly_fix = get_monthly_fixed(p)
        monthly_emi = p["emi_lac_mth"] * 1e5 if month >= 19 else 0

        monthly_profit = monthly_rev - monthly_var - monthly_fix - monthly_emi
        cumulative_profit += monthly_profit

        if cumulative_profit >= total_investment:
            return month

    return None  # Not reached in 5 years


def calculate_roi_timeline(key, years=7):
    """Year-by-year financial projection."""
    p = PLANTS[key]
    rows = []
    utilizations = {1: 0.60, 2: 0.70, 3: 0.80, 4: 0.85, 5: 0.90, 6: 0.90, 7: 0.90}

    for yr in range(1, years + 1):
        util = utilizations.get(yr, 0.90)
        rev = get_annual_rev(p, util)
        var_cost = get_var_cost_per_day(p, util) * WORKING_DAYS / 1e7
        fixed_cost = get_monthly_fixed(p) * 12 / 1e7
        emi_annual = p["emi_lac_mth"] * 12 / 100  # Lac to Cr
        ebitda = rev - var_cost - fixed_cost
        profit_after_emi = ebitda - emi_annual

        rows.append({
            "Year": yr,
            "Utilization": f"{util:.0%}",
            "Revenue (Cr)": round(rev, 2),
            "Variable Cost (Cr)": round(var_cost, 2),
            "Fixed Cost (Cr)": round(fixed_cost, 2),
            "EBITDA (Cr)": round(ebitda, 2),
            "EMI (Cr)": round(emi_annual, 2),
            "Net Surplus (Cr)": round(profit_after_emi, 2),
        })

    return pd.DataFrame(rows)
