"""
Bio Bitumen — AI Image & Drawing Generator (UPGRADED)
=======================================================
Uses FREE AI image APIs with EXACT computed specifications.
Every dimension from plant_engineering.py — nothing generic.

Free AI APIs:
1. Pollinations.ai — Free, no API key, unlimited
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


def _load_openai_key():
    """Read OpenAI key directly from config file — avoids circular import issues."""
    import json
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "ai_config.json"
    )
    try:
        with open(config_path, encoding="utf-8") as f:
            return json.load(f).get("openai_key", "")
    except Exception:
        return ""


def generate_with_dalle(prompt, filename, size="1792x1024"):
    """Generate image using OpenAI DALL-E 3 (paid, high quality). Returns path or None."""
    api_key = _load_openai_key()
    if not api_key:
        return None

    _ensure_dir()
    path = os.path.join(OUTPUT_DIR, filename)

    try:
        resp = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "dall-e-3", "prompt": prompt[:4000], "n": 1,
                  "size": size, "quality": "hd", "style": "natural"},
            timeout=120,
        )
        data = resp.json()
        img_url = data.get("data", [{}])[0].get("url")
        if img_url:
            img_resp = requests.get(img_url, timeout=60)
            if img_resp.status_code == 200 and len(img_resp.content) > 5000:
                with open(path, "wb") as f:
                    f.write(img_resp.content)
                return path
        # Log error for debugging
        error_msg = data.get("error", {}).get("message", str(data))
        import sys
        print(f"[DALL-E ERROR] {error_msg}", file=sys.stderr)
    except Exception as e:
        import sys
        print(f"[DALL-E EXCEPTION] {e}", file=sys.stderr)

    return None


def generate_with_pollinations(prompt, filename, width=1344, height=768):
    """Generate image using Pollinations.ai FREE API."""
    _ensure_dir()
    path = os.path.join(OUTPUT_DIR, filename)
    encoded = urllib.parse.quote(prompt)

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


def generate_image(prompt, filename, width=1344, height=768):
    """Best-quality image generator: DALL-E 3 first (if key set), Pollinations fallback.
    Returns (path, provider) tuple."""
    path = generate_with_dalle(prompt, filename)
    if path:
        return path, "dall-e-3"
    path = generate_with_pollinations(prompt, filename, width, height)
    if path:
        return path, "pollinations"
    return None, "failed"


# ═══════════════════════════════════════════════════════════════════
# COMPUTED SPECS — Used in every drawing prompt
# ═══════════════════════════════════════════════════════════════════
def _get_specs(cfg):
    """Get computed specs from plant_engineering for drawing prompts."""
    try:
        from engines.plant_engineering import compute_all, get_machinery_list, SAFETY_CLEARANCES
        comp = compute_all(cfg)
        machinery = get_machinery_list(cfg, comp)
        return comp, machinery, SAFETY_CLEARANCES
    except Exception:
        tpd = cfg.get("capacity_tpd", 20)
        return {
            "reactor_dia_m": round(1 + tpd * 0.04, 1),
            "reactor_ht_m": round(3 + tpd * 0.12, 1),
            "reactor_qty": 1 if tpd <= 30 else 2,
            "dryer_dia_m": round(1 + tpd * 0.02, 1),
            "dryer_len_m": round(5 + tpd * 0.25, 1),
            "bio_oil_tank_dia_m": round(2 + tpd * 0.05, 1),
            "bio_oil_tank_ht_m": round(1.5 + tpd * 0.04, 1),
            "feed_shed_l_m": round(20 + tpd * 0.5, 0),
            "feed_shed_w_m": round(15 + tpd * 0.3, 0),
            "plot_l_m": max(60, int(tpd * 4)),
            "plot_w_m": max(40, int(tpd * 3)),
            "feed_per_hour_kg": round(tpd / 16 * 1000, 0),
            "bio_oil_tpd": round(tpd * 0.32, 1),
            "bio_char_tpd": round(tpd * 0.28, 1),
            "blend_output_tpd": round(tpd * 0.32 * 0.85 / 0.2, 1),
            "elec_kva": max(100, int(tpd * 8)),
            "main_bus_amps": round(max(100, tpd * 8) * 1000 / (1.732 * 415), 0),
        }, [], {}


# ═══════════════════════════════════════════════════════════════════
# DRAWING PROMPTS — All with EXACT computed specifications
# ═══════════════════════════════════════════════════════════════════
def get_prompts(tpd, cfg=None):
    """Return drawing prompts with EXACT computed specs from plant_engineering."""
    if cfg is None:
        cfg = {"capacity_tpd": tpd, "bio_oil_yield_pct": 32, "bio_char_yield_pct": 28,
               "syngas_yield_pct": 22, "process_loss_pct": 18, "bio_blend_pct": 20}
    else:
        # Override capacity with the tpd parameter (user may have changed it on the page)
        cfg = dict(cfg)
        cfg["capacity_tpd"] = tpd

    comp, machinery, clearances = _get_specs(cfg)

    # Extract key dimensions
    state = cfg.get("state", "Maharashtra")
    r_dia = comp.get("reactor_dia_m", 1.5)
    r_ht = comp.get("reactor_ht_m", 4.5)
    r_qty = comp.get("reactor_qty", 1)
    d_dia = comp.get("dryer_dia_m", 1.3)
    d_len = comp.get("dryer_len_m", 6.5)
    tank_dia = comp.get("bio_oil_tank_dia_m", 2.5)
    tank_ht = comp.get("bio_oil_tank_ht_m", 2.0)
    shed_l = comp.get("feed_shed_l_m", 30)
    shed_w = comp.get("feed_shed_w_m", 20)
    plot_l = comp.get("plot_l_m", 120)
    plot_w = comp.get("plot_w_m", 80)
    feed_hr = comp.get("feed_per_hour_kg", 1250)
    oil_tpd = comp.get("bio_oil_tpd", 6.4)
    char_tpd = comp.get("bio_char_tpd", 5.6)
    blend_tpd = comp.get("blend_output_tpd", 27)
    elec_kva = comp.get("elec_kva", 200)

    # Safety clearances
    react_boundary = clearances.get("reactor_to_boundary_m", 15)
    tank_boundary = clearances.get("bio_oil_tank_to_boundary_m", 15)
    ctrl_react = clearances.get("reactor_to_control_room_m", 30)
    road_w = clearances.get("road_width_internal_m", 6)
    hydrant_sp = clearances.get("fire_hydrant_spacing_m", 45)

    return {
        "3D_Isometric_Plant_View": {
            "prompt": (
                f"Professional 3D isometric architectural render of a {tpd} TPD bio-bitumen pyrolysis plant, "
                f"bird eye view on {plot_l}m x {plot_w}m plot. "
                f"Show: raw material storage shed {shed_l}m x {shed_w}m with biomass piles, "
                f"biomass hammer mill shredder 75kW, rotary drum dryer {d_dia}m diameter x {d_len}m long, "
                f"{r_qty} cylindrical pyrolysis reactor {r_dia}m diameter x {r_ht}m height on 1.5m skirt with insulation cladding, "
                f"shell and tube condenser, {tank_dia}m diameter bio-oil tanks x 2 inside concrete dyke bund, "
                f"bitumen blending tanks insulated, product tank farm with {int(blend_tpd*3/3):.0f}m3 heated tanks, "
                f"30m stack chimney, truck loading platform, weighbridge 18m at entry gate, "
                f"office building 2-storey, laboratory, {road_w}m wide internal RCC roads, "
                f"5m green belt trees around boundary wall, fire hydrant posts every {hydrant_sp}m, "
                f"control room {ctrl_react}m from reactor, parking area. "
                f"Photorealistic render, engineering visualization, labeled sections, 4k quality"
            ),
            "filename": f"3D_Isometric_Plant_View_{tpd}TPD.png",
        },
        "Site_Layout_GA_Drawing": {
            "prompt": (
                f"Professional top-view site layout plan for {tpd} TPD bio-bitumen plant in {state}. "
                f"Plot {plot_l}m x {plot_w}m. Output: bio-oil {oil_tpd}T/day, bio-char {char_tpd}T/day, blend {blend_tpd}T/day. "
                f"IS 14489 safety clearances, IS 2379 colour codes. Equipment tags SC-101, PR-101, MX-101 visible. "
                f"Zone A (blue): Gate with weighbridge 18m, guard booth. "
                f"Zone B (green): RM shed {shed_l}m x {shed_w}m. "
                f"Zone C (purple): Pre-processing building with shredder + dryer {d_dia}m x {d_len}m. "
                f"Zone D (red): Reactor area {r_qty}x reactor {r_dia}m dia, {react_boundary}m clearance from boundary, HAZARDOUS. "
                f"Zone E (light blue): Oil recovery with condenser + {tank_dia}m oil tanks in dyke bund. "
                f"Zone F (lime): Blending section with heated tanks + mixer. "
                f"Zone G (purple): Storage tank farm with {int(blend_tpd*3):.0f}m3 bitumen tanks. "
                f"Zone H (orange): Dispatch area with loading dock + truck parking. "
                f"Zone I (teal): Electrical substation + {elec_kva}kVA transformer + DG set. "
                f"Zone J (brown): Utilities — ETP, water tank, compressor. "
                f"Zone K (red): QC Laboratory 12m x 9m. "
                f"Zone L (navy): Safety station + fire hydrant ring main. "
                f"Zone M: Compound wall perimeter, {road_w}m roads, 5m green belt. "
                f"Zone N: Office 2-storey, canteen, toilets. "
                f"Zone O: Maintenance workshop with 5T crane. "
                f"North arrow top-right, scale bar, dimension chains, engineering drawing style"
            ),
            "filename": f"Site_Layout_GA_Drawing_{tpd}TPD.png",
        },
        "Process_Flow_Diagram_PFD": {
            "prompt": (
                f"Professional process flow diagram PFD for {tpd} TPD bio-bitumen plant, "
                f"showing material flow with arrows: "
                f"Step 1: Truck unloading {tpd}T/day agro-waste to storage shed. "
                f"Step 2: Hammer mill shredder reducing to 50mm then 3mm. "
                f"Step 3: Rotary drum dryer {d_dia}m x {d_len}m removing moisture to <12%. "
                f"Step 4: Pyrolysis reactor {r_dia}m x {r_ht}m at 500C, producing: "
                f"bio-oil {oil_tpd:.1f}T/day (32%), bio-char {char_tpd:.1f}T/day (28%), syngas (22%), loss (18%). "
                f"Step 5: Shell tube condenser cooling vapors to bio-oil liquid at 40C. "
                f"Step 6: Bio-oil blending with VG30 bitumen in high shear mixer, "
                f"blend output {blend_tpd:.1f}T/day. "
                f"Step 7: Quality testing per IS:73, storage in heated tanks, dispatch. "
                f"Stream table showing kg/hr, temperature, phase for each stream. "
                f"IS 10234 standard symbols, flow arrows, equipment tag numbers, clean engineering style"
            ),
            "filename": f"Process_Flow_Diagram_PFD_{tpd}TPD.png",
        },
        "Reactor_Cutaway_Detail": {
            "prompt": (
                f"Detailed 3D cutaway cross-section of industrial pyrolysis reactor, {tpd} TPD. "
                f"Reactor vessel: {r_dia}m diameter x {r_ht}m height, AISI 310S stainless steel inner shell "
                f"{12}mm thick, {100}mm mineral wool insulation with SS304 cladding. "
                f"Show: feed inlet nozzle 300mm at top, bio-oil vapor outlet 200mm side, "
                f"syngas outlet 150mm top, char discharge 250mm bottom, "
                f"6 thermowell nozzles 50mm at various heights, "
                f"manway 600mm on side, PSV relief valve 100mm at top. "
                f"1.5m support skirt on RCC M25 foundation 600mm thick. "
                f"Temperature: 500C operating, design 550C. "
                f"Pressure: atmospheric to +0.5 barg. "
                f"RAL 3002 Carmine Red body, RAL 7035 insulation cladding. "
                f"Technical cutaway illustration, labeled components, engineering drawing style"
            ),
            "filename": f"Reactor_Cutaway_Detail_{tpd}TPD.png",
        },
        "Tank_Farm_Layout": {
            "prompt": (
                f"Professional 3D render of bio-bitumen tank farm, {tpd} TPD plant. "
                f"Show: 2x bio-oil storage tanks {tank_dia}m dia x {tank_ht}m height, "
                f"3x finished bitumen tanks {int(blend_tpd*5/3):.0f}m3 each heated to 160C with insulation, "
                f"1x biochar storage silo 6m height with 60-degree cone, "
                f"all liquid tanks inside RCC dyke bund 1m height (110% max tank volume), "
                f"tanks painted RAL 3002 red (Class B petroleum), "
                f"drain sump with isolation valve in dyke, "
                f"flame arrestors on all tank vents, "
                f"fire hydrant posts at {hydrant_sp}m spacing around tank farm, "
                f"foam pourers on bitumen tanks, "
                f"level gauges and temperature transmitters on each tank, "
                f"pipe rack connecting to blending section, "
                f"tanker loading arm and drum filling machine, "
                f"minimum {tank_boundary}m clearance from boundary. "
                f"Industrial photorealistic render, engineering visualization"
            ),
            "filename": f"Tank_Farm_Layout_{tpd}TPD.png",
        },
        "Electrical_Single_Line_Diagram": {
            "prompt": (
                f"Professional electrical single line diagram SLD for {tpd} TPD bio-bitumen plant. "
                f"Show: 11kV incoming from grid, {elec_kva}kVA transformer 11kV/415V ONAN CRGO, "
                f"main LT panel MCC {int(comp.get('main_bus_amps', 400))}A bus 415V 3-phase 50Hz, "
                f"DG set {max(50, int(tpd*5))}kVA diesel with AMF panel, "
                f"power factor correction panel, "
                f"motor feeders for: shredder 75kW, dryer 37kW, grinder 45kW, pelletizer 55kW, "
                f"reactor drive 55kW, condenser pump 5.5kW, blending mixer 15kW, "
                f"colloid mill 22kW, transfer pumps, fire pump 37kW, compressor 22kW, "
                f"UPS 20kVA for SCADA/PLC, lighting circuits with RCCB, "
                f"earthing bus 50x6mm GI, IS 3043 earth mat. "
                f"Standard SLD symbols per IS 732, circuit breakers, overload relays, "
                f"engineering drawing style, clean white background"
            ),
            "filename": f"Electrical_Single_Line_Diagram_{tpd}TPD.png",
        },
        "Fire_Safety_Layout": {
            "prompt": (
                f"Professional fire safety and emergency layout plan for {tpd} TPD bio-bitumen plant, "
                f"plot {plot_l}m x {plot_w}m. "
                f"Show: underground fire hydrant ring main DN150 looped around entire plant, "
                f"fire hydrant posts every {hydrant_sp}m marked FH-01 to FH-N, "
                f"fire water tank {50 if tpd<=30 else 100}m3 with diesel pump 18m3/hr, "
                f"reactor zone marked HAZARDOUS with {react_boundary}m exclusion zone, "
                f"control room {ctrl_react}m away from reactor, "
                f"2 emergency assembly points 50m from hazard areas, "
                f"emergency exit routes 2.5m wide marked with green arrows, "
                f"fire tender access road {road_w}m wide continuous ring with 9m turning radius, "
                f"eyewash stations within 10m of every hazard point, "
                f"portable extinguisher stations every 15m, "
                f"wind sock location visible from process area, "
                f"first aid room, safety shower positions, "
                f"color coded: red for fire equipment, green for exits, yellow for assembly. "
                f"NBC 2016 Part 4 compliant layout, engineering drawing style"
            ),
            "filename": f"Fire_Safety_Layout_{tpd}TPD.png",
        },
        "Civil_Foundation_Plan": {
            "prompt": (
                f"Professional civil foundation plan for {tpd} TPD bio-bitumen plant. "
                f"Show: RCC M25 mat foundation 600mm thick for {r_qty}x reactor {r_dia+1.5:.1f}m dia, "
                f"anti-vibration pad 300mm for shredder 4m x 3m, "
                f"dryer support foundations for {d_dia}m diameter drum, "
                f"column footings on 6m grid for PEB process hall, "
                f"equipment foundation bolts pattern, "
                f"plinth level +450mm above natural ground level, "
                f"internal road 200mm M25 RCC on 150mm WBM sub-base, "
                f"compound wall foundation strip 300mm wide, "
                f"storm water drain 600mm U-drain gradient 1:100, "
                f"tank foundations with ring wall for {tank_dia}m dia tanks, "
                f"earth pit locations for IS 3043 earthing, "
                f"FFL elevation markers at each building, "
                f"dimension chains with column grid A-A B-B, "
                f"engineering drawing style, structural plan, IS 456 compliant"
            ),
            "filename": f"Civil_Foundation_Plan_{tpd}TPD.png",
        },
        "Piping_Layout": {
            "prompt": (
                f"Professional 3D piping layout for {tpd} TPD bio-bitumen plant. "
                f"Elevated steel pipe rack 4.5m height with multiple parallel pipes, "
                f"color coded per IS 2379: "
                f"RAL 3002 red = fire water DN150, "
                f"RAL 6018 green = process water DN50, "
                f"RAL 1003 yellow = syngas fuel line DN100, "
                f"RAL 8025 brown with yellow band = bio-oil DN65, "
                f"RAL 9005 black with yellow band = bitumen DN80, "
                f"RAL 5012 blue = compressed air DN40, "
                f"RAL 7035 grey with black band = nitrogen DN25. "
                f"Show: flanged connections, gate valves, ball valves, "
                f"pressure gauges, flow meters, expansion loops, "
                f"pipe supports and hangers, drain valves at low points, "
                f"vent valves at high points, insulation on hot lines, "
                f"pipe labels showing size and service. "
                f"Isometric view, engineering technical illustration"
            ),
            "filename": f"Piping_Layout_{tpd}TPD.png",
        },
    }


# ═══════════════════════════════════════════════════════════════════
# GENERATE ALL AI IMAGES
# ═══════════════════════════════════════════════════════════════════
def generate_all_ai_images(tpd, progress_callback=None, cfg=None):
    """Generate all AI images for a given capacity with exact specs."""
    _ensure_dir()
    prompts = get_prompts(tpd, cfg)
    results = {}

    for i, (key, data) in enumerate(prompts.items()):
        if progress_callback:
            progress_callback(i + 1, len(prompts), key)

        path, provider = generate_image(data["prompt"], data["filename"])
        if path:
            results[key] = {"path": path, "filename": data["filename"], "status": "OK", "provider": provider}
        else:
            results[key] = {"path": None, "filename": data["filename"], "status": "FAILED", "provider": "failed"}

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


def get_prompt_for_custom(description, cfg=None):
    """Generate a custom prompt with specs for any drawing request."""
    specs = ""
    if cfg:
        comp, _, _ = _get_specs(cfg)
        tpd = cfg.get("capacity_tpd", 20)
        specs = (f" Plant: {tpd} TPD, reactor {comp.get('reactor_dia_m',1.5)}m x {comp.get('reactor_ht_m',4.5)}m, "
                 f"dryer {comp.get('dryer_dia_m',1.3)}m x {comp.get('dryer_len_m',6.5)}m, "
                 f"plot {comp.get('plot_l_m',120)}m x {comp.get('plot_w_m',80)}m.")
    return (f"Professional 3D photorealistic engineering render of {description}.{specs} "
            f"Industrial plant setting, clean background, high detail, "
            f"technical illustration style, labeled components, 4k quality")
