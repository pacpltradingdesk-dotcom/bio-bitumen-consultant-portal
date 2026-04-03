"""
Agro Biomass Engine — Professional Sourcing, Yield, Cost, Inventory
====================================================================
Crop-specific data, seasonal planning, quality specs, procurement calculator.
"""

# ══════════════════════════════════════════════════════════════════════
# CROP DATABASE — Yield, Quality, Availability by Region
# ══════════════════════════════════════════════════════════════════════
CROP_DATABASE = {
    "Rice Straw": {
        "pyrolysis_yield_pct": 40, "biochar_yield_pct": 32, "syngas_yield_pct": 23, "loss_pct": 5,
        "calorific_value_kcal_kg": 3200, "moisture_max_pct": 15, "ash_content_pct": 18,
        "bulk_density_kg_m3": 80, "harvest_months": [10, 11, 12],
        "farm_gate_rs_mt": {"Punjab": 1200, "UP": 1500, "Haryana": 1300, "Bihar": 1000, "WB": 1100,
                             "AP": 1400, "TN": 1600, "Karnataka": 1500, "default": 1500},
        "availability_mt_yr": {"Punjab": 20000000, "UP": 25000000, "Haryana": 10000000, "Bihar": 8000000,
                                "WB": 6000000, "AP": 5000000, "default": 3000000},
        "pellet_conversion_ratio": 0.85, "storage_loss_pct_month": 2,
    },
    "Wheat Straw": {
        "pyrolysis_yield_pct": 38, "biochar_yield_pct": 30, "syngas_yield_pct": 27, "loss_pct": 5,
        "calorific_value_kcal_kg": 3400, "moisture_max_pct": 12, "ash_content_pct": 8,
        "bulk_density_kg_m3": 100, "harvest_months": [3, 4, 5],
        "farm_gate_rs_mt": {"Punjab": 1500, "Haryana": 1400, "UP": 1200, "MP": 1100, "Rajasthan": 1300, "default": 1400},
        "availability_mt_yr": {"Punjab": 18000000, "Haryana": 8000000, "UP": 20000000, "MP": 15000000, "default": 5000000},
        "pellet_conversion_ratio": 0.88, "storage_loss_pct_month": 1.5,
    },
    "Sugarcane Bagasse": {
        "pyrolysis_yield_pct": 42, "biochar_yield_pct": 28, "syngas_yield_pct": 25, "loss_pct": 5,
        "calorific_value_kcal_kg": 3800, "moisture_max_pct": 50, "ash_content_pct": 3,
        "bulk_density_kg_m3": 120, "harvest_months": [1, 2, 3, 11, 12],
        "farm_gate_rs_mt": {"UP": 1000, "Maharashtra": 1200, "Karnataka": 1300, "TN": 1100, "Gujarat": 1200, "default": 1200},
        "availability_mt_yr": {"UP": 15000000, "Maharashtra": 25000000, "Karnataka": 8000000, "default": 5000000},
        "pellet_conversion_ratio": 0.70, "storage_loss_pct_month": 3,
    },
    "Cotton Stalk": {
        "pyrolysis_yield_pct": 35, "biochar_yield_pct": 33, "syngas_yield_pct": 27, "loss_pct": 5,
        "calorific_value_kcal_kg": 3500, "moisture_max_pct": 12, "ash_content_pct": 5,
        "bulk_density_kg_m3": 90, "harvest_months": [10, 11, 12, 1],
        "farm_gate_rs_mt": {"Gujarat": 1800, "Maharashtra": 2000, "Rajasthan": 1700, "MP": 1600, "Telangana": 1900, "default": 1800},
        "availability_mt_yr": {"Gujarat": 5000000, "Maharashtra": 10000000, "Rajasthan": 3000000, "default": 2000000},
        "pellet_conversion_ratio": 0.82, "storage_loss_pct_month": 1,
    },
    "Groundnut Shell": {
        "pyrolysis_yield_pct": 38, "biochar_yield_pct": 35, "syngas_yield_pct": 22, "loss_pct": 5,
        "calorific_value_kcal_kg": 4200, "moisture_max_pct": 8, "ash_content_pct": 4,
        "bulk_density_kg_m3": 200, "harvest_months": [3, 4, 10, 11],
        "farm_gate_rs_mt": {"Gujarat": 2500, "Rajasthan": 2200, "AP": 2000, "TN": 2300, "default": 2300},
        "availability_mt_yr": {"Gujarat": 3000000, "Rajasthan": 2000000, "AP": 2000000, "default": 1000000},
        "pellet_conversion_ratio": 0.92, "storage_loss_pct_month": 0.5,
    },
    "Coconut Shell": {
        "pyrolysis_yield_pct": 36, "biochar_yield_pct": 38, "syngas_yield_pct": 21, "loss_pct": 5,
        "calorific_value_kcal_kg": 4500, "moisture_max_pct": 10, "ash_content_pct": 2,
        "bulk_density_kg_m3": 250, "harvest_months": list(range(1, 13)),
        "farm_gate_rs_mt": {"Kerala": 3000, "Karnataka": 2800, "TN": 2700, "default": 3000},
        "availability_mt_yr": {"Kerala": 1000000, "Karnataka": 800000, "TN": 1500000, "default": 500000},
        "pellet_conversion_ratio": 0.95, "storage_loss_pct_month": 0.3,
    },
}

# State name mapping for short codes
STATE_MAP = {
    "Punjab": "Punjab", "UP": "Uttar Pradesh", "Haryana": "Haryana", "Bihar": "Bihar",
    "WB": "West Bengal", "AP": "Andhra Pradesh", "TN": "Tamil Nadu", "Karnataka": "Karnataka",
    "Gujarat": "Gujarat", "Maharashtra": "Maharashtra", "Rajasthan": "Rajasthan",
    "MP": "Madhya Pradesh", "Kerala": "Kerala", "Telangana": "Telangana",
}

# Month names
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def get_crop_list():
    return list(CROP_DATABASE.keys())


def get_crop_data(crop_name):
    return CROP_DATABASE.get(crop_name, {})


def calculate_procurement_cost(crop_name, state_short, distance_km=50, storage_months=1):
    """
    Calculate total delivered cost per MT of biomass.
    Components: Farm gate + Transport + Storage + Processing (pelletization)
    """
    crop = CROP_DATABASE.get(crop_name, {})
    if not crop:
        return {"error": f"Crop '{crop_name}' not found"}

    farm_gate = crop["farm_gate_rs_mt"].get(state_short, crop["farm_gate_rs_mt"]["default"])
    transport_rate = 5.5  # Rs per MT per km
    transport_cost = transport_rate * distance_km
    storage_cost = 300 * storage_months  # Rs 300/MT/month
    storage_loss_value = farm_gate * crop["storage_loss_pct_month"] / 100 * storage_months
    pelletization_cost = 800  # Rs/MT for pelletization
    loading_unloading = 200  # Rs/MT

    total_delivered = farm_gate + transport_cost + storage_cost + storage_loss_value + pelletization_cost + loading_unloading

    return {
        "crop": crop_name,
        "state": state_short,
        "farm_gate_rs_mt": round(farm_gate, 0),
        "transport_cost": round(transport_cost, 0),
        "transport_distance_km": distance_km,
        "storage_cost": round(storage_cost, 0),
        "storage_months": storage_months,
        "storage_loss_value": round(storage_loss_value, 0),
        "pelletization_cost": pelletization_cost,
        "loading_unloading": loading_unloading,
        "total_delivered_rs_mt": round(total_delivered, 0),
        "components": {
            "Farm Gate": farm_gate,
            "Transport": round(transport_cost, 0),
            "Storage": round(storage_cost + storage_loss_value, 0),
            "Pelletization": pelletization_cost,
            "Loading/Unloading": loading_unloading,
        },
    }


def calculate_plant_requirement(tpd, crop_name, working_days=300):
    """
    Calculate daily, monthly, annual biomass requirement for a plant.
    Accounts for crop-specific yield and loss.
    """
    crop = CROP_DATABASE.get(crop_name, {})
    if not crop:
        return {"error": f"Crop '{crop_name}' not found"}

    oil_yield = crop["pyrolysis_yield_pct"] / 100
    # Output = Input × Oil Yield, so Input = Output / Oil Yield
    # But for bio-bitumen, we need oil + bitumen blending
    # Input biomass per MT of bio-oil output
    input_per_mt_output = 1 / oil_yield if oil_yield > 0 else 2.5

    daily_biomass = tpd * input_per_mt_output
    monthly_biomass = daily_biomass * 25  # 25 working days/month
    annual_biomass = daily_biomass * working_days
    buffer_90_days = daily_biomass * 90
    storage_area_sqft = buffer_90_days / crop["bulk_density_kg_m3"] * 1000 / 0.3048 / 0.3048 / 3  # 3m stacking height

    return {
        "crop": crop_name,
        "plant_tpd": tpd,
        "input_ratio": round(input_per_mt_output, 2),
        "daily_biomass_mt": round(daily_biomass, 1),
        "monthly_biomass_mt": round(monthly_biomass, 0),
        "annual_biomass_mt": round(annual_biomass, 0),
        "buffer_90_days_mt": round(buffer_90_days, 0),
        "storage_area_sqft": round(storage_area_sqft, 0),
        "bio_oil_output_mt_day": round(tpd * oil_yield, 1),
        "biochar_output_mt_day": round(tpd * crop["biochar_yield_pct"] / 100, 1),
        "syngas_output_mt_day": round(tpd * crop["syngas_yield_pct"] / 100, 1),
    }


def get_monthly_availability(crop_name, state_short="default"):
    """
    Get monthly biomass availability percentage.
    Harvest months get higher availability, off-season lower.
    """
    crop = CROP_DATABASE.get(crop_name, {})
    if not crop:
        return [0] * 12

    harvest = crop["harvest_months"]
    monthly = []
    for m in range(1, 13):
        if m in harvest:
            monthly.append(100)  # Full availability during harvest
        elif (m - 1) % 12 + 1 in harvest or (m + 1) % 12 + 1 in harvest:
            monthly.append(60)  # Adjacent months — stored stock
        else:
            monthly.append(30)  # Off-season — pellet stock only
    return monthly


def calculate_inventory_plan(tpd, crop_name, state_short="default", working_days=300):
    """
    Monthly inventory plan: procurement, consumption, closing stock.
    Ensures 90-day buffer maintained throughout year.
    """
    crop = CROP_DATABASE.get(crop_name, {})
    if not crop:
        return []

    oil_yield = crop["pyrolysis_yield_pct"] / 100
    daily_consumption = tpd / oil_yield if oil_yield > 0 else tpd * 2.5
    monthly_consumption = daily_consumption * 25
    target_buffer = daily_consumption * 90
    availability = get_monthly_availability(crop_name, state_short)

    plan = []
    closing_stock = target_buffer  # Start with full buffer

    for month_idx in range(12):
        avail_pct = availability[month_idx]
        consumption = monthly_consumption

        # Procurement: buy enough to maintain buffer + monthly consumption
        gap = target_buffer + consumption - closing_stock
        procurement = max(0, gap)

        # Adjust procurement based on availability
        if avail_pct >= 80:
            procurement *= 1.2  # Buy extra during high availability
        elif avail_pct <= 40:
            procurement *= 0.8  # Reduce during scarcity (use buffer)

        closing_stock = closing_stock + procurement - consumption
        buffer_days = closing_stock / daily_consumption if daily_consumption > 0 else 0

        plan.append({
            "Month": MONTH_NAMES[month_idx],
            "Availability (%)": avail_pct,
            "Procurement (MT)": round(procurement, 0),
            "Consumption (MT)": round(consumption, 0),
            "Closing Stock (MT)": round(max(0, closing_stock), 0),
            "Buffer (Days)": round(max(0, buffer_days), 0),
            "Status": "OK" if buffer_days >= 60 else ("Low" if buffer_days >= 30 else "Critical"),
        })

    return plan


def get_quality_specs():
    """Return quality specifications for all biomass types."""
    specs = []
    for crop_name, data in CROP_DATABASE.items():
        specs.append({
            "Biomass Type": crop_name,
            "Moisture Max (%)": data["moisture_max_pct"],
            "Ash Content (%)": data["ash_content_pct"],
            "Calorific Value (kcal/kg)": data["calorific_value_kcal_kg"],
            "Bulk Density (kg/m3)": data["bulk_density_kg_m3"],
            "Bio-Oil Yield (%)": data["pyrolysis_yield_pct"],
            "Biochar Yield (%)": data["biochar_yield_pct"],
            "Pellet Ratio": data["pellet_conversion_ratio"],
            "Storage Loss (%/mo)": data["storage_loss_pct_month"],
        })
    return specs


def get_supplier_types():
    """Return standardized supplier type database."""
    return [
        {"Type": "Farmer Producer Organization (FPO)", "Typical Volume": "5,000-20,000 MT/yr",
         "Reliability": "High", "Price Negotiation": "Moderate", "Contract": "Annual",
         "Pros": "Consistent quality, bulk supply, government-supported",
         "Cons": "Higher price, advance payment expected"},
        {"Type": "Sugar Mill (Bagasse)", "Typical Volume": "10,000-50,000 MT/yr",
         "Reliability": "Very High", "Price Negotiation": "Low", "Contract": "Season-based",
         "Pros": "Year-round, consistent quality, large volumes",
         "Cons": "Premium price, limited to sugarcane belt"},
        {"Type": "Cotton Ginning Mill", "Typical Volume": "3,000-8,000 MT/yr",
         "Reliability": "Medium", "Price Negotiation": "High", "Contract": "Seasonal",
         "Pros": "Low cost, waste product for them",
         "Cons": "Seasonal only, variable quality"},
        {"Type": "Oil Extraction Mill", "Typical Volume": "2,000-5,000 MT/yr",
         "Reliability": "Medium", "Price Negotiation": "Moderate", "Contract": "Monthly",
         "Pros": "Steady supply from processing operations",
         "Cons": "Limited volumes, mixed quality"},
        {"Type": "Biomass Aggregator", "Typical Volume": "1,000-10,000 MT/yr",
         "Reliability": "Medium", "Price Negotiation": "High", "Contract": "Spot/Monthly",
         "Pros": "Flexible quantities, multiple sources",
         "Cons": "Higher cost (middleman), variable quality"},
        {"Type": "Direct Farmer Purchase", "Typical Volume": "100-500 MT/yr per farmer",
         "Reliability": "Low", "Price Negotiation": "Very High", "Contract": "Seasonal",
         "Pros": "Lowest cost, direct relationship",
         "Cons": "Logistics burden, inconsistent quality, small lots"},
    ]
