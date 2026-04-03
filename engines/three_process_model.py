"""
Three Process Model Engine — CA-Grade Financial Analysis
==========================================================
Process 1: Biomass → Pyrolysis → Bio-Oil → Bitumen (FULL CHAIN)
Process 2: Buy Bio-Oil → Blend with VG30 → Bio-Bitumen (BLENDING ONLY)
Process 3: Buy Biomass Pellets → Pyrolysis → Sell Oil + Char (RAW OUTPUT)

Each model calculates: Capex, Opex, Revenue, P&L, ROI, IRR, DSCR, Break-even
"""
import numpy as np


UTIL = {1: 0.40, 2: 0.55, 3: 0.70, 4: 0.80, 5: 0.85, 6: 0.90, 7: 0.90}
WORKING_DAYS = 300
OIL_YIELD = 0.40
CHAR_YIELD = 0.30


def _calc_irr(cash_flows, guess=0.20):
    """Newton-Raphson IRR."""
    irr = guess
    for _ in range(200):
        npv = sum(cf / (1 + irr) ** t for t, cf in enumerate(cash_flows))
        dnpv = sum(-t * cf / (1 + irr) ** (t + 1) for t, cf in enumerate(cash_flows))
        if abs(dnpv) < 1e-10:
            break
        irr = irr - npv / dnpv
        if irr < -0.5 or irr > 5:
            return 0
    return max(0, min(irr * 100, 200))


def _calc_emi(loan_lac, rate, months):
    r = rate / 12
    if r <= 0 or months <= 0 or loan_lac <= 0:
        return 0
    return round(loan_lac * r * (1 + r) ** months / ((1 + r) ** months - 1), 2)


def calculate_process(process_id, tpd, state_costs=None, **overrides):
    """
    Calculate full financials for a given process model.

    Args:
        process_id: 1, 2, or 3
        tpd: Capacity in MT/Day (biomass input)
        state_costs: dict from STATE_COSTS (optional, for state-specific calc)
        **overrides: Override any default parameter

    Returns: dict with all financial outputs
    """
    # ── DEFAULT PARAMETERS ────────────────────────────────────────
    params = {
        "interest_rate": 0.115,
        "equity_ratio": 0.40,
        "emi_tenure": 84,
        "tax_rate": 0.25,
        "depreciation_rate": 0.10,
        "insurance_pct": 0.01,
        "admin_pct": 0.02,
        "maintenance_pct": 0.03,
        "working_days": WORKING_DAYS,
    }
    params.update(overrides)

    # State-specific adjustments
    if state_costs:
        biomass_cost = state_costs.get("biomass_cost_mt", 2000)
        power_rate = state_costs.get("power_rate", 7.50)
        labor_daily = state_costs.get("labor_daily", 450)
        land_cost = state_costs.get("land_lac_acre", 15)
        transport_km = state_costs.get("transport_per_km", 5.5)
        subsidy_pct = state_costs.get("subsidy_pct", 0) / 100
    else:
        biomass_cost = 2000
        power_rate = 7.50
        labor_daily = 450
        land_cost = 15
        transport_km = 5.5
        subsidy_pct = 0

    output_mt_day = tpd * OIL_YIELD  # MT of product per day
    annual_output_full = output_mt_day * params["working_days"]

    # ═══════════════════════════════════════════════════════════════
    # PROCESS 1: FULL CHAIN (Biomass → Pyrolysis → Bio-Oil → Bitumen)
    # ═══════════════════════════════════════════════════════════════
    if process_id == 1:
        name = "Full Chain: Biomass → Pyrolysis → Bio-Bitumen"
        short = "Full Chain"

        # Capex (scales with capacity)
        capex_lac = max(150, tpd * 32)  # Rs 32 Lac per TPD (from master data)
        capex_cr = capex_lac / 100

        # Variable cost per MT output
        raw_material = biomass_cost * 2  # 2 MT biomass per 1 MT output (40% yield)
        power_cost = power_rate * 600  # 600 kWh per MT output
        labour = labor_daily * 25 / (output_mt_day if output_mt_day > 0 else 1)  # 25 workers/day
        chemicals = 1500
        packaging = 500
        transport = transport_km * 200  # avg 200 km delivery
        qc = 500
        misc = 1000
        var_cost_mt = raw_material + power_cost + labour + chemicals + packaging + transport + qc + misc

        # Revenue per MT
        selling_price = 35000  # Bio-Modified Bitumen
        biochar_rev = 4000    # Per MT output (biochar byproduct)
        syngas_val = 1250     # Captive fuel saving
        revenue_per_mt = selling_price + biochar_rev + syngas_val

        staff = max(8, int(tpd * 0.9))
        payroll_lac_yr = staff * 2.5
        power_kw = max(25, int(tpd * 5))

    # ═══════════════════════════════════════════════════════════════
    # PROCESS 2: BLENDING ONLY (Buy Bio-Oil + VG30 → Blend → Sell)
    # ═══════════════════════════════════════════════════════════════
    elif process_id == 2:
        name = "Blending Only: Buy Bio-Oil + VG30 → Bio-Bitumen"
        short = "Blending Only"

        # Much lower capex (only blending unit)
        capex_lac = max(40, tpd * 4)  # Rs 4 Lac per TPD
        capex_cr = capex_lac / 100

        # Variable cost per MT — buying inputs externally
        bio_oil_purchase = 25000  # Rs/MT of bio-oil (market price)
        vg30_purchase = 50000    # Rs/MT of VG30 bitumen
        # Blending ratio: 20% bio-oil + 80% VG30
        raw_material = bio_oil_purchase * 0.20 + vg30_purchase * 0.80  # Rs 45,000/MT
        power_cost = power_rate * 100  # Only blending power
        labour = labor_daily * 8 / (output_mt_day if output_mt_day > 0 else 1)
        chemicals = 500  # Additives
        packaging = 500
        transport = transport_km * 150
        qc = 500
        misc = 500
        var_cost_mt = raw_material + power_cost + labour + chemicals + packaging + transport + qc + misc

        # Revenue — selling blended bio-bitumen at VG30 market price
        selling_price = 51000  # Competitive with VG30 (Rs 48-54K range)
        biochar_rev = 0
        syngas_val = 0
        revenue_per_mt = selling_price

        # Output = blended product (not pyrolysis output)
        output_mt_day = tpd  # Direct 1:1 (blending throughput)
        annual_output_full = output_mt_day * params["working_days"]

        staff = max(5, int(tpd * 0.4))
        payroll_lac_yr = staff * 2.5
        power_kw = max(15, int(tpd * 2))

    # ═══════════════════════════════════════════════════════════════
    # PROCESS 3: RAW OUTPUT (Biomass → Pyrolysis → Sell Oil + Char)
    # ═══════════════════════════════════════════════════════════════
    elif process_id == 3:
        name = "Raw Output: Biomass → Pyrolysis → Sell Oil + Char"
        short = "Raw Output"

        # Moderate capex (pyrolysis only, no blending)
        capex_lac = max(80, tpd * 15)
        capex_cr = capex_lac / 100

        # Variable cost per MT output
        raw_material = biomass_cost * 2  # 2 MT input per 1 MT output
        power_cost = power_rate * 500
        labour = labor_daily * 15 / (output_mt_day if output_mt_day > 0 else 1)
        chemicals = 500
        packaging = 800  # More packaging for liquid oil
        transport = transport_km * 250
        qc = 300
        misc = 600
        var_cost_mt = raw_material + power_cost + labour + chemicals + packaging + transport + qc + misc

        # Revenue — selling raw pyrolysis products
        oil_price_per_litre = 38
        oil_revenue = oil_price_per_litre * 1000 * OIL_YIELD  # per MT biomass → litres
        char_revenue = 12000 * CHAR_YIELD  # Biochar at Rs 12K/MT × 30% yield
        revenue_per_mt = oil_revenue + char_revenue  # Per MT of output (oil-equivalent)
        # Simplified: ~Rs 27,200/MT output

        selling_price = revenue_per_mt
        biochar_rev = 0
        syngas_val = 0

        staff = max(8, int(tpd * 0.7))
        payroll_lac_yr = staff * 2.5
        power_kw = max(20, int(tpd * 4))

    else:
        raise ValueError(f"Invalid process_id: {process_id}")

    # ═══════════════════════════════════════════════════════════════
    # COMMON FINANCIAL CALCULATIONS
    # ═══════════════════════════════════════════════════════════════
    profit_per_mt = revenue_per_mt - var_cost_mt
    inv_lac = capex_lac
    inv_cr = capex_cr

    # Apply subsidy
    effective_inv = inv_lac * (1 - subsidy_pct)
    loan_lac = effective_inv * (1 - params["equity_ratio"])
    equity_lac = effective_inv * params["equity_ratio"]

    emi = _calc_emi(loan_lac, params["interest_rate"], params["emi_tenure"])

    # 7-Year P&L
    timeline = []
    for yr in range(1, 8):
        util = UTIL.get(yr, 0.90)
        prod = annual_output_full * util
        rev = prod * revenue_per_mt / 1e5  # Lakhs
        var = prod * var_cost_mt / 1e5
        fixed = effective_inv * (params["insurance_pct"] + params["admin_pct"] + params["maintenance_pct"])
        ebitda = rev - var - fixed
        depr = effective_inv * params["depreciation_rate"]
        interest = loan_lac * params["interest_rate"]
        pbt = ebitda - depr - interest
        tax = max(0, pbt * params["tax_rate"])
        pat = pbt - tax
        cash = pat + depr
        ds = emi * 12
        dscr = cash / ds if ds > 0 else 0

        timeline.append({
            "Year": yr, "Utilization": f"{util:.0%}",
            "Production (MT)": round(prod, 0),
            "Revenue (Lac)": round(rev, 2),
            "Variable Cost (Lac)": round(var, 2),
            "Fixed Cost (Lac)": round(fixed, 2),
            "EBITDA (Lac)": round(ebitda, 2),
            "Depreciation (Lac)": round(depr, 2),
            "Interest (Lac)": round(interest, 2),
            "PBT (Lac)": round(pbt, 2),
            "Tax (Lac)": round(tax, 2),
            "PAT (Lac)": round(pat, 2),
            "Cash Accrual (Lac)": round(cash, 2),
            "DSCR": round(dscr, 2),
        })

    # ROI
    roi = timeline[4]["PAT (Lac)"] / effective_inv * 100 if effective_inv > 0 else 0

    # IRR
    flows = [-equity_lac]
    for t in timeline:
        flows.append(t["Cash Accrual (Lac)"] - emi * 12 * 0.5)
    irr = _calc_irr(flows)

    # Break-even
    avg_monthly = sum(t["PAT (Lac)"] for t in timeline[:5]) / 60
    be_months = int(np.ceil(effective_inv / (avg_monthly + timeline[0]["Depreciation (Lac)"] / 12))) if avg_monthly > 0 else 0

    return {
        "process_id": process_id,
        "process_name": name,
        "process_short": short,
        "capacity_tpd": tpd,
        "output_mt_day": round(output_mt_day, 1),
        "annual_output": round(annual_output_full, 0),

        # Investment
        "capex_lac": round(inv_lac, 1),
        "capex_cr": round(inv_cr, 2),
        "effective_inv_lac": round(effective_inv, 1),
        "subsidy_pct": round(subsidy_pct * 100, 1),
        "loan_lac": round(loan_lac, 1),
        "equity_lac": round(equity_lac, 1),

        # Per MT
        "revenue_per_mt": round(revenue_per_mt, 0),
        "var_cost_per_mt": round(var_cost_mt, 0),
        "profit_per_mt": round(profit_per_mt, 0),

        # Key metrics
        "emi_lac_mth": emi,
        "roi_pct": round(roi, 1),
        "irr_pct": round(irr, 1),
        "dscr_yr3": timeline[2]["DSCR"] if len(timeline) > 2 else 0,
        "break_even_months": be_months,

        # Revenue details
        "rev_yr1_lac": timeline[0]["Revenue (Lac)"],
        "rev_yr5_lac": timeline[4]["Revenue (Lac)"] if len(timeline) > 4 else 0,
        "pat_yr5_lac": timeline[4]["PAT (Lac)"] if len(timeline) > 4 else 0,

        # Operations
        "staff": staff,
        "payroll_lac_yr": round(payroll_lac_yr, 1),
        "power_kw": power_kw,

        # Timeline
        "timeline": timeline,
    }


def compare_all_processes(tpd, state_costs=None, **overrides):
    """Calculate all 3 processes and return comparison dict."""
    results = {}
    for pid in [1, 2, 3]:
        results[pid] = calculate_process(pid, tpd, state_costs, **overrides)
    return results


def state_profitability(tpd, process_id=1, state_costs_dict=None):
    """Calculate profitability for ALL states."""
    from config import STATE_COSTS
    costs = state_costs_dict or STATE_COSTS
    results = []
    for state, sc in costs.items():
        r = calculate_process(process_id, tpd, sc)
        results.append({
            "State": state,
            "Investment (Lac)": r["capex_lac"],
            "Subsidy (%)": r["subsidy_pct"],
            "Effective Inv (Lac)": r["effective_inv_lac"],
            "Revenue/MT": r["revenue_per_mt"],
            "Cost/MT": r["var_cost_per_mt"],
            "Profit/MT": r["profit_per_mt"],
            "ROI (%)": r["roi_pct"],
            "IRR (%)": r["irr_pct"],
            "DSCR Yr3": r["dscr_yr3"],
            "Break-Even (months)": r["break_even_months"],
            "Rev Yr5 (Lac)": r["rev_yr5_lac"],
            "PAT Yr5 (Lac)": r["pat_yr5_lac"],
            "Biomass Cost (Rs/MT)": sc.get("biomass_cost_mt", 0),
            "Power Rate (Rs/kWh)": sc.get("power_rate", 0),
            "Demand (MT/yr)": sc.get("bitumen_demand_mt", 0),
            "Risk": "Low" if r["roi_pct"] > 30 else "Medium" if r["roi_pct"] > 15 else "High",
        })
    return sorted(results, key=lambda x: -x["ROI (%)"])
