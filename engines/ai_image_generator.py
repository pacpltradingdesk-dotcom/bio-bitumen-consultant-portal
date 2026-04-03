"""
Bio Bitumen — AI Image & Drawing Generator
=============================================
Uses FREE AI image APIs to generate professional 3D renders,
plant layouts, and engineering drawings.

Free AI APIs used:
1. Pollinations.ai — Free, no API key, unlimited
2. Together.ai — Free tier available
"""
import os
import requests
import urllib.parse
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "ai_drawings")


def _ensure_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_with_pollinations(prompt, filename, width=1344, height=768):
    """
    Generate image using multiple FREE AI APIs (tries each until one works).
    APIs tried in order:
    1. Pollinations.ai — Free, no key
    2. Pollinations flux model
    3. Pollinations turbo model
    Returns path to saved image or None if all fail.
    """
    _ensure_dir()
    path = os.path.join(OUTPUT_DIR, filename)
    encoded = urllib.parse.quote(prompt)

    # Try multiple endpoints
    urls = [
        f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true",
        f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model=flux&nologo=true",
        f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model=turbo&nologo=true",
    ]

    for url in urls:
        try:
            resp = requests.get(url, timeout=180, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and len(resp.content) > 5000:
                with open(path, "wb") as f:
                    f.write(resp.content)
                return path
        except Exception:
            continue

    return None


# ═══════════════════════════════════════════════════════════════════
# PROMPTS FOR EACH DRAWING TYPE
# ═══════════════════════════════════════════════════════════════════

def get_prompts(tpd):
    """Return optimized prompts for each drawing type."""
    return {
        "3D_Plant_Layout": {
            "prompt": f"Professional 3D isometric architectural render of a {tpd} ton per day bio-bitumen pyrolysis industrial plant layout, bird eye view, showing raw material storage yard with biomass piles, biomass shredder machine, rotary dryer, large cylindrical pyrolysis reactor with chimney stack, condenser units, bitumen blending tanks, product storage tank farm with bund wall, truck loading platform, office building, weigh bridge, internal concrete roads, green belt trees around boundary, industrial setting, photorealistic render, engineering visualization, clean white background, labeled sections, high detail, 4k quality",
            "filename": f"3D_Plant_Layout_{tpd}TPD.jpg",
        },
        "3D_Reactor_Detail": {
            "prompt": f"Detailed 3D cutaway cross-section render of an industrial pyrolysis reactor for biomass processing, {tpd} TPD capacity, showing internal auger screw mechanism, refractory lining, biomass feed inlet hopper at top, bio-oil vapor outlet pipe, biochar discharge at bottom, thermic fluid heating jacket around cylinder, temperature gauges and pressure instruments, steel vessel with flanges and bolts, industrial equipment photorealistic render, technical illustration, engineering drawing style, clean background",
            "filename": f"3D_Reactor_Detail_{tpd}TPD.jpg",
        },
        "3D_Tank_Farm": {
            "prompt": f"Professional 3D render of industrial petroleum storage tank farm for bio-bitumen plant, {max(2,int(tpd/10))} large cylindrical heated bitumen storage tanks with insulation, concrete containment bund wall around tanks, fire spacing between tanks marked, pipe rack with elevated steel piping connecting tanks, pump house, fire water tank and hydrant system, tanker truck loading platform, automated drum filling machine with 200L drums, safety signage, industrial setting, photorealistic, engineering visualization",
            "filename": f"3D_Tank_Farm_{tpd}TPD.jpg",
        },
        "Site_Layout_TopView": {
            "prompt": f"Professional top view architectural site layout plan of a {tpd} TPD bio-bitumen industrial plant on a rectangular plot, color coded sections: green area for raw material storage, yellow for biomass processing with shredder and dryer, red zone for pyrolysis reactor section, orange for bio-oil blending area, blue for storage tank farm, purple for product dispatch with truck parking, gray for utility area with DG set and transformer, white for office building, internal 6 meter wide concrete road, green belt trees along boundary wall, weigh bridge at entry gate, north arrow, dimension markings, engineering drawing style, clean white background, labeled sections, high quality architectural rendering",
            "filename": f"Site_Layout_TopView_{tpd}TPD.jpg",
        },
        "Process_Flow_3D": {
            "prompt": f"3D illustrated process flow diagram for bio-bitumen production from agricultural biomass, showing step by step: truck delivering rice straw to storage yard, biomass going through shredder machine, then rotary dryer, then pelletizer, feeding into large pyrolysis reactor at 450-550 degrees celsius, vapors going to 4 condenser units in series producing bio-oil, bio-oil flowing to blending tank mixing with conventional bitumen, quality testing lab, final bio-modified bitumen product in drums and tanker, biochar byproduct output, syngas recycled as fuel, arrows showing material flow direction, technical illustration, clean engineering style",
            "filename": f"Process_Flow_3D_{tpd}TPD.jpg",
        },
        "Electrical_Room": {
            "prompt": f"Professional 3D render of industrial electrical control room and power distribution for a {tpd} TPD plant, showing HT transformer on concrete plinth with fencing, LT distribution panel boards in a row inside control room, DG set {max(250,int(tpd*6))} kVA with exhaust silencer, cable trays on wall with organized cables, PLC SCADA control screens on desk, MCC panel with motor starters, earthing busbar with copper strips, LED indicator lights on panels, clean industrial electrical room, photorealistic engineering visualization",
            "filename": f"Electrical_Room_{tpd}TPD.jpg",
        },
        "Fire_Safety_System": {
            "prompt": f"Professional 3D render of industrial fire safety system for a chemical plant, showing fire water storage tank 50000 liters, fire pump house with diesel and electric pumps, fire hydrant posts with red painted posts and hose reels spaced along internal road, portable fire extinguishers mounted on walls, emergency assembly point sign, fire escape route arrows on floor painted green, smoke detectors on ceiling, sprinkler system pipes on ceiling, emergency exit doors with illuminated signs, industrial safety visualization, photorealistic",
            "filename": f"Fire_Safety_{tpd}TPD.jpg",
        },
        "Civil_Structure": {
            "prompt": f"Professional 3D architectural render of industrial factory building structure for a bio-bitumen plant, showing pre-engineered steel building PEB with metal roof sheets and wall cladding, RCC column foundations with anchor bolts visible, concrete floor with VDF finish, overhead crane beam, roller shutter door for truck entry, ventilation louvers on walls, mezzanine floor with railing, office cabin inside factory, equipment foundations with holding down bolts, clean industrial architecture render, engineering visualization",
            "filename": f"Civil_Structure_{tpd}TPD.jpg",
        },
        "Water_System": {
            "prompt": f"Professional 3D technical illustration of industrial water supply and treatment system for a plant, showing overhead water tank on steel tower, underground water storage sump, water treatment plant with sand filter and softener, pump house with centrifugal pumps, pipeline routing in blue color pipes to different plant sections, effluent treatment plant ETP with settling tank equalization tank and treated water storage, rainwater harvesting system with collection drains and recharge pit, labeled pipes with flow direction arrows, engineering visualization style",
            "filename": f"Water_System_{tpd}TPD.jpg",
        },
        "Piping_Layout": {
            "prompt": f"Professional 3D render of industrial plant piping layout for bio-bitumen production, showing elevated steel pipe rack with multiple parallel pipes of different sizes color coded: black for process lines, blue for water, red for fire water, green for compressed air, brown for steam, yellow for gas, pipe supports and hangers, flanged connections with bolts, gate valves and ball valves, pressure gauges, flow meters, expansion loops, pipe labels with size and material, isometric view, engineering technical illustration",
            "filename": f"Piping_Layout_{tpd}TPD.jpg",
        },
    }


# ═══════════════════════════════════════════════════════════════════
# GENERATE ALL AI IMAGES
# ═══════════════════════════════════════════════════════════════════
def generate_all_ai_images(tpd, progress_callback=None):
    """Generate all AI images for a given capacity."""
    _ensure_dir()
    prompts = get_prompts(tpd)
    results = {}

    for i, (key, data) in enumerate(prompts.items()):
        if progress_callback:
            progress_callback(i + 1, len(prompts), key)

        path = generate_with_pollinations(data["prompt"], data["filename"])
        if path:
            results[key] = {"path": path, "filename": data["filename"], "status": "OK"}
        else:
            results[key] = {"path": None, "filename": data["filename"], "status": "FAILED"}

    return results


def get_existing_ai_images():
    """List all existing AI-generated images."""
    _ensure_dir()
    images = []
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.endswith(('.jpg', '.png')):
            path = os.path.join(OUTPUT_DIR, f)
            images.append({
                "name": f,
                "path": path,
                "size_kb": os.path.getsize(path) / 1024,
            })
    return images


def get_prompt_for_custom(description):
    """Generate a custom prompt for any drawing request."""
    return (f"Professional 3D photorealistic engineering render of {description}, "
            f"industrial plant setting, clean background, high detail, "
            f"technical illustration style, labeled components, 4k quality")
