"""
Seasonal Operations Engine — 365-Day Plant Running Strategy
=============================================================
Covers: seasonal RM pricing, procurement plan, storage strategy,
product switching, yield variation, season-wise profit model.

This is the KEY to convincing clients their plant runs year-round.
"""


# ══════════════════════════════════════════════════════════════════════
# SEASONAL RAW MATERIAL PRICING (monthly, Rs/tonne)
# ══════════════════════════════════════════════════════════════════════
SEASONAL_RM_PRICES = {
    # Month: {feedstock: price_per_tonne}
    "Jan": {"rice_straw": 1800, "wheat_straw": 1500, "bagasse": 1000, "cotton_stalk": 2000, "mixed": 1800},
    "Feb": {"rice_straw": 2200, "wheat_straw": 1400, "bagasse": 1000, "cotton_stalk": 2200, "mixed": 1900},
    "Mar": {"rice_straw": 2800, "wheat_straw": 1600, "bagasse": 1100, "cotton_stalk": 2500, "mixed": 2200},
    "Apr": {"rice_straw": 3500, "wheat_straw": 2000, "bagasse": 1200, "cotton_stalk": 3000, "mixed": 2800},
    "May": {"rice_straw": 4000, "wheat_straw": 2500, "bagasse": 1300, "cotton_stalk": 3500, "mixed": 3200},
    "Jun": {"rice_straw": 4500, "wheat_straw": 3000, "bagasse": 1400, "cotton_stalk": 3800, "mixed": 3500},
    "Jul": {"rice_straw": 5000, "wheat_straw": 3500, "bagasse": 1500, "cotton_stalk": 4000, "mixed": 3800},
    "Aug": {"rice_straw": 4500, "wheat_straw": 3200, "bagasse": 1400, "cotton_stalk": 3500, "mixed": 3500},
    "Sep": {"rice_straw": 3500, "wheat_straw": 2800, "bagasse": 1200, "cotton_stalk": 3000, "mixed": 2800},
    "Oct": {"rice_straw": 2000, "wheat_straw": 2200, "bagasse": 1100, "cotton_stalk": 2500, "mixed": 2200},
    "Nov": {"rice_straw": 1200, "wheat_straw": 1800, "bagasse": 1000, "cotton_stalk": 2000, "mixed": 1500},
    "Dec": {"rice_straw": 1200, "wheat_straw": 1700, "bagasse": 1000, "cotton_stalk": 1800, "mixed": 1400},
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ══════════════════════════════════════════════════════════════════════
# YIELD VARIATION BY FEEDSTOCK
# ══════════════════════════════════════════════════════════════════════
FEEDSTOCK_YIELDS = {
    "rice_straw": {"bio_oil": 30, "bio_char": 32, "syngas": 20, "loss": 18, "quality": "Good", "moisture": 25},
    "rice_husk": {"bio_oil": 38, "bio_char": 28, "syngas": 22, "loss": 12, "quality": "Best", "moisture": 12},
    "wheat_straw": {"bio_oil": 28, "bio_char": 30, "syngas": 24, "loss": 18, "quality": "Good", "moisture": 20},
    "bagasse": {"bio_oil": 35, "bio_char": 25, "syngas": 25, "loss": 15, "quality": "Good", "moisture": 50},
    "cotton_stalk": {"bio_oil": 32, "bio_char": 30, "syngas": 22, "loss": 16, "quality": "Medium", "moisture": 18},
    "groundnut_shell": {"bio_oil": 34, "bio_char": 28, "syngas": 24, "loss": 14, "quality": "Good", "moisture": 10},
    "mustard_straw": {"bio_oil": 29, "bio_char": 33, "syngas": 22, "loss": 16, "quality": "Medium", "moisture": 22},
    "mixed_waste": {"bio_oil": 30, "bio_char": 30, "syngas": 22, "loss": 18, "quality": "Variable", "moisture": 25},
}


# ══════════════════════════════════════════════════════════════════════
# STATE-WISE BIOMASS AVAILABILITY (top source per state)
# ══════════════════════════════════════════════════════════════════════
STATE_BIOMASS = {
    "Punjab":       {"primary": "rice_straw", "secondary": "wheat_straw", "annual_mt": 25000000, "peak": "Oct-Dec", "rating": 5},
    "Haryana":      {"primary": "rice_straw", "secondary": "wheat_straw", "annual_mt": 12000000, "peak": "Oct-Dec", "rating": 5},
    "Uttar Pradesh":{"primary": "wheat_straw", "secondary": "rice_straw", "annual_mt": 30000000, "peak": "Nov-Mar", "rating": 5},
    "Bihar":        {"primary": "rice_straw", "secondary": "wheat_straw", "annual_mt": 8000000, "peak": "Nov-Jan", "rating": 4},
    "Gujarat":      {"primary": "groundnut_shell", "secondary": "cotton_stalk", "annual_mt": 6000000, "peak": "Oct-Feb", "rating": 3},
    "Maharashtra":  {"primary": "bagasse", "secondary": "cotton_stalk", "annual_mt": 15000000, "peak": "Nov-Apr", "rating": 4},
    "Madhya Pradesh":{"primary": "wheat_straw", "secondary": "mustard_straw", "annual_mt": 10000000, "peak": "Dec-Mar", "rating": 4},
    "Rajasthan":    {"primary": "mustard_straw", "secondary": "wheat_straw", "annual_mt": 5000000, "peak": "Jan-Apr", "rating": 3},
    "Tamil Nadu":   {"primary": "bagasse", "secondary": "rice_straw", "annual_mt": 8000000, "peak": "Jan-Jun", "rating": 3},
    "Karnataka":    {"primary": "bagasse", "secondary": "rice_straw", "annual_mt": 6000000, "peak": "Dec-May", "rating": 3},
    "West Bengal":  {"primary": "rice_straw", "secondary": "rice_husk", "annual_mt": 10000000, "peak": "Nov-Feb", "rating": 4},
    "Odisha":       {"primary": "rice_straw", "secondary": "rice_husk", "annual_mt": 5000000, "peak": "Nov-Feb", "rating": 3},
}


# ══════════════════════════════════════════════════════════════════════
# SEASON-WISE PRODUCTION STRATEGY
# ══════════════════════════════════════════════════════════════════════
SEASONAL_STRATEGY = {
    "Oct-Dec": {
        "season": "Peak Harvest",
        "rm_cost": "LOWEST (Rs 1,200-2,000/T)",
        "strategy": "Bulk buy + store 6 months + run full capacity",
        "utilization": 95,
        "product_focus": "Bio-Bitumen (maximum margin)",
        "profit_level": "HIGHEST",
        "color": "#00AA44",
    },
    "Jan-Mar": {
        "season": "Post Harvest",
        "rm_cost": "LOW-MEDIUM (Rs 1,500-2,500/T)",
        "strategy": "Mix stored + fresh wheat straw + bagasse",
        "utilization": 90,
        "product_focus": "Bio-Bitumen + Bio-Char (balanced)",
        "profit_level": "HIGH",
        "color": "#006699",
    },
    "Apr-Jun": {
        "season": "Off Season",
        "rm_cost": "MEDIUM-HIGH (Rs 2,500-4,000/T)",
        "strategy": "Use stored stock + switch to bagasse/industrial waste",
        "utilization": 75,
        "product_focus": "Bio-Char focus (higher char demand in summer)",
        "profit_level": "MEDIUM",
        "color": "#FF8800",
    },
    "Jul-Sep": {
        "season": "Monsoon",
        "rm_cost": "HIGH (Rs 3,500-5,000/T, wet biomass)",
        "strategy": "Use stored dry stock + reduce capacity + maintenance",
        "utilization": 60,
        "product_focus": "Bio-Char + Syngas (internal fuel) + plant maintenance",
        "profit_level": "LOW",
        "color": "#CC3333",
    },
}


# ══════════════════════════════════════════════════════════════════════
# STORAGE PLANNING
# ══════════════════════════════════════════════════════════════════════
def calculate_storage_requirement(cfg):
    """Calculate raw material storage needed for 365-day operation."""
    tpd = cfg.get("capacity_tpd", 20)
    working_days = cfg.get("working_days", 300)
    daily_feed = tpd  # tonnes/day of biomass

    # Storage for off-season (6 months = ~150 working days)
    storage_days = 150
    storage_tonnes = daily_feed * storage_days
    bulk_density = 120  # kg/m3 for loose straw
    storage_volume_m3 = storage_tonnes * 1000 / bulk_density
    stack_height = 3.5  # metres
    storage_area_m2 = storage_volume_m3 / stack_height

    # Cost of storage
    storage_cost_per_mt = 300  # Rs/tonne/month average
    monthly_storage_cost = daily_feed * 30 * storage_cost_per_mt

    return {
        "daily_feed_tonnes": daily_feed,
        "storage_days": storage_days,
        "storage_tonnes": round(storage_tonnes),
        "storage_volume_m3": round(storage_volume_m3),
        "storage_area_m2": round(storage_area_m2),
        "storage_area_acres": round(storage_area_m2 / 4047, 2),
        "stack_height_m": stack_height,
        "monthly_storage_cost": round(monthly_storage_cost),
        "annual_storage_cost_lac": round(monthly_storage_cost * 6 / 100000, 1),
        "strategy": "Buy 60% of annual requirement in Oct-Dec at lowest price. Store in covered shed. Use through Apr-Sep.",
    }


# ══════════════════════════════════════════════════════════════════════
# SEASON-WISE PROFIT MODEL
# ══════════════════════════════════════════════════════════════════════
def calculate_seasonal_profit(cfg):
    """Calculate profit variation across 4 seasons."""
    tpd = cfg.get("capacity_tpd", 20)
    selling_price = cfg.get("selling_price_per_mt", 44000)
    processing_cost = 4000  # Rs/tonne average

    seasons = []
    for period, data in SEASONAL_STRATEGY.items():
        util = data["utilization"] / 100
        months_str = period.split("-")

        # Get average RM cost for this season
        month_indices = {
            "Oct-Dec": ["Oct", "Nov", "Dec"],
            "Jan-Mar": ["Jan", "Feb", "Mar"],
            "Apr-Jun": ["Apr", "May", "Jun"],
            "Jul-Sep": ["Jul", "Aug", "Sep"],
        }
        months = month_indices.get(period, ["Jan", "Feb", "Mar"])
        primary_feed = cfg.get("biomass_source", "rice_straw").lower().replace(" ", "_")
        if primary_feed not in SEASONAL_RM_PRICES.get("Jan", {}):
            primary_feed = "mixed"
        avg_rm_cost = sum(SEASONAL_RM_PRICES[m].get(primary_feed, 2000) for m in months) / len(months)

        # Output per day at utilization
        output_tpd = tpd * 0.4 * util  # 40% yield × utilization
        daily_revenue = output_tpd * selling_price
        daily_rm_cost = tpd * util * avg_rm_cost
        daily_processing = output_tpd * processing_cost
        daily_profit = daily_revenue - daily_rm_cost - daily_processing

        # 3 months = ~75 working days
        working_days = 75
        season_revenue = daily_revenue * working_days
        season_profit = daily_profit * working_days

        seasons.append({
            "period": period,
            "season_name": data["season"],
            "utilization": data["utilization"],
            "avg_rm_cost": round(avg_rm_cost),
            "daily_output_mt": round(output_tpd, 1),
            "daily_revenue": round(daily_revenue),
            "daily_profit": round(daily_profit),
            "season_revenue_lac": round(season_revenue / 100000, 1),
            "season_profit_lac": round(season_profit / 100000, 1),
            "product_focus": data["product_focus"],
            "strategy": data["strategy"],
            "profit_level": data["profit_level"],
            "color": data["color"],
        })

    annual_profit = sum(s["season_profit_lac"] for s in seasons)
    annual_revenue = sum(s["season_revenue_lac"] for s in seasons)

    return {
        "seasons": seasons,
        "annual_profit_lac": round(annual_profit, 1),
        "annual_revenue_lac": round(annual_revenue, 1),
        "best_season": max(seasons, key=lambda s: s["season_profit_lac"])["period"],
        "worst_season": min(seasons, key=lambda s: s["season_profit_lac"])["period"],
    }


# ══════════════════════════════════════════════════════════════════════
# PRODUCT SWITCHING STRATEGY
# ══════════════════════════════════════════════════════════════════════
def get_product_switching_strategy(cfg):
    """Recommend which product to focus on each season."""
    return [
        {"season": "Oct-Dec", "primary": "Bio-Bitumen (70%)", "secondary": "Bio-Char (20%)",
         "tertiary": "Bio-Oil surplus (10%)", "reason": "Cheapest RM → maximize high-value output"},
        {"season": "Jan-Mar", "primary": "Bio-Bitumen (60%)", "secondary": "Bio-Char (25%)",
         "tertiary": "Carbon Credits (15%)", "reason": "Road construction peak → bitumen demand high"},
        {"season": "Apr-Jun", "primary": "Bio-Char (50%)", "secondary": "Bio-Bitumen (35%)",
         "tertiary": "Bio-Oil fuel (15%)", "reason": "RM costly → shift to higher-margin char"},
        {"season": "Jul-Sep", "primary": "Bio-Char (45%)", "secondary": "Maintenance (25%)",
         "tertiary": "Bio-Oil (30%)", "reason": "Monsoon → wet RM → char yield higher, plant maintenance"},
    ]


# ══════════════════════════════════════════════════════════════════════
# MONTHLY PROCUREMENT PLAN
# ══════════════════════════════════════════════════════════════════════
def get_monthly_procurement_plan(cfg):
    """Month-wise raw material procurement plan."""
    tpd = cfg.get("capacity_tpd", 20)
    state = cfg.get("state", "Gujarat")
    state_info = STATE_BIOMASS.get(state, STATE_BIOMASS.get("Gujarat"))
    primary = state_info["primary"]

    plan = []
    for month in MONTHS:
        prices = SEASONAL_RM_PRICES[month]
        price = prices.get(primary, prices.get("mixed", 2000))
        is_buy = price <= 2500  # Buy when cheap

        plan.append({
            "month": month,
            "feedstock": primary.replace("_", " ").title(),
            "price_per_tonne": price,
            "action": "BULK BUY + STORE" if is_buy else ("Normal Buy" if price <= 3500 else "Use Stored Stock"),
            "quantity_tonnes": round(tpd * 30 * (1.5 if is_buy else (1.0 if price <= 3500 else 0.3))),
            "cost_lac": round(tpd * 30 * (1.5 if is_buy else (1.0 if price <= 3500 else 0.3)) * price / 100000, 1),
        })

    return {
        "plan": plan,
        "state": state,
        "primary_feedstock": primary.replace("_", " ").title(),
        "peak_months": state_info["peak"],
        "annual_mt": state_info["annual_mt"],
    }
