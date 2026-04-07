"""
Client Convincer Engine — Tools that make clients say YES
============================================================
Everything here is designed to answer the client's real questions:
1. "Kitna milega?" (How much will I earn?)
2. "Kab milega?" (When will I get returns?)
3. "Kya risk hai?" (What's the risk?)
4. "Subsidy milegi?" (Will I get government support?)
5. "Delay se kya hoga?" (What if I delay?)
"""


def get_project_summary_card(cfg):
    """One-screen summary of the client's EXACT project.
    This is what the client takes home in their mind."""
    tpd = cfg.get("capacity_tpd", 20)
    inv = cfg.get("investment_cr", 8)
    loan = cfg.get("loan_cr", inv * 0.6)
    equity = cfg.get("equity_cr", inv * 0.4)
    emi = cfg.get("emi_lac_mth", 0)
    monthly_profit = cfg.get("monthly_profit_lac", 0)
    cash_after_emi = monthly_profit - emi if monthly_profit > emi else 0

    return {
        "title": f"{tpd:.0f} TPD Bio-Bitumen Plant — {cfg.get('location', '')}, {cfg.get('state', '')}",
        "client": cfg.get("client_name", ""),
        "company": cfg.get("client_company", ""),

        # Money IN
        "investment": f"Rs {inv:.2f} Cr",
        "your_equity": f"Rs {equity:.2f} Cr ({cfg.get('equity_ratio', 0.4)*100:.0f}%)",
        "bank_loan": f"Rs {loan:.2f} Cr ({(1-cfg.get('equity_ratio', 0.4))*100:.0f}%)",

        # Money OUT (returns)
        "monthly_emi": f"Rs {emi:.2f} Lac",
        "monthly_profit": f"Rs {monthly_profit:.1f} Lac",
        "cash_in_hand": f"Rs {cash_after_emi:.1f} Lac/month",
        "annual_cash": f"Rs {cash_after_emi * 12 / 100:.2f} Cr/year",
        "roi": f"{cfg.get('roi_pct', 0):.1f}%",
        "payback": f"{cfg.get('break_even_months', 0)} months",

        # Products
        "daily_output": f"{tpd * 0.4:.1f} MT bio-bitumen + {tpd * 0.3:.1f} MT bio-char",
        "annual_revenue": f"Rs {cfg.get('revenue_yr5_lac', 0) / 100:.2f} Cr (Year 5)",

        # What client needs
        "land_needed": f"{cfg.get('site_area_acres', 2)} acres",
        "timeline": "12-15 months",
        "staff": f"{cfg.get('staff', 20)} persons",
    }


def get_subsidy_calculator(cfg):
    """Calculate EXACT subsidy amount the client can get."""
    inv = cfg.get("investment_cr", 8)
    state = cfg.get("state", "Gujarat")
    tpd = cfg.get("capacity_tpd", 20)

    subsidies = []

    # 1. MNRE Biomass
    mnre_42L = tpd * 42  # Rs 42 Lac per TPD capacity
    mnre_30pct = inv * 100 * 0.30  # 30% of plant cost
    mnre_max = 210  # Max Rs 2.1 Cr = 210 Lac
    mnre_amount = min(mnre_42L, mnre_30pct, mnre_max)
    subsidies.append({
        "scheme": "MNRE Waste-to-Wealth",
        "amount_lac": round(mnre_amount, 1),
        "how": f"Rs 42L/TPD × {tpd:.0f} TPD = Rs {mnre_42L:.0f}L (capped at Rs {mnre_max} Lac)",
        "status": "Apply at mnre.gov.in",
        "probability": "HIGH" if tpd <= 50 else "MEDIUM",
    })

    # 2. State MSME subsidy
    try:
        from config import STATE_COSTS
        state_pct = STATE_COSTS.get(state, {}).get("subsidy_pct", 15)
    except Exception:
        state_pct = 15
    state_amount = inv * 100 * state_pct / 100
    subsidies.append({
        "scheme": f"State MSME Subsidy ({state})",
        "amount_lac": round(state_amount, 1),
        "how": f"{state_pct}% of Rs {inv:.2f} Cr = Rs {state_amount:.0f} Lac",
        "status": "Apply at State Industries Dept",
        "probability": "HIGH",
    })

    # 3. CGTMSE (collateral-free loan guarantee)
    loan = cfg.get("loan_cr", inv * 0.6)
    cgtmse_eligible = loan * 100 <= 500  # Max Rs 5 Cr
    subsidies.append({
        "scheme": "CGTMSE (Collateral-Free Loan)",
        "amount_lac": round(min(loan * 100, 500), 1) if cgtmse_eligible else 0,
        "how": f"Loan Rs {loan:.2f} Cr {'< Rs 5 Cr — ELIGIBLE' if cgtmse_eligible else '> Rs 5 Cr — NOT eligible'}",
        "status": "Apply through bank" if cgtmse_eligible else "Not applicable",
        "probability": "HIGH" if cgtmse_eligible else "N/A",
    })

    # 4. Carbon Credits
    carbon_per_year = tpd * 300 * 0.35  # tonnes CO2 saved
    carbon_value = carbon_per_year * 12500 / 100000  # in Lac
    subsidies.append({
        "scheme": "Carbon Credits (Annual Income)",
        "amount_lac": round(carbon_value, 1),
        "how": f"{carbon_per_year:.0f} tonnes CO2/year × Rs 12,500/credit",
        "status": "Register with Verra/Gold Standard",
        "probability": "MEDIUM",
    })

    total_lac = sum(s["amount_lac"] for s in subsidies)
    effective_investment = inv * 100 - total_lac

    return {
        "subsidies": subsidies,
        "total_subsidy_lac": round(total_lac, 1),
        "total_subsidy_cr": round(total_lac / 100, 2),
        "original_investment": f"Rs {inv:.2f} Cr",
        "effective_investment": f"Rs {effective_investment / 100:.2f} Cr",
        "savings_pct": round(total_lac / (inv * 100) * 100, 1),
    }


def get_cost_of_delay(cfg):
    """Calculate what the client LOSES by delaying 1/3/6 months."""
    monthly_profit = cfg.get("monthly_profit_lac", 5)
    tpd = cfg.get("capacity_tpd", 20)
    daily_revenue = tpd * 0.4 * cfg.get("selling_price_per_mt", 35000)
    monthly_revenue = daily_revenue * 25 / 100000  # 25 working days, in Lac

    return {
        "monthly_revenue_lost": round(monthly_revenue, 1),
        "monthly_profit_lost": round(monthly_profit, 1),
        "delays": [
            {"months": 1, "revenue_lost": round(monthly_revenue, 1),
             "profit_lost": round(monthly_profit, 1),
             "reason": "Bank resubmission, wrong DPR format"},
            {"months": 3, "revenue_lost": round(monthly_revenue * 3, 1),
             "profit_lost": round(monthly_profit * 3, 1),
             "reason": "Wrong approval sequence, PCB rejection"},
            {"months": 6, "revenue_lost": round(monthly_revenue * 6, 1),
             "profit_lost": round(monthly_profit * 6, 1),
             "reason": "Wrong machinery, rework, vendor disputes"},
            {"months": 12, "revenue_lost": round(monthly_revenue * 12, 1),
             "profit_lost": round(monthly_profit * 12, 1),
             "reason": "Complete restart — technology change, site change"},
        ],
        "market_risk": "Every month, more competitors enter. CSIR-CRRI has given 14 licenses already.",
    }


def get_bio_vs_conventional(cfg):
    """Compare bio-bitumen plant vs conventional bitumen business."""
    inv = cfg.get("investment_cr", 10)
    return {
        "headers": ["Parameter", "Bio-Bitumen Plant", "Conventional Bitumen Trading"],
        "rows": [
            ["Investment", f"Rs {inv:.1f} Cr", f"Rs {inv*2:.0f}-{inv*3:.0f} Cr (refinery level)"],
            ["Raw Material", "Agro-waste Rs 1,200/T (farmer)", "Crude oil $85/barrel (import)"],
            ["Import Dependency", "ZERO (local biomass)", "49% of India's bitumen imported"],
            ["Govt Support", "MNRE subsidy + NHAI mandate", "No special support"],
            ["Carbon Credits", f"Rs {cfg.get('capacity_tpd',20)*300*0.35*12500/100000:.1f} Lac/year", "None — actually ADDS carbon"],
            ["Competition", "< 20 plants in India (new sector)", "500+ traders (saturated)"],
            ["Technology Moat", "CSIR-CRRI license (limited to 14)", "No technology advantage"],
            ["Growth Potential", "130-216 plants needed by 2030", "Market growing at 3-4% only"],
            ["Margin", f"{cfg.get('roi_pct',20):.0f}% ROI", "5-8% trading margin"],
            ["Sustainability", "Green product, ESG compliant", "Petroleum based, ESG risk"],
        ],
    }


def get_cash_in_hand_display(cfg):
    """The #1 number every client wants to know: monthly cash after EMI."""
    monthly_profit = cfg.get("monthly_profit_lac", 5)
    emi = cfg.get("emi_lac_mth", 7)
    cash = max(0, monthly_profit - emi)
    annual = cash * 12

    # After loan repayment (Year 8+)
    cash_after_loan = monthly_profit

    return {
        "during_loan": {
            "monthly_profit": round(monthly_profit, 1),
            "monthly_emi": round(emi, 1),
            "cash_in_hand": round(cash, 1),
            "annual_cash": round(annual, 1),
            "period": "Year 1-7 (during loan repayment)",
        },
        "after_loan": {
            "monthly_profit": round(monthly_profit, 1),
            "monthly_emi": 0,
            "cash_in_hand": round(cash_after_loan, 1),
            "annual_cash": round(cash_after_loan * 12, 1),
            "period": "Year 8+ (loan fully repaid)",
        },
        "headline": f"Rs {cash:.1f} Lac/month in your pocket (during loan) → Rs {cash_after_loan:.1f} Lac/month (after loan)",
    }
