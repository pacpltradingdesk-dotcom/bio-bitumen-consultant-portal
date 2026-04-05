"""
AI Plant Layout Generator — Professional 3D Layouts via DALL-E 3
=================================================================
Generates presentation-ready industrial plant visualizations.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from state_manager import get_config, init_state
from config import COMPANY
from engines.dalle_layout_engine import (
    PLANT_MACHINES, VISUAL_STYLES, ENVIRONMENTS, DOC_PROMPTS,
    build_dalle_prompt, build_doc_prompt, generate_layout_image,
    save_layout_image, get_saved_layouts
)

st.set_page_config(page_title="AI Plant Layouts", page_icon="🏗️", layout="wide")
init_state()
cfg = get_config()

st.title("AI Plant Layout Generator")
st.markdown("**Professional 3D Industrial Layouts — Powered by OpenAI DALL-E 3**")
st.caption("Generate presentation-ready plant visualizations for investor decks, bank proposals, and client meetings")
st.markdown("---")

# Check API key
try:
    from engines.ai_engine import load_ai_config
    ai_cfg = load_ai_config()
    has_key = bool(ai_cfg.get("openai_key"))
except Exception:
    has_key = False

if not has_key:
    st.error("OpenAI API key required for DALL-E 3 image generation. Go to AI Settings to add your key.")
    st.page_link("pages/17_🔑_AI_Settings.py", label="Go to AI Settings", icon="🔑")
    st.stop()

st.success("OpenAI API connected — DALL-E 3 ready")

# ══════════════════════════════════════════════════════════════════════
# TAB 1: CUSTOM LAYOUT | TAB 2: DOCUMENT DRAWINGS | TAB 3: GALLERY
# ══════════════════════════════════════════════════════════════════════
tab_custom, tab_docs, tab_gallery = st.tabs(["Custom Layout", "Document Drawings", "Gallery"])

# ── TAB 1: CUSTOM LAYOUT ────────────────────────────────────────────
with tab_custom:
    st.subheader("Generate Custom Plant Layout")

    col1, col2 = st.columns(2)
    with col1:
        plant_type = st.selectbox("Plant Type", list(PLANT_MACHINES.keys()),
                                   index=0, key="dal_plant")
        capacity = st.number_input("Capacity (TPD)", 5, 100,
                                    int(cfg["capacity_tpd"]), 5, key="dal_cap")
        visual_style = st.selectbox("Visual Style", list(VISUAL_STYLES.keys()),
                                     index=0, key="dal_style")
        environment = st.selectbox("Environment", list(ENVIRONMENTS.keys()),
                                    index=0, key="dal_env")

    with col2:
        plot_length = st.number_input("Plot Length (m)", 20, 200, 60, 5, key="dal_len")
        plot_width = st.number_input("Plot Width (m)", 15, 100, 35, 5, key="dal_wid")
        size = st.selectbox("Image Size", ["1792x1024 (Landscape)", "1024x1024 (Square)",
                                            "1024x1792 (Portrait)"], index=0, key="dal_size")
        size_param = size.split(" ")[0]

    # Show machine list
    plant = PLANT_MACHINES.get(plant_type, PLANT_MACHINES["Bio-bitumen"])
    st.markdown(f"**Process Flow:** {plant['flow']}")
    st.markdown(f"**Equipment ({len(plant['machines'])} items):** {', '.join(plant['machines'][:10])}")
    st.markdown(f"**Safety:** {plant['safety_zones']}")

    # Build prompt
    prompt = build_dalle_prompt(plant_type, capacity, environment, visual_style,
                                 plot_length, plot_width)

    with st.expander("View/Edit Generated Prompt"):
        edited_prompt = st.text_area("DALL-E 3 Prompt", value=prompt, height=200,
                                      key="dal_prompt_edit")
        st.caption(f"Characters: {len(edited_prompt)}/4000")
        if len(edited_prompt) > 4000:
            st.error("Prompt exceeds 4000 character DALL-E limit. Shorten it.")

    st.markdown("---")

    if st.button("Generate Layout Image", type="primary", key="dal_generate"):
        with st.spinner("Generating layout with DALL-E 3... (30-60 seconds)"):
            final_prompt = edited_prompt if edited_prompt != prompt else prompt
            img_url, info = generate_layout_image(final_prompt, size_param)

        if img_url:
            st.success("Layout generated successfully!")
            st.image(img_url, caption=f"{plant_type} — {capacity} TPD — {visual_style}",
                     use_container_width=True)

            # Save button
            filename = f"{plant_type.replace(' ','_')}_{capacity}TPD_{visual_style.replace(' ','_')}.png"
            saved_path = save_layout_image(img_url, filename)
            if saved_path:
                st.success(f"Saved to: {filename}")
                with open(saved_path, "rb") as f:
                    st.download_button("Download Layout Image", f.read(), filename,
                                        "image/png", key="dl_layout")

            if info:
                with st.expander("DALL-E Revised Prompt"):
                    st.text(info)
        else:
            st.error(f"Generation failed: {info}")

# ── TAB 2: DOCUMENT-SPECIFIC DRAWINGS ───────────────────────────────
with tab_docs:
    st.subheader("Generate Document-Specific Drawings")
    st.caption("Professional engineering drawings for DPR, bank proposals, and compliance submissions")

    doc_type = st.selectbox("Drawing Type", list(DOC_PROMPTS.keys()), key="dal_doc_type")

    doc_prompt = build_doc_prompt(doc_type, plant_type, int(cfg["capacity_tpd"]),
                                   plot_length, plot_width)

    st.markdown(f"**Drawing:** {doc_type}")
    st.markdown(f"**For:** {cfg['capacity_tpd']:.0f} TPD {plant_type} Plant")

    with st.expander("View/Edit Prompt"):
        doc_edited = st.text_area("Prompt", value=doc_prompt, height=150, key="dal_doc_prompt")
        st.caption(f"Characters: {len(doc_edited)}/4000")

    if st.button(f"Generate {doc_type}", type="primary", key="dal_doc_gen"):
        with st.spinner(f"Generating {doc_type}... (30-60 seconds)"):
            img_url, info = generate_layout_image(doc_edited, "1792x1024")

        if img_url:
            st.success(f"{doc_type} generated!")
            st.image(img_url, caption=doc_type, use_container_width=True)

            fname = f"{doc_type.replace(' ','_').replace('(','').replace(')','')}" \
                    f"_{int(cfg['capacity_tpd'])}TPD.png"
            saved = save_layout_image(img_url, fname)
            if saved:
                with open(saved, "rb") as f:
                    st.download_button(f"Download {doc_type}", f.read(), fname,
                                        "image/png", key="dl_doc_drawing")
        else:
            st.error(f"Failed: {info}")

    # Generate ALL drawings button
    st.markdown("---")
    if st.button("Generate ALL 8 Drawing Types", key="dal_gen_all"):
        progress = st.progress(0)
        status = st.empty()
        generated = 0

        for i, (dtype, _) in enumerate(DOC_PROMPTS.items()):
            status.text(f"Generating {dtype}... ({i+1}/{len(DOC_PROMPTS)})")
            progress.progress((i + 1) / len(DOC_PROMPTS))

            dp = build_doc_prompt(dtype, plant_type, int(cfg["capacity_tpd"]))
            img_url, info = generate_layout_image(dp, "1792x1024")

            if img_url:
                fname = f"{dtype.replace(' ','_').replace('(','').replace(')','')}" \
                        f"_{int(cfg['capacity_tpd'])}TPD.png"
                save_layout_image(img_url, fname)
                generated += 1

        status.text(f"Done! Generated {generated}/{len(DOC_PROMPTS)} drawings")
        st.success(f"All drawings saved to gallery. {generated} generated successfully.")

# ── TAB 3: GALLERY ──────────────────────────────────────────────────
with tab_gallery:
    st.subheader("Generated Layout Gallery")

    layouts = get_saved_layouts()
    if layouts:
        st.metric("Total Layouts", len(layouts))
        for i, layout in enumerate(layouts):
            with st.expander(f"{layout['name']} ({layout['size_kb']:.0f} KB)"):
                try:
                    st.image(layout["path"], use_container_width=True)
                    with open(layout["path"], "rb") as f:
                        st.download_button(f"Download {layout['name']}", f.read(),
                                            f"{layout['name']}.png", "image/png",
                                            key=f"dl_gallery_{i}")
                except Exception:
                    st.warning(f"Cannot display: {layout['name']}")
    else:
        st.info("No AI-generated layouts yet. Use Custom Layout or Document Drawings tab to generate.")

st.markdown("---")
st.caption(f"{COMPANY['name']} | AI Layout Engine — Powered by OpenAI DALL-E 3")
