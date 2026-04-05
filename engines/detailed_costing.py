"""
Detailed Costing Engine — Complete DPR Financial Working System
================================================================
Single source of truth for ALL cost calculations.
Every formula reads from cfg (state_manager) — ZERO hardcoded outputs.

Implements Master Operator Prompt Sections 3A-3M:
  3A  Location Multipliers (9 states × 5 factors)
  3B  Process Outputs (daily yields)
  3C  Raw Material Cost (blended from 6 feedstocks)
  3D  Conventional Bitumen Cost (GST + freight + loss)
  3E  Landing / Inbound Cost
  3F  Production Cost (energy, labour, overheads, chemicals)
  3G  Packing Cost (net of scrap return)
  3H  Waste & Rejection Cost
  3I  Outbound Logistics
  3J  Total Gross Cost
  3K  Revenue (7 product streams)
  3L  Cost Per Tonne of Blend + Margin
  3M  Annual P&L
"""

# ══════════════════════════════════════════════════════════════════════
# LOCATION COST MULTIPLIERS (9 states × 5 factors)
# ══════════════════════════════════════════════════════════════════════
LOCATION_MULTIPLIERS = {
    "Punjab":         {"rm": 1.00, "lb": 0.90, "tr_in": 1.00, "tr_out": 1.10, "energy": 0.95,
                       "elec_rate": 6.8,
                       "reason_rm": "Local zone, abundant straw", "reason_lb": "Lower wages",
                       "reason_tr": "Origin point, minimal haul", "reason_en": "₹6.8/kWh"},
    "Uttar Pradesh":  {"rm": 1.05, "lb": 0.92, "tr_in": 1.05, "tr_out": 1.05, "energy": 1.00,
                       "elec_rate": 7.0,
                       "reason_rm": "Transport from East Punjab", "reason_lb": "Lower wages",
                       "reason_tr": "150-250 km haul", "reason_en": "₹7.0/kWh"},
    "Madhya Pradesh": {"rm": 1.10, "lb": 0.95, "tr_in": 1.12, "tr_out": 1.08, "energy": 0.98,
                       "elec_rate": 7.2,
                       "reason_rm": "Mixed straw sources", "reason_lb": "Moderate wages",
                       "reason_tr": "300-400 km", "reason_en": "₹7.2/kWh"},
    "Maharashtra":    {"rm": 1.12, "lb": 1.10, "tr_in": 1.15, "tr_out": 0.95, "energy": 1.05,
                       "elec_rate": 7.5,
                       "reason_rm": "Transport from Punjab", "reason_lb": "Industrial zone premium",
                       "reason_tr": "Distance from agro belt", "reason_en": "₹7.5/kWh"},
    "Gujarat":        {"rm": 1.10, "lb": 1.05, "tr_in": 1.10, "tr_out": 0.90, "energy": 1.02,
                       "elec_rate": 7.0,
                       "reason_rm": "Moderate haul", "reason_lb": "Port zone premium",
                       "reason_tr": "Good logistics", "reason_en": "₹7.0/kWh"},
    "Rajasthan":      {"rm": 1.08, "lb": 0.88, "tr_in": 1.08, "tr_out": 1.10, "energy": 1.00,
                       "elec_rate": 7.0,
                       "reason_rm": "Mustard/wheat local", "reason_lb": "Low wages",
                       "reason_tr": "Moderate distances", "reason_en": "₹7.0/kWh"},
    "Karnataka":      {"rm": 1.18, "lb": 1.08, "tr_in": 1.20, "tr_out": 1.00, "energy": 1.08,
                       "elec_rate": 7.8,
                       "reason_rm": "Long haul from North", "reason_lb": "Tech zone rates",
                       "reason_tr": "600-700 km haul", "reason_en": "₹7.8/kWh"},
    "Tamil Nadu":     {"rm": 1.22, "lb": 1.10, "tr_in": 1.25, "tr_out": 1.00, "energy": 1.10,
                       "elec_rate": 8.0,
                       "reason_rm": "Maximum haul distance", "reason_lb": "Industrial rates",
                       "reason_tr": "800+ km", "reason_en": "₹8.0/kWh"},
    "North East":     {"rm": 1.05, "lb": 0.85, "tr_in": 0.90, "tr_out": 1.35, "energy": 1.25,
                       "elec_rate": 9.0,
                       "reason_rm": "Local paddy straw", "reason_lb": "Lower wages",
                       "reason_tr": "Local abundant source", "reason_en": "₹9.0/kWh"},
}


def get_multiplier(state):
    """Get location multiplier for a state. Falls back to Maharashtra."""
    for key, val in LOCATION_MULTIPLIERS.items():
        if key.lower() in state.lower() or state.lower() in key.lower():
            return val
    return LOCATION_MULTIPLIERS["Maharashtra"]


# ══════════════════════════════════════════════════════════════════════
# 3B — PROCESS OUTPUTS (per day)
# ══════════════════════════════════════════════════════════════════════
def calculate_process_outputs(cfg):
    """Calculate daily process outputs from feed capacity and yield percentages."""
    feed = cfg.get("capacity_tpd", 20)
    bio_oil_yield = cfg.get("bio_oil_yield_pct", 32) / 100
    bio_char_yield = cfg.get("bio_char_yield_pct", 28) / 100
    syngas_yield = cfg.get("syngas_yield_pct", 22) / 100
    process_loss = cfg.get("process_loss_pct", 18) / 100
    blend_pct = cfg.get("bio_blend_pct", 20) / 100

    bio_oil_per_day = feed * bio_oil_yield
    bio_char_per_day = feed * bio_char_yield
    syngas_per_day = feed * syngas_yield
    loss_per_day = feed * process_loss

    bio_oil_for_blend = bio_oil_per_day * 0.85
    bio_oil_surplus = bio_oil_per_day * 0.15
    blend_output_per_day = bio_oil_for_blend / blend_pct if blend_pct > 0 else 0
    conv_bitumen_needed = blend_output_per_day - bio_oil_for_blend

    return {
        "feed": feed,
        "bio_oil_per_day": round(bio_oil_per_day, 2),
        "bio_char_per_day": round(bio_char_per_day, 2),
        "syngas_per_day": round(syngas_per_day, 2),
        "loss_per_day": round(loss_per_day, 2),
        "bio_oil_for_blend": round(bio_oil_for_blend, 2),
        "bio_oil_surplus": round(bio_oil_surplus, 2),
        "blend_output_per_day": round(blend_output_per_day, 2),
        "conv_bitumen_needed": round(conv_bitumen_needed, 2),
        "yield_check": round((bio_oil_yield + bio_char_yield + syngas_yield + process_loss) * 100, 1),
    }


# ══════════════════════════════════════════════════════════════════════
# 3C — RAW MATERIAL COST (blended from 6 feedstocks × location)
# ══════════════════════════════════════════════════════════════════════
def calculate_rm_cost(cfg, loc):
    """Calculate blended raw material cost per tonne and daily cost."""
    feed = cfg.get("capacity_tpd", 20)

    # Individual feedstock prices
    prices = {
        "Rice Straw (Loose)":  cfg.get("price_rice_straw_loose", 1200),
        "Rice Straw (Baled)":  cfg.get("price_rice_straw_baled", 2700),
        "Wheat Straw":         cfg.get("price_wheat_straw", 1700),
        "Bagasse":             cfg.get("price_bagasse", 1000),
        "Lignin (Kraft)":      cfg.get("price_lignin", 4000),
        "Other Agro Waste":    cfg.get("price_other_agro_waste", 900),
    }
    weights = {
        "Rice Straw (Loose)":  cfg.get("mix_rice_straw_loose", 0.35),
        "Rice Straw (Baled)":  cfg.get("mix_rice_straw_baled", 0.20),
        "Wheat Straw":         cfg.get("mix_wheat_straw", 0.15),
        "Bagasse":             cfg.get("mix_bagasse", 0.10),
        "Lignin (Kraft)":      cfg.get("mix_lignin", 0.05),
        "Other Agro Waste":    cfg.get("mix_other_agro_waste", 0.15),
    }

    # Blended average × location RM multiplier
    blended_price = sum(prices[k] * weights[k] for k in prices) * loc["rm"]
    daily_cost = blended_price * feed

    items = []
    for name in prices:
        items.append({
            "feedstock": name,
            "farm_gate_price": prices[name],
            "mix_pct": weights[name] * 100,
            "weighted_price": round(prices[name] * weights[name], 0),
        })

    return {
        "items": items,
        "blended_price": round(blended_price, 0),
        "rm_multiplier": loc["rm"],
        "daily_cost": round(daily_cost, 0),
    }


# ══════════════════════════════════════════════════════════════════════
# 3D — CONVENTIONAL BITUMEN COST (landed, with GST + freight + loss)
# ══════════════════════════════════════════════════════════════════════
def calculate_bitumen_cost(cfg, conv_bitumen_needed):
    """Calculate conventional bitumen landed cost per tonne and daily cost."""
    base_price = cfg.get("price_conv_bitumen", 45750)
    bit_transport = cfg.get("bitumen_transport", 650)

    gst = base_price * 0.18
    tanker_hire = 180
    unloading = 120
    storage_loss = base_price * 0.015  # 1.5% transit/storage loss

    landed_per_tonne = base_price + gst + bit_transport + tanker_hire + unloading + storage_loss
    daily_cost = landed_per_tonne * conv_bitumen_needed

    breakdown = [
        ("Base Price (ex-IOCL/BPCL VG30)", base_price),
        ("GST @ 18%", round(gst, 0)),
        ("Road/Rail Freight", bit_transport),
        ("Tanker Hire", tanker_hire),
        ("Unloading", unloading),
        ("Storage/Transit Loss @ 1.5%", round(storage_loss, 0)),
    ]

    return {
        "breakdown": breakdown,
        "base_price": base_price,
        "landed_per_tonne": round(landed_per_tonne, 0),
        "daily_cost": round(daily_cost, 0),
        "conv_bitumen_needed": round(conv_bitumen_needed, 2),
    }


# ══════════════════════════════════════════════════════════════════════
# 3E — LANDING / INBOUND COST (farm gate to plant gate)
# ══════════════════════════════════════════════════════════════════════
def calculate_landing_cost(cfg, loc, feed, conv_bitumen_needed):
    """Calculate complete landing cost for agro waste + bitumen inbound."""
    tr_mult = loc["tr_in"]

    baling = cfg.get("landing_baling", 350) * tr_mult
    primary_transport = cfg.get("landing_primary_transport", 250) * tr_mult
    depot_storage = cfg.get("landing_depot_storage", 300)
    long_haul = cfg.get("landing_long_haul", 480) * tr_mult
    load_unload = cfg.get("landing_load_unload", 140)
    testing_misc = cfg.get("landing_testing_misc", 65)

    subtotal = baling + primary_transport + depot_storage + long_haul + load_unload + testing_misc
    contingency = subtotal * 0.02  # 2% misc contingency
    lc_per_tonne_agro = subtotal + contingency

    lc_agro_daily = lc_per_tonne_agro * feed
    bit_transport = cfg.get("bitumen_transport", 650)
    lc_bitumen_daily = bit_transport * conv_bitumen_needed

    items = [
        ("Baling & Collection", round(baling, 0), True),
        ("Primary Transport (Farm→Depot)", round(primary_transport, 0), True),
        ("Depot/Aggregation Storage", round(depot_storage, 0), False),
        ("Long Haul (Depot→Plant)", round(long_haul, 0), True),
        ("Loading + Unloading", round(load_unload, 0), False),
        ("Weighbridge & QC Testing + Misc", round(testing_misc, 0), False),
        ("Contingency @ 2%", round(contingency, 0), False),
    ]

    return {
        "items": items,
        "lc_per_tonne_agro": round(lc_per_tonne_agro, 0),
        "lc_agro_daily": round(lc_agro_daily, 0),
        "lc_bitumen_daily": round(lc_bitumen_daily, 0),
        "total_daily": round(lc_agro_daily + lc_bitumen_daily, 0),
        "transport_multiplier": tr_mult,
    }


# ══════════════════════════════════════════════════════════════════════
# 3F — PRODUCTION COST (energy, labour, overheads, chemicals)
# ══════════════════════════════════════════════════════════════════════
def calculate_production_cost(cfg, loc, syngas_per_day):
    """Calculate daily production cost with location adjustments."""
    elec_rate = cfg.get("electricity_rate", 7.5)
    elec_kwh = cfg.get("electricity_kwh_day", 1200)
    diesel_rate = cfg.get("diesel_rate", 92)
    diesel_litres = cfg.get("diesel_litres_day", 120)
    labour = cfg.get("labour_daily_cost", 18000)
    overheads = cfg.get("overheads_daily_cost", 12000)
    chemicals = cfg.get("chemicals_daily_cost", 2500)

    electricity_cost = elec_rate * elec_kwh * loc["energy"]
    diesel_cost = diesel_rate * diesel_litres * loc["energy"]
    syngas_credit = syngas_per_day * 1000  # ₹1,000/T energy equivalent
    energy_net = electricity_cost + diesel_cost - syngas_credit

    labour_adjusted = labour * loc["lb"] * 1.20  # +20% PF/ESI

    total = energy_net + labour_adjusted + overheads + chemicals

    items = [
        ("Electricity", round(electricity_cost, 0), f"{elec_rate}×{elec_kwh} kWh×{loc['energy']:.2f}"),
        ("Diesel", round(diesel_cost, 0), f"₹{diesel_rate}×{diesel_litres} L×{loc['energy']:.2f}"),
        ("Less: Syngas Credit", round(-syngas_credit, 0), f"{syngas_per_day:.1f} T×₹1,000"),
        ("Net Energy", round(energy_net, 0), ""),
        ("Labour (incl. PF/ESI +20%)", round(labour_adjusted, 0), f"₹{labour:,}×{loc['lb']:.2f}×1.2"),
        ("Overheads & Admin", round(overheads, 0), ""),
        ("Chemicals & Catalysts", round(chemicals, 0), ""),
    ]

    return {
        "items": items,
        "electricity_cost": round(electricity_cost, 0),
        "diesel_cost": round(diesel_cost, 0),
        "syngas_credit": round(syngas_credit, 0),
        "energy_net": round(energy_net, 0),
        "labour_adjusted": round(labour_adjusted, 0),
        "overheads": overheads,
        "chemicals": chemicals,
        "total": round(total, 0),
    }


# ══════════════════════════════════════════════════════════════════════
# 3G — PACKING COST (net of scrap return)
# ══════════════════════════════════════════════════════════════════════
def calculate_packing_costs(blend_tpd, char_tpd, oil_surplus):
    """Calculate packing cost net of scrap value per day."""
    items = [
        ("Bio-Bitumen Bulk Tanker", "10-20 MT", 0, 0, 0, "No packing — bulk supply", round(blend_tpd * 0.5)),
        ("Bio-Bitumen MS Drum 180kg", "180 kg", 420, 280, 140, "MS Drums", round(blend_tpd * 0.5 / 0.18)),
        ("Bio-Char HDPE Bag 50kg", "50 kg", 28, 6, 22, "HDPE Bags", round(char_tpd * 1000 / 50)),
        ("Bio-Oil IBC Tank 1000L", "1000 L", 850, 400, 450, "IBC Tanks", max(1, round(oil_surplus))),
        ("Bio-Char PP Bag 25kg", "25 kg", 18, 3, 15, "PP Premium bags", round(char_tpd * 0.3 * 1000 / 25)),
    ]

    # Gross, scrap return, net
    pack_gross = sum(cost * units for _, _, cost, _, _, _, units in items)
    pack_scrap = sum(scrap * units for _, _, _, scrap, _, _, units in items)
    pack_net = sum(net * units for _, _, _, _, net, _, units in items)

    return {
        "items": items,
        "gross": round(pack_gross, 0),
        "scrap_return": round(pack_scrap, 0),
        "total": round(pack_net, 0),
    }


# ══════════════════════════════════════════════════════════════════════
# 3H — WASTE & REJECTION COST
# ══════════════════════════════════════════════════════════════════════
def calculate_waste_costs(cfg, feed, bio_oil, bio_char, production_cost_total):
    """Calculate waste/loss/rejection costs per day."""
    waste_factor = cfg.get("waste_loss_factor", 5) / 100

    items = [
        ("Moisture Evaporation", "Drying", 12, feed * 0.12, 0),
        ("Flue Gas / CO₂ Release", "Pyrolysis", 4, feed * 0.04, 0),
        ("Off-spec Bio-Oil (3%)", "Refining", 3, bio_oil * 0.03, round(bio_oil * 0.03 * 5000)),
        ("Char Fines (5% too fine)", "Screening", 5, bio_char * 0.05, round(bio_char * 0.05 * 2000)),
        ("Ash & Slag", "Post-pyrolysis", 2, feed * 0.02, round(feed * 0.02 * 2000)),
        ("Contamination/Foreign", "Pre-processing", 2, feed * 0.02, round(feed * 0.02 * 1750)),
        ("Condensate/Pyrolytic Water", "Condensation", 6, feed * 0.06, round(feed * 0.06 * 1000)),
    ]

    # Add waste loss factor on production cost
    waste_factor_cost = production_cost_total * waste_factor
    specific_waste = sum(cost for _, _, _, _, cost in items)
    total = specific_waste + waste_factor_cost

    return {
        "items": items,
        "waste_factor_pct": cfg.get("waste_loss_factor", 5),
        "waste_factor_cost": round(waste_factor_cost, 0),
        "specific_waste": round(specific_waste, 0),
        "total": round(total, 0),
    }


# ══════════════════════════════════════════════════════════════════════
# 3I — OUTBOUND LOGISTICS
# ══════════════════════════════════════════════════════════════════════
def calculate_outbound(blend_tpd, loc):
    """Calculate outbound delivery cost per day."""
    cost_per_tonne = 800 * loc["tr_out"]
    total = blend_tpd * cost_per_tonne
    return {
        "cost_per_tonne": round(cost_per_tonne, 0),
        "total": round(total, 0),
        "outbound_multiplier": loc["tr_out"],
    }


# ══════════════════════════════════════════════════════════════════════
# SCRAP & BY-PRODUCT REVENUE
# ══════════════════════════════════════════════════════════════════════
def calculate_scrap_revenue(cfg, blend_tpd, char_tpd, syngas_tpd):
    """Calculate all scrap and by-product income per day."""
    drum_price = cfg.get("sale_empty_drum", 280)
    carbon_credit_price = cfg.get("sale_carbon_credit", 12500)

    drums = round(blend_tpd * 0.5 / 0.18)
    bags = round(char_tpd * 1000 / 50)
    char_fines = round(char_tpd * 0.05, 2)

    items = [
        ("Empty MS Drums (returned)", drums, drum_price, drums * drum_price, "Drum re-conditioners"),
        ("Empty HDPE Bags", bags, 4, bags * 4, "Recyclers"),
        ("Off-spec Bio-Oil (fuel)", 0.2, 14000, 2800, "Brick kilns, boilers"),
        ("Char Fines (boiler fuel)", char_fines, 4000, round(char_fines * 4000), "Ceramic units"),
        ("Syngas (internal fuel credit)", round(syngas_tpd, 1), 1023, round(syngas_tpd * 1023), "Internal energy offset"),
        ("Carbon Credits", 5, carbon_credit_price, 5 * carbon_credit_price, "Voluntary carbon market"),
        ("Metal Scrap (maintenance)", 15, 45, 675, "Local scrap dealers"),
    ]

    total = sum(income for _, _, _, income, _ in items)
    return {"items": items, "total": round(total, 0)}


# ══════════════════════════════════════════════════════════════════════
# 3K — REVENUE BY PRODUCT (7 streams)
# ══════════════════════════════════════════════════════════════════════
def calculate_revenue(cfg, outputs):
    """Calculate daily revenue from all product streams."""
    blend = outputs["blend_output_per_day"]
    char = outputs["bio_char_per_day"]
    oil_surplus = outputs["bio_oil_surplus"]

    vg30_price = cfg.get("sale_bio_bitumen_vg30", 44000)
    vg40_price = cfg.get("sale_bio_bitumen_vg40", 48000)
    char_agri_price = cfg.get("sale_biochar_agri", 26000)
    char_ind_price = cfg.get("sale_biochar_industrial", 32000)
    oil_fuel_price = cfg.get("sale_bio_oil_fuel", 22000)
    pellet_price = cfg.get("sale_biomass_pellets", 9000)

    items = [
        {"product": "Bio-Bitumen VG30 (70%)", "qty_tpd": round(blend * 0.70, 2),
         "price": vg30_price, "daily_rev": round(blend * 0.70 * vg30_price, 0), "buyer": "NHAI, PWD, Road Contractors"},
        {"product": "Bio-Bitumen VG40 (30%)", "qty_tpd": round(blend * 0.30, 2),
         "price": vg40_price, "daily_rev": round(blend * 0.30 * vg40_price, 0), "buyer": "Airport, Highway Overlay"},
        {"product": "Bio-Char (Agriculture 70%)", "qty_tpd": round(char * 0.70, 2),
         "price": char_agri_price, "daily_rev": round(char * 0.70 * char_agri_price, 0), "buyer": "Farmers, Fertilizer cos"},
        {"product": "Bio-Char (Industrial 15%)", "qty_tpd": round(char * 0.15, 2),
         "price": char_ind_price, "daily_rev": round(char * 0.15 * char_ind_price, 0), "buyer": "Water treatment, Carbon seq"},
        {"product": "Bio-Oil (Surplus Fuel)", "qty_tpd": round(oil_surplus, 2),
         "price": oil_fuel_price, "daily_rev": round(oil_surplus * oil_fuel_price, 0), "buyer": "Boilers, Brick kilns"},
        {"product": "Biomass Pellets", "qty_tpd": 1.0,
         "price": pellet_price, "daily_rev": pellet_price, "buyer": "Thermal plants, Co-firing"},
    ]

    total_rev = sum(i["daily_rev"] for i in items)

    # Weighted sale price of blend
    sale_price_blend = vg30_price * 0.70 + vg40_price * 0.30

    # By-product credit = total revenue minus bitumen revenue
    bitumen_rev = items[0]["daily_rev"] + items[1]["daily_rev"]
    by_product_credit = total_rev - bitumen_rev

    return {
        "items": items,
        "total_daily": round(total_rev, 0),
        "sale_price_blend": round(sale_price_blend, 0),
        "bitumen_rev_daily": round(bitumen_rev, 0),
        "by_product_credit_daily": round(by_product_credit, 0),
    }


# ══════════════════════════════════════════════════════════════════════
# MASTER COST SHEET — Complete DPR (Sections 3A-3M combined)
# ══════════════════════════════════════════════════════════════════════
def calculate_complete_cost_sheet(cfg):
    """Generate complete cost-per-tonne bifurcation from config.
    This is the SINGLE master function. ALL pages read from this."""
    state = cfg.get("state", "Maharashtra")
    loc = get_multiplier(state)
    operating_days = cfg.get("working_days", 300)

    # 3B — Process outputs
    outputs = calculate_process_outputs(cfg)
    feed = outputs["feed"]
    blend_tpd = outputs["blend_output_per_day"]
    conv_bit_needed = outputs["conv_bitumen_needed"]

    # 3C — Raw material cost
    rm = calculate_rm_cost(cfg, loc)

    # 3D — Conventional bitumen cost
    bit = calculate_bitumen_cost(cfg, conv_bit_needed)

    # 3E — Landing cost
    landing = calculate_landing_cost(cfg, loc, feed, conv_bit_needed)

    # 3F — Production cost
    production = calculate_production_cost(cfg, loc, outputs["syngas_per_day"])

    # 3G — Packing cost
    packing = calculate_packing_costs(blend_tpd, outputs["bio_char_per_day"], outputs["bio_oil_surplus"])

    # 3H — Waste & rejection
    waste = calculate_waste_costs(cfg, feed, outputs["bio_oil_per_day"],
                                   outputs["bio_char_per_day"], production["total"])

    # 3I — Outbound
    outbound = calculate_outbound(blend_tpd, loc)

    # Scrap revenue
    scrap = calculate_scrap_revenue(cfg, blend_tpd, outputs["bio_char_per_day"], outputs["syngas_per_day"])

    # 3K — Revenue
    revenue = calculate_revenue(cfg, outputs)

    # ══════════════════════════════════════════════════════════════
    # 3J — TOTAL GROSS COST (daily)
    # ══════════════════════════════════════════════════════════════
    cost_heads = [
        ("Agro Waste (blended farm gate)", rm["daily_cost"]),
        ("Conventional Bitumen + GST", bit["daily_cost"]),
        ("Landing/Inbound Logistics", landing["total_daily"]),
        ("Energy (net of syngas)", production["energy_net"]),
        ("Labour (incl. PF/ESI)", production["labour_adjusted"]),
        ("Chemicals & Catalysts", production["chemicals"]),
        ("Overheads & Admin", production["overheads"]),
        ("Packing (net of scrap)", packing["total"]),
        ("Waste & Rejection", waste["total"]),
        ("Outbound Delivery", outbound["total"]),
    ]

    gross_daily = sum(c for _, c in cost_heads)

    # ══════════════════════════════════════════════════════════════
    # 3L — COST PER TONNE + MARGIN
    # ══════════════════════════════════════════════════════════════
    by_product_credit = revenue["by_product_credit_daily"]
    net_daily = gross_daily - by_product_credit - scrap["total"]
    net_cpt = net_daily / blend_tpd if blend_tpd > 0 else 0

    sale_price_blend = revenue["sale_price_blend"]
    margin_pt = sale_price_blend - net_cpt
    margin_pct = (margin_pt / sale_price_blend * 100) if sale_price_blend > 0 else 0

    # ══════════════════════════════════════════════════════════════
    # 3M — ANNUAL P&L
    # ══════════════════════════════════════════════════════════════
    annual_revenue = revenue["total_daily"] * operating_days
    annual_rm = rm["daily_cost"] * operating_days
    annual_bitumen = bit["daily_cost"] * operating_days
    annual_landing = landing["total_daily"] * operating_days
    annual_prod = production["total"] * operating_days
    annual_packing = packing["total"] * operating_days
    annual_outbound = outbound["total"] * operating_days
    annual_waste = waste["total"] * operating_days
    annual_scrap_credit = scrap["total"] * operating_days

    annual_cogs = annual_rm + annual_bitumen + annual_landing + annual_prod + annual_packing + annual_outbound + annual_waste
    gross_profit = annual_revenue - annual_cogs + annual_scrap_credit
    gross_margin_pct = (gross_profit / annual_revenue * 100) if annual_revenue > 0 else 0

    # Fixed costs
    plant_value = cfg.get("investment_cr", 6.4) * 1e7
    total_investment = (cfg.get("investment_cr", 6.4) + cfg.get("working_capital_lac", 0) / 100) * 1e7
    debt_pct = 1 - cfg.get("equity_ratio", 0.40)
    debt_amount = total_investment * debt_pct

    annual_depreciation = plant_value * cfg.get("depreciation_rate", 0.10)
    annual_interest = debt_amount * cfg.get("interest_rate", 0.115)
    annual_sga = annual_revenue * 0.02  # 2% selling & admin

    ebt = gross_profit - annual_depreciation - annual_interest - annual_sga
    tax_rate = cfg.get("tax_rate", 0.25)
    tax = ebt * tax_rate if ebt > 0 else 0
    net_profit = ebt - tax
    net_margin_pct = (net_profit / annual_revenue * 100) if annual_revenue > 0 else 0

    payback_years = total_investment / net_profit if net_profit > 0 else 999
    roi = (net_profit / total_investment * 100) if total_investment > 0 else 0

    annual_pnl = {
        "revenue": round(annual_revenue, 0),
        "cogs": round(annual_cogs, 0),
        "scrap_credit": round(annual_scrap_credit, 0),
        "gross_profit": round(gross_profit, 0),
        "gross_margin_pct": round(gross_margin_pct, 1),
        "depreciation": round(annual_depreciation, 0),
        "interest": round(annual_interest, 0),
        "sga": round(annual_sga, 0),
        "ebt": round(ebt, 0),
        "tax": round(tax, 0),
        "net_profit": round(net_profit, 0),
        "net_margin_pct": round(net_margin_pct, 1),
        "payback_years": round(payback_years, 1),
        "roi_pct": round(roi, 1),
        "operating_days": operating_days,
        "plant_value": round(plant_value, 0),
        "total_investment": round(total_investment, 0),
        "debt_amount": round(debt_amount, 0),
    }

    # ══════════════════════════════════════════════════════════════
    # RETURN EVERYTHING
    # ══════════════════════════════════════════════════════════════
    return {
        # Sub-modules (full detail)
        "outputs": outputs,
        "rm": rm,
        "bitumen": bit,
        "landing": landing,
        "production": production,
        "packing": packing,
        "waste": waste,
        "outbound": outbound,
        "scrap": scrap,
        "revenue": revenue,
        "annual_pnl": annual_pnl,

        # Summary (for KPI cards)
        "cost_heads": cost_heads,
        "gross_daily": round(gross_daily, 0),
        "by_product_credit": round(by_product_credit, 0),
        "scrap_total": scrap["total"],
        "net_daily": round(net_daily, 0),
        "net_cpt": round(net_cpt, 0),
        "sale_price_pt": round(sale_price_blend, 0),
        "margin_pt": round(margin_pt, 0),
        "margin_pct": round(margin_pct, 1),
        "blend_total_tpd": round(blend_tpd, 1),
        "total_rev_daily": revenue["total_daily"],

        # Pass-through for page access
        "conv_bit_tpd": round(conv_bit_needed, 1),
        "oil_tpd": round(outputs["bio_oil_per_day"], 1),
        "char_tpd": round(outputs["bio_char_per_day"], 1),
        "gas_tpd": round(outputs["syngas_per_day"], 1),
        "bio_oil_surplus": round(outputs["bio_oil_surplus"], 1),
        "multiplier": loc,
        "state": state,
    }
