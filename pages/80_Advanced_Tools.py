"""
Advanced Tools — Bank Forms, Maps, QR Codes, Video, Mobile Test
================================================================
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import io
from state_manager import get_config, init_state
from config import COMPANY

st.set_page_config(page_title="Advanced Tools", page_icon="🔧", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.title("Advanced Tools")
st.markdown("**Bank Forms | Map View | QR Codes | Video Script | Mobile Test**")
st.markdown("---")

tab_bank, tab_map, tab_qr, tab_video = st.tabs([
    "🏦 Bank Forms", "🗺️ Map View", "📱 QR Codes", "🎬 Video Script"
])

# ═══ BANK FORMS ═══
with tab_bank:
    st.subheader("Bank Application Auto-Fill")
    st.caption("Auto-filled from your Project Setup — download and submit to bank")

    bank_type = st.selectbox("Select Bank Form", ["SBI MSME Term Loan", "CGTMSE Guarantee"], key="bank_form")

    if st.button("Generate Application", type="primary", key="gen_bank_form"):
        with st.spinner(f"Generating {bank_type} application..."):
            try:
                from engines.bank_forms import BANK_FORMS
                gen_func = BANK_FORMS.get(bank_type)
                if gen_func:
                    doc = gen_func(cfg, COMPANY)
                    buf = io.BytesIO()
                    doc.save(buf)
                    buf.seek(0)
                    fname = f"{bank_type.replace(' ', '_')}_Application.docx"
                    st.success(f"{bank_type} application generated with your project data!")
                    st.download_button(f"Download {bank_type}", buf.getvalue(), fname,
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="dl_bank_form")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("""
    **What's auto-filled from your project data:**
    - Client name, company, GST, PAN
    - Plant capacity, location, investment
    - Loan amount, interest rate, tenure
    - Financial projections (ROI, IRR, DSCR)
    - CGTMSE eligibility status
    - Document checklist
    """)

# ═══ MAP VIEW ═══
with tab_map:
    st.subheader("Plant Location & Biomass Sources")

    try:
        from engines.maps_engine import get_plant_map_data, get_streamlit_map_df
        map_data = get_plant_map_data(cfg)
        map_df = get_streamlit_map_df(cfg)

        st.markdown(f"**Plant Location:** {map_data['city']}, {map_data['state']}")
        st.map(map_df, zoom=8)

        # Show biomass sources
        if map_data["biomass_sources"]:
            st.subheader("Nearby Biomass Sources")
            import pandas as pd
            src_df = pd.DataFrame(map_data["biomass_sources"])
            st.dataframe(src_df, width="stretch", hide_index=True)
        else:
            st.info("No biomass source data for this location yet")

        # Points legend
        st.markdown("""
        **Map Legend:**
        - Red: Plant Location
        - Green: Biomass Sources (within 100 km)
        - Blue: NHAI Regional Office
        """)
    except Exception as e:
        st.error(f"Map error: {e}")

# ═══ QR CODES ═══
with tab_qr:
    st.subheader("QR Code for Document Verification")
    st.caption("Add QR code to your documents — links to project verification data")

    try:
        from engines.qr_engine import generate_project_qr, QR_AVAILABLE
        if QR_AVAILABLE:
            qr_bytes = generate_project_qr(cfg)
            if qr_bytes:
                st.image(qr_bytes, caption="Project Verification QR Code", width=200)
                st.download_button("Download QR Code PNG", qr_bytes, "project_qr.png", "image/png", key="dl_qr")

                st.markdown("""
                **How to use:**
                1. Download the QR code above
                2. Insert into your DPR, Bank Proposal, or Quotation
                3. When scanned, it shows project verification data
                4. Adds credibility — proves documents are authentic
                """)
            else:
                st.warning("Could not generate QR code")
        else:
            st.warning("QR code library not installed. Run: `pip install qrcode[pil]`")
            st.code("pip install qrcode[pil]", language="bash")
    except Exception as e:
        st.info(f"QR code feature requires: `pip install qrcode[pil]` — {e}")

# ═══ VIDEO SCRIPT ═══
with tab_video:
    st.subheader("Plant Walkthrough Video Generator")
    st.caption("AI generates 60-second narration script + storyboard matching your drawings")

    try:
        from engines.ai_engine import is_ai_available
        from engines.video_engine import generate_walkthrough_script, generate_storyboard, get_video_creation_guide

        # Storyboard (always available)
        st.markdown("### Storyboard")
        storyboard = generate_storyboard(cfg)
        import pandas as pd
        sb_df = pd.DataFrame(storyboard)
        st.dataframe(sb_df[["shot", "duration", "description", "camera"]], width="stretch", hide_index=True)

        # AI Script (needs API key)
        if is_ai_available():
            if st.button("Generate AI Narration Script", type="primary", key="gen_video_script"):
                with st.spinner("AI writing 60-second narration script..."):
                    script, provider = generate_walkthrough_script(cfg, COMPANY)
                if script:
                    st.markdown("### Narration Script")
                    st.markdown(script)
                    st.download_button("Download Script", script, "walkthrough_script.txt", "text/plain", key="dl_script")
        else:
            st.info("Add API keys in AI Settings to generate narration script")

        # Video creation guide
        with st.expander("How to Create the Video (FREE methods)"):
            st.markdown(get_video_creation_guide())

    except Exception as e:
        st.error(f"Video engine error: {e}")

st.markdown("---")
st.caption(f"{COMPANY['name']} | Advanced Tools")


# ── Next Steps Navigation ──
try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "80")
except Exception:
    pass
