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

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass


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

if has_key:
    st.success("OpenAI API connected — DALL-E 3 + Pollinations AI ready")
else:
    st.info("Pollinations AI ready (FREE, no key needed). Add OpenAI key in AI Settings for DALL-E 3 option.")

# ── MASTER CONTEXT VALIDATION — Block if critical data missing ────
from engines.master_context import validate_before_generation, get_parameter_popup
is_valid, master_context, missing_popup = validate_before_generation(cfg)

if not is_valid:
    st.error("Missing required project data! Fill these before generating professional layouts:")
    st.markdown(missing_popup)
    st.page_link("pages/10_📝_Project_Setup.py", label="Go to Project Setup", icon="📝")
    st.caption("AI will NOT guess missing values — all inputs must be provided for accurate output")

# Show what data is being used
with st.expander("Project Context — Data used for all AI generations"):
    st.text(master_context[:2000] + "..." if len(master_context) > 2000 else master_context)
    st.caption("This data is prepended to every AI prompt. AI will NEVER guess — it uses only YOUR values.")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# DRAWING REGISTRY — Who needs what
# ══════════════════════════════════════════════════════════════════════
from engines.drawing_master import (DRAWING_REGISTRY, DRAWING_CATEGORIES,
    get_drawings_for_stakeholder, build_prompt_with_context, get_scope_of_work_drawings)

tab_stakeholder, tab_custom, tab_combo, tab_docs, tab_gallery, tab_scope = st.tabs([
    "By Stakeholder", "Custom Layout", "Smart Prompts", "Document Drawings", "Gallery", "Scope of Work"
])

# ── TAB: BY STAKEHOLDER ─────────────────────────────────────────────
with tab_stakeholder:
    st.subheader("Drawings by Stakeholder — Who Needs What")
    st.caption("Select who you're preparing for — see exactly what drawings they need and why")

    stakeholder = st.selectbox("Preparing drawings for:",
        ["Bank", "Investor", "Government", "Engineer", "Contractor"], key="dal_stakeholder")

    drawings = get_drawings_for_stakeholder(stakeholder)

    for d in drawings:
        with st.expander(f"{'🟢' if d['ai_capable'] else '🔴'} {d['name']} — for {d['for_whom']}"):
            st.markdown(f"**Purpose:** {d['purpose']}")
            st.markdown(f"**What it must show:** {d['what_it_shows']}")
            st.markdown(f"**Required for:** {', '.join(d.get('required_for', []))}")
            if d.get("note"):
                st.warning(d["note"])

            if d["ai_capable"]:
                prompt = build_prompt_with_context(d, cfg)
                st.text_area(f"DALL-E Prompt", value=prompt, height=100, key=f"prompt_{d['id']}")

                if st.button(f"Generate {d['name']}", type="primary", key=f"gen_{d['id']}"):
                    with st.spinner(f"Generating {d['name']}... (30-60 seconds)"):
                        img_url, info = generate_layout_image(prompt, "1792x1024")
                    if img_url:
                        st.image(img_url, caption=d['name'], use_container_width=True)
                        st.caption("⚠️ AI-generated image — text labels may be approximate. For precise engineering drawings, use Drawings section.")
                        fname = f"{d['id']}_{int(cfg['capacity_tpd'])}TPD.png"
                        saved = save_layout_image(img_url, fname)
                        if saved:
                            with open(saved, "rb") as f:
                                st.download_button(f"Download", f.read(), fname, "image/png", key=f"dl_{d['id']}")
                    else:
                        st.error(f"Failed: {info}")
            else:
                st.info("This drawing requires a human CAD engineer. AI can generate concept only.")

# ══════════════════════════════════════════════════════════════════════
# TAB: CUSTOM LAYOUT | DOCUMENT DRAWINGS | GALLERY (existing tabs)
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
        plot_length = st.number_input("Plot Length (m)", 20, 200, int(cfg.get('plot_length_m', 120)), 5, key="dal_len")
        plot_width = st.number_input("Plot Width (m)", 15, 100, int(cfg.get('plot_width_m', 80)), 5, key="dal_wid")
        size = st.selectbox("Image Size", ["1792x1024 (Landscape)", "1024x1024 (Square)",
                                            "1024x1792 (Portrait)"], index=0, key="dal_size")
        size_param = size.split(" ")[0]

    # Show COMPUTED equipment specs (not generic list)
    plant = PLANT_MACHINES.get(plant_type, PLANT_MACHINES["Bio-bitumen"])
    st.markdown(f"**Process Flow:** {plant['flow']}")

    if plant_type == "Bio-bitumen":
        try:
            from engines.plant_engineering import compute_all, get_machinery_list
            comp = compute_all(cfg)
            real_machines = get_machinery_list(cfg, comp)
            st.markdown(f"**Equipment ({len(real_machines)} items with COMPUTED specs):**")
            for m in real_machines[:8]:
                st.caption(f"  {m['tag']}: {m['name']} — {m['dims'][:60]}")
            st.markdown(f"**Key Dimensions:** Reactor Ø{comp['reactor_dia_m']}m × {comp['reactor_ht_m']}m | "
                        f"Dryer Ø{comp['dryer_dia_m']}m × {comp['dryer_len_m']}m | "
                        f"Oil Tank Ø{comp['bio_oil_tank_dia_m']}m")
        except Exception:
            st.markdown(f"**Equipment ({len(plant['machines'])} items):** {', '.join(plant['machines'][:10])}")
    else:
        st.markdown(f"**Equipment ({len(plant['machines'])} items):** {', '.join(plant['machines'][:10])}")

    st.markdown(f"**Safety:** {plant['safety_zones']}")

    # Build prompt WITH cfg for computed specs
    prompt = build_dalle_prompt(plant_type, capacity, environment, visual_style,
                                 plot_length, plot_width, cfg=cfg)

    with st.expander("View/Edit Generated Prompt"):
        edited_prompt = st.text_area("DALL-E 3 Prompt", value=prompt, height=200,
                                      key="dal_prompt_edit")
        st.caption(f"Characters: {len(edited_prompt)}/4000")
        if len(edited_prompt) > 4000:
            st.error("Prompt exceeds 4000 character DALL-E limit. Shorten it.")

    st.markdown("---")

    gen_method = st.radio("Generation Method", ["Pollinations AI (FREE, no limits)", "DALL-E 3 (OpenAI, paid)"],
                           index=0, key="gen_method", horizontal=True)

    if st.button("Generate Layout Image", type="primary", key="dal_generate"):
        final_prompt = edited_prompt if edited_prompt != prompt else prompt
        filename = f"{plant_type.replace(' ','_')}_{capacity}TPD_{visual_style.replace(' ','_')}.png"

        if gen_method.startswith("Pollinations"):
            with st.spinner("Generating with Pollinations AI (FREE)... 30-60 seconds"):
                from engines.ai_image_generator import generate_with_pollinations
                path = generate_with_pollinations(final_prompt, filename)
            if path:
                st.success("Layout generated successfully!")
                st.image(path, caption=f"{plant_type} — {capacity} TPD — {visual_style}",
                         use_container_width=True)
                with open(path, "rb") as f:
                    st.download_button("Download Layout Image", f.read(), filename,
                                        "image/png", key="dl_layout")
            else:
                st.error("Generation failed. Check internet connection.")
        else:
            with st.spinner("Generating with DALL-E 3... 30-60 seconds"):
                img_url, info = generate_layout_image(final_prompt, size_param)
            if img_url:
                st.success("Layout generated!")
                st.image(img_url, caption=f"{plant_type} — {capacity} TPD",
                         use_container_width=True)
                saved_path = save_layout_image(img_url, filename)
                if saved_path:
                    with open(saved_path, "rb") as f:
                        st.download_button("Download", f.read(), filename, "image/png", key="dl_layout")
            else:
                st.error(f"DALL-E failed: {info}\n\nTip: Try Pollinations AI instead (FREE, no content filter).")

# ── TAB: SMART PROMPTS (Combination Engine) ─────────────────────────
with tab_combo:
    st.subheader("Smart Drawing Prompts — Auto-Generated from Config")
    st.caption("Change process/capacity → prompts update instantly. No API needed.")

    try:
        from engines.combination_engine import (
            generate_all_prompts_for_config, TECHNOLOGIES, DRAWING_TYPES
        )

        sc1, sc2 = st.columns(2)
        with sc1:
            sp_process = st.selectbox("Process", [1, 2, 3],
                format_func=lambda x: f"P{x}: {TECHNOLOGIES[x]['short']}",
                index=cfg.get("process_id", 1) - 1, key="sp_proc")
        with sc2:
            sp_cap = st.number_input("Capacity", 5, 100,
                int(cfg.get("capacity_tpd", 20)), 5, key="sp_cap")

        sp_cfg = dict(cfg)
        sp_cfg["process_id"] = sp_process
        sp_cfg["capacity_tpd"] = sp_cap

        all_sp = generate_all_prompts_for_config(sp_cfg)

        st.success(f"**{len(all_sp)} prompts ready** | {TECHNOLOGIES[sp_process]['short']} | "
                   f"{sp_cap} TPD | {all_sp['site_layout']['variables']['machinery_count']} equipment | "
                   f"{all_sp['site_layout']['variables']['zone_count']} zones")

        for dt_key, dt_label in DRAWING_TYPES.items():
            r = all_sp[dt_key]
            with st.expander(f"{dt_label} ({r['char_count']} chars)"):
                st.code(r["prompt"], language="text")
                st.caption(f"Reactor: Ø{r['variables']['reactor_dia_m']}m × {r['variables']['reactor_ht_m']}m | "
                           f"Dryer: Ø{r['variables']['dryer_dia_m']}m × {r['variables']['dryer_len_m']}m | "
                           f"Products: {r['variables']['products']}")
    except Exception as e:
        st.error(f"Combination engine: {e}")

# ── TAB: DOCUMENT-SPECIFIC DRAWINGS ─────────────────────────────────
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
            st.caption("⚠️ AI-generated — text labels approximate. Use Drawings section for precise engineering.")

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
        st.info("No AI-generated layouts yet. Use tabs above to generate.")

# ── TAB: SCOPE OF WORK ──────────────────────────────────────────────
with tab_scope:
    st.subheader("Complete Drawing Scope — For Client Proposal")
    st.caption("Include this in your consulting proposal to show the client exactly what drawings you'll provide")

    import pandas as pd
    scope_data = get_scope_of_work_drawings()
    scope_df = pd.DataFrame(scope_data)
    st.dataframe(scope_df, width="stretch", hide_index=True)

    st.markdown(f"""
    ### Drawing Delivery Summary
    - **Total Drawings:** {len(DRAWING_REGISTRY)}
    - **AI-Generated (Concept):** {sum(1 for d in DRAWING_REGISTRY if d['ai_capable'])} drawings
    - **Human CAD Required:** {sum(1 for d in DRAWING_REGISTRY if not d['ai_capable'])} drawings
    - **For Bank/Investor:** {len(get_drawings_for_stakeholder('Bank'))} drawings
    - **For Government:** {len(get_drawings_for_stakeholder('Government'))} drawings
    - **For Engineers:** {len(get_drawings_for_stakeholder('Engineer'))} drawings
    - **For Contractors:** {len(get_drawings_for_stakeholder('Contractor'))} drawings

    ### Important Note for Client:
    AI-generated drawings are **CONCEPT STAGE** — professional quality for presentations,
    bank proposals, and initial approvals. For actual **CONSTRUCTION**, these concepts
    will be converted to precise CAD drawings by a licensed engineer.
    """)

    # Export scope as Excel
    if st.button("Download Scope as Excel", type="primary", key="dl_scope"):
        import io
        buf = io.BytesIO()
        scope_df.to_excel(buf, index=False, sheet_name="Drawing Scope")
        buf.seek(0)
        st.download_button("Download", buf.getvalue(), "Drawing_Scope_of_Work.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_scope_xl")

st.markdown("---")
st.caption(f"{COMPANY['name']} | AI Layout Engine — Powered by OpenAI DALL-E 3")

# Print
if st.sidebar.button("Print", key="prt_73AI"):
    import streamlit.components.v1 as _stc
    _stc.html("<script>window.print();</script>", height=0)


# ── Next Steps Navigation ──
try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "52")
except Exception:
    pass
