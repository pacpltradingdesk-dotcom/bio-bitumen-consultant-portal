"""
Drawing Master — Complete Drawing Registry for Industrial Plant Projects
=========================================================================
Maps every drawing type to: who needs it, what it must show, AI prompt,
and whether AI can generate it or needs a human CAD engineer.
"""

# ══════════════════════════════════════════════════════════════════════
# COMPLETE DRAWING REGISTRY — Every drawing for every stakeholder
# ══════════════════════════════════════════════════════════════════════
DRAWING_REGISTRY = [
    # ── FOR BANKS & INVESTORS ────────────────────────────────────
    {
        "id": "3d_isometric",
        "name": "3D Isometric Plant Layout",
        "category": "Investor & Bank",
        "for_whom": "Bank Manager, Credit Committee, Investors",
        "purpose": "Make the plant look professional, premium, and well-planned for funding approval",
        "what_it_shows": "Bird's eye 3D view of entire plant — all equipment, roads, tanks, buildings",
        "ai_capable": True,
        "ai_prompt": (
            "A highly professional, ultra-realistic 3D isometric architectural rendering of a "
            "{capacity} TPD Bio-Bitumen Production Plant on a {length}m x {width}m plot. "
            "Show a clean, modern 'mini-refinery' layout. Include biomass receiving area with "
            "hopper and conveyor, central pyrolysis reactor under industrial steel shed, and "
            "tank farm with storage tanks surrounded by concrete safety bund wall. "
            "Style: High-end investor pitch deck visual, bright daylight, clean concrete floors, "
            "photorealistic, 8k resolution, cinematic lighting, corporate industrial aesthetic."
        ),
        "required_for": ["DPR", "Bank Proposal", "Investor Pitch"],
    },
    {
        "id": "block_flow",
        "name": "Block Flow Diagram (BFD)",
        "category": "Investor & Bank",
        "for_whom": "Bank Manager, Non-technical investors",
        "purpose": "Simple box-and-arrow showing how biomass becomes bitumen — easy to understand",
        "what_it_shows": "Input → Process steps → Output with arrows and simple boxes",
        "ai_capable": True,
        "ai_prompt": (
            "A clean, professional Block Flow Diagram for {capacity} TPD bio-bitumen plant. "
            "Simple boxes connected by arrows: Biomass Input → Shredding → Drying → Pyrolysis → "
            "Bio-Oil → Blending with VG-30 → Bio-Modified Bitumen → Quality Testing → Dispatch. "
            "Show byproducts: Biochar (30%) and Syngas (25%). Clean white background, corporate "
            "style, blue and grey colors, professional engineering presentation quality."
        ),
        "required_for": ["DPR", "Bank Proposal", "Executive Summary"],
    },
    {
        "id": "process_flow",
        "name": "Process Flow Diagram (PFD)",
        "category": "Investor & Bank",
        "for_whom": "Bank Technical Appraiser, Lead Engineer",
        "purpose": "Shows equipment, flow rates, temperatures — proves the process works",
        "what_it_shows": "Main equipment with temperatures, pressures, flow rates, material balance",
        "ai_capable": True,
        "ai_prompt": (
            "A clean, technical isometric schematic drawing of a {capacity} TPD bio-bitumen "
            "processing line. Vector illustration style, clean lines, white background, muted "
            "industrial colors. Show sequence: Biomass Hopper → Belt Conveyor → Shredder → "
            "Rotary Dryer → Pyrolysis Reactor (450-550°C) → Condenser → Bio-Oil Storage → "
            "High Shear Mixer → Bitumen Storage Tank. Show temperatures at each stage. "
            "Engineering textbook style, minimal background."
        ),
        "required_for": ["DPR", "Technical Report"],
    },

    # ── FOR GOVERNMENT & REGULATORY ─────────────────────────────
    {
        "id": "plot_plan_gpcb",
        "name": "Plot Plan with Environmental Layout",
        "category": "Government & Regulatory",
        "for_whom": "Gujarat PCB (GPCB), State Pollution Control Board",
        "purpose": "CTE/CTO application — must show pollution control measures and green belt",
        "what_it_shows": "Chimney stack (min 20m), gas scrubber, ETP, biochar storage, green belt (33% of plot)",
        "ai_capable": True,
        "ai_prompt": (
            "Top-down architectural plot plan for {capacity} TPD bio-bitumen plant on "
            "{length}m x {width}m plot. Show: Chimney Stack location (20m height marked), "
            "Gas Scrubber, Bag Filter, Biochar storage area, Green Belt (33% of total area "
            "shaded in green), boundary wall, entry gate, parking, internal roads (6m wide). "
            "Include North arrow and scale bar. Clean architectural blueprint style."
        ),
        "required_for": ["CTE Application", "CTO Application", "Environmental Clearance"],
    },
    {
        "id": "fire_safety",
        "name": "Equipment Layout & Fire Safety Plan",
        "category": "Government & Regulatory",
        "for_whom": "Factory Inspector (DISH), Fire Department",
        "purpose": "Factory license and Fire NOC application — must show safety compliance",
        "what_it_shows": "Equipment spacing (2m clearance), emergency exits, fire extinguishers, safe zones",
        "ai_capable": True,
        "ai_prompt": (
            "Fire safety and equipment layout plan for {capacity} TPD bio-bitumen plant. "
            "Show: equipment positions with 2m clearance between machines, emergency exit "
            "routes (green arrows), fire extinguisher positions (red markers), fire hydrant "
            "ring main, assembly point, 5m safety zone around pyrolysis reactor, first aid "
            "room. Red and grey color scheme on white background. Technical safety drawing."
        ),
        "required_for": ["Factory License", "Fire NOC"],
    },
    {
        "id": "tank_farm_peso",
        "name": "Tank Farm Layout (PESO Compliance)",
        "category": "Government & Regulatory",
        "for_whom": "PESO (Petroleum and Explosives Safety Organization)",
        "purpose": "PESO license for bitumen/oil storage — must show OISD-117 spacing",
        "what_it_shows": "Tank positions, bund wall height (110% capacity), fire spacing (4m min), distance from heat sources",
        "ai_capable": True,
        "ai_prompt": (
            "Tank farm layout for {capacity} TPD bio-bitumen plant per OISD-117 standards. "
            "Show: circular storage tanks with dimensions, concrete bund wall enclosure "
            "(110% tank capacity), 4m minimum fire spacing between tanks, pipe manifold, "
            "pump house, dyke drain valve, foam monitor positions. Include distance markers "
            "from Thermic Fluid Heater (fire source). Technical engineering drawing style."
        ),
        "required_for": ["PESO License Application"],
    },

    # ── FOR ENGINEERS (CONCEPT STAGE) ───────────────────────────
    {
        "id": "pid_concept",
        "name": "P&ID Concept (Piping & Instrumentation)",
        "category": "Engineering",
        "for_whom": "Process/Chemical Engineer",
        "purpose": "Master map showing every pipe, valve, and instrument — concept stage for AI",
        "what_it_shows": "Equipment with piping connections, valve symbols, instrument tags",
        "ai_capable": True,
        "ai_prompt": (
            "Conceptual Piping and Instrumentation Diagram (P&ID) for {capacity} TPD "
            "bio-bitumen plant. Show ISO standard symbols for: pumps, vessels, heat exchangers, "
            "control valves, temperature indicators, pressure gauges, level indicators. "
            "Connect Reactor R-101 → Condenser HE-101 → Storage T-201 → Mixer M-301 → "
            "Product Tank T-301. Include instrument bubble tags. Clean P&ID style, black "
            "lines on white background."
        ),
        "required_for": ["Detailed Engineering", "Contractor Tender"],
        "note": "AI generates CONCEPT only — final P&ID needs human CAD engineer",
    },
    {
        "id": "electrical_sld",
        "name": "Electrical Single Line Diagram (SLD)",
        "category": "Engineering",
        "for_whom": "Electrical Engineer, State DISCOM",
        "purpose": "Shows power distribution from grid to every motor — needed for HT connection",
        "what_it_shows": "HT incoming, transformer, LT panels, MCC, VFDs, motor connections, DG set, UPS, earthing",
        "ai_capable": True,
        "ai_prompt": (
            "Professional Electrical Single Line Diagram (SLD) for {capacity} TPD "
            "bio-bitumen plant. Show: 11kV HT incoming line → Transformer (500 kVA) → "
            "LT Bus Bar → Main Panel → MCC (Motor Control Center) → Individual motor "
            "feeders for Shredder (75HP), Dryer (40HP), Conveyor (10HP). Show DG Set "
            "(100 kVA) with ATS changeover, UPS for PLC, earthing pit. IEC standard "
            "symbols. Technical blueprint style."
        ),
        "required_for": ["HT Connection Application", "Detailed Engineering"],
        "note": "AI generates CONCEPT — final SLD needs licensed electrical engineer",
    },

    # ── FOR CONTRACTORS (CONCEPT ONLY — AI LIMITATIONS) ─────────
    {
        "id": "civil_foundation",
        "name": "Civil Foundation Plan (Concept)",
        "category": "Construction",
        "for_whom": "Civil Contractor",
        "purpose": "Shows where to dig, concrete depth, equipment loads — CONCEPT for discussion",
        "what_it_shows": "Equipment foundation positions, column footings, floor slab, bund walls, drainage",
        "ai_capable": True,
        "ai_prompt": (
            "Top-down civil foundation layout for {capacity} TPD bio-bitumen plant on "
            "{length}m x {width}m plot. Architectural blueprint style, dark blue background "
            "with white and cyan line-art. Show: main equipment foundation footprints with "
            "dimensions, column footings grid, floor slab outline, bund wall for tanks, "
            "6m access roads, 2m safety spacing between equipment blocks, drainage slopes "
            "toward oil trap. Engineering sketch style."
        ),
        "required_for": ["Construction Planning"],
        "note": "CONCEPT ONLY — actual foundation needs structural engineer with soil test data",
    },
    {
        "id": "piping_layout",
        "name": "Piping Layout (Concept)",
        "category": "Construction",
        "for_whom": "Piping/Mechanical Contractor",
        "purpose": "Shows pipe routing, valve positions, rack heights — CONCEPT for quoting",
        "what_it_shows": "Main pipe routes, valve stations, pipe rack elevation (4.5m), color-coded by service",
        "ai_capable": True,
        "ai_prompt": (
            "3D piping layout concept for {capacity} TPD bio-bitumen plant. Show elevated "
            "pipe rack at 4.5m height with color-coded pipes: process (blue), steam (red), "
            "water (green), air (yellow). Show valve stations, pump connections, and "
            "instrument tapping points. Include reactor vessel, condenser, and storage tanks "
            "with piping connections. Professional engineering visualization style."
        ),
        "required_for": ["Contractor Quotation", "Construction Planning"],
        "note": "CONCEPT ONLY — actual isometrics need piping engineer with stress analysis",
    },
    {
        "id": "cable_routing",
        "name": "Cable Routing & Lighting Plan",
        "category": "Construction",
        "for_whom": "Electrical Contractor",
        "purpose": "Shows cable tray paths, lighting positions — needed for wiring estimation",
        "what_it_shows": "Cable tray routes from MCC to each motor, lighting positions, earthing grid",
        "ai_capable": True,
        "ai_prompt": (
            "Electrical cable routing layout for {capacity} TPD bio-bitumen plant. "
            "Top-down view showing: cable tray routes from electrical room to each motor "
            "(dashed lines), overhead lighting positions (circle symbols), earthing grid "
            "with earth pits (triangle symbols), lightning arrester location. "
            "Technical drawing style, clean lines."
        ),
        "required_for": ["Electrical Estimation", "Construction Planning"],
        "note": "CONCEPT ONLY — actual cable sizing needs electrical engineer",
    },

    # ── MUNICIPAL & BUILDING (NEW) ──────────────────────────────
    {
        "id": "architectural_elevation",
        "name": "Architectural Elevations & Building Drawings",
        "category": "Municipal & Building",
        "for_whom": "Municipal Corporation (VMC), Town Planning Department, Civil Architect",
        "purpose": "Building permit — admin office, factory shed height, parking, restrooms",
        "what_it_shows": "Building elevations (front/side/rear), shed height, office layout, parking, restrooms, gate",
        "ai_capable": True,
        "ai_prompt": (
            "Architectural elevation drawings for {capacity} TPD bio-bitumen plant facility. "
            "Show front elevation of: main factory shed (PEB structure, 10m height), admin office "
            "(2-storey, modern industrial), security gatehouse, weighbridge cabin. Include parking "
            "for 10 vehicles, worker restrooms, canteen. Clean architectural rendering style, "
            "professional building submission quality with height dimensions marked."
        ),
        "required_for": ["Building Permit", "Municipal Approval"],
    },

    # ── FIRE & SAFETY (NEW) ─────────────────────────────────────
    {
        "id": "fire_hydrant_system",
        "name": "Fire Hydrant & Emergency Response Layout",
        "category": "Fire & Safety",
        "for_whom": "Gujarat Fire Services, Fire NOC Authority, Fire Safety Contractor",
        "purpose": "Fire NOC application — shows complete fire protection system",
        "what_it_shows": "Underground fire water tank, fire ring main piping, hydrant positions, foam monitors, "
                         "emergency exits, evacuation routes, assembly point, fire alarm panel location",
        "ai_capable": True,
        "ai_prompt": (
            "Professional fire hydrant and emergency response layout for {capacity} TPD "
            "bio-bitumen plant on {length}m x {width}m plot. Show: underground fire water "
            "tank (50,000L), red fire ring main pipeline around entire plant, fire hydrant "
            "positions (every 30m), foam monitors near bitumen tank farm, emergency exit "
            "routes (green arrows), assembly point location, fire alarm panel in security "
            "cabin, emergency vehicle access road (6m wide). Fire safety drawing style."
        ),
        "required_for": ["Fire NOC", "Factory License"],
    },

    # ── FABRICATION (NEW) ───────────────────────────────────────
    {
        "id": "reactor_fabrication",
        "name": "Reactor Fabrication / Shop Drawing",
        "category": "Fabrication",
        "for_whom": "Heavy Engineering Workshop, Reactor Fabricator",
        "purpose": "Tells welder exact steel grade, plate thickness, nozzle angles for reactor manufacturing",
        "what_it_shows": "Steel plate thickness (mm), welding specifications, nozzle positions and sizes, "
                         "flange ratings, internal baffles, thermocouple ports, pressure rating",
        "ai_capable": False,
        "ai_prompt": "",
        "required_for": ["Equipment Procurement", "Manufacturing"],
        "note": "REQUIRES HUMAN: Mechanical engineer with ASME/IS standards for pressure vessel design",
    },
    {
        "id": "tank_fabrication",
        "name": "Storage Tank Fabrication Drawing",
        "category": "Fabrication",
        "for_whom": "Tank Fabricator, Welding Inspector",
        "purpose": "Manufacturing drawing for bitumen/bio-oil storage tanks",
        "what_it_shows": "Tank diameter, height, plate thickness, nozzle schedule, manhole position, "
                         "heating coil details, insulation specs, vent pipe, level gauge connection",
        "ai_capable": False,
        "ai_prompt": "",
        "required_for": ["Equipment Procurement"],
        "note": "REQUIRES HUMAN: Mechanical engineer with API-650 / IS-803 tank design standards",
    },

    # ── UTILITY (NEW) ───────────────────────────────────────────
    {
        "id": "hvac_layout",
        "name": "HVAC Layout (Control Room & Ventilation)",
        "category": "Utilities",
        "for_whom": "HVAC Contractor, Plant Operations Team",
        "purpose": "Air conditioning for control room, exhaust ventilation for gas areas",
        "what_it_shows": "AC unit positions for PLC room, industrial exhaust fans near scrubber/condenser, "
                         "fresh air intake positions, duct routing, temperature zones",
        "ai_capable": True,
        "ai_prompt": (
            "HVAC and ventilation layout for {capacity} TPD bio-bitumen plant. Show: "
            "split AC units in PLC control room and admin office, industrial exhaust fans "
            "near gas scrubber and condenser area, fresh air intake louvers, duct routing "
            "paths on ceiling, temperature zone marking (hot zone near reactor in red, "
            "cool zone in blue). Clean technical layout style."
        ),
        "required_for": ["MEP Design", "Construction Planning"],
    },
    {
        "id": "drainage_network",
        "name": "Underground Drainage & Effluent Network",
        "category": "Utilities",
        "for_whom": "Civil Plumber, GPCB (Pollution Control Board)",
        "purpose": "Two separate drain systems: rainwater + oily-water sewer to oil trap",
        "what_it_shows": "Stormwater drain (to boundary), oily-water drain (to oil interceptor), "
                         "oil trap/interceptor location, drain slopes, manhole positions, ETP connection",
        "ai_capable": True,
        "ai_prompt": (
            "Underground drainage network layout for {capacity} TPD bio-bitumen plant on "
            "{length}m x {width}m plot. Show TWO separate drainage systems: (1) Stormwater "
            "drain (blue dashed lines) sloping to boundary outlet, (2) Oily-water sewer "
            "(red dashed lines) from tank farm and process area to oil interceptor pit then "
            "to sealed collection tank. Show manhole positions, drain slopes (1:100), "
            "oil trap detail. Technical drainage drawing style."
        ),
        "required_for": ["CTE Application", "Environmental Clearance"],
    },

    # ── OPERATIONS (NEW) ────────────────────────────────────────
    {
        "id": "as_built",
        "name": "As-Built Drawings (Post-Construction)",
        "category": "Operations",
        "for_whom": "Plant Manager, Maintenance Engineer, Safety Auditors",
        "purpose": "Final true map of actual built plant — for future maintenance and inspections",
        "what_it_shows": "Actual positions of all equipment, pipes, cables as built (may differ from design), "
                         "underground pipe/cable routes, valve tag numbers, instrument locations",
        "ai_capable": False,
        "ai_prompt": "",
        "required_for": ["Plant Handover", "Annual Safety Audit", "Insurance"],
        "note": "CREATED AFTER CONSTRUCTION: Site survey team updates original drawings to match reality",
    },
]

# Group by category
DRAWING_CATEGORIES = {}
for d in DRAWING_REGISTRY:
    cat = d["category"]
    if cat not in DRAWING_CATEGORIES:
        DRAWING_CATEGORIES[cat] = []
    DRAWING_CATEGORIES[cat].append(d)

# Group by required_for
DRAWINGS_BY_DOCUMENT = {}
for d in DRAWING_REGISTRY:
    for doc in d.get("required_for", []):
        if doc not in DRAWINGS_BY_DOCUMENT:
            DRAWINGS_BY_DOCUMENT[doc] = []
        DRAWINGS_BY_DOCUMENT[doc].append(d)


def get_drawings_for_stakeholder(stakeholder):
    """Get drawings needed for a specific stakeholder type."""
    stakeholder_map = {
        "Bank": "Investor & Bank",
        "Investor": "Investor & Bank",
        "Government": "Government & Regulatory",
        "GPCB": "Government & Regulatory",
        "Engineer": "Engineering",
        "Contractor": "Construction",
    }
    cat = stakeholder_map.get(stakeholder, stakeholder)
    return DRAWING_CATEGORIES.get(cat, [])


def get_drawings_for_document(doc_name):
    """Get drawings required for a specific document type."""
    return DRAWINGS_BY_DOCUMENT.get(doc_name, [])


def build_prompt_with_context(drawing, cfg):
    """Build the DALL-E prompt with actual project parameters."""
    capacity = cfg.get("capacity_tpd", 30)
    site_area = cfg.get("site_area_acres", 0.5)
    length = int((site_area * 43560) ** 0.5 * 1.2) if site_area > 0 else 60
    width = int((site_area * 43560) ** 0.5 / 1.2) if site_area > 0 else 35

    prompt = drawing["ai_prompt"].format(
        capacity=int(capacity),
        length=length,
        width=width,
    )
    return prompt


def get_scope_of_work_drawings():
    """Return drawing list formatted for scope of work / proposal."""
    scope = []
    for d in DRAWING_REGISTRY:
        scope.append({
            "Drawing": d["name"],
            "For": d["for_whom"],
            "Purpose": d["purpose"],
            "AI Generated": "Yes — Concept" if d["ai_capable"] else "No — Human CAD",
            "Required For": ", ".join(d.get("required_for", [])),
        })
    return scope
