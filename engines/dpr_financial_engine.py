"""
DPR Financial Engine — Working Capital, Break-Even, Sensitivity, 5-Year Cash Flow
==================================================================================
Reads from DPR cost sheet outputs. NEVER hardcodes financial results.
Implements Master Operator Prompt Sections 6, 7, 8, 9.
"""
from engines.detailed_costing import calculate_complete_cost_sheet


# ══════════════════════════════════════════════════════════════════════
# SECTION 6 — WORKING CAPITAL CALCULATOR
# ══════════════════════════════════════════════════════════════════════
def calculate_working_capital(cfg, cs=None):
    """Calculate working capital requirement from DPR cost sheet outputs.

    Args:
        cfg: Master config dict from state_manager
        cs: Pre-calculated cost sheet (optional, will compute if None)
    Returns:
        Dict with WC components, total, and detailed breakdown
    """
    if cs is None:
        cs = calculate_complete_cost_sheet(cfg)

    rm_daily = cs["rm"]["daily_cost"]
    bit_daily = cs["bitumen"]["daily_cost"]
    gross_daily = cs["gross_daily"]
    rev_daily = cs["total_rev_daily"]

    # Working capital component days (editable defaults)
    debtor_days_rm = cfg.get("wc_debtor_days_rm", 30)
    debtor_days_bit = cfg.get("wc_debtor_days_bit", 15)
    wip_days = cfg.get("wc_wip_days", 3)
    fg_days = cfg.get("wc_fg_days", 7)
    debtor_days_sales = cfg.get("wc_debtor_days_sales", 30)
    creditor_days = cfg.get("wc_creditor_days", 15)
    advance_pct = cfg.get("wc_advance_pct", 5) / 100

    # Current Assets
    rm_stock = rm_daily * debtor_days_rm
    bit_stock = bit_daily * debtor_days_bit
    wip = gross_daily * wip_days
    fg_stock = rev_daily * fg_days
    debtors = rev_daily * debtor_days_sales

    total_current_assets = rm_stock + bit_stock + wip + fg_stock + debtors

    # Current Liabilities
    creditors = rm_daily * creditor_days
    advances = rev_daily * advance_pct * 30  # 30-day equivalent

    total_current_liabilities = creditors + advances

    # Net Working Capital
    net_wc = total_current_assets - total_current_liabilities

    # WC as % of investment
    investment = cfg.get("investment_cr", 6.4) * 1e7
    wc_pct_of_investment = (net_wc / investment * 100) if investment > 0 else 0

    items = [
        {"component": "Raw Material Stock", "days": debtor_days_rm,
         "basis": "RM Daily Cost", "amount": round(rm_stock, 0), "type": "asset"},
        {"component": "Conv. Bitumen Stock", "days": debtor_days_bit,
         "basis": "Bitumen Daily Cost", "amount": round(bit_stock, 0), "type": "asset"},
        {"component": "Work-in-Progress", "days": wip_days,
         "basis": "Gross Daily Cost", "amount": round(wip, 0), "type": "asset"},
        {"component": "Finished Goods Stock", "days": fg_days,
         "basis": "Daily Revenue", "amount": round(fg_stock, 0), "type": "asset"},
        {"component": "Sundry Debtors", "days": debtor_days_sales,
         "basis": "Daily Revenue", "amount": round(debtors, 0), "type": "asset"},
        {"component": "Less: Sundry Creditors", "days": creditor_days,
         "basis": "RM Daily Cost", "amount": round(-creditors, 0), "type": "liability"},
        {"component": "Less: Advances Received", "days": 30,
         "basis": f"{advance_pct*100:.0f}% of Revenue", "amount": round(-advances, 0), "type": "liability"},
    ]

    return {
        "items": items,
        "total_current_assets": round(total_current_assets, 0),
        "total_current_liabilities": round(total_current_liabilities, 0),
        "net_working_capital": round(net_wc, 0),
        "net_wc_lac": round(net_wc / 1e5, 1),
        "net_wc_cr": round(net_wc / 1e7, 2),
        "wc_pct_of_investment": round(wc_pct_of_investment, 1),
        "current_ratio": round(total_current_assets / total_current_liabilities, 2) if total_current_liabilities > 0 else 0,
    }


# ══════════════════════════════════════════════════════════════════════
# SECTION 7 — BREAK-EVEN ANALYSIS
# ══════════════════════════════════════════════════════════════════════
def calculate_break_even(cfg, cs=None):
    """Calculate break-even in tonnes, days, and capacity utilization %.

    Uses fixed/variable cost split from DPR cost sheet.
    """
    if cs is None:
        cs = calculate_complete_cost_sheet(cfg)

    pnl = cs["annual_pnl"]
    blend_tpd = cs["blend_total_tpd"]
    operating_days = pnl["operating_days"]
    annual_output = blend_tpd * operating_days

    # Fixed costs (don't change with production volume)
    fixed_costs = (
        pnl["depreciation"]
        + pnl["interest"]
        + pnl["sga"]
        + cs["production"]["overheads"] * operating_days
        + cs["production"]["labour_adjusted"] * operating_days
    )

    # Variable costs per tonne of blend
    variable_daily = (
        cs["rm"]["daily_cost"]
        + cs["bitumen"]["daily_cost"]
        + cs["landing"]["total_daily"]
        + cs["production"]["energy_net"]
        + cs["production"]["chemicals"]
        + cs["waste"]["total"]
        + cs["packing"]["total"]
        + cs["outbound"]["total"]
    )
    variable_per_tonne = variable_daily / blend_tpd if blend_tpd > 0 else 0

    # Revenue per tonne (blended sale price + by-product credit per tonne)
    by_product_per_tonne = cs["revenue"]["by_product_credit_daily"] / blend_tpd if blend_tpd > 0 else 0
    scrap_per_tonne = cs["scrap"]["total"] / blend_tpd if blend_tpd > 0 else 0
    effective_revenue_per_tonne = cs["sale_price_pt"] + by_product_per_tonne + scrap_per_tonne

    # Contribution margin
    contribution_per_tonne = effective_revenue_per_tonne - variable_per_tonne
    contribution_ratio = contribution_per_tonne / effective_revenue_per_tonne if effective_revenue_per_tonne > 0 else 0

    # Break-even calculations
    if contribution_per_tonne > 0:
        be_tonnes = fixed_costs / contribution_per_tonne
        be_days = be_tonnes / blend_tpd if blend_tpd > 0 else 999
        be_pct = (be_tonnes / annual_output * 100) if annual_output > 0 else 999
    else:
        be_tonnes = 999999
        be_days = 999
        be_pct = 999

    margin_of_safety = max(0, 100 - be_pct)

    # Price break-even (min selling price at given costs)
    total_cost_per_tonne = variable_per_tonne + (fixed_costs / annual_output if annual_output > 0 else 0)
    min_selling_price = total_cost_per_tonne - by_product_per_tonne - scrap_per_tonne

    # Volume break-even at different prices
    price_scenarios = []
    base_price = cs["sale_price_pt"]
    for pct_change in [-20, -10, 0, 10, 20]:
        test_price = base_price * (1 + pct_change / 100)
        test_contribution = test_price + by_product_per_tonne + scrap_per_tonne - variable_per_tonne
        if test_contribution > 0:
            test_be_tonnes = fixed_costs / test_contribution
            test_be_pct = (test_be_tonnes / annual_output * 100) if annual_output > 0 else 999
        else:
            test_be_tonnes = 999999
            test_be_pct = 999
        price_scenarios.append({
            "price_change": f"{pct_change:+d}%",
            "selling_price": round(test_price, 0),
            "be_tonnes": round(test_be_tonnes, 0),
            "be_pct": round(test_be_pct, 1),
            "viable": test_be_pct < 100,
        })

    return {
        "fixed_costs_annual": round(fixed_costs, 0),
        "variable_per_tonne": round(variable_per_tonne, 0),
        "effective_revenue_per_tonne": round(effective_revenue_per_tonne, 0),
        "contribution_per_tonne": round(contribution_per_tonne, 0),
        "contribution_ratio": round(contribution_ratio, 3),
        "be_tonnes_annual": round(be_tonnes, 0),
        "be_days": round(be_days, 0),
        "be_pct": round(be_pct, 1),
        "margin_of_safety": round(margin_of_safety, 1),
        "min_selling_price": round(min_selling_price, 0),
        "total_cost_per_tonne": round(total_cost_per_tonne, 0),
        "price_scenarios": price_scenarios,
        "blend_tpd": blend_tpd,
        "annual_output": round(annual_output, 0),
    }


# ══════════════════════════════════════════════════════════════════════
# SECTION 8 — SENSITIVITY ANALYSIS (±10%, ±20%, ±30%)
# ══════════════════════════════════════════════════════════════════════
def calculate_sensitivity(cfg, cs=None):
    """Stress-test 6 key variables at ±10%, ±20%, ±30%.

    For each variable at each stress level:
    - Temporarily set DPR variable to stressed value
    - Run full cost sheet recalc
    - Capture net_profit, cost_per_tonne, gross_margin
    - Reset variable
    - Color code: green = better, red = worse than base
    """
    if cs is None:
        cs = calculate_complete_cost_sheet(cfg)

    base_profit = cs["annual_pnl"]["net_profit"]
    base_cpt = cs["net_cpt"]
    base_margin = cs["margin_pct"]

    # Variables to stress-test
    variables = [
        {"key": "price_conv_bitumen", "label": "Conv. Bitumen Price",
         "base": cfg.get("price_conv_bitumen", 45750), "impact": "cost"},
        {"key": "sale_bio_bitumen_vg30", "label": "Sale Price VG30",
         "base": cfg.get("sale_bio_bitumen_vg30", 44000), "impact": "revenue"},
        {"key": "capacity_tpd", "label": "Plant Capacity (TPD)",
         "base": cfg.get("capacity_tpd", 20), "impact": "volume"},
        {"key": "bio_blend_pct", "label": "Bio-Oil Blend Ratio %",
         "base": cfg.get("bio_blend_pct", 20), "impact": "mix"},
        {"key": "bio_oil_yield_pct", "label": "Bio-Oil Yield %",
         "base": cfg.get("bio_oil_yield_pct", 32), "impact": "efficiency"},
        {"key": "price_rice_straw_loose", "label": "Rice Straw Price",
         "base": cfg.get("price_rice_straw_loose", 1200), "impact": "cost"},
    ]

    stress_levels = [-30, -20, -10, 10, 20, 30]
    results = []

    for var in variables:
        row = {"variable": var["label"], "base_value": var["base"], "scenarios": []}
        for pct in stress_levels:
            stressed_value = var["base"] * (1 + pct / 100)
            # Create temporary config with stressed value
            temp_cfg = dict(cfg)
            temp_cfg[var["key"]] = stressed_value
            try:
                temp_cs = calculate_complete_cost_sheet(temp_cfg)
                temp_profit = temp_cs["annual_pnl"]["net_profit"]
                temp_cpt = temp_cs["net_cpt"]
                temp_margin = temp_cs["margin_pct"]
                profit_change = temp_profit - base_profit
                profit_change_pct = (profit_change / abs(base_profit) * 100) if base_profit != 0 else 0
            except Exception:
                temp_profit = base_profit
                temp_cpt = base_cpt
                temp_margin = base_margin
                profit_change = 0
                profit_change_pct = 0

            row["scenarios"].append({
                "stress_pct": pct,
                "stressed_value": round(stressed_value, 0),
                "net_profit": round(temp_profit, 0),
                "cost_per_tonne": round(temp_cpt, 0),
                "margin_pct": round(temp_margin, 1),
                "profit_change": round(profit_change, 0),
                "profit_change_pct": round(profit_change_pct, 1),
                "better": profit_change > 0,
            })
        results.append(row)

    return {
        "base_profit": round(base_profit, 0),
        "base_cpt": round(base_cpt, 0),
        "base_margin": round(base_margin, 1),
        "variables": results,
        "stress_levels": stress_levels,
    }


# ══════════════════════════════════════════════════════════════════════
# SECTION 9 — 5-YEAR CASH FLOW MODEL (with capacity ramp-up)
# ══════════════════════════════════════════════════════════════════════
def calculate_5year_cashflow(cfg, cs=None):
    """Project 5-year cash flow with capacity ramp-up schedule.

    Ramp-up: Year 1=60%, Year 2=75%, Year 3=85%, Year 4=90%, Year 5=95%
    Cost scaling: semi-variable (70% fixed base + 30% scales with utilization)
    """
    if cs is None:
        cs = calculate_complete_cost_sheet(cfg)

    pnl = cs["annual_pnl"]
    utilization_schedule = [0.60, 0.75, 0.85, 0.90, 0.95]

    # Base annual figures at 100% utilization
    annual_revenue_100 = pnl["revenue"]
    annual_rm = cs["rm"]["daily_cost"] * pnl["operating_days"]
    annual_bitumen = cs["bitumen"]["daily_cost"] * pnl["operating_days"]
    annual_landing = cs["landing"]["total_daily"] * pnl["operating_days"]
    annual_prod = cs["production"]["total"] * pnl["operating_days"]
    annual_packing = cs["packing"]["total"] * pnl["operating_days"]
    annual_outbound = cs["outbound"]["total"] * pnl["operating_days"]
    annual_waste = cs["waste"]["total"] * pnl["operating_days"]
    annual_scrap = cs["scrap"]["total"] * pnl["operating_days"]

    annual_total_variable = annual_rm + annual_bitumen + annual_landing + annual_prod + annual_packing + annual_outbound + annual_waste

    total_investment = pnl["total_investment"]
    debt_amount = pnl["debt_amount"]
    interest_rate = cfg.get("interest_rate", 0.115)
    depreciation = pnl["depreciation"]
    tax_rate = cfg.get("tax_rate", 0.25)

    years = []
    cumulative_cf = -total_investment
    payback_year = None

    for n in range(5):
        util = utilization_schedule[n]
        revenue_scaler = util
        cost_scaler = 0.70 + util * 0.30  # Semi-variable

        revenue = annual_revenue_100 * revenue_scaler
        total_cost = annual_total_variable * cost_scaler
        scrap_credit = annual_scrap * revenue_scaler

        gross_profit = revenue - total_cost + scrap_credit

        sga = revenue * 0.02
        ebitda = gross_profit - sga
        ebit = ebitda - depreciation

        # Reducing debt: interest decreases 10% per year
        debt_reduction_factor = max(0, 1 - n * 0.10)
        interest = debt_amount * interest_rate * debt_reduction_factor

        ebt = ebit - interest
        tax = max(0, ebt) * tax_rate
        pat = ebt - tax

        operating_cf = pat + depreciation
        investing_cf = 0  # No capex after year 1
        free_cf = operating_cf + investing_cf

        cumulative_cf += free_cf

        if payback_year is None and cumulative_cf >= 0:
            payback_year = n + 1

        years.append({
            "year": n + 1,
            "utilization": util,
            "utilization_pct": f"{util*100:.0f}%",
            "revenue": round(revenue, 0),
            "revenue_cr": round(revenue / 1e7, 2),
            "total_cost": round(total_cost, 0),
            "scrap_credit": round(scrap_credit, 0),
            "gross_profit": round(gross_profit, 0),
            "gross_margin_pct": round(gross_profit / revenue * 100, 1) if revenue > 0 else 0,
            "sga": round(sga, 0),
            "ebitda": round(ebitda, 0),
            "ebitda_cr": round(ebitda / 1e7, 2),
            "depreciation": round(depreciation, 0),
            "ebit": round(ebit, 0),
            "interest": round(interest, 0),
            "ebt": round(ebt, 0),
            "tax": round(tax, 0),
            "pat": round(pat, 0),
            "pat_cr": round(pat / 1e7, 2),
            "operating_cf": round(operating_cf, 0),
            "free_cf": round(free_cf, 0),
            "cumulative_cf": round(cumulative_cf, 0),
            "cumulative_cf_cr": round(cumulative_cf / 1e7, 2),
        })

    # Summary metrics
    total_pat_5yr = sum(y["pat"] for y in years)
    avg_roi = (total_pat_5yr / 5 / total_investment * 100) if total_investment > 0 else 0

    return {
        "years": years,
        "total_investment": round(total_investment, 0),
        "total_investment_cr": round(total_investment / 1e7, 2),
        "payback_year": payback_year or ">5",
        "total_pat_5yr": round(total_pat_5yr, 0),
        "total_pat_5yr_cr": round(total_pat_5yr / 1e7, 2),
        "avg_annual_roi": round(avg_roi, 1),
        "utilization_schedule": utilization_schedule,
        "year5_pat_cr": years[4]["pat_cr"] if len(years) >= 5 else 0,
    }


# ══════════════════════════════════════════════════════════════════════
# FINISHED GOODS TABLE — Revenue by product with buyers
# ══════════════════════════════════════════════════════════════════════
def calculate_finished_goods(cfg, cs=None):
    """Generate finished goods pricing table with buyer segments."""
    if cs is None:
        cs = calculate_complete_cost_sheet(cfg)

    revenue = cs["revenue"]
    operating_days = cfg.get("working_days", 300)

    items = []
    for item in revenue["items"]:
        items.append({
            "product": item["product"],
            "qty_per_day": item["qty_tpd"],
            "qty_per_year": round(item["qty_tpd"] * operating_days, 0),
            "sale_price": item["price"],
            "daily_revenue": item["daily_rev"],
            "annual_revenue": round(item["daily_rev"] * operating_days, 0),
            "annual_revenue_cr": round(item["daily_rev"] * operating_days / 1e7, 2),
            "buyer": item["buyer"],
            "pct_of_total": round(item["daily_rev"] / revenue["total_daily"] * 100, 1) if revenue["total_daily"] > 0 else 0,
        })

    # Add scrap/carbon credits as a line
    scrap = cs["scrap"]
    items.append({
        "product": "Scrap & Carbon Credits",
        "qty_per_day": "-",
        "qty_per_year": "-",
        "sale_price": "-",
        "daily_revenue": scrap["total"],
        "annual_revenue": round(scrap["total"] * operating_days, 0),
        "annual_revenue_cr": round(scrap["total"] * operating_days / 1e7, 2),
        "buyer": "Various (drums, bags, carbon market)",
        "pct_of_total": round(scrap["total"] / (revenue["total_daily"] + scrap["total"]) * 100, 1) if revenue["total_daily"] > 0 else 0,
    })

    grand_total_daily = revenue["total_daily"] + scrap["total"]
    grand_total_annual = grand_total_daily * operating_days

    return {
        "items": items,
        "total_daily": round(grand_total_daily, 0),
        "total_annual": round(grand_total_annual, 0),
        "total_annual_cr": round(grand_total_annual / 1e7, 2),
    }
