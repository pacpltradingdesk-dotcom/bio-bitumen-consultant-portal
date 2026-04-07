"""
DALL-E 3 Industrial Layout Engine — Professional Plant Visualization
=====================================================================
Generates high-end 3D isometric layouts, P&IDs, site plans using OpenAI DALL-E 3.
Builds engineering-grade prompts from plant parameters.
"""
import requests
import json
import os
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "ai_layouts"


def _ensure_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════
# PLANT CONFIGURATIONS — Machine lists by plant type and capacity
# ══════════════════════════════════════════════════════════════════════
PLANT_MACHINES = {
    "Bio-bitumen": {
        "machines": [
            "Raw Biomass Receiving Hopper",
            "Inclined Belt Conveyor",
            "Biomass Shredder/Hammer Mill",
            "Rotary Dryer",
            "Pelletization Unit",
            "Batch Pyrolysis Reactor R-101",
            "Bio-Oil Condenser HE-101",
            "Bio-Oil Storage Tank T-201",
            "Bitumen Heating Tank",
            "High Shear Blending Mixer",
            "Bio-Bitumen Storage Tank T-301",
            "Quality Control Lab",
            "DG Set Room",
            "Weighbridge",
        ],
        "flow": "Biomass → Shredding → Drying → Pyrolysis → Condensation → Blending → Storage → Dispatch",
        "safety_zones": "5m safety zone around Pyrolysis Reactor, 4m fire spacing between tanks",
    },
    "Emulsion": {
        "machines": [
            "Bitumen Heating Tank",
            "Emulsifier Chemical Tank",
            "Colloid Mill",
            "High Speed Mixer",
            "Emulsion Storage Tanks",
            "Dosing Pumps",
            "Loading Bay",
            "Lab & QC Room",
        ],
        "flow": "Bitumen Heating → Chemical Mixing → Colloid Mill → Storage → Dispatch",
        "safety_zones": "3m spacing between chemical tanks, fire hydrant coverage",
    },
    "CRMB": {
        "machines": [
            "Bitumen Heating Tank",
            "Crumb Rubber Hopper",
            "Screw Feeder",
            "Reaction Vessel with Agitator",
            "Holding Tank",
            "Circulation Pump",
            "Storage Tanks",
            "Loading Gantry",
        ],
        "flow": "Bitumen Heating → Rubber Addition → Reaction → Holding → Storage → Dispatch",
        "safety_zones": "4m spacing, ventilation for rubber fumes",
    },
    "Blown Bitumen": {
        "machines": [
            "Bitumen Feed Tank",
            "Oxidation Reactor (Blowing Still)",
            "Air Compressor",
            "Condenser",
            "Product Storage Tanks",
            "Thermal Oil Heater",
            "Control Room",
        ],
        "flow": "Feed Tank → Oxidation → Condensation → Storage → Dispatch",
        "safety_zones": "5m around reactor, gas detection system",
    },
    "Import Terminal": {
        "machines": [
            "Ship Unloading Arm",
            "Pipeline from Jetty",
            "Receiving Tanks",
            "Heating System",
            "Decanting Unit",
            "Storage Tank Farm",
            "Truck Loading Gantry",
            "Weighbridge",
            "Fire Water System",
        ],
        "flow": "Ship → Pipeline → Receiving → Heating → Decanting → Storage → Truck Loading",
        "safety_zones": "OISD-117 spacing rules, bund walls at 110% capacity",
    },
}

VISUAL_STYLES = {
    "Isometric 3D": "clean isometric schematic with 3D depth perspective",
    "Photorealistic": "photorealistic 3D rendered factory visualization",
    "Blueprint": "technical engineering blueprint with blue background and white lines",
    "Aerial View": "aerial bird's eye view photograph of industrial facility",
    "Cutaway": "architectural cutaway cross-section showing internal equipment layout",
}

ENVIRONMENTS = {
    "Industrial Estate": "on a clean concrete pad within a GIDC/MIDC industrial estate with compound wall and gate",
    "Open Land": "on open agricultural land converted to industrial use with gravel roads and tree boundary",
    "Warehouse": "inside a modern industrial warehouse with steel PEB structure and natural lighting",
    "Desert": "on flat desert terrain with dust-free concrete flooring and windbreak walls",
    "Coastal": "near coastal area with corrosion-resistant structures and elevated foundations",
}


def build_dalle_prompt(plant_type, capacity_tpd, environment, visual_style,
                        plot_length=60, plot_width=35, custom_machines=None, cfg=None):
    """
    Build a DALL-E 3 optimized prompt from plant parameters.
    Uses COMPUTED specs from plant_engineering when cfg is provided.
    Max 4000 chars. Returns the prompt string.
    """
    plant = PLANT_MACHINES.get(plant_type, PLANT_MACHINES["Bio-bitumen"])
    style = VISUAL_STYLES.get(visual_style, VISUAL_STYLES["Isometric 3D"])
    env = ENVIRONMENTS.get(environment, ENVIRONMENTS["Industrial Estate"])

    # Override capacity in cfg with the parameter value
    if cfg:
        cfg = dict(cfg)
        cfg["capacity_tpd"] = capacity_tpd

    # Get REAL computed specs if cfg available
    specs_text = ""
    if cfg and plant_type == "Bio-bitumen":
        try:
            from engines.plant_engineering import compute_all, get_machinery_list, SAFETY_CLEARANCES
            comp = compute_all(cfg)
            machinery = get_machinery_list(cfg, comp)

            # Use computed plot dimensions
            plot_length = comp.get("plot_l_m", plot_length)
            plot_width = comp.get("plot_w_m", plot_width)

            # Build machine list from actual computed machinery with specs
            real_machines = []
            for m in machinery[:10]:
                real_machines.append(f"{m['tag']} {m['name']} ({m['dims'][:50]})")
            machine_list = ", ".join(real_machines) if real_machines else ", ".join((custom_machines or plant["machines"])[:10])

            # Build specs text with actual dimensions
            specs_text = (
                f"Reactor: {comp['reactor_qty']}x cylindrical vessel "
                f"{comp['reactor_dia_m']}m diameter x {comp['reactor_ht_m']}m height "
                f"on 1.5m skirt, insulated with SS cladding (RAL 3002 red). "
                f"Dryer: rotary drum {comp['dryer_dia_m']}m dia x {comp['dryer_len_m']}m long. "
                f"Oil tanks: 2x {comp['bio_oil_tank_dia_m']}m dia x {comp['bio_oil_tank_ht_m']}m "
                f"inside concrete dyke bund. "
                f"Feed shed: {comp['feed_shed_l_m']:.0f}m x {comp['feed_shed_w_m']:.0f}m covered. "
                f"Safety: {SAFETY_CLEARANCES['reactor_to_boundary_m']}m reactor-to-boundary, "
                f"{SAFETY_CLEARANCES['reactor_to_control_room_m']}m to control room, "
                f"{SAFETY_CLEARANCES['fire_hydrant_spacing_m']}m hydrant spacing. "
            )

            # Update safety zones with real clearances
            safety = (
                f"{SAFETY_CLEARANCES['reactor_to_boundary_m']}m safety zone around reactor, "
                f"{SAFETY_CLEARANCES['fire_road_width_m']}m fire road, "
                f"fire hydrants every {SAFETY_CLEARANCES['fire_hydrant_spacing_m']}m"
            )
        except Exception:
            machine_list = ", ".join((custom_machines or plant["machines"])[:10])
            safety = plant["safety_zones"]
    else:
        machines = custom_machines or plant["machines"]
        machine_list = ", ".join(machines[:10])
        safety = plant["safety_zones"]

    prompt = (
        f"Create a highly detailed, professional {style} of a "
        f"{capacity_tpd} TPD (tonnes per day) {plant_type} Production Plant "
        f"on a {plot_length}m x {plot_width}m industrial plot. "
        f"Environment: The facility is located {env}. "
    )

    if specs_text:
        prompt += f"EXACT EQUIPMENT SPECIFICATIONS: {specs_text} "

    prompt += (
        f"Layout & Machinery: Arrange the equipment logically in sequential "
        f"processing order from left to right following the process flow: "
        f"{plant['flow']}. "
        f"The core components: {machine_list}. "
        f"Connect using industrial piping, belt conveyors, safety walkways. "
        f"Include {safety}. "
        f"Show {SAFETY_CLEARANCES.get('road_width_internal_m', 6) if cfg else 6}m wide road, "
        f"pipe rack at 4.5m height, green belt boundary. "
        f"Clean modern industrial colors (steel, concrete grey, safety orange). "
        f"Floating labels pointing to equipment. "
        f"High-end architectural quality, 8k, ultra-sharp, technical."
    )

    # Ensure within 4000 char limit
    if len(prompt) > 3900:
        prompt = prompt[:3900] + "..."

    return prompt


def generate_layout_image(prompt, size="1792x1024", api_key=None):
    """
    Call OpenAI DALL-E 3 API to generate layout image.
    Returns: (image_url, revised_prompt) or (None, error_message)
    """
    if not api_key:
        try:
            from engines.ai_engine import load_ai_config
            cfg = load_ai_config()
            api_key = cfg.get("openai_key", "")
        except Exception:
            pass

    if not api_key:
        return None, "No OpenAI API key configured. Go to AI Settings."

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": "hd",
            "style": "natural",
        }

        resp = requests.post("https://api.openai.com/v1/images/generations",
                              headers=headers, json=body, timeout=120)
        data = resp.json()

        if "data" in data and data["data"]:
            img_url = data["data"][0].get("url", "")
            revised = data["data"][0].get("revised_prompt", "")
            return img_url, revised
        elif "error" in data:
            return None, f"DALL-E Error: {data['error'].get('message', 'Unknown')}"
        else:
            return None, "No image returned"

    except requests.Timeout:
        return None, "Request timed out (120s). Try again."
    except Exception as e:
        return None, f"API Error: {str(e)}"


def save_layout_image(image_url, filename):
    """Download and save image from URL."""
    _ensure_dir()
    try:
        resp = requests.get(image_url, timeout=60)
        if resp.status_code == 200:
            path = OUTPUT_DIR / filename
            path.write_bytes(resp.content)
            return str(path)
    except Exception:
        pass
    return None


def get_saved_layouts():
    """List all previously generated layouts."""
    _ensure_dir()
    files = []
    for f in sorted(OUTPUT_DIR.glob("*.png")):
        files.append({
            "name": f.stem,
            "path": str(f),
            "size_kb": f.stat().st_size / 1024,
        })
    return files


# ══════════════════════════════════════════════════════════════════════
# DOCUMENT-SPECIFIC PROMPT TEMPLATES
# ══════════════════════════════════════════════════════════════════════
DOC_PROMPTS = {
    "Site Layout (GA Drawing)": (
        "Create a professional General Arrangement (GA) site layout drawing for a "
        "{capacity} TPD {plant_type} plant on {length}m x {width}m plot. "
        "Show: main road (6m), internal roads (4m), equipment positions with labels, "
        "green belt (3m boundary), parking, gate, security cabin, utility area, "
        "admin building, lab, weighbridge. Include North arrow, scale bar, "
        "and drawing border with title block. Engineering blueprint style, precise."
    ),
    "Process Flow Diagram (PFD)": (
        "Create a professional Process Flow Diagram (PFD) for a {capacity} TPD "
        "{plant_type} plant. Show process flow: {flow}. Use standard ISO process "
        "symbols for pumps, vessels, heat exchangers, and storage tanks. Include "
        "material flow arrows, stream numbers, and temperature/pressure annotations. "
        "Clean white background, professional engineering diagram style."
    ),
    "3D Isometric Plant View": (
        "Create a highly detailed 3D isometric view of a {capacity} TPD {plant_type} "
        "production facility. Show all major equipment: {machines}. Include pipe racks, "
        "walkways with yellow safety railings, concrete foundations, and cable trays. "
        "Photorealistic rendering, soft lighting, suitable for investor presentation."
    ),
    "Tank Farm Layout": (
        "Create a professional tank farm layout for a {capacity} TPD {plant_type} plant. "
        "Show storage tanks with bund walls (110% capacity), fire spacing (4m minimum), "
        "pipe manifold, pump house, and fire hydrant positions. Include OISD-117 spacing "
        "markers and safety signs. Technical drawing style with dimensions."
    ),
    "Electrical Single Line Diagram": (
        "Create a professional Electrical Single Line Diagram (SLD) for a {capacity} TPD "
        "{plant_type} plant. Show: HT incoming, transformer, LT panels, MCC, VFDs, "
        "motor connections, DG set, UPS, and earthing. Use standard IEC symbols. "
        "Include cable sizes, breaker ratings, and bus bar connections. Blueprint style."
    ),
    "Fire Safety Layout": (
        "Create a fire safety layout plan for a {capacity} TPD {plant_type} plant on "
        "{length}m x {width}m plot. Show: fire hydrant ring main, foam monitors near "
        "tanks, fire extinguisher positions, emergency exits, assembly points, "
        "fire water tank, and pump house. Red fire equipment markers on grey layout."
    ),
    "Piping Layout": (
        "Create a professional piping layout for a {capacity} TPD {plant_type} plant. "
        "Show main process piping routes, pipe rack elevations (4.5m), valve stations, "
        "instrument connections, utility headers (steam, water, air), and drainage. "
        "Color-coded: process=blue, steam=red, water=green, air=yellow. ISO standard."
    ),
    "Civil Foundation Plan": (
        "Create a civil foundation plan for a {capacity} TPD {plant_type} plant. "
        "Show equipment foundations with dimensions, column footings, grade beams, "
        "floor slab thickness, bund wall sections, road cross-sections, and "
        "drainage slopes. Technical drawing with section callouts."
    ),
}


def build_doc_prompt(doc_type, plant_type, capacity_tpd, plot_length=60, plot_width=35):
    """Build a document-specific prompt."""
    template = DOC_PROMPTS.get(doc_type, DOC_PROMPTS["3D Isometric Plant View"])
    plant = PLANT_MACHINES.get(plant_type, PLANT_MACHINES["Bio-bitumen"])

    return template.format(
        capacity=capacity_tpd,
        plant_type=plant_type,
        length=plot_length,
        width=plot_width,
        flow=plant["flow"],
        machines=", ".join(plant["machines"][:8]),
    )
