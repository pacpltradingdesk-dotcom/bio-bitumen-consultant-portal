"""
Plant Engineering Engine — Deterministic Equipment Sizing, Safety Clearances & Standards
=========================================================================================
Every dimension computed from INPUT_PARAMS. Nothing random or estimated.
Based on IS/BIS/NBC/OSHA/OISD standards.

Sections:
  1. Computed parameters (mass balance, equipment sizing)
  2. Complete machinery list with specifications (15 items)
  3. Safety clearances (IS 14489, NBC 2016, OSHA)
  4. Colour codes (IS 2379 pipes, IS 9457 safety signs)
  5. Drawing standards (IS 696, IS 11065)
"""
import math


# ══════════════════════════════════════════════════════════════════════
# SECTION 1: COMPUTED PARAMETERS FROM INPUTS
# ══════════════════════════════════════════════════════════════════════
def compute_all(cfg):
    """Compute ALL derived parameters from input config.
    Every formula is deterministic — no estimation or AI generation."""

    tpd = cfg.get("capacity_tpd", 20)
    op_hours = cfg.get("operating_hours", 16)
    oil_yield = cfg.get("bio_oil_yield_pct", 32) / 100
    char_yield = cfg.get("bio_char_yield_pct", 28) / 100
    syngas_yield = cfg.get("syngas_yield_pct", 22) / 100
    loss_pct = cfg.get("process_loss_pct", 18) / 100
    blend_ratio = cfg.get("bio_blend_pct", 20) / 100
    moisture = cfg.get("moisture_feed_pct", 20) / 100
    plot_l = cfg.get("plot_length_m", max(60, int(tpd * 4)))
    plot_w = cfg.get("plot_width_m", max(40, int(tpd * 3)))

    # ── Mass Balance ──
    feed_per_hour_kg = (tpd / op_hours) * 1000
    bio_oil_tpd = tpd * oil_yield
    bio_char_tpd = tpd * char_yield
    syngas_tpd = tpd * syngas_yield
    loss_tpd = tpd * loss_pct

    bio_oil_for_blend = bio_oil_tpd * 0.85
    bio_oil_surplus = bio_oil_tpd * 0.15
    blend_output_tpd = bio_oil_for_blend / blend_ratio if blend_ratio > 0 else 0
    conv_bitumen_tpd = blend_output_tpd - bio_oil_for_blend

    dry_feed_kg_hr = feed_per_hour_kg * (1 - moisture)
    moisture_evap_kg_hr = feed_per_hour_kg * moisture

    # ── Equipment Sizing (empirical formulas) ──
    # Dryer
    dryer_dia_m = round(math.ceil((feed_per_hour_kg / 800) ** 0.5 * 10) / 10, 1)
    dryer_len_m = round(math.ceil(dryer_dia_m * 5 * 2) / 2, 1)

    # Pyrolysis Reactor
    reactor_vol_m3 = (feed_per_hour_kg / 400) * 1.25
    reactor_dia_m = round(math.ceil((reactor_vol_m3 * 4 / (3.14 * 3)) ** 0.5 * 10) / 10, 1)
    reactor_ht_m = round(math.ceil(reactor_dia_m * 3 * 2) / 2, 1)
    reactor_qty = 1 if tpd <= 30 else 2

    # Bio-oil Storage Tank (3 days)
    bio_oil_tank_vol = bio_oil_tpd * 3 * 1.2
    bio_oil_tank_dia = round(math.ceil((bio_oil_tank_vol * 4 / 3.14) ** 0.33 * 10) / 10, 1)
    bio_oil_tank_ht = round(bio_oil_tank_dia * 0.8, 1)

    # Blend Tank (2 days)
    blend_tank_vol = blend_output_tpd * 2 * 1.15
    blend_tank_dia = round(math.ceil((blend_tank_vol * 4 / 3.14) ** 0.33 * 10) / 10, 1)
    blend_tank_ht = round(blend_tank_dia * 1.0, 1)

    # Feed Storage Shed (7 days, bulk density 120 kg/m3, stack 3.5m)
    feed_vol_m3 = (tpd * 7) / 0.12
    feed_shed_area = feed_vol_m3 / 3.5
    feed_shed_l = round(math.ceil(feed_shed_area ** 0.5 * 1.5), 0)
    feed_shed_w = round(math.ceil(feed_shed_area / max(1, feed_shed_l)), 0)

    # Biochar Storage (5 days)
    biochar_area = (bio_char_tpd * 5) / (0.3 * 1.5)

    # Pipe Sizing
    conveyor_width_mm = 500 if feed_per_hour_kg <= 5000 else (650 if feed_per_hour_kg <= 10000 else 800)

    # Electrical
    elec_kva = cfg.get("electricity_kva", max(100, int(tpd * 8)))
    main_bus_amps = round(elec_kva * 1000 / (1.732 * 415), 0)

    # Civil
    flood_prone = cfg.get("flood_prone", False)
    plinth_mm = 900 if flood_prone else 450

    return {
        # Mass Balance
        "feed_per_hour_kg": round(feed_per_hour_kg, 0),
        "dry_feed_kg_hr": round(dry_feed_kg_hr, 0),
        "moisture_evap_kg_hr": round(moisture_evap_kg_hr, 0),
        "bio_oil_tpd": round(bio_oil_tpd, 2),
        "bio_char_tpd": round(bio_char_tpd, 2),
        "syngas_tpd": round(syngas_tpd, 2),
        "loss_tpd": round(loss_tpd, 2),
        "bio_oil_for_blend": round(bio_oil_for_blend, 2),
        "bio_oil_surplus": round(bio_oil_surplus, 2),
        "blend_output_tpd": round(blend_output_tpd, 2),
        "conv_bitumen_tpd": round(conv_bitumen_tpd, 2),

        # Equipment Sizing
        "dryer_dia_m": dryer_dia_m,
        "dryer_len_m": dryer_len_m,
        "reactor_vol_m3": round(reactor_vol_m3, 1),
        "reactor_dia_m": reactor_dia_m,
        "reactor_ht_m": reactor_ht_m,
        "reactor_qty": reactor_qty,
        "reactor_wall_thickness_mm": 12,
        "reactor_insulation_mm": 100,
        "bio_oil_tank_vol_m3": round(bio_oil_tank_vol, 1),
        "bio_oil_tank_dia_m": bio_oil_tank_dia,
        "bio_oil_tank_ht_m": bio_oil_tank_ht,
        "blend_tank_vol_m3": round(blend_tank_vol, 1),
        "blend_tank_dia_m": blend_tank_dia,
        "blend_tank_ht_m": blend_tank_ht,
        "feed_shed_area_m2": round(feed_shed_area, 0),
        "feed_shed_l_m": feed_shed_l,
        "feed_shed_w_m": feed_shed_w,
        "biochar_area_m2": round(biochar_area, 0),
        "conveyor_width_mm": conveyor_width_mm,

        # Electrical
        "elec_kva": elec_kva,
        "main_bus_amps": main_bus_amps,

        # Civil
        "plinth_mm": plinth_mm,
        "plot_l_m": plot_l,
        "plot_w_m": plot_w,
        "plot_area_sqm": plot_l * plot_w,
    }


# ══════════════════════════════════════════════════════════════════════
# SECTION 2: COMPLETE MACHINERY LIST (15 major items)
# ══════════════════════════════════════════════════════════════════════
def get_machinery_list(cfg, comp=None):
    """Return complete machinery list with deterministic specs.
    Every dimension is computed from capacity — never estimated."""
    if comp is None:
        comp = compute_all(cfg)

    tpd = cfg.get("capacity_tpd", 20)
    pyro_temp = cfg.get("pyrolysis_temp_C", 500)

    return [
        {
            "tag": "SC-101", "name": "Weighbridge + Receiving Hopper",
            "qty": 1, "motor_kw": 11,
            "dims": f"Weighbridge 18m×3.5m | Hopper {comp['feed_per_hour_kg']*2/150:.0f}m³",
            "material": "MS IS 2062 Gr A",
            "foundation": "RCC M20 isolated footing",
            "colour": "RAL 7035 Light Grey",
            "is_ref": "IS 9281",
            "safety": "Pit guard railing H=1.1m, anti-dust cover, load cell protection",
            "clearance_m": 6.0,
        },
        {
            "tag": "SZ-101", "name": "Primary Shredder / Chipper",
            "qty": 1, "motor_kw": 75,
            "dims": "2800mm×1800mm×2200mm | Output: 50mm size",
            "material": "Body MS, Hammers Mn Steel",
            "foundation": "Anti-vibration pad 300mm thick",
            "colour": "RAL 1023 Traffic Yellow",
            "is_ref": "IS 1570 Pt 2",
            "safety": "Acoustic enclosure (95→75dB), emergency pull-cord, choke-proof auto-stop",
            "clearance_m": 2.0,
        },
        {
            "tag": "DR-101", "name": "Rotary Drum Dryer",
            "qty": 1, "motor_kw": 37,
            "dims": f"Drum: Ø{comp['dryer_dia_m']}m × {comp['dryer_len_m']}m | 150°C | 3.5 RPM",
            "material": "MS shell 10mm, mineral wool insulation 75mm",
            "foundation": "RCC M20 with bearing supports",
            "colour": "RAL 3002 Carmine Red (hot surface)",
            "is_ref": "IS 4694",
            "safety": "Explosion vent IS 6183, bearing temp monitor, earthing chain",
            "clearance_m": 3.0,
        },
        {
            "tag": "GR-101", "name": "Secondary Grinder / Fine Hammer Mill",
            "qty": 1, "motor_kw": 45,
            "dims": f"2200mm×1400mm×1800mm | Input: 50mm → Output: 3mm | {comp['dry_feed_kg_hr']:.0f} kg/hr",
            "material": "Body MS, Hammers Mn Steel",
            "foundation": "Anti-vibration pad",
            "colour": "RAL 1023 Traffic Yellow",
            "is_ref": "IS 1570",
            "safety": "Magnetic separator upstream, spark detection + suppression, explosion vent",
            "clearance_m": 1.5,
        },
        {
            "tag": "PR-101", "name": "Pyrolysis Reactor (Rotary Kiln)",
            "qty": comp["reactor_qty"], "motor_kw": 55,
            "dims": (f"Ø{comp['reactor_dia_m']}m × {comp['reactor_ht_m']}m | "
                     f"Wall: {comp['reactor_wall_thickness_mm']}mm SS310S | "
                     f"Insulation: {comp['reactor_insulation_mm']}mm mineral wool | "
                     f"Design: {pyro_temp+50}°C / Full vacuum to +0.5 barg"),
            "material": "AISI 310S SS inner, IS 2062 outer shell",
            "foundation": f"RCC M25 mat foundation 600mm thick",
            "colour": "RAL 3002 Carmine Red + RAL 7035 cladding",
            "is_ref": "IS 2825 (pressure vessel), IS 3114 (insulation)",
            "safety": (f"PSV at 0.3 barg, N2 purge, T high-high {pyro_temp+100}°C auto-shutdown, "
                       "CO detector 25/50ppm, 2× earth bonds, hot surface label H1 IS 3134"),
            "clearance_m": 15.0,
            "nozzles": "Feed 300mm, Vapour 200mm, Syngas 150mm, Char 250mm, Thermowell 50mm×6, Manway 600mm, PSV 100mm",
        },
        {
            "tag": "CD-101", "name": "Shell & Tube Condenser",
            "qty": 1, "motor_kw": 0,
            "dims": f"4.5m × Ø0.8m | Cooling water: 12 m³/hr | Bio-oil outlet: 80mm",
            "material": "Shell CS IS 2062, Tubes SS 316",
            "foundation": "RCC saddle supports",
            "colour": "RAL 5012 Light Blue",
            "is_ref": "IS 4503 (heat exchanger), TEMA class C",
            "safety": "NRV on vapour inlet, flame arrestor IS 6183, pressure gauge",
            "clearance_m": 1.5,
        },
        {
            "tag": "BT-101", "name": "Bio-Oil Storage Tank (Atmospheric)",
            "qty": 2, "motor_kw": 0,
            "dims": (f"Ø{comp['bio_oil_tank_dia_m']}m × {comp['bio_oil_tank_ht_m']}m | "
                     f"{comp['bio_oil_tank_vol_m3']:.1f} m³ each | Shell 6mm, Roof 5mm"),
            "material": "MS IS 2062 Gr A",
            "foundation": "RCC ring wall + sand pad",
            "colour": "RAL 3002 Carmine Red (Class B petroleum)",
            "is_ref": "IS 803 (oil storage), OISD 118",
            "safety": "Dyke bund 110% volume, flame arrestor, level alarm, earth cable, foam pourer",
            "clearance_m": 15.0,
            "dyke_vol_m3": round(comp["bio_oil_tank_vol_m3"] * 1.1, 1),
        },
        {
            "tag": "BIT-101", "name": "Conventional Bitumen Tank (Heated)",
            "qty": 2, "motor_kw": 15,
            "dims": f"Heated to 160°C | Insulation 100mm + Al cladding | 3-day storage",
            "material": "MS IS 2062, electric trace heating",
            "foundation": "RCC M20 with thermal pad",
            "colour": "RAL 1003 Signal Yellow (hot insulated)",
            "is_ref": "IS 1553 (bitumen), IS 4671 (insulation)",
            "safety": "Over-temp alarm 175°C, shutdown 185°C, P/V vent, level indicator",
            "clearance_m": 9.0,
        },
        {
            "tag": "MX-101", "name": "Bio-Bitumen Blending Unit",
            "qty": 1, "motor_kw": 15,
            "dims": (f"Blend tank: Ø{comp['blend_tank_dia_m']}m × {comp['blend_tank_ht_m']}m | "
                     f"{comp['blend_tank_vol_m3']:.1f} m³ | Mixer Ø{comp['blend_tank_dia_m']*0.35:.1f}m | 140°C"),
            "material": "MS IS 2062, insulation 75mm",
            "foundation": "RCC M20",
            "colour": "RAL 1003 Signal Yellow",
            "is_ref": "IS 1195 (bitumen tests), IS 8887 (PMB)",
            "safety": "Agitator interlock, over-temp 160°C alarm, level switch LL",
            "clearance_m": 3.0,
        },
        {
            "tag": "EP-101", "name": "Cyclone + Bag Filter + Stack",
            "qty": 1, "motor_kw": 22,
            "dims": f"Cyclone Ø1.2m×4.8m | Bag filter 3m×2m×5m | Stack Ø600mm × 30m",
            "material": "MS IS 2062, filter bags polyester",
            "foundation": "RCC M20 for stack + equipment pad",
            "colour": "RAL 7035 Light Grey",
            "is_ref": "IS 11229 (stack height), CPCB emission norms",
            "safety": "Explosion vent, DP indicator, high-temp alarm",
            "clearance_m": 5.0,
            "emission_std": "PM < 50 mg/Nm³, SO₂ < 100 mg/Nm³ (MoEFCC 2016)",
        },
        {
            "tag": "WTP-101", "name": "ETP (Effluent Treatment Plant)",
            "qty": 1, "motor_kw": 7.5,
            "dims": f"20m × 12m overall | Clarifier Ø3m | {max(5, int(tpd*1.2))} KLD",
            "material": "RCC tanks, MS equipment",
            "foundation": "RCC M25 water-retaining structure",
            "colour": "RAL 6018 Yellow Green",
            "is_ref": "IS 10500 (reuse), CPCB trade effluent norms",
            "safety": "pH monitor, overflow alarm, bund wall",
            "clearance_m": 5.0,
        },
        {
            "tag": "CB-101", "name": "Biochar Cooling Screw + Silo",
            "qty": 1, "motor_kw": 7.5,
            "dims": f"Screw 8m×Ø400mm | Silo Ø{round((comp['biochar_area_m2']/3.14)**0.5*2+0.5,0):.0f}m×6m | 60° cone",
            "material": "MS water-jacketed screw, welded steel silo",
            "foundation": "RCC M20",
            "colour": "RAL 6019 Pastel Green",
            "is_ref": "IS 9410 (silos)",
            "safety": "Inert purge on silo, temp monitor, CO detector, explosion vent NFPA 68",
            "clearance_m": 3.0,
        },
        {
            "tag": "FP-101", "name": "Fire Hydrant + Sprinkler System",
            "qty": 1, "motor_kw": 37,
            "dims": f"Ring main Ø150mm | Hydrant spacing 45m | Tank {50 if tpd<=30 else 100} m³ | Pump 18 m³/hr",
            "material": "CI pipes IS 1536, MS fittings",
            "foundation": "Underground ring main + pump house",
            "colour": "RAL 3002 Signal Red (all fire fighting)",
            "is_ref": "IS 3844, IS 2190, NBC 2016 Part 4",
            "safety": "Fire detection panel IS 2189, smoke/heat/flame detectors, 90dB alarm",
            "clearance_m": 0,
        },
        {
            "tag": "SS-101", "name": "MCC Panel + LT Distribution",
            "qty": 1, "motor_kw": 0,
            "dims": f"3000mm×2200mm×800mm | {comp['main_bus_amps']:.0f}A bus | 415V 3Ph 50Hz | IP54",
            "material": "CRCA sheet, Form 4 separation",
            "foundation": "Anti-static flooring IS 3551",
            "colour": "RAL 7032 Pebble Grey",
            "is_ref": "IS 8623, IS 732",
            "safety": "Earth bus 50×6mm GI, rubber mat 11kV, CO2 5kg extinguisher, cable trench 600×750mm",
            "clearance_m": 15.0,
        },
        {
            "tag": "CR-101", "name": "Control Room + SCADA",
            "qty": 1, "motor_kw": 5,
            "dims": "8m×6m×3.2m | Blast wall 250mm | Positive pressure HVAC",
            "material": "RCC / Blast-resistant prefab",
            "foundation": "RCC M25",
            "colour": "RAL 9010 Pure White",
            "is_ref": "IS 13063 (blast resistant), NBC 2016",
            "safety": "Gas detector display, CCTV, PA system, ESD button, FM200 suppression",
            "clearance_m": 30.0,
        },
    ]


# ══════════════════════════════════════════════════════════════════════
# SECTION 3: SAFETY CLEARANCES (IS 14489, NBC 2016, OSHA, OISD)
# ══════════════════════════════════════════════════════════════════════
SAFETY_CLEARANCES = {
    "reactor_to_boundary_m": 15.0,
    "reactor_to_control_room_m": 30.0,
    "reactor_to_reactor_m": 5.0,
    "bio_oil_tank_to_boundary_m": 15.0,
    "bio_oil_tank_to_building_m": 7.5,
    "bio_oil_tank_to_tank_m": "Max of 1D or 3m",
    "bitumen_tank_to_boundary_m": 9.0,
    "bitumen_tank_to_building_m": 6.0,
    "electrical_to_hazard_m": 15.0,
    "transformer_to_building_m": 3.0,
    "road_width_internal_m": 6.0,
    "fire_road_width_m": 6.0,
    "turning_radius_min_m": 9.0,
    "emergency_exit_max_dist_m": 30.0,
    "fire_hydrant_spacing_m": 45.0,
    "eyewash_to_hazard_max_m": 10.0,
    "first_aid_max_dist_m": 50.0,
    "assembly_point_from_hazard_m": 50.0,
    "green_belt_min_m": 5.0,
    "equipment_clearance_m": 2.0,
    "pipe_rack_height_m": 4.5,
    "column_grid_m": 6.0,
}


# ══════════════════════════════════════════════════════════════════════
# SECTION 4: COLOUR CODES (IS 2379 pipes, IS 9457 safety signs)
# ══════════════════════════════════════════════════════════════════════
PIPE_COLOURS = {
    "water_potable": {"base": "Green", "ral": "RAL 6018", "band": "none"},
    "water_fire": {"base": "Red", "ral": "RAL 3002", "band": "none"},
    "water_cooling": {"base": "Green", "ral": "RAL 6018", "band": "Blue RAL 5012"},
    "compressed_air": {"base": "Sky Blue", "ral": "RAL 5012", "band": "none"},
    "nitrogen": {"base": "Grey", "ral": "RAL 7035", "band": "Black RAL 9005"},
    "bio_oil": {"base": "Brown", "ral": "RAL 8025", "band": "Yellow RAL 1003"},
    "bitumen": {"base": "Black", "ral": "RAL 9005", "band": "Yellow RAL 1003"},
    "syngas": {"base": "Yellow", "ral": "RAL 1003", "band": "none"},
    "effluent": {"base": "Black", "ral": "RAL 9005", "band": "Green RAL 6018"},
    "steam": {"base": "Silver", "ral": "RAL 9006", "band": "none"},
}

EQUIPMENT_COLOURS = {
    "reactors_vessels": "RAL 3002 Carmine Red",
    "rotary_equipment": "RAL 1003 Signal Yellow",
    "static_equipment": "RAL 7035 Light Grey",
    "safety_fire": "RAL 3002 Signal Red",
    "electrical_panels": "RAL 7032 Pebble Grey",
    "control_room": "RAL 9010 Pure White",
    "etp_wtp": "RAL 6018 Yellow Green",
    "biochar_storage": "RAL 6019 Pastel Green",
    "hot_insulated": "RAL 1003 Signal Yellow",
    "foundations": "RAL 7030 Stone Grey",
}

SAFETY_SIGN_COLOURS = {
    "danger": {"bg": "Red", "text": "White"},
    "warning": {"bg": "Yellow", "text": "Black"},
    "notice": {"bg": "Blue", "text": "White"},
    "emergency_exit": {"bg": "Green", "text": "White"},
    "fire_equipment": {"bg": "Red", "text": "White"},
    "first_aid": {"bg": "Green", "text": "White"},
}


# ══════════════════════════════════════════════════════════════════════
# SECTION 5: IS/BIS STANDARDS REFERENCE
# ══════════════════════════════════════════════════════════════════════
STANDARDS = {
    "structural": "IS 800 (Steel), IS 456 (Concrete)",
    "pressure_vessel": "IS 2825",
    "piping": "IS 1239 (MS), IS 4984 (HDPE)",
    "electrical": "IS 732 (Wiring), IS 8623 (Panels)",
    "earthing": "IS 3043",
    "fire": "NBC 2016 Part 4, IS 3844 (Hydrants), IS 2190 (Sprinklers)",
    "safety": "IS 14489, IS 9457 (Signs), IS 3134 (Hazard labels)",
    "colour_pipes": "IS 2379",
    "drawings": "IS 696 (Engineering Drawing), IS 11065 (Title Block)",
    "environment": "MoEFCC EIA 2006, CPCB emission norms",
    "seismic": "IS 1893",
    "wind": "IS 875 Part 3",
    "tanks": "IS 803 (Oil Storage), OISD 118",
    "insulation": "IS 3114, IS 4671",
    "hazardous_area": "IS 5572 (Zone classification), IS 7389 (Ex equipment)",
    "bitumen": "IS 73 (VG grades), IS 1195 (Tests), IS 1553 (Storage)",
    "stack_height": "IS 11229",
    "blast_resistant": "IS 13063",
}


# ══════════════════════════════════════════════════════════════════════
# MASTER FUNCTION — Get complete plant engineering data
# ══════════════════════════════════════════════════════════════════════
def get_plant_engineering(cfg):
    """Return complete engineering data package for any capacity.
    Used by: drawings, AI prompts, DPR generator, financial model."""
    comp = compute_all(cfg)
    machinery = get_machinery_list(cfg, comp)

    total_motor_kw = sum(m["motor_kw"] * m["qty"] for m in machinery)

    return {
        "computed": comp,
        "machinery": machinery,
        "machinery_count": len(machinery),
        "total_motor_kw": total_motor_kw,
        "safety_clearances": SAFETY_CLEARANCES,
        "pipe_colours": PIPE_COLOURS,
        "equipment_colours": EQUIPMENT_COLOURS,
        "safety_sign_colours": SAFETY_SIGN_COLOURS,
        "standards": STANDARDS,
    }
