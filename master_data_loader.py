"""
Bio Bitumen Consultant Portal — Master Data Loader
Imports MASTER_DATA.py from PROFESSIONAL_UPGRADE/ and exposes helper functions.
"""
import importlib.util
import pandas as pd
from config import MASTER_DATA_PATH

# ── Dynamic import of MASTER_DATA.py ──────���──────────────────────────
_spec = importlib.util.spec_from_file_location("MASTER_DATA", str(MASTER_DATA_PATH))
_md = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_md)

# Re-export key constants
PLANTS = _md.PLANTS
OIL_PRICE = _md.OIL_PRICE
CHAR_PRICE = _md.CHAR_PRICE
BIOMASS_COST = _md.BIOMASS_COST
INT_RATE = _md.INT_RATE
EMI_TENURE = _md.EMI_TENURE
TAX_RATE = _md.TAX_RATE
WORKING_DAYS = _md.WORKING_DAYS
RAMP = _md.RAMP
STEADY_STATE = _md.STEADY_STATE
OIL_YIELD = _md.OIL_YIELD
CHAR_YIELD = _md.CHAR_YIELD

# Re-export functions
get_annual_rev = _md.get_annual_rev
get_var_cost_per_day = _md.get_var_cost_per_day
get_monthly_fixed = _md.get_monthly_fixed


def get_plants():
    """Return all plants dict."""
    return PLANTS


def get_plant(key):
    """Return a single plant dict by capacity key (e.g. '20MT')."""
    return PLANTS[key]


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
