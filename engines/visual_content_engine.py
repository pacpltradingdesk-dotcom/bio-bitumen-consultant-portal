"""
Visual Content Engine — Reference Images + Diagrams for Dashboard
==================================================================
Generates relevant visual content for each module using FREE APIs.
Every section gets: text + numbers + chart + image.
"""
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "visual_references")


def _ensure_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════
# IMAGE MAPPING — What image to show on each page
# ══════════════════════════════════════════════════════════════════════
IMAGE_MAP = {
    "technology": {
        "prompt": "Professional industrial diagram of biomass pyrolysis process, showing agro-waste input, pyrolysis reactor at 500 degrees celsius, bio-oil condenser, biochar collection, clean technical illustration",
        "filename": "ref_pyrolysis_process.png",
    },
    "reactor": {
        "prompt": "Industrial pyrolysis reactor vessel cutaway showing internal screw mechanism, refractory lining, inlet and outlet nozzles, insulation layer, steel construction, technical engineering illustration",
        "filename": "ref_reactor_cutaway.png",
    },
    "raw_material": {
        "prompt": "Agricultural biomass raw materials collage: rice straw bales, wheat straw, sugarcane bagasse, cotton stalks, groundnut shells, arranged professionally with labels, clean white background",
        "filename": "ref_raw_materials.png",
    },
    "plant_layout": {
        "prompt": "Professional bird eye view of industrial bio-bitumen plant with labeled sections: raw material area, processing, reactor zone, tank farm, dispatch, office, green belt, clean architectural render",
        "filename": "ref_plant_layout.png",
    },
    "products": {
        "prompt": "Bio-bitumen products display: black bio-modified bitumen in steel drum, biochar in HDPE bag, bio-oil in container, arranged professionally with labels, clean studio photography style",
        "filename": "ref_products.png",
    },
    "laboratory": {
        "prompt": "Professional quality control laboratory for bitumen testing: penetration tester, softening point apparatus, viscosity bath, flash point tester, lab benches with equipment, clean industrial lab",
        "filename": "ref_laboratory.png",
    },
    "safety": {
        "prompt": "Industrial plant safety equipment: fire hydrant post red, fire extinguisher, safety shower, eyewash station, PPE kit (helmet gloves boots), safety signs, arranged professionally",
        "filename": "ref_safety_equipment.png",
    },
    "construction": {
        "prompt": "Industrial construction site: RCC foundation pouring, steel PEB structure erection, compound wall brick work, concrete road laying, professional construction photography",
        "filename": "ref_construction.png",
    },
    "financial": {
        "prompt": "Professional financial dashboard display showing bar charts, pie charts, line graphs, ROI gauge, investment breakdown, Indian rupee currency, clean modern business infographic style",
        "filename": "ref_financial_dashboard.png",
    },
    "compliance": {
        "prompt": "Indian government compliance documents: factory license, pollution control board consent, fire NOC, MSME registration, arranged on desk with stamp and seal, professional document photography",
        "filename": "ref_compliance_docs.png",
    },
    "road_bitumen": {
        "prompt": "Bitumen road construction in India: hot mix asphalt laying machine on highway, road roller compacting, workers in safety gear, NHAI highway project, professional construction photography",
        "filename": "ref_road_construction.png",
    },
    "tank_farm": {
        "prompt": "Industrial storage tank farm: cylindrical steel tanks with insulation, concrete bund wall, pipe rack, fire hydrant system, loading platform, professional industrial photography",
        "filename": "ref_tank_farm.png",
    },
}


def get_image_path(key):
    """Get path to reference image. Returns None if not generated yet."""
    _ensure_dir()
    path = os.path.join(OUTPUT_DIR, IMAGE_MAP.get(key, {}).get("filename", ""))
    return path if os.path.exists(path) else None


def generate_reference_image(key):
    """Generate a reference image using Pollinations.ai (FREE)."""
    _ensure_dir()
    data = IMAGE_MAP.get(key)
    if not data:
        return None

    try:
        from engines.ai_image_generator import generate_with_pollinations
        path = generate_with_pollinations(data["prompt"], data["filename"], width=1024, height=576)
        return path
    except Exception:
        return None


def generate_all_reference_images(progress_callback=None):
    """Generate ALL reference images. Takes ~5-10 minutes."""
    results = {}
    for i, (key, data) in enumerate(IMAGE_MAP.items()):
        if progress_callback:
            progress_callback(i + 1, len(IMAGE_MAP), key)
        path = generate_reference_image(key)
        results[key] = {"path": path, "status": "OK" if path else "FAILED"}
    return results


def get_all_image_status():
    """Check which reference images exist."""
    _ensure_dir()
    status = {}
    for key, data in IMAGE_MAP.items():
        path = os.path.join(OUTPUT_DIR, data["filename"])
        status[key] = {
            "exists": os.path.exists(path),
            "path": path,
            "filename": data["filename"],
        }
    return status


# ══════════════════════════════════════════════════════════════════════
# STREAMLIT HELPER — Show image on any page
# ══════════════════════════════════════════════════════════════════════
def show_reference_image(st, key, caption=None):
    """Show a reference image on a Streamlit page. Auto-generates if missing."""
    path = get_image_path(key)
    if path:
        try:
            st.image(path, caption=caption or key.replace("_", " ").title(), use_container_width=True)
            return True
        except Exception:
            pass

    # Image not available — show placeholder
    data = IMAGE_MAP.get(key, {})
    st.info(f"Reference image: {caption or key.replace('_', ' ').title()} — "
            f"Generate in AI Drawings → Gallery tab")
    return False
