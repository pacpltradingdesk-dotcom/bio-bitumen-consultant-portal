"""
AI-Generated Engineering Drawings & 3D Renders
================================================
Uses Pollinations.ai (FREE, no API key) to generate professional
3D plant renders, layouts, and engineering visualizations.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from state_manager import get_config, init_state
from engines.ai_image_generator import (generate_all_ai_images, get_existing_ai_images,
                                          generate_with_pollinations, get_prompt_for_custom,
                                          get_prompts)

st.set_page_config(page_title="AI 3D Drawings", page_icon="🎨", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass


st.title("AI-Generated 3D Drawings & Renders")
st.markdown(f"**Professional 3D renders for {cfg['capacity_tpd']:.0f} TPD plant — powered by Pollinations AI (FREE)**")
st.markdown("---")

tab_gallery, tab_generate, tab_custom = st.tabs(["Image Gallery", "Generate New Set", "Custom Drawing"])

# ═══════════════════════════════════════════════════════════════════
# TAB 1: GALLERY — Show existing AI images
# ═══════════════════════════════════════════════════════════════════
with tab_gallery:
    st.subheader("Generated AI Drawings")

    images = get_existing_ai_images()
    if images:
        st.success(f"**{len(images)} AI-generated images available**")

        # Group by type
        cols = st.columns(2)
        for i, img in enumerate(images):
            with cols[i % 2]:
                name = img["name"].replace("_", " ").replace(".jpg", "").replace(".png", "")
                st.markdown(f"**{name}**")
                try:
                    st.image(img["path"], width="stretch")
                except Exception:
                    st.warning(f"Cannot display: {img['name']}")

                with open(img["path"], "rb") as f:
                    st.download_button(f"Download", f.read(), img["name"], key=f"dl_ai_{i}")
                st.markdown("---")
    else:
        st.info("No AI images generated yet. Go to **Generate New Set** tab to create them.")
        st.markdown("""
        ### What will be generated:
        1. **3D Plant Layout** — Complete bird-eye view of the entire plant
        2. **3D Reactor Detail** — Cutaway view of pyrolysis reactor
        3. **3D Tank Farm** — Storage tanks with bund wall and fire safety
        4. **Site Layout (Top View)** — Color-coded architectural plan
        5. **Process Flow (3D)** — Step-by-step material flow
        6. **Electrical Room** — HT/LT panels, DG set, control room
        7. **Fire Safety System** — Hydrants, extinguishers, assembly points
        8. **Civil Structure** — PEB building with foundations
        9. **Water System** — Supply, treatment, rainwater harvesting
        10. **Piping Layout** — Color-coded pipe routing on rack
        """)

# ═══════════════════════════════════════════════════════════════════
# TAB 2: GENERATE NEW SET
# ═══════════════════════════════════════════════════════════════════
with tab_generate:
    st.subheader(f"Generate Complete Drawing Set — {cfg['capacity_tpd']:.0f} TPD")
    st.markdown("""
    **10 professional 3D renders will be generated using AI:**
    - 3D Plant Layout (bird-eye view)
    - 3D Reactor Detail (cutaway)
    - 3D Tank Farm (storage area)
    - Site Layout (top view, color-coded)
    - Process Flow (3D illustrated)
    - Electrical Room & Power Distribution
    - Fire Safety System
    - Civil Structure & Building
    - Water Supply & Treatment System
    - Piping Layout (color-coded)

    **Time:** ~2-3 minutes for all 10 images (uses free AI, no API key needed)
    """)

    tpd_gen = st.number_input("Capacity (TPD)", min_value=5.0, max_value=100.0,
                               value=float(cfg["capacity_tpd"]), step=5.0, key="ai_tpd")

    # Select which drawings to generate
    prompts = get_prompts(tpd_gen, cfg)
    drawing_names = list(prompts.keys())
    selected = st.multiselect("Select drawings to generate",
                               drawing_names, default=drawing_names,
                               format_func=lambda x: x.replace("_", " "))

    if st.button("Generate AI Drawings", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        generated = 0
        failed = 0

        for i, key in enumerate(selected):
            data = prompts[key]
            status_text.text(f"Generating {i+1}/{len(selected)}: {key.replace('_', ' ')}...")
            progress_bar.progress((i + 1) / len(selected))

            path = generate_with_pollinations(data["prompt"], data["filename"])
            if path:
                generated += 1
                st.image(path, caption=key.replace("_", " "), width="stretch")
                with open(path, "rb") as f:
                    st.download_button(f"Download {key}", f.read(), data["filename"], key=f"gen_{key}")
            else:
                failed += 1
                st.warning(f"Failed to generate: {key}")

        progress_bar.progress(1.0)
        status_text.text(f"Done! Generated: {generated} | Failed: {failed}")
        st.success(f"**{generated} images generated!** View them in the Gallery tab.")

# ═══════════════════════════════════════════════════════════════════
# TAB 3: CUSTOM DRAWING
# ═══════════════════════════════════════════════════════════════════
with tab_custom:
    st.subheader("Generate Custom Drawing")
    st.markdown("Describe any drawing you need — AI will generate it.")

    custom_desc = st.text_area("Describe the drawing you want",
                                placeholder="Example: Detailed foundation drawing of a pyrolysis reactor showing RCC footing 3m x 4m with 12mm rebar at 150mm spacing, M30 grade concrete, anchor bolts layout, side elevation showing 1.5m depth",
                                height=100)

    custom_name = st.text_input("Filename", value="custom_drawing.jpg")

    if st.button("Generate Custom Drawing", type="primary", key="gen_custom"):
        if custom_desc:
            with st.spinner("Generating custom drawing..."):
                prompt = get_prompt_for_custom(custom_desc, cfg)
                st.caption(f"Prompt: {prompt[:200]}...")
                path = generate_with_pollinations(prompt, custom_name)
                if path:
                    st.success("Generated!")
                    st.image(path, width="stretch")
                    with open(path, "rb") as f:
                        st.download_button("Download", f.read(), custom_name)
                else:
                    st.error("Generation failed. Check internet connection and try again.")
        else:
            st.warning("Enter a description first.")

    st.markdown("---")
    st.markdown("""
    ### Example Prompts You Can Use:
    - **Foundation:** "RCC foundation detail for 10 TPD pyrolysis reactor, showing M30 concrete, 12mm rebar at 150mm c/c, 1.5m depth, holding down bolts 20mm dia"
    - **Pipe routing:** "Isometric piping drawing for bio-oil transfer from condenser to storage tank, 4 inch MS pipe, gate valves, check valve, pressure gauge, flow meter"
    - **Cable tray:** "Cable tray layout showing HT cables from transformer to MCC panel, LT power cables to motors, control cables separate, 750mm depth underground"
    - **Earthing:** "Earthing layout for industrial plant showing earth pits at 4 corners, 25x3mm GI strip connecting all equipment, copper earth rods"
    - **Building elevation:** "Front elevation of pre-engineered steel building 30m x 15m x 8m height, metal roof sheets, wall cladding, roller shutter door 5m wide, ventilation louvers"
    """)


# ── AI Assist ────────────────────────────────────────────────────
try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("AI Assist"):
            if st.button("Generate AI Summary", type="primary", key="ai_56AI"):
                with st.spinner("AI working..."):
                    _p = f"Summarize this section for a {cfg.get('capacity_tpd',20):.0f} TPD bio-bitumen plant in {cfg.get('state','')}. Investment Rs {cfg.get('investment_cr',8):.2f} Cr. Professional consultant format."
                    _r, _pv = ask_ai(_p, "Senior industrial consultant.", 800)
                if _r:
                    st.markdown(_r)
except Exception:
    pass

# Print
if st.sidebar.button("Print", key="prt_56AI"):
    import streamlit.components.v1 as _stc
    _stc.html("<script>window.print();</script>", height=0)
