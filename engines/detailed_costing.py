"""
Detailed Costing Engine — Complete cost-per-tonne bifurcation
==============================================================
Landing cost, waste/rejection, packing, scrap, location multipliers.
Single source of truth — all pages read from here.
"""

# ══════════════════════════════════════════════════════════════════════
# LOCATION COST MULTIPLIERS (9 states × 5 factors)
# ══════════════════════════════════════════════════════════════════════
LOCATION_MULTIPLIERS = {
    "Punjab": {"rm": 1.0, "lb": 0.9, "tr_in": 1.0, "tr_out": 1.1, "energy": 0.95,
               "reason_rm": "Local zone, abundant straw", "reason_lb": "Lower wages",
               "reason_tr": "Origin point, minimal haul", "reason_en": "₹6.8/kWh"},
    "Uttar Pradesh": {"rm": 1.05, "lb": 0.92, "tr_in": 1.05, "tr_out": 1.05, "energy": 1.0,
               "reason_rm": "Transport from East Punjab", "reason_lb": "Lower wages",
               "reason_tr": "150-250 km haul", "reason_en": "₹7.0/kWh"},
    "Madhya Pradesh": {"rm": 1.1, "lb": 0.95, "tr_in": 1.12, "tr_out": 1.08, "energy": 0.98,
               "reason_rm": "Mixed straw sources", "reason_lb": "Moderate wages",
               "reason_tr": "300-400 km", "reason_en": "₹7.2/kWh"},
    "Maharashtra": {"rm": 1.12, "lb": 1.1, "tr_in": 1.15, "tr_out": 0.95, "energy": 1.05,
               "reason_rm": "Transport from Punjab", "reason_lb": "Industrial zone premium",
               "reason_tr": "Distance from agro belt", "reason_en": "₹7.5/kWh"},
    "Gujarat": {"rm": 1.1, "lb": 1.05, "tr_in": 1.1, "tr_out": 0.9, "energy": 1.02,
               "reason_rm": "Moderate haul", "reason_lb": "Port zone premium",
               "reason_tr": "Good logistics", "reason_en": "₹7.0/kWh"},
    "Rajasthan": {"rm": 1.08, "lb": 0.88, "tr_in": 1.08, "tr_out": 1.1, "energy": 1.0,
               "reason_rm": "Mustard/wheat local", "reason_lb": "Low wages",
               "reason_tr": "Moderate distances", "reason_en": "₹7.0/kWh"},
    "Karnataka": {"rm": 1.18, "lb": 1.08, "tr_in": 1.2, "tr_out": 1.0, "energy": 1.08,
               "reason_rm": "Long haul from North", "reason_lb": "Tech zone rates",
               "reason_tr": "600-700 km haul", "reason_en": "₹7.8/kWh"},
    "Tamil Nadu": {"rm": 1.22, "lb": 1.1, "tr_in": 1.25, "tr_out": 1.0, "energy": 1.1,
               "reason_rm": "Maximum haul distance", "reason_lb": "Industrial rates",
               "reason_tr": "800+ km", "reason_en": "₹8.0/kWh"},
    "North East": {"rm": 1.05, "lb": 0.85, "tr_in": 0.9, "tr_out": 1.35, "energy": 1.25,
               "reason_rm": "Local paddy straw", "reason_lb": "Lower wages",
               "reason_tr": "Local abundant source", "reason_en": "₹9.0/kWh"},
}


def get_multiplier(state):
    """Get location multiplier for a state. Falls back to Maharashtra."""
    for key, val in LOCATION_MULTIPLIERS.items():
        if key.lower() in state.lower():
            return val
    return LOCATION_MULTIPLIERS["Maharashtra"]


# ══════════════════════════════════════════════════════════════════════
# LANDING COST CALCULATOR (per tonne of agro waste)
# ══════════════════════════════════════════════════════════════════════
def calculate_landing_cost(avg_farm_price, state="Maharashtra",
                            baling=350, loading=80, primary_transport=250,
                            depot_storage=300, long_haul=480, unloading=60,
                            testing=40, fumigation=25, octroi=0):
    """Calculate complete landing cost per tonne of agro waste at plant gate."""
    mult = get_multiplier(state)
    tr_mult = mult["tr_in"]

    items = [
        ("Farm Gate Price", avg_farm_price, False),
        ("Baling & Collection", baling * tr_mult, True),
        ("Loading at Source", loading, True),
        ("Primary Transport (Farm→Depot)", primary_transport * tr_mult, True),
        ("Depot/Aggregation Point", depot_storage, True),
        ("Depot Storage", 300, True),
        ("Long Haul (Depot→Plant)", long_haul * tr_mult, True),
        ("Unloading at Plant", unloading, True),
        ("Weighbridge & QC Testing", testing, True),
        ("Insurance in Transit (0.2%)", avg_farm_price * 0.002, False),
        ("Fumigation/Pest Control", fumigation, True),
        ("Octroi/State Entry Tax", octroi, True),
    ]

    subtotal = sum(cost for _, cost, _ in items)
    misc = subtotal * 0.02  # 2% contingency
    items.append(("Misc Handling & Contingency (2%)", misc, False))

    total = subtotal + misc
    return {"items": items, "total": round(total, 0), "farm_gate": avg_farm_price}


# ══════════════════════════════════════════════════════════════════════
# WASTE & REJECTION CALCULATOR
# ══════════════════════════════════════════════════════════════════════
def calculate_waste_costs(feed_tpd, oil_tpd, char_tpd, avg_rm_price):
    """Calculate all waste/loss/rejection costs per day."""
    items = [
        ("Moisture Evaporation", "Drying", 12, feed_tpd * 0.12, feed_tpd * 0.12 * avg_rm_price * 1.5),
        ("Flue Gas / CO₂ Release", "Pyrolysis", 4, feed_tpd * 0.04, feed_tpd * 0.04 * avg_rm_price),
        ("Off-spec Bio-Oil", "Refining", 3, oil_tpd * 0.03, oil_tpd * 0.03 * 30000),
        ("Char Fines (too fine)", "Screening", 5, char_tpd * 0.05, char_tpd * 0.05 * 10000),
        ("Ash & Slag", "Post-pyrolysis", 2, feed_tpd * 0.02, feed_tpd * 0.02 * 2000),
        ("Contamination/Foreign", "Pre-processing", 2, feed_tpd * 0.02, feed_tpd * 0.02 * 1750),
        ("Condensate/Pyrolytic Water", "Condensation", 6, feed_tpd * 0.06, feed_tpd * 0.06 * 1000),
    ]

    total = sum(cost for _, _, _, _, cost in items)
    return {"items": items, "total": round(total, 0)}


# ══════════════════════════════════════════════════════════════════════
# PACKING COST CALCULATOR
# ══════════════════════════════════════════════════════════════════════
def calculate_packing_costs(blend_tpd, char_tpd, oil_tpd):
    """Calculate packing cost net of scrap value."""
    items = [
        ("Bio-Bitumen Bulk Tanker", "10-20 MT", 0, 0, 0, "Bulk supply", round(blend_tpd * 0.5)),
        ("Bio-Bitumen MS Drum 180kg", "180 kg", 420, 280, 140, "Drums", round(blend_tpd * 0.5 / 0.18)),
        ("Bio-Char HDPE Bag 50kg", "50 kg", 28, 6, 22, "Bags", round(char_tpd * 1000 / 50)),
        ("Bio-Oil IBC Tank 1000L", "1000 L", 850, 400, 450, "IBC", max(1, round(oil_tpd))),
        ("Bio-Char PP Bag 25kg", "25 kg", 18, 3, 15, "Premium bags", round(char_tpd * 0.3 * 1000 / 25)),
    ]

    total = sum(net_cost * units for _, _, _, _, net_cost, _, units in items)
    return {"items": items, "total": round(total, 0)}


# ══════════════════════════════════════════════════════════════════════
# SCRAP & BY-PRODUCT REVENUE
# ══════════════════════════════════════════════════════════════════════
def calculate_scrap_revenue(blend_tpd, char_tpd, gas_tpd,
                             drum_price=280, carbon_credit_price=12500):
    """Calculate all scrap and by-product income per day."""
    drums = round(blend_tpd * 0.5 / 0.18)
    items = [
        ("Empty MS Drums (returned)", drums, drum_price, drums * drum_price, "Drum re-conditioners"),
        ("Empty HDPE Bags", round(char_tpd * 1000 / 50), 4, round(char_tpd * 1000 / 50) * 4, "Recyclers"),
        ("Off-spec Bio-Oil (fuel)", 0.2, 14000, 2800, "Brick kilns, boilers"),
        ("Char Fines (boiler fuel)", round(char_tpd * 0.05, 2), 4000, round(char_tpd * 0.05 * 4000), "Ceramic units"),
        ("Syngas (internal fuel credit)", round(gas_tpd, 1), 1023, round(gas_tpd * 1023), "Internal energy offset"),
        ("Carbon Credits", 5, carbon_credit_price, 5 * carbon_credit_price, "Voluntary carbon market"),
        ("Metal Scrap (maintenance)", 15, 45, 675, "Local scrap dealers"),
    ]

    total = sum(income for _, _, _, income, _ in items)
    return {"items": items, "total": round(total, 0)}


# ══════════════════════════════════════════════════════════════════════
# COMPLETE COST SHEET (per tonne of blend)
# ══════════════════════════════════════════════════════════════════════
def calculate_complete_cost_sheet(cfg):
    """Generate complete cost-per-tonne bifurcation from config."""
    tpd = cfg.get("capacity_tpd", 20)
    state = cfg.get("state", "Maharashtra")
    mult = get_multiplier(state)

    # Yields
    oil_yield = 0.40
    char_yield = 0.30
    gas_yield = 0.25
    blend_pct = cfg.get("bio_blend_pct", 20) / 100

    oil_tpd = tpd * oil_yield
    char_tpd = tpd * char_yield
    gas_tpd = tpd * gas_yield

    bio_oil_for_blend = oil_tpd * 0.85
    bio_oil_surplus = oil_tpd * 0.15
    blend_total = bio_oil_for_blend / blend_pct if blend_pct > 0 else 0
    conv_bit_tpd = blend_total - bio_oil_for_blend

    # Costs
    rm_cost_per_t = cfg.get("raw_material_cost_per_mt", 8000) / 2.5  # Convert output cost to input
    rm_daily = rm_cost_per_t * tpd * mult["rm"]
    bit_price = 45750  # VG30 base
    bit_landed = bit_price * 1.18 + 650 + 180 + 120 + bit_price * 0.015  # GST + freight + tanker + unload + loss
    bit_daily = bit_landed * conv_bit_tpd

    # Landing surcharge (agro waste only)
    landing = calculate_landing_cost(rm_cost_per_t * mult["rm"], state)
    landing_daily = (landing["total"] - landing["farm_gate"]) * tpd

    # Energy
    elec = 7.5 * 1200 * mult["energy"]
    diesel = 92 * 120 * mult["energy"]
    syngas_credit = gas_tpd * 1023
    energy_net = elec + diesel - syngas_credit

    # Labour
    labour = 18000 * mult["lb"] * 1.2  # 20% PF/ESI

    # Overheads
    overheads = 12000  # depreciation, maintenance, water, admin, WC interest

    # Chemicals
    chemicals = 2500

    # Packing
    packing = calculate_packing_costs(blend_total, char_tpd, bio_oil_surplus)

    # Waste
    waste = calculate_waste_costs(tpd, oil_tpd, char_tpd, rm_cost_per_t * mult["rm"])

    # Outbound
    outbound = blend_total * 800 * mult["tr_out"]

    # Scrap & by-product
    scrap = calculate_scrap_revenue(blend_total, char_tpd, gas_tpd)

    # Finished goods revenue
    sp1 = cfg.get("selling_price_per_mt", 35000)
    rev_blend = blend_total * sp1
    rev_char = char_tpd * 0.85 * 26000
    rev_oil = bio_oil_surplus * 22000
    rev_pellet = 1.0 * 9000
    total_rev = rev_blend + rev_char + rev_oil + rev_pellet + scrap["total"]

    # Cost sheet
    gross_daily = rm_daily + bit_daily + landing_daily + energy_net + labour + overheads + chemicals + packing["total"] + waste["total"] + outbound
    by_product_credit = rev_char + rev_oil + rev_pellet
    net_daily = gross_daily - by_product_credit - scrap["total"]
    net_cpt = net_daily / blend_total if blend_total > 0 else 0
    margin_pt = sp1 - net_cpt
    margin_pct = (margin_pt / sp1 * 100) if sp1 > 0 else 0

    cost_heads = [
        ("Agro Waste (farm gate)", rm_daily),
        ("Conventional Bitumen + GST", bit_daily),
        ("Landing/Inbound Logistics", landing_daily + conv_bit_tpd * 650),
        ("Energy (net of syngas)", energy_net),
        ("Labour (incl. PF/ESI)", labour),
        ("Chemicals & Catalysts", chemicals),
        ("Overheads & Depreciation", overheads),
        ("Packing (net of scrap)", packing["total"]),
        ("Waste & Rejection", waste["total"]),
        ("Outbound Delivery", outbound),
    ]

    return {
        "cost_heads": cost_heads,
        "gross_daily": round(gross_daily),
        "by_product_credit": round(by_product_credit),
        "scrap_total": scrap["total"],
        "net_daily": round(net_daily),
        "net_cpt": round(net_cpt),
        "sale_price_pt": sp1,
        "margin_pt": round(margin_pt),
        "margin_pct": round(margin_pct, 1),
        "blend_total_tpd": round(blend_total, 1),
        "total_rev_daily": round(total_rev),
        "conv_bit_tpd": round(conv_bit_tpd, 1),
        "oil_tpd": round(oil_tpd, 1),
        "char_tpd": round(char_tpd, 1),
        "gas_tpd": round(gas_tpd, 1),
        "bio_oil_surplus": round(bio_oil_surplus, 1),
        "landing": landing,
        "waste": waste,
        "packing": packing,
        "scrap": scrap,
        "multiplier": mult,
        "state": state,
    }
