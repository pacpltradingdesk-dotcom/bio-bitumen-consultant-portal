"""
Document Hub — Client-Personalized Generation & Download Center (UPGRADED)
===========================================================================
Select client → All documents auto-personalize → One-click export
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import io
import zipfile
from pathlib import Path
from state_manager import get_config, update_fields, init_state
from database import init_db, get_report_generations, get_all_customers
from config import COMPANY

st.set_page_config(page_title="Document Hub", page_icon="📁", layout="wide")
init_db()
init_state()
cfg = get_config()

st.sidebar.markdown("---")
if st.sidebar.button("Print This Page", key="print_page"):
    import streamlit.components.v1 as _stc; _stc.html('<script>window.print();</script>', height=0)

st.title("Document Hub — Personalized Generation & Export")
st.markdown("**Set Client Info → Generate ALL Formats → Download Submission-Ready Package**")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# PROJECT INFO PANEL (shows current client or prompts to fill)
# ══════════════════════════════════════════════════════════════════════
client_name = cfg.get("client_name", "")
project_name = cfg.get("project_name", "")
site_address = cfg.get("site_address", "")

# Master Context Validation — block if critical data missing
try:
    from engines.master_context import validate_before_generation
    _valid, _ctx, _missing = validate_before_generation(cfg)
    if not _valid:
        st.error("Missing required project data for professional document output:")
        st.markdown(_missing)
        st.page_link("pages/03_📝_Project_Setup.py", label="Fill Project Setup", icon="📝")
except Exception:
    pass

# Contradiction Alerts — show BEFORE any document generation
try:
    from utils.contradiction_alerts import show_alerts, get_readiness_score
    errs, warns, infos = show_alerts(cfg, show_info=False)
    score, details = get_readiness_score(cfg)
    st.markdown(f"""
    <div style="background: {'#00AA44' if score >= 80 else '#FF8800' if score >= 50 else '#CC3333'}15;
                border: 2px solid {'#00AA44' if score >= 80 else '#FF8800' if score >= 50 else '#CC3333'};
                border-radius: 10px; padding: 10px 15px; margin-bottom: 10px; text-align: center;">
        <strong>Submission Readiness: {score}/100</strong> —
        {'Ready for Bank Submission' if score >= 80 else 'Some issues need fixing' if score >= 50 else 'Not ready — fix errors first'}
    </div>
    """, unsafe_allow_html=True)
except Exception:
    pass

if client_name and project_name:
    st.markdown(f"""
    <div style="background: #00336610; border: 2px solid #003366; border-radius: 12px;
                padding: 15px 20px; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="color: #003366; margin: 0;">Generating for: {client_name}</h4>
                <p style="margin: 2px 0; color: #666;">Project: {project_name} | {cfg.get('location', '')}, {cfg.get('state', '')} | {cfg['capacity_tpd']:.0f} TPD</p>
            </div>
            <span style="background: #00AA44; color: white; padding: 4px 12px; border-radius: 15px;">Client Set</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("**No client/project info set.** Documents will be generated with generic information.")
    lc1, lc2 = st.columns(2)

    # Quick load from CRM
    customers = get_all_customers()
    with lc1:
        if customers:
            cust_map = {0: "-- Select Customer --"}
            cust_map.update({c["id"]: f"{c['name']} ({c.get('company', '')})" for c in customers})
            sel_cust = st.selectbox("Load from CRM", list(cust_map.keys()),
                                     format_func=lambda x: cust_map[x], key="hub_load_cust")
            if sel_cust and sel_cust != 0:
                cust = next(c for c in customers if c["id"] == sel_cust)
                if st.button("Load This Customer", key="hub_load_btn"):
                    update_fields({
                        "client_name": cust.get("name", ""),
                        "client_company": cust.get("company", ""),
                        "client_email": cust.get("email", ""),
                        "client_phone": cust.get("phone", ""),
                        "state": cust.get("state", cfg["state"]),
                        "location": cust.get("city", cfg["location"]),
                    })
                    st.rerun()

    with lc2:
        st.page_link("pages/03_📝_Project_Setup.py", label="Go to Full Project Setup", icon="📝")
        st.caption("Set client name, project name, site address, and all details")

st.markdown("---")

# Helper: get project info dict for generators
def get_project_info():
    return {
        "client_name": cfg.get("client_name", ""),
        "client_company": cfg.get("client_company", ""),
        "project_name": cfg.get("project_name", ""),
        "site_address": cfg.get("site_address", ""),
        "site_pincode": cfg.get("site_pincode", ""),
        "project_id": cfg.get("project_id", ""),
    }

# File name prefix
client_prefix = cfg.get("client_name", "").replace(" ", "_")[:20] or "Bio_Bitumen"

# ══════════════════════════════════════════════════════════════════════
# INDIVIDUAL DOCUMENT GENERATION
# ══════════════════════════════════════════════════════════════════════
st.subheader(f"Generate Documents — {cfg['capacity_tpd']:.0f} TPD")

gen_col1, gen_col2 = st.columns(2)

with gen_col1:
    st.markdown("**Business Documents**")

    if st.button("Generate DPR (DOCX)", key="gen_dpr", type="primary"):
        try:
            from engines.dynamic_doc_generator import generate_dpr_docx
            doc = generate_dpr_docx(cfg, COMPANY)
            buf = io.BytesIO()
            doc.save(buf)
            buf.seek(0)
            st.success("DPR generated with client info!")
            st.download_button("Download DPR.docx", buf.getvalue(),
                                f"{client_prefix}_DPR_{cfg['capacity_tpd']:.0f}TPD.docx",
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key="dl_dpr")
        except Exception as e:
            st.error(f"DPR generation failed: {e}")

    if st.button("Generate Bank Proposal (DOCX)", key="gen_bank"):
        try:
            from engines.dynamic_doc_generator import generate_bank_proposal_docx
            customer = {"name": client_name, "company": cfg.get("client_company", "")} if client_name else None
            doc = generate_bank_proposal_docx(cfg, COMPANY, customer)
            buf = io.BytesIO()
            doc.save(buf)
            buf.seek(0)
            st.success("Bank Proposal generated!")
            st.download_button("Download Bank_Proposal.docx", buf.getvalue(),
                                f"{client_prefix}_Bank_Proposal_{cfg['capacity_tpd']:.0f}TPD.docx",
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key="dl_bank")
        except Exception as e:
            st.error(f"Bank Proposal generation failed: {e}")

    if st.button("Generate Investor Pitch (PPTX)", key="gen_pptx"):
        try:
            from engines.dynamic_doc_generator import generate_investor_pptx
            pptx = generate_investor_pptx(cfg, COMPANY)
            buf = io.BytesIO()
            pptx.save(buf)
            buf.seek(0)
            st.success("Investor Pitch generated!")
            st.download_button("Download Investor_Pitch.pptx", buf.getvalue(),
                                f"{client_prefix}_Investor_Pitch_{cfg['capacity_tpd']:.0f}TPD.pptx",
                                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                key="dl_pptx")
        except Exception as e:
            st.error(f"Investor Pitch generation failed: {e}")

    # AI DPR Writer
    try:
        from engines.ai_engine import is_ai_available, ai_write_dpr_section, ai_auto_report
        if is_ai_available():
            st.markdown("---")
            st.markdown("**AI-Powered Writing**")
            ai_section = st.selectbox("AI Write Section",
                ["executive_summary", "market_analysis", "technical_description",
                 "risk_assessment", "compliance_narrative"], key="ai_section",
                format_func=lambda x: x.replace("_", " ").title())
            if st.button("Generate with AI", key="ai_write"):
                with st.spinner("AI writing..."):
                    text, provider = ai_auto_report(ai_section, cfg, COMPANY)
                if text:
                    st.markdown(text)
                    st.download_button("Download AI Text", text,
                                        f"AI_{ai_section}_{client_prefix}.txt", "text/plain", key="dl_ai_text")
    except Exception:
        pass

with gen_col2:
    st.markdown("**Financial & Technical Documents**")

    if st.button("Generate Financial Model (XLSX)", key="gen_xlsx"):
        try:
            from engines.dynamic_doc_generator import generate_financial_xlsx
            wb = generate_financial_xlsx(cfg, COMPANY)
            buf = io.BytesIO()
            wb.save(buf)
            buf.seek(0)
            st.success("Financial Model generated!")
            st.download_button("Download Financial_Model.xlsx", buf.getvalue(),
                                f"{client_prefix}_Financial_{cfg['capacity_tpd']:.0f}TPD.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key="dl_xlsx")
        except Exception as e:
            st.error(f"Financial Model generation failed: {e}")

    if st.button("Generate DPR PDF", key="gen_pdf"):
        try:
            from engines.report_generator_engine import generate_dpr_pdf
            pdf_path = os.path.join(os.path.dirname(__file__), "..", "data", "test_outputs",
                                     f"{client_prefix}_DPR.pdf")
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            generate_dpr_pdf(pdf_path, cfg, COMPANY)
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.success("DPR PDF generated!")
                st.download_button("Download DPR.pdf", pdf_bytes,
                                    f"{client_prefix}_DPR_{cfg['capacity_tpd']:.0f}TPD.pdf",
                                    "application/pdf", key="dl_pdf")
        except Exception as e:
            st.error(f"PDF generation failed: {e}")

    if st.button("Generate Quotation PDF", key="gen_quote"):
        try:
            from engines.pdf_quotation_engine import generate_quotation_pdf
            from interpolation_engine import get_all_known_plants
            import pandas as _pd

            plants = get_all_known_plants()
            cap_key = f"{int(cfg['capacity_tpd']):02d}MT"
            plant_data = plants.get(cap_key, {})

            customer_data = {"name": client_name or "Customer",
                              "company": cfg.get("client_company", ""),
                              "city": cfg.get("location", ""),
                              "state": cfg.get("state", "")}

            pdf_path = os.path.join(os.path.dirname(__file__), "..", "data", "test_outputs",
                                     f"{client_prefix}_Quotation.pdf")
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            roi_df = _pd.DataFrame(cfg.get("roi_timeline", [])) if cfg.get("roi_timeline") else None
            generate_quotation_pdf(pdf_path, customer_data, plant_data,
                                    roi_df=roi_df, company=COMPANY)
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.success("Quotation generated!")
                st.download_button("Download Quotation.pdf", pdf_bytes,
                                    f"{client_prefix}_Quotation_{cfg['capacity_tpd']:.0f}TPD.pdf",
                                    "application/pdf", key="dl_quote")
        except Exception as e:
            st.error(f"Quotation generation failed: {e}")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# GENERATE ALL + ZIP
# ══════════════════════════════════════════════════════════════════════
st.subheader("Generate Complete Package (All Formats)")

if st.button("GENERATE ALL DOCUMENTS — ZIP DOWNLOAD", type="primary", key="gen_all_zip"):
    progress = st.progress(0)
    status = st.empty()
    all_docs = {}
    errors = []

    # 1. DPR DOCX
    status.text("Generating DPR (DOCX)...")
    progress.progress(0.1)
    try:
        from engines.dynamic_doc_generator import generate_dpr_docx
        doc = generate_dpr_docx(cfg, COMPANY)
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        all_docs[f"{client_prefix}_DPR_{cfg['capacity_tpd']:.0f}TPD.docx"] = buf.getvalue()
    except Exception as e:
        errors.append(f"DPR: {e}")

    # 2. Bank Proposal
    status.text("Generating Bank Proposal (DOCX)...")
    progress.progress(0.25)
    try:
        from engines.dynamic_doc_generator import generate_bank_proposal_docx
        customer = {"name": client_name, "company": cfg.get("client_company", "")} if client_name else None
        doc = generate_bank_proposal_docx(cfg, COMPANY, customer)
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        all_docs[f"{client_prefix}_Bank_Proposal_{cfg['capacity_tpd']:.0f}TPD.docx"] = buf.getvalue()
    except Exception as e:
        errors.append(f"Bank: {e}")

    # 3. Investor Pitch
    status.text("Generating Investor Pitch (PPTX)...")
    progress.progress(0.4)
    try:
        from engines.dynamic_doc_generator import generate_investor_pptx
        pptx = generate_investor_pptx(cfg, COMPANY)
        buf = io.BytesIO(); pptx.save(buf); buf.seek(0)
        all_docs[f"{client_prefix}_Investor_Pitch_{cfg['capacity_tpd']:.0f}TPD.pptx"] = buf.getvalue()
    except Exception as e:
        errors.append(f"PPTX: {e}")

    # 4. Financial Model
    status.text("Generating Financial Model (XLSX)...")
    progress.progress(0.55)
    try:
        from engines.dynamic_doc_generator import generate_financial_xlsx
        wb = generate_financial_xlsx(cfg, COMPANY)
        buf = io.BytesIO(); wb.save(buf); buf.seek(0)
        all_docs[f"{client_prefix}_Financial_{cfg['capacity_tpd']:.0f}TPD.xlsx"] = buf.getvalue()
    except Exception as e:
        errors.append(f"XLSX: {e}")

    # 5. DPR PDF
    status.text("Generating DPR (PDF)...")
    progress.progress(0.7)
    try:
        from engines.report_generator_engine import generate_dpr_pdf
        pdf_path = os.path.join(os.path.dirname(__file__), "..", "data", "test_outputs", "_temp_dpr.pdf")
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        generate_dpr_pdf(pdf_path, cfg, COMPANY)
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                all_docs[f"{client_prefix}_DPR_{cfg['capacity_tpd']:.0f}TPD.pdf"] = f.read()
    except Exception as e:
        errors.append(f"PDF: {e}")

    # 6. Quotation PDF
    status.text("Generating Quotation (PDF)...")
    progress.progress(0.85)
    try:
        from engines.pdf_quotation_engine import generate_quotation_pdf
        from interpolation_engine import get_all_known_plants
        import pandas as _pd

        plants = get_all_known_plants()
        cap_key = f"{int(cfg['capacity_tpd']):02d}MT"
        plant_data = plants.get(cap_key, {})
        customer_data = {"name": client_name or "Customer",
                          "company": cfg.get("client_company", ""),
                          "city": cfg.get("location", ""), "state": cfg.get("state", "")}
        pdf_path2 = os.path.join(os.path.dirname(__file__), "..", "data", "test_outputs", "_temp_quote.pdf")
        roi_df = _pd.DataFrame(cfg.get("roi_timeline", [])) if cfg.get("roi_timeline") else None
        generate_quotation_pdf(pdf_path2, customer_data, plant_data, roi_df=roi_df, company=COMPANY)
        if os.path.exists(pdf_path2):
            with open(pdf_path2, "rb") as f:
                all_docs[f"{client_prefix}_Quotation_{cfg['capacity_tpd']:.0f}TPD.pdf"] = f.read()
    except Exception as e:
        errors.append(f"Quote: {e}")

    # Create ZIP
    status.text("Creating ZIP package...")
    progress.progress(0.95)

    if all_docs:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename, content in all_docs.items():
                zf.writestr(filename, content)
        zip_buf.seek(0)

        progress.progress(1.0)
        status.text(f"Complete! {len(all_docs)} documents generated.")

        st.download_button(
            f"DOWNLOAD COMPLETE PACKAGE ({len(all_docs)} files)",
            zip_buf.getvalue(),
            f"{client_prefix}_{cfg['capacity_tpd']:.0f}TPD_Complete_Package.zip",
            "application/zip",
            key="dl_zip_all"
        )

        if errors:
            st.warning(f"{len(errors)} documents had issues: {'; '.join(errors)}")
        else:
            st.success("All documents generated successfully — submission ready!")
    else:
        st.error("No documents generated. Check error details above.")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# QUALITY CHECKLIST
# ══════════════════════════════════════════════════════════════════════
st.subheader("Document Quality Checklist")

checks = [
    ("Client name set", bool(cfg.get("client_name"))),
    ("Project name set", bool(cfg.get("project_name"))),
    ("Site address provided", bool(cfg.get("site_address"))),
    ("Plant capacity configured", cfg.get("capacity_tpd", 0) > 0),
    ("Financial model calculated", cfg.get("roi_pct", 0) > 0),
    ("7-year P&L complete", len(cfg.get("roi_timeline", [])) == 7),
    ("DSCR above 1.5x", cfg.get("dscr_yr3", 0) >= 1.5),
    ("State/location selected", bool(cfg.get("state"))),
    ("Break-even calculated", cfg.get("break_even_months", 0) > 0),
    ("Investment breakdown ready", cfg.get("investment_cr", 0) > 0),
]

passed = sum(1 for _, ok in checks if ok)
st.progress(passed / len(checks))
st.metric("Readiness", f"{passed}/{len(checks)} checks passed ({passed*100//len(checks)}%)")

for name, ok in checks:
    st.markdown(f"{'✅' if ok else '❌'} {name}")

if passed < len(checks):
    missing = [name for name, ok in checks if not ok]
    st.info(f"Complete these to get 100% submission-ready documents: {', '.join(missing)}")

st.markdown("---")
st.caption(f"{COMPANY['name']} | Document Hub | Client-personalized professional output")

# ══════════════════════════════════════════════════════════════════════
# AI DOCUMENT SKILLS — Generate specialized content
# ══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("AI-Powered Document Generation")

try:
    from engines.ai_engine import is_ai_available
    if is_ai_available():
        from engines.ai_skills import generate_investor_deck_content, generate_financial_projection_json, format_site_report
        from config import COMPANY as _COMP

        doc_skill1, doc_skill2, doc_skill3 = st.tabs(["💼 Investor Deck", "📊 AI Financial Projection", "🏗️ Site Report"])

        with doc_skill1:
            st.caption("Generate 10-slide investor presentation content")
            if st.button("Generate Investor Deck", type="primary", key="gen_inv_deck"):
                with st.spinner("AI creating investor presentation... (30 seconds)"):
                    result, prov = generate_investor_deck_content(cfg, _COMP)
                if result:
                    st.markdown(result)
                    st.download_button("Download Deck Content", result, "Investor_Deck_Content.txt", "text/plain", key="dl_deck")

        with doc_skill2:
            st.caption("AI generates 5-year projection as structured data")
            if st.button("Generate AI Financial Projection", type="primary", key="gen_ai_fin"):
                with st.spinner("AI generating financial projection..."):
                    data, prov = generate_financial_projection_json(cfg)
                if data:
                    import pandas as pd
                    st.json(data)
                    if "yearly" in data:
                        st.dataframe(pd.DataFrame(data["yearly"]), width="stretch", hide_index=True)
                else:
                    st.warning("Could not generate structured projection. Try again.")

        with doc_skill3:
            st.caption("Paste raw site notes → get formal daily progress report")
            site_notes = st.text_area("Raw site notes:", height=120, key="site_notes_hub",
                placeholder="Today poured concrete for reactor foundation. Cement truck 2 hrs late. Tomorrow start tank walls.")
            if st.button("Generate Site Report", type="primary", key="gen_site_rpt") and site_notes:
                with st.spinner("AI formatting site report..."):
                    result, prov = format_site_report(site_notes, cfg)
                if result:
                    st.markdown(result)
                    st.download_button("Download Report", result, "Site_Progress_Report.txt", "text/plain", key="dl_site_rpt")
    else:
        st.info("Add API keys in AI Settings for AI document generation")
except Exception:
    pass
