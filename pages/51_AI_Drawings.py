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

tab_gallery, tab_generate, tab_prompts, tab_custom = st.tabs(["Image Gallery", "Generate New Set", "Prompt Library", "Custom Drawing"])

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
# TAB 3: PROMPT LIBRARY (Combination Engine — zero API calls)
# ═══════════════════════════════════════════════════════════════════
with tab_prompts:
    st.subheader("Drawing Prompt Library — Auto-Generated from Your Config")
    st.caption("These prompts update instantly when you change capacity, process, or state. No API call needed.")

    try:
        from engines.combination_engine import (
            generate_combination_prompt, generate_all_prompts_for_config,
            get_all_combinations_count, TECHNOLOGIES, DRAWING_TYPES, auto_heal_inputs
        )

        st.info(f"**{get_all_combinations_count()} combinations** supported. Current config: "
                f"**{cfg['capacity_tpd']:.0f} TPD** | Process {cfg.get('process_id', 1)} | {cfg.get('state', 'N/A')}")

        # Process selector
        pc1, pc2 = st.columns(2)
        with pc1:
            process_sel = st.selectbox("Technology / Process",
                [1, 2, 3], format_func=lambda x: f"Process {x}: {TECHNOLOGIES[x]['short']}",
                index=cfg.get("process_id", 1) - 1, key="combo_process")
        with pc2:
            cap_sel = st.number_input("Capacity (TPD)", 5, 100,
                int(cfg.get("capacity_tpd", 20)), 5, key="combo_cap")

        # Build config for combination engine
        combo_cfg = dict(cfg)
        combo_cfg["process_id"] = process_sel
        combo_cfg["capacity_tpd"] = cap_sel

        # Generate all 9 prompts
        all_prompts = generate_all_prompts_for_config(combo_cfg)

        st.markdown(f"**{len(all_prompts)} drawing prompts ready** — each with exact specs for {cap_sel} TPD")

        # ── MASTER BUTTON: Generate ALL images at once ──
        if st.button(f"Generate ALL {len(all_prompts)} Drawings (FREE — Pollinations AI)", type="primary", key="gen_all_combo"):
            progress = st.progress(0)
            status = st.empty()
            generated = 0

            for idx, (dt_key, result) in enumerate(all_prompts.items()):
                dt_label = DRAWING_TYPES.get(dt_key, dt_key)
                status.text(f"Generating {idx+1}/{len(all_prompts)}: {dt_label}...")
                progress.progress((idx + 1) / len(all_prompts))

                fname = f"{dt_key}_{int(cap_sel)}TPD_P{process_sel}.png"
                path = generate_with_pollinations(result["prompt"], fname)

                if path:
                    generated += 1
                    st.image(path, caption=f"{dt_label} — {cap_sel} TPD Process {process_sel}", use_container_width=True)
                    with open(path, "rb") as f:
                        st.download_button(f"Download {dt_label}", f.read(), fname, key=f"dlall_{dt_key}")
                else:
                    st.warning(f"Failed: {dt_label}")

            progress.progress(1.0)
            status.text(f"Done! {generated}/{len(all_prompts)} images generated.")
            if generated == len(all_prompts):
                st.success(f"ALL {generated} drawings generated! Scroll down to view and download.")
            st.balloons()

        st.markdown("---")
        st.caption("Or generate individual drawings below:")

        # Show each prompt with individual generate button
        for dt_key, dt_label in DRAWING_TYPES.items():
            result = all_prompts[dt_key]
            with st.expander(f"{dt_label} — {result['char_count']} chars | {result['variables']['machinery_count']} equipment"):
                # Show key specs inline
                v = result["variables"]
                st.markdown(f"**Reactor:** Ø{v['reactor_dia_m']}m × {v['reactor_ht_m']}m × {v['reactor_qty']} | "
                            f"**Dryer:** Ø{v['dryer_dia_m']}m × {v['dryer_len_m']}m | "
                            f"**Plot:** {v['plot_l_m']}m × {v['plot_w_m']}m | "
                            f"**Pipes:** Fire DN{v['fire_pipe_dn']}, Oil DN{v['oil_pipe_dn']}")

                st.code(result["prompt"], language="text")

                # Generate single image
                if st.button(f"Generate This Drawing", key=f"gen1_{dt_key}", type="primary"):
                    with st.spinner(f"Generating {dt_label}..."):
                        fname = f"{dt_key}_{int(cap_sel)}TPD_P{process_sel}.png"
                        path = generate_with_pollinations(result["prompt"], fname)
                        if path:
                            st.image(path, caption=dt_label, use_container_width=True)
                            with open(path, "rb") as f:
                                st.download_button("Download", f.read(), fname, key=f"dl1_{dt_key}")
                        else:
                            st.error("Generation failed. Check internet.")

        # Auto-heal info
        healed = result["healed_inputs"]
        if healed:
            st.warning(f"Auto-healed {len(healed)} missing inputs: {', '.join(healed)}")

    except Exception as e:
        st.error(f"Combination engine error: {e}")

# ═══════════════════════════════════════════════════════════════════
# TAB 4: CUSTOM DRAWING
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
