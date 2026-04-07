"""
Combination Engine — Auto-Select Prompts from Pre-Built Template Library
=========================================================================
Instead of calling AI for every configuration, this engine:
1. Pre-defines BASE PROMPT templates (5 drawing types)
2. Auto-fills VARIABLE BLOCKS from computed specs
3. Returns ready-to-use prompts instantly — ZERO API calls

Supports all combinations:
- 3 technologies × 8 capacities × 9 states × 5 drawing types = 1,080 combos
- Each combo resolved in <10ms (no API needed)

Auto-Healing: If any input is missing, uses nearest logical match.
"""
from engines.plant_engineering import (compute_all, get_machinery_list, SAFETY_CLEARANCES,
    PIPE_COLOURS, EQUIPMENT_COLOURS, get_civil_specs, CIVIL_DRAWING_TYPES)


# ══════════════════════════════════════════════════════════════════════
# TECHNOLOGY DEFINITIONS
# ══════════════════════════════════════════════════════════════════════
TECHNOLOGIES = {
    1: {
        "name": "Full Chain (Biomass → Pyrolysis → Bio-Bitumen)",
        "short": "Full Chain",
        "process_flow": "Biomass Receiving → Shredding → Drying → Pyrolysis (500°C) → Condensation → Bio-Oil Blending with VG30 → Quality Testing → Storage → Dispatch",
        "zones_active": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"],
        "key_equipment": ["Shredder", "Rotary Dryer", "Pyrolysis Reactor", "Condenser", "High Shear Mixer", "Bitumen Tanks"],
        "products": ["Bio-Bitumen VG30/VG40", "Bio-Char", "Syngas (captive)", "Carbon Credits"],
        "capex_factor": 1.0,
    },
    2: {
        "name": "Blending Only (Buy Bio-Oil → Blend with VG30)",
        "short": "Blending Only",
        "process_flow": "Bio-Oil Receiving → Heating → VG30 Bitumen Heating → High Shear Blending → Quality Testing → Storage → Dispatch",
        "zones_active": ["A", "B", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"],
        "key_equipment": ["Bio-Oil Storage", "Bitumen Heating Tank", "High Shear Mixer", "Colloid Mill", "Product Tanks"],
        "products": ["Bio-Bitumen VG30/VG40"],
        "capex_factor": 0.35,
    },
    3: {
        "name": "Raw Output (Biomass → Pyrolysis → Sell Oil + Char)",
        "short": "Raw Output",
        "process_flow": "Biomass Receiving → Shredding → Drying → Pyrolysis (500°C) → Condensation → Bio-Oil Storage → Bio-Char Cooling → Packing → Dispatch",
        "zones_active": ["A", "B", "C", "D", "E", "G", "H", "I", "J", "K", "L", "M", "N", "O"],
        "key_equipment": ["Shredder", "Rotary Dryer", "Pyrolysis Reactor", "Condenser", "Bio-Oil Tanks", "Char Silo"],
        "products": ["Bio-Oil (fuel grade)", "Bio-Char (agriculture/industrial)", "Syngas (captive)"],
        "capex_factor": 0.7,
    },
}

CAPACITIES = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]

BUDGET_LEVELS = {
    "low": {"automation": "Manual controls, basic instruments", "build": "PEB sheds, minimum finish", "factor": 0.7},
    "medium": {"automation": "Semi-auto PLC, basic SCADA", "build": "PEB + RCC critical areas", "factor": 1.0},
    "high": {"automation": "Full SCADA, automated controls", "build": "Full RCC, premium finish", "factor": 1.4},
}

DRAWING_TYPES = {
    "site_layout": "2D Site Layout Plan (Top View)",
    "3d_isometric": "3D Isometric Plant View",
    "process_flow": "Process Flow Diagram (PFD)",
    "equipment_ga": "Equipment General Arrangement",
    "fire_safety": "Fire Safety & Emergency Layout",
    "civil_foundation": "Civil Foundation Plan (for Structural Engineer)",
    "civil_building": "Building Plan + Section (for Municipal Authority)",
    "civil_drainage": "Drainage + ETP Layout (for PCB / Environmental)",
    "civil_compound": "Compound Wall + Road Section (for Contractor)",
}


# ══════════════════════════════════════════════════════════════════════
# AUTO-HEAL: Fill missing inputs with defaults
# ══════════════════════════════════════════════════════════════════════
def auto_heal_inputs(cfg):
    """Fill any missing inputs with nearest logical match."""
    healed = dict(cfg)
    changes = []

    if not healed.get("capacity_tpd") or healed["capacity_tpd"] <= 0:
        healed["capacity_tpd"] = 20
        changes.append("capacity_tpd defaulted to 20")

    if not healed.get("process_id") or healed["process_id"] not in [1, 2, 3]:
        healed["process_id"] = 1
        changes.append("process_id defaulted to 1 (Full Chain)")

    if not healed.get("state"):
        healed["state"] = "Maharashtra"
        changes.append("state defaulted to Maharashtra")

    if not healed.get("plot_length_m") or healed["plot_length_m"] <= 0:
        tpd = healed["capacity_tpd"]
        healed["plot_length_m"] = max(60, int(tpd * 4))
        changes.append(f"plot_length_m auto-calculated: {healed['plot_length_m']}m")

    if not healed.get("plot_width_m") or healed["plot_width_m"] <= 0:
        tpd = healed["capacity_tpd"]
        healed["plot_width_m"] = max(40, int(tpd * 3))
        changes.append(f"plot_width_m auto-calculated: {healed['plot_width_m']}m")

    for field, default in [
        ("bio_oil_yield_pct", 32), ("bio_char_yield_pct", 28),
        ("syngas_yield_pct", 22), ("process_loss_pct", 18),
        ("bio_blend_pct", 20), ("pyrolysis_temp_C", 500),
    ]:
        if not healed.get(field):
            healed[field] = default
            changes.append(f"{field} defaulted to {default}")

    budget = healed.get("budget_level", "medium")
    if budget not in BUDGET_LEVELS:
        healed["budget_level"] = "medium"
        changes.append("budget_level defaulted to medium")

    return healed, changes


# ══════════════════════════════════════════════════════════════════════
# VARIABLE BLOCK GENERATOR — Computed from inputs
# ══════════════════════════════════════════════════════════════════════
def build_variable_block(cfg):
    """Build the variable block from cfg — all computed values."""
    cfg, healed = auto_heal_inputs(cfg)
    comp = compute_all(cfg)
    process_id = cfg.get("process_id", 1)
    machinery = get_machinery_list(cfg, comp)
    tech = TECHNOLOGIES.get(process_id, TECHNOLOGIES[1])

    tpd = cfg["capacity_tpd"]
    plot_l = comp["plot_l_m"]
    plot_w = comp["plot_w_m"]
    plot_area_sqm = plot_l * plot_w
    plot_acres = round(plot_area_sqm / 4047, 2)

    # Machinery table
    mach_lines = []
    for m in machinery:
        mach_lines.append(f"- {m['tag']}: {m['name']} (Qty: {m['qty']}) — {m['dims'][:60]}")

    # Zone list
    zone_names = {
        "A": "Gate & Security", "B": "RM Receiving", "C": "Pre-Processing",
        "D": "Reactor Zone", "E": "Oil Recovery", "F": "Blending",
        "G": "Storage", "H": "Packing & Dispatch", "I": "Electrical",
        "J": "Utilities", "K": "Laboratory", "L": "Safety & Environment",
        "M": "Civil Works", "N": "Office & Admin", "O": "Maintenance",
    }
    active_zones = [f"Zone {z}: {zone_names[z]}" for z in tech["zones_active"]]

    # Additional computed dimensions
    bio_oil_tank_ht = comp.get("bio_oil_tank_ht_m", 2.0)
    blend_tank_dia = comp.get("blend_tank_dia_m", 2.0)
    blend_tank_ht = comp.get("blend_tank_ht_m", 2.0)
    plinth_mm = comp.get("plinth_mm", 450)
    conveyor_w = comp.get("conveyor_width_mm", 500)
    main_bus_amps = comp.get("main_bus_amps", 300)
    feed_hr_kg = comp.get("feed_per_hour_kg", 1250)

    # Pipe sizes (from capacity)
    fire_pipe_dn = 150  # IS 3844 minimum
    oil_pipe_dn = 65 if tpd <= 30 else 80
    syngas_pipe_dn = 100 if tpd <= 50 else 150
    water_pipe_dn = 50 if tpd <= 30 else 80
    bitumen_pipe_dn = 80 if tpd <= 30 else 100

    # Stack height
    stack_height = max(30, int(tpd * 0.8))  # IS 11229 minimum 30m

    # Motor loads per major equipment
    motor_loads = "\n".join(f"  {m['tag']}: {m['name']} — {m['motor_kw']} kW" for m in machinery if m.get('motor_kw', 0) > 0)
    total_motor_kw = sum(m.get('motor_kw', 0) * m.get('qty', 1) for m in machinery)

    return {
        "technology": tech["name"],
        "technology_short": tech["short"],
        "process_flow": tech["process_flow"],
        "capacity_tpd": tpd,
        "plot_l_m": plot_l,
        "plot_w_m": plot_w,
        "plot_area_sqm": plot_area_sqm,
        "plot_acres": plot_acres,
        "state": cfg.get("state", "Maharashtra"),
        # Reactor
        "reactor_dia_m": comp["reactor_dia_m"],
        "reactor_ht_m": comp["reactor_ht_m"],
        "reactor_qty": comp["reactor_qty"],
        "reactor_wall_mm": 12,
        "reactor_insulation_mm": 100,
        # Dryer
        "dryer_dia_m": comp["dryer_dia_m"],
        "dryer_len_m": comp["dryer_len_m"],
        # Tanks
        "bio_oil_tank_dia_m": comp["bio_oil_tank_dia_m"],
        "bio_oil_tank_ht_m": bio_oil_tank_ht,
        "blend_tank_dia_m": blend_tank_dia,
        "blend_tank_ht_m": blend_tank_ht,
        # Shed & buildings
        "feed_shed_l_m": comp["feed_shed_l_m"],
        "feed_shed_w_m": comp["feed_shed_w_m"],
        "office_area_sqm": max(200, int(tpd * 8)),
        "lab_area_sqm": max(108, int(tpd * 5)),
        "control_room_area_sqm": 48,
        # Process outputs
        "bio_oil_tpd": comp["bio_oil_tpd"],
        "bio_char_tpd": comp["bio_char_tpd"],
        "blend_output_tpd": comp["blend_output_tpd"],
        "feed_hr_kg": feed_hr_kg,
        # Electrical
        "elec_kva": comp["elec_kva"],
        "main_bus_amps": main_bus_amps,
        "total_motor_kw": total_motor_kw,
        "motor_loads": motor_loads,
        # Pipe sizes
        "fire_pipe_dn": fire_pipe_dn,
        "oil_pipe_dn": oil_pipe_dn,
        "syngas_pipe_dn": syngas_pipe_dn,
        "water_pipe_dn": water_pipe_dn,
        "bitumen_pipe_dn": bitumen_pipe_dn,
        # Civil
        "plinth_mm": plinth_mm,
        "stack_height_m": stack_height,
        "conveyor_w_mm": conveyor_w,
        # Machinery
        "machinery_count": len(machinery),
        "machinery_lines": "\n".join(mach_lines),
        "active_zones": "\n".join(active_zones),
        "zone_count": len(tech["zones_active"]),
        "products": ", ".join(tech["products"]),
        "key_equipment": ", ".join(tech["key_equipment"]),
        # Safety
        "clearance_reactor": SAFETY_CLEARANCES.get("reactor_to_boundary_m", 15),
        "clearance_control": SAFETY_CLEARANCES.get("reactor_to_control_room_m", 30),
        "clearance_hydrant": SAFETY_CLEARANCES.get("fire_hydrant_spacing_m", 45),
        "clearance_tank": SAFETY_CLEARANCES.get("bio_oil_tank_to_boundary_m", 15),
        "clearance_eyewash": SAFETY_CLEARANCES.get("eyewash_to_hazard_max_m", 10),
        "road_width": SAFETY_CLEARANCES.get("road_width_internal_m", 6),
        "turning_radius": SAFETY_CLEARANCES.get("turning_radius_min_m", 9),
        "green_belt_m": SAFETY_CLEARANCES.get("green_belt_min_m", 5),
        # Civil construction specs
        "civil_specs": "",  # placeholder — built below
        # Meta
        "healed_inputs": healed,
    }

    # Add civil specs text block
    try:
        cs = get_civil_specs(cfg)
        civil_lines = []
        # Foundations
        rf = cs["reactor_foundation"]
        civil_lines.append(f"REACTOR FOUNDATION: {rf['type']}, {rf['size_m']}, depth {rf['depth_m']}m, {rf['thickness_mm']}mm thick, {rf['rebar']}, {rf['grade']}")
        sf = cs["shredder_foundation"]
        civil_lines.append(f"SHREDDER FOUNDATION: {sf['type']}, {sf['size_m']}, {sf['grade']}")
        tf = cs["tank_foundation"]
        civil_lines.append(f"TANK FOUNDATION: {tf['type']}, ring {tf['ring_width_mm']}mm, sand {tf['sand_thickness_mm']}mm")
        cf_data = cs["column_foundation"]
        civil_lines.append(f"COLUMN FOOTINGS: {cf_data['type']}, {cf_data['size_m']}, depth {cf_data['depth_m']}m, {cf_data['grade']}")
        # Buildings
        ph = cs["process_hall"]
        civil_lines.append(f"PROCESS HALL: {ph['type']}, {ph['length_m']}m × {ph['width_m']}m × {ph['eave_height_m']}m eave, {ph['column_grid_m']}m grid, {ph['floor']}")
        ob = cs["office_building"]
        civil_lines.append(f"OFFICE: {ob['type']}, {ob['length_m']}m × {ob['width_m']}m × {ob['height_m']}m, {ob['stories']} storey, {ob['floor']}")
        lb = cs["laboratory"]
        civil_lines.append(f"LAB: {lb['type']}, {lb['length_m']}m × {lb['width_m']}m × {lb['height_m']}m, {lb['floor']}")
        cr = cs["control_room"]
        civil_lines.append(f"CONTROL ROOM: {cr['type']}, {cr['length_m']}m × {cr['width_m']}m, wall {cr['wall_thickness_mm']}mm, {cr['is_standard']}")
        # Compound wall
        cw = cs["compound_wall"]
        civil_lines.append(f"COMPOUND WALL: {cw['total_length_m']}m perimeter, {cw['height_m']}m ht, {cw['material']}, {cw['foundation']}")
        # Roads
        rd = cs["internal_roads"]
        civil_lines.append(f"ROADS: {rd['width_m']}m wide, {rd['pavement']}, {rd['camber']} camber, total {rd['total_area_sqm']} sqm")
        # Drainage
        sd = cs["storm_drainage"]
        civil_lines.append(f"STORM DRAIN: {sd['type']}, gradient {sd['gradient']}, {sd['catch_pits']} catch pits, {sd['total_length_m']}m")
        # Bund
        bw = cs["bund_wall"]
        civil_lines.append(f"BUND WALL: {bw['height_m']}m × {bw['thickness_m']}m, {bw['material']}, {bw['capacity']}")
        # Underground
        eg = cs["earthing_grid"]
        civil_lines.append(f"EARTHING: {eg['conductor']}, {eg['electrodes']}, resistance {eg['resistance']}, {eg['standard']}")

        result["civil_specs"] = "\n".join(civil_lines)
    except Exception:
        result["civil_specs"] = "Civil specs not available"

    return result


# ══════════════════════════════════════════════════════════════════════
# BASE PROMPT TEMPLATES (5 drawing types)
# ══════════════════════════════════════════════════════════════════════
BASE_PROMPTS = {
    "site_layout": """Professional 2D top-view site layout plan for {capacity_tpd} TPD {technology_short} bio-bitumen plant.
Plot: {plot_l_m}m × {plot_w_m}m ({plot_area_sqm} sqm / {plot_acres} acres). State: {state}.

ZONES ({zone_count} active):
{active_zones}

KEY EQUIPMENT (with dimensions):
{machinery_lines}

SPECIFIC DIMENSIONS:
- Reactor: {reactor_qty}× vessel Ø{reactor_dia_m}m × {reactor_ht_m}m, wall {reactor_wall_mm}mm, insulation {reactor_insulation_mm}mm
- Dryer: rotary drum Ø{dryer_dia_m}m × {dryer_len_m}m, 3° inclination
- Bio-oil tanks: 2× Ø{bio_oil_tank_dia_m}m × {bio_oil_tank_ht_m}m inside dyke bund
- Blend tank: Ø{blend_tank_dia_m}m × {blend_tank_ht_m}m, insulated, 140°C
- Feed storage shed: {feed_shed_l_m}m × {feed_shed_w_m}m covered
- Office: {office_area_sqm} sqm, 2-storey RCC
- Lab: {lab_area_sqm} sqm, fume hood, AC
- Control room: {control_room_area_sqm} sqm, blast-resistant 250mm walls
- Stack/chimney: {stack_height_m}m height, Ø600mm
- Plinth height: {plinth_mm}mm above GL

PIPE SIZES (IS 2379 colour coded):
- Fire water: DN{fire_pipe_dn} RAL 3002 Red
- Bio-oil: DN{oil_pipe_dn} RAL 8025 Brown + Yellow band
- Syngas: DN{syngas_pipe_dn} RAL 1003 Yellow
- Process water: DN{water_pipe_dn} RAL 6018 Green
- Bitumen: DN{bitumen_pipe_dn} RAL 9005 Black + Yellow band
- Pipe rack height: 4.5m

SAFETY CLEARANCES (IS 14489 / NBC 2016):
- Reactor to boundary: {clearance_reactor}m MIN
- Reactor to control room: {clearance_control}m MIN
- Tanks to boundary: {clearance_tank}m MIN
- Internal roads: {road_width}m wide
- Fire hydrants: every {clearance_hydrant}m
- Eyewash: within {clearance_eyewash}m of hazard
- Turning radius: {turning_radius}m for fire tender
- Green belt: {green_belt_m}m around perimeter

ELECTRICAL: {elec_kva} kVA transformer, {total_motor_kw} kW total load, {main_bus_amps:.0f}A bus

PROCESS FLOW: {process_flow}

EQUIPMENT COLOURS (IS 2379): Reactors=RAL3002, Rotating=RAL1003, Static=RAL7035, Fire=RAL3002, Panels=RAL7032
Must include: North arrow, scale bar, 3 dimension chains, all equipment tag numbers, legend table.
Engineering drawing style, clean white background, labeled sections, professional quality.""",

    "3d_isometric": """Professional 3D isometric architectural render of {capacity_tpd} TPD {technology_short} bio-bitumen plant.
Bird-eye view on {plot_l_m}m × {plot_w_m}m plot ({plot_acres} acres). State: {state}.

EQUIPMENT WITH EXACT DIMENSIONS:
- Reactor: {reactor_qty}× cylindrical vessel Ø{reactor_dia_m}m × {reactor_ht_m}m on 1.5m skirt, insulated {reactor_insulation_mm}mm, RAL 3002 red
- Dryer: rotary drum Ø{dryer_dia_m}m × {dryer_len_m}m, 3° incline, RAL 1003 yellow
- Oil tanks: 2× Ø{bio_oil_tank_dia_m}m × {bio_oil_tank_ht_m}m inside 1m concrete dyke bund, RAL 3002 red
- Blend tank: Ø{blend_tank_dia_m}m × {blend_tank_ht_m}m, insulated, 140°C, RAL 1003 yellow
- Feed shed: {feed_shed_l_m}m × {feed_shed_w_m}m PEB covered shed with open sides
- Office: {office_area_sqm} sqm 2-storey RCC, RAL 9010 white
- Stack: {stack_height_m}m chimney Ø600mm with pollution control
- Plinth: {plinth_mm}mm above ground level

PIPING (colour coded IS 2379):
- Fire water DN{fire_pipe_dn} red, bio-oil DN{oil_pipe_dn} brown+yellow, syngas DN{syngas_pipe_dn} yellow
- Pipe rack 4.5m height connecting all process areas

TOTAL: {machinery_count} equipment items, {total_motor_kw} kW motor load, {elec_kva} kVA transformer

OUTPUT: {products}
Daily: Bio-oil {bio_oil_tpd}T + Bio-char {bio_char_tpd}T + Blend {blend_output_tpd}T

Show: weighbridge 18m at entry, {road_width}m RCC roads, control room {clearance_control}m from reactor, fire hydrant posts every {clearance_hydrant}m, parking area, {green_belt_m}m green belt, DG set room.
Photorealistic render, engineering visualization, labeled floating text boxes, 4k quality.""",

    "process_flow": """Professional Process Flow Diagram (PFD) for {capacity_tpd} TPD {technology_short} bio-bitumen plant.
IS 10234 standard symbols.

PROCESS: {process_flow}

MASS BALANCE (per day):
- Feed: {capacity_tpd} T/day agro-waste
- Bio-Oil: {bio_oil_tpd} T/day
- Bio-Char: {bio_char_tpd} T/day
- Blend Output: {blend_output_tpd} T/day

EQUIPMENT:
{machinery_lines}

Show: stream numbers S-01 to S-11, flow arrows, stream table (kg/hr, temperature, phase).
Colour: Water=Green, Oil=Brown, Gas=Yellow, Fire=Red, Bitumen=Black.
Engineering drawing style, clean background.""",

    "equipment_ga": """Equipment General Arrangement drawing for {capacity_tpd} TPD {technology_short} plant.
IS 696 standard.

MAIN EQUIPMENT:
{machinery_lines}

REACTOR DETAIL: {reactor_qty}× vessel Ø{reactor_dia_m}m × {reactor_ht_m}m
- Wall: 12mm AISI 310S, Insulation 100mm
- Nozzles: Feed 300mm, Vapour 200mm, Syngas 150mm, Char 250mm, Manway 600mm, PSV 100mm
- Foundation: RCC M25 mat 600mm thick

DRYER: Ø{dryer_dia_m}m × {dryer_len_m}m, 3.5 RPM, 3° inclination

Show: Front elevation, side elevation, plan view, section A-A through reactor.
All dimensions in mm, equipment tag numbers, foundation details.""",

    "fire_safety": """Fire Safety and Emergency Layout for {capacity_tpd} TPD {technology_short} plant.
Plot: {plot_l_m}m × {plot_w_m}m. NBC 2016 Part 4 + IS 3844.

HAZARD ZONES:
- Reactor area: HIGH (Class B petroleum), {clearance_reactor}m from boundary
- Tank farm: HIGH (flammable liquids), dyke bund mandatory
- Feed storage: MEDIUM (combustible solid)
- Control room: LOW (pressurized, {clearance_control}m from reactor)

FIRE PROTECTION:
- Underground ring main DN150, hydrants every {clearance_hydrant}m
- Fire water tank: 50-100 m³ with diesel pump
- Assembly points: 2 locations, 50m from hazard
- Emergency exits: min 2 per area, max 30m to nearest
- Eyewash within 10m of every hazard point

Show: hydrant positions FH-01 to FH-N, assembly points, exit routes (green arrows),
fire tender access road {road_width}m wide with 9m turning radius, wind sock.
Colour: Fire equipment=Red, Exits=Green, Assembly=Yellow.""",

    "civil_foundation": """Civil Foundation Plan for {capacity_tpd} TPD {technology_short} plant.
IS 456 (RCC), IS 1893 Zone {state} (Seismic), IS 800 (Steel). Plot: {plot_l_m}m × {plot_w_m}m.

FOUNDATION SCHEDULE:
{civil_specs}

COLUMN LAYOUT:
- Grid spacing: 6.0m × 6.0m standard bay
- Grid lines: A, B, C... (horizontal) × 1, 2, 3... (vertical)
- Column size: 230mm × 230mm RCC for single storey, 300×300mm for 2-storey
- Plinth beam: 230mm × 300mm RCC M20 at plinth level (+{plinth_mm}mm)

SECTION REQUIREMENTS:
- Section A-A: Through reactor foundation (show mat, rebar, anchor bolts)
- Section B-B: Through process hall (show footing, column, truss/beam, roof)
- Section C-C: Through compound wall (show strip footing, brick, coping, barbed wire)

LEVELS (show on drawing):
- Natural Ground Level (NGL): ±0.000
- Plinth Level: +{plinth_mm}mm
- Floor Finish Level (FFL): +{plinth_mm}mm + 50mm
- Tie Beam Level: +300mm
- Lintel Level: +2100mm
- Roof Level: varies per building

Must include: All footing dimensions, rebar details, anchor bolt patterns, equipment tag numbers at each foundation.
Engineering structural drawing, IS 456 notation, clean background.""",

    "civil_building": """Building Plans + Sections for {capacity_tpd} TPD {technology_short} plant.
For Municipal Building Permission + Factory License. IS 456, NBC 2016.

FLOOR PLANS REQUIRED:
1. Process Hall: {feed_shed_l_m}m × {feed_shed_w_m}m, eave height {capacity_tpd}m-scaled
   - Show: equipment foundations, floor drains, roller shutter doors, fire exits
2. Office (Ground Floor): Reception 4×3m, Conference 5×4m, Toilets M/F, Staircase
3. Office (First Floor): GM cabin 4×3m, Accounts, HR, Open office {office_area_sqm}sqm
4. Laboratory: 12m × 9m, fume hood, instrument room 4×3m, wash area, benches
5. Control Room: 8m × 6m, blast walls {control_room_area_sqm}sqm, raised floor
6. Canteen: seating area, kitchen, wash area, IS 7250
7. Toilet Block: M/F separate, disabled WC, IS 5965, Factories Act

BUILDING SECTIONS:
- Section X-X through Office: Show NGL, plinth, GF slab, FF slab, parapet, stair
- Section Y-Y through Process Hall: Show foundation, column, truss, ridge, gutter

ELEVATIONS:
- Front Elevation: Office building with signage, entrance, windows
- Side Elevation: Process hall showing roof slope, louvers, doors

DOOR/WINDOW SCHEDULE:
- D1: Roller shutter 5m×5m (process hall), D2: MS door 1.2m×2.1m, D3: Fire exit 0.9m×2.1m
- W1: Aluminium sliding 1.5m×1.2m, W2: Fixed glass 1.2m×1.2m, W3: Ventilator 0.6m×0.6m

Must include: room names, areas in sqm, door/window marks, floor finish schedule, staircase detail.
Architectural drawing style, IS 962 notation.""",

    "civil_drainage": """Drainage + ETP Layout for {capacity_tpd} TPD {technology_short} plant.
For PCB (Pollution Control Board) CTE/CTO application. CPCB norms, IS 10500.

STORM WATER DRAINAGE:
- U-drain 600mm × 450mm RCC along all internal roads
- Gradient: 1:100 minimum towards collection sump
- Catch pits: 600×600×600mm at all road junctions with CI grating
- Total drain length: approx {plot_l_m}×2 + {plot_w_m}×2 = running metres
- Outfall: to rainwater harvesting pit (50 KL underground)

PROCESS DRAINAGE (separate system):
- Acid-resistant channel 300×300mm in process area
- Gradient: 1:80 towards ETP collection tank
- Floor drains: 150mm dia every 6m in process area
- Oil trap: before ETP entry

ETP LAYOUT (show as separate area):
- Collection tank → Equalization tank → Aeration tank → Clarifier → Treated water tank
- Capacity: {capacity_tpd} KLD approximately
- Outlet quality: IS 10500 for reuse, CPCB trade effluent norms
- Sludge drying bed: 6m × 4m

BUND WALL (around tank farm):
- Height: 1.0m, thickness 300mm RCC M20
- Capacity: 110% of largest tank
- Drain valve: 150mm gate valve, normally closed
- Waterproofing: bituminous coating inside

GREEN BELT:
- 5m wide around entire perimeter
- Native trees at 3m spacing, drip irrigation
- Total area: {plot_l_m}×2 + {plot_w_m}×2 multiplied by 5m width

Must include: drain routes with gradient arrows, manhole positions, ETP equipment arrangement, bund outline.
Environmental engineering drawing, clean layout.""",

    "civil_compound": """Compound Wall + Road Section Details for {capacity_tpd} TPD plant.
For Contractor Execution. IS 1596, IS 15658, NBC 2016.

COMPOUND WALL SECTION:
- Foundation: RCC strip footing 600mm wide × 600mm deep, M15 PCC 75mm
- Plinth: 230mm brick, 2 courses below GL
- Wall: 230mm brick masonry, cement mortar 1:6, total height 2.4m above GL
- Pillars: RCC 230×230mm @ 3m c/c, M20, 4-12mm bars + 8mm stirrups @ 150mm
- Coping: RCC coping 50mm with drip mould, weathering slope
- Plaster: 12mm cement plaster both sides, exterior weather coat paint
- Barbed wire: 3 rows GI wire on MS angle brackets 45°
- Total perimeter: {plot_l_m}×2 + {plot_w_m}×2 metres

GATE DETAILS:
- Main gate: MS fabricated sliding, 6m opening, motor operated, RAL 5012
- Emergency gate: 4m opening, swing type, manual + remote
- Guard booth: 3m × 3m RCC, 3.2m height

ROAD CROSS-SECTION (to scale):
Layer 1: Compacted subgrade 300mm
Layer 2: GSB (Granular Sub-Base) 200mm
Layer 3: WBM (Wet Mix Macadam) 150mm
Layer 4: RCC pavement M25, 200mm thick
Surface: Broomed finish with joints @ 3m
Kerb: RCC precast 150mm × 300mm, IS 15658
Camber: 2% cross-slope
Total road width: 6m carriageway + 0.15m kerb each side
Turning area: {turning_radius}m radius at dead ends

PARKING AREA:
- Staff parking: {capacity_tpd} car bays × 2.5m × 5m
- Truck parking: 4-6 bays × 3.5m × 12m (scale with capacity)

Must include: wall section 1:10 scale, road section 1:20 scale, gate elevation, turning circle.
Civil construction detail drawing style.""",
}


# ══════════════════════════════════════════════════════════════════════
# MASTER FUNCTION: Generate prompt for ANY combination
# ══════════════════════════════════════════════════════════════════════
def generate_combination_prompt(cfg, drawing_type="site_layout"):
    """Generate a complete drawing prompt for any combination of inputs.
    Uses BASE_PROMPT + VARIABLE_BLOCK — no API call needed.

    Args:
        cfg: Master config dict (capacity, process_id, state, etc.)
        drawing_type: One of DRAWING_TYPES keys

    Returns:
        dict with: prompt, variables, healed_inputs, drawing_type, combo_id
    """
    variables = build_variable_block(cfg)
    base = BASE_PROMPTS.get(drawing_type, BASE_PROMPTS["site_layout"])

    # Fill template with variables
    prompt = base.format(**variables)

    # Generate combo ID for caching
    combo_id = f"T{cfg.get('process_id', 1)}_C{int(cfg.get('capacity_tpd', 20))}_S{cfg.get('state', 'MH')[:2]}_{drawing_type}"

    return {
        "prompt": prompt,
        "variables": variables,
        "healed_inputs": variables.get("healed_inputs", []),
        "drawing_type": drawing_type,
        "drawing_label": DRAWING_TYPES.get(drawing_type, drawing_type),
        "combo_id": combo_id,
        "technology": variables["technology"],
        "capacity": variables["capacity_tpd"],
        "char_count": len(prompt),
    }


def get_all_combinations_count():
    """Return total number of possible combinations."""
    return len(TECHNOLOGIES) * len(CAPACITIES) * 9 * len(DRAWING_TYPES)  # 3 × 10 × 9 × 5 = 1350


def generate_all_prompts_for_config(cfg):
    """Generate ALL 5 drawing prompts for a single configuration."""
    results = {}
    for dt in DRAWING_TYPES:
        results[dt] = generate_combination_prompt(cfg, dt)
    return results
