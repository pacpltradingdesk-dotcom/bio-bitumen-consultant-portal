"""
Drawing Prompt Generator — Deterministic AI Drawing Prompts
=============================================================
Generates complete, anti-randomness drawing prompts for any AI.
Every dimension from COMPUTED values. Nothing invented.
Based on IS 696, IS 2379, IS 11065, IS 14489, NBC 2016.
"""
from engines.plant_engineering import (
    compute_all, get_machinery_list, SAFETY_CLEARANCES,
    PIPE_COLOURS, EQUIPMENT_COLOURS, STANDARDS
)


# ══════════════════════════════════════════════════════════════════════
# ANTI-RANDOMNESS PRIMER (prepended to every drawing prompt)
# ══════════════════════════════════════════════════════════════════════
DRAWING_SYSTEM_PRIMER = """You are a professional Indian industrial draughtsman.
Standards you follow: IS 696, IS 2379, IS 11065, IS 14489, NBC 2016.
You NEVER invent or estimate any dimension.
Every number must come from the DATA provided below.
If any dimension is not in the data: write [VALUE NEEDED: fieldname]
and stop. Do not guess. Do not use a "typical" value."""

ANTI_RANDOMNESS_CLAUSE = """
=== ANTI-RANDOMNESS CLAUSE ===
Every dimension shown must match data above exactly.
Do not resize equipment for visual balance.
Do not move equipment to "look better."
Do not add equipment not listed.
Do not omit any mandatory element.
List all dimensions used and confirm source."""


# ══════════════════════════════════════════════════════════════════════
# COLOUR CODE TABLE (for prompt insertion)
# ══════════════════════════════════════════════════════════════════════
def _colour_table():
    """Generate colour code reference for drawing prompt."""
    lines = ["PIPE COLOURS (IS 2379):"]
    for service, data in PIPE_COLOURS.items():
        band = f" + {data['band']} band" if data['band'] != 'none' else ""
        lines.append(f"  {service.replace('_',' ').title()}: {data['ral']} {data['base']}{band}")

    lines.append("\nEQUIPMENT COLOURS:")
    for equip, colour in EQUIPMENT_COLOURS.items():
        lines.append(f"  {equip.replace('_',' ').title()}: {colour}")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
# TITLE BLOCK (IS 11065)
# ══════════════════════════════════════════════════════════════════════
def _title_block(cfg, drawing_type, drawing_no):
    """Generate title block fields for prompt."""
    return (
        f"Company: PPS Anantams Corporation Pvt Ltd\n"
        f"Project: {cfg.get('project_name', 'Bio-Bitumen Plant')}\n"
        f"Client: {cfg.get('client_name', '')}\n"
        f"Drawing: {drawing_type}\n"
        f"Drawing No: {drawing_no} Rev R0\n"
        f"Scale: {cfg.get('drawing_scale', '1:100')}\n"
        f"Paper: {cfg.get('paper_size', 'A1')}\n"
        f"Date: {cfg.get('report_date', '2026')}\n"
        f"Prepared: {cfg.get('prepared_by', '')}\n"
        f"Location: {cfg.get('location', '')}, {cfg.get('state', '')}"
    )


# ══════════════════════════════════════════════════════════════════════
# GENERATE DRAWING PROMPT
# ══════════════════════════════════════════════════════════════════════
DRAWING_TYPES = {
    "SITE_LAYOUT": "Site Layout Plan (all 15 zones)",
    "EQUIPMENT_GA": "Equipment General Arrangement",
    "PFD": "Process Flow Diagram",
    "ELECTRICAL_SLD": "Electrical Single Line Diagram",
    "FIRE_LAYOUT": "Fire Fighting & Emergency Layout",
    "CIVIL_PLAN": "Civil & Foundation Plan",
}


def generate_drawing_prompt(cfg, drawing_type="SITE_LAYOUT"):
    """Generate a complete, deterministic drawing prompt from cfg.
    Every dimension computed — nothing random or estimated.

    Args:
        cfg: Master config from state_manager
        drawing_type: One of DRAWING_TYPES keys

    Returns:
        Complete prompt string ready to paste into any AI
    """
    comp = compute_all(cfg)
    machinery = get_machinery_list(cfg, comp)
    tpd = cfg.get("capacity_tpd", 20)
    state = cfg.get("state", "Maharashtra")
    drawing_no = f"BB-{drawing_type[:3]}-{int(tpd):02d}-001"

    # Equipment table
    equip_lines = []
    for m in machinery:
        equip_lines.append(f"  {m['tag']}: {m['name']} (Qty: {m['qty']}) — {m['dims']}")

    # Safety clearances
    safety_lines = []
    for key, val in SAFETY_CLEARANCES.items():
        label = key.replace("_", " ").replace(" m", "").title()
        safety_lines.append(f"  {label}: {val}m")

    # Build prompt based on type
    if drawing_type == "SITE_LAYOUT":
        specific = f"""
=== ZONE LAYOUT ===
Plot: {comp['plot_l_m']}m x {comp['plot_w_m']}m ({comp['plot_area_sqm']} sqm)
North-East: Zone B (RM Receiving) — {comp['feed_shed_l_m']}m x {comp['feed_shed_w_m']}m shed
Central: Zone D (Reactor) — HAZARDOUS AREA Zone 1 — {comp['reactor_qty']}x reactors
         Reactor: {comp['reactor_dia_m']}m dia x {comp['reactor_ht_m']}m ht each
East: Zone G (Tank Farm) — Bio-oil tanks {comp['bio_oil_tank_dia_m']}m dia with DYKE BUND
West: Zone I (Electrical) + Zone CR (Control Room, 30m from reactor)
South: Main gate + weighbridge + guard cabin
Perimeter: 6m fire access road + 5m green belt

Show: All 15 zone boundaries (A-O), zone labels, equipment footprints,
internal roads 6m wide, turning radius 9m, parking area, green belt hatched.
"""

    elif drawing_type == "PFD":
        specific = f"""
=== MASS BALANCE (per day) ===
Feed input: {tpd} T/day ({comp['feed_per_hour_kg']:.0f} kg/hr)
After drying: {comp['dry_feed_kg_hr']:.0f} kg/hr (moisture removed: {comp['moisture_evap_kg_hr']:.0f} kg/hr)
Bio-oil output: {comp['bio_oil_tpd']:.2f} T/day
Bio-char output: {comp['bio_char_tpd']:.2f} T/day
Syngas output: {comp['syngas_tpd']:.2f} T/day (captive fuel)
Loss: {comp['loss_tpd']:.2f} T/day

Bio-oil for blend: {comp['bio_oil_for_blend']:.2f} T/day
Conv bitumen needed: {comp['conv_bitumen_tpd']:.2f} T/day
Blend output: {comp['blend_output_tpd']:.2f} T/day

Show: Standard PFD symbols per IS 10234, stream numbers S-01 to S-11,
flow arrows on all lines, stream table with kg/hr + temperature + phase.
"""

    elif drawing_type == "ELECTRICAL_SLD":
        specific = f"""
=== ELECTRICAL DATA ===
Incoming: 11kV from grid
Transformer: {comp['elec_kva']} kVA, 11kV/415V, ONAN, Dyn11
Bus rating: {comp['main_bus_amps']:.0f}A at 415V 3Ph 50Hz
DG backup: {max(50, int(tpd*5))} kVA

Motor loads:
{chr(10).join(f'  {m["tag"]}: {m["name"]} — {m["motor_kw"]} kW' for m in machinery if m['motor_kw'] > 0)}

Total connected load: {sum(m['motor_kw']*m['qty'] for m in machinery)} kW

Show: Standard SLD symbols per IS 732, incomer ACB, bus section,
each motor feeder with MCB/MCCB + OL relay, DG with AMF panel,
PF correction panel, earthing bus, UPS for SCADA.
"""

    elif drawing_type == "FIRE_LAYOUT":
        specific = f"""
=== FIRE HAZARD ZONES ===
Tank farm (bio-oil): Class B petroleum — HIGH HAZARD
Reactor area: Class B vapour — HIGH HAZARD (15m clearance to boundary)
Feed storage: Solid combustible — MEDIUM HAZARD
Biochar storage: Combustible dust — MEDIUM HAZARD
Control room/offices: LOW HAZARD

Fire water tank: {50 if tpd<=30 else 100} m3
Ring main: DN150, looped underground
Hydrant spacing: MAX 45m
Pump: 18 m3/hr at 0.7 barg + jockey pump

Show: All hydrant positions (FH-01 to FH-N), assembly points (2 locations,
50m from hazard), emergency exits, fire tender access road (6m wide),
wind sock position, first aid centre, eyewash stations within 10m of hazard.
"""

    elif drawing_type == "CIVIL_PLAN":
        specific = f"""
=== CIVIL DATA ===
Plot: {comp['plot_l_m']}m x {comp['plot_w_m']}m
Seismic zone: {cfg.get('seismic_zone', 'III')} (IS 1893)
Build type: {cfg.get('build_type', 'PEB').upper()}
Plinth: {comp['plinth_mm']}mm above GL
Column grid: 6m c/c standard bay
Foundation depth: {'2.0m' if cfg.get('flood_prone') else '1.5m'} minimum

Buildings:
  Process hall: {int(tpd*80)} sqm ({cfg.get('build_type','PEB').upper()})
  Office: 200 sqm (RCC 2-storey)
  Lab: 108 sqm (RCC)
  Control room: 48 sqm (blast-resistant 250mm walls)

Show: Foundation plan, column positions, plinth levels, floor drain gradients,
compound wall perimeter, internal road sections, storm drain layout.
"""
    else:
        specific = f"Drawing type: {drawing_type}\nCapacity: {tpd} TPD\n"

    # Assemble complete prompt
    prompt = f"""{DRAWING_SYSTEM_PRIMER}

DRAWING: {DRAWING_TYPES.get(drawing_type, drawing_type)}
PROJECT: {cfg.get('project_name', 'Bio-Bitumen Plant')}
CAPACITY: {tpd} TPD feed
LOCATION: {cfg.get('location', '')}, {state}

=== TITLE BLOCK (IS 11065) ===
{_title_block(cfg, DRAWING_TYPES.get(drawing_type, drawing_type), drawing_no)}

{specific}

=== EQUIPMENT LIST ({len(machinery)} items) ===
{chr(10).join(equip_lines)}

=== SAFETY CLEARANCES (IS 14489 / NBC 2016) ===
{chr(10).join(safety_lines)}

=== COLOUR CODE (IS 2379) ===
{_colour_table()}

=== MANDATORY ELEMENTS ===
- Title block (IS 11065) — bottom right
- North arrow — top right of plan views
- Scale bar — below title block
- Dimension chains — minimum 3 (outer total / middle zones / inner items)
- Grid lines: A-A, B-B etc.
- Legend table for all symbols
- All equipment TAG numbers visible
- All safety signs (IS 9457)

{ANTI_RANDOMNESS_CLAUSE}
"""
    return prompt


def get_all_drawing_types():
    """Return available drawing types."""
    return DRAWING_TYPES
