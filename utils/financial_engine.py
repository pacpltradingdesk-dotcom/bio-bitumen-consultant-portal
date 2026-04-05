"""
UNIFIED Financial Engine — SINGLE SOURCE OF TRUTH for ALL calculations.
Every page MUST call calculate_financials() from here.
NO page may have its own independent financial formula.

CAPEX Rate: Rs 32 Lac/TPD (plant + machinery)
Working Capital: 3 months of operating cost
Pre-operative: 5% of plant CAPEX
Total = Plant CAPEX + WC + Pre-op
"""
import numpy as np


# Fixed parameters
CAPEX_PER_TPD = 32  # Rs Lakhs per TPD
OIL_YIELD = 0.40
CHAR_YIELD = 0.30
SYNGAS_YIELD = 0.25
UTIL_SCHEDULE = {1: 0.40, 2: 0.55, 3: 0.70, 4: 0.80, 5: 0.85, 6: 0.90, 7: 0.90}


def calculate_financials(
    capacity_tpd=20,
    selling_price=35000,
    raw_material_cost=8000,
    power_cost=4500,
    labour_cost=3000,
    chemical_cost=1500,
    packaging_cost=500,
    transport_cost=2000,
    qc_cost=500,
    misc_cost=1000,
    biochar_price=4000,
    syngas_value=1250,
    interest_rate_pct=11.5,
    equity_pct=40,
    working_days=300,
    emi_tenure_months=84,
    tax_rate_pct=25,
    depreciation_rate_pct=10,
):
    """
    THE unified financial calculator. All pages must use this.
    Returns dict with every metric needed across the system.
    """
    tpd = max(1, capacity_tpd)
    days = max(200, working_days)

    # ── CAPEX ────────────────────────────────────────────────────
    plant_capex_lac = max(150, tpd * CAPEX_PER_TPD)
    wc_months = 3
    output_per_day = tpd * OIL_YIELD
    annual_output = output_per_day * days

    var_cost_per_mt = (raw_material_cost + power_cost + labour_cost +
                        chemical_cost + packaging_cost + transport_cost +
                        qc_cost + misc_cost)

    monthly_var_cost = (var_cost_per_mt * annual_output * 0.85 / 12) / 1e5  # Lac
    working_capital_lac = round(monthly_var_cost * wc_months, 1)
    pre_operative_lac = round(plant_capex_lac * 0.05, 1)

    investment_lac = round(plant_capex_lac + working_capital_lac + pre_operative_lac, 1)
    investment_cr = round(investment_lac / 100, 2)

    # ── LOAN / EQUITY ────────────────────────────────────────────
    equity_ratio = equity_pct / 100
    equity_lac = round(investment_lac * equity_ratio, 1)
    loan_lac = round(investment_lac * (1 - equity_ratio), 1)
    equity_cr = round(equity_lac / 100, 2)
    loan_cr = round(loan_lac / 100, 2)

    # ── EMI ──────────────────────────────────────────────────────
    interest_rate = interest_rate_pct / 100
    r = interest_rate / 12
    n = emi_tenure_months
    if r > 0 and n > 0 and loan_lac > 0:
        emi_lac = round(loan_lac * r * (1 + r) ** n / ((1 + r) ** n - 1), 2)
    else:
        emi_lac = 0

    # ── REVENUE ──────────────────────────────────────────────────
    rev_per_mt = selling_price + biochar_price + syngas_value
    profit_per_mt = rev_per_mt - var_cost_per_mt

    # ── 7-YEAR P&L ──────────────────────────────────────────────
    dep_rate = depreciation_rate_pct / 100
    tax_rate = tax_rate_pct / 100
    timeline = []

    for yr in range(1, 8):
        util = UTIL_SCHEDULE.get(yr, 0.90)
        prod = annual_output * util
        rev_lac = prod * rev_per_mt / 1e5
        var_lac = prod * var_cost_per_mt / 1e5
        fixed_lac = investment_lac * 0.06  # insurance + admin + maintenance
        ebitda_lac = rev_lac - var_lac - fixed_lac
        dep_lac = investment_lac * dep_rate
        interest_lac = loan_lac * interest_rate
        pbt_lac = ebitda_lac - dep_lac - interest_lac
        tax_lac = max(0, pbt_lac * tax_rate)
        pat_lac = pbt_lac - tax_lac
        cash_lac = pat_lac + dep_lac
        ds_lac = emi_lac * 12
        dscr = cash_lac / ds_lac if ds_lac > 0 else 0

        timeline.append({
            "Year": yr, "Utilization": f"{util:.0%}",
            "Production (MT)": round(prod),
            "Revenue (Lac)": round(rev_lac, 1),
            "Variable Cost (Lac)": round(var_lac, 1),
            "Fixed Cost (Lac)": round(fixed_lac, 1),
            "EBITDA (Lac)": round(ebitda_lac, 1),
            "Depreciation (Lac)": round(dep_lac, 1),
            "Interest (Lac)": round(interest_lac, 1),
            "PBT (Lac)": round(pbt_lac, 1),
            "Tax (Lac)": round(tax_lac, 1),
            "PAT (Lac)": round(pat_lac, 1),
            "Cash Accrual (Lac)": round(cash_lac, 1),
            "DSCR": round(dscr, 2),
        })

    # ── KEY METRICS ──────────────────────────────────────────────
    roi = timeline[4]["PAT (Lac)"] / investment_lac * 100 if investment_lac > 0 else 0
    monthly_profit = timeline[4]["PAT (Lac)"] / 12 if len(timeline) >= 5 else 0
    dscr_yr3 = timeline[2]["DSCR"] if len(timeline) >= 3 else 0
    rev_yr5 = timeline[4]["Revenue (Lac)"] if len(timeline) >= 5 else 0
    rev_yr1 = timeline[0]["Revenue (Lac)"] if timeline else 0

    # Break-even
    avg_monthly_profit = sum(t["PAT (Lac)"] for t in timeline[:5]) / 60 if len(timeline) >= 5 else 0
    avg_monthly_dep = timeline[0]["Depreciation (Lac)"] / 12 if timeline else 0
    if avg_monthly_profit + avg_monthly_dep > 0:
        break_even = int(np.ceil(investment_lac / (avg_monthly_profit + avg_monthly_dep)))
    else:
        break_even = 0

    # IRR (Newton-Raphson)
    flows = [-equity_lac]
    for t in timeline:
        flows.append(t["Cash Accrual (Lac)"] - emi_lac * 12 * 0.5)
    irr = 0.20
    try:
        for _ in range(200):
            npv_val = sum(cf / (1 + irr) ** i for i, cf in enumerate(flows))
            dnpv = sum(-i * cf / (1 + irr) ** (i + 1) for i, cf in enumerate(flows))
            if abs(dnpv) < 1e-10:
                break
            irr = irr - npv_val / dnpv
        irr_pct = round(max(0, min(irr * 100, 200)), 1)
    except Exception:
        irr_pct = 0

    # NPV at 15%
    npv = -equity_lac
    for i, t in enumerate(timeline, 1):
        npv += t["Cash Accrual (Lac)"] / (1.15 ** i)

    # Staff
    staff = max(8, int(tpd * 0.9))
    power_kw = max(25, int(tpd * 5))

    return {
        # Investment
        "investment_lac": investment_lac,
        "investment_cr": investment_cr,
        "plant_capex_lac": plant_capex_lac,
        "working_capital_lac": working_capital_lac,
        "pre_operative_lac": pre_operative_lac,
        "loan_lac": loan_lac,
        "loan_cr": loan_cr,
        "equity_lac": equity_lac,
        "equity_cr": equity_cr,

        # Per MT
        "revenue_per_mt": rev_per_mt,
        "var_cost_per_mt": var_cost_per_mt,
        "profit_per_mt": profit_per_mt,

        # Key Metrics
        "roi_pct": round(roi, 1),
        "irr_pct": irr_pct,
        "dscr_yr3": round(dscr_yr3, 2),
        "break_even_months": break_even,
        "emi_lac": emi_lac,
        "monthly_profit_lac": round(monthly_profit, 1),
        "npv_lac": round(npv, 1),
        "debt_equity_ratio": round(loan_lac / equity_lac, 2) if equity_lac > 0 else 0,

        # Revenue
        "revenue_yr1_lac": round(rev_yr1, 1),
        "revenue_yr5_lac": round(rev_yr5, 1),

        # Operations
        "staff": staff,
        "power_kw": power_kw,
        "annual_output_mt": round(annual_output),

        # Timeline
        "timeline": timeline,
        "dscr_schedule": [round(t["DSCR"], 2) for t in timeline],

        # Capacity reference
        "capex_per_tpd": CAPEX_PER_TPD,
    }
