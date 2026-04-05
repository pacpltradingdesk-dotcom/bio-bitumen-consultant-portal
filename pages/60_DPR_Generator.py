"""
Client Presentation & Document Generator
==========================================
ONE-CLICK generation of ALL document types for ANY capacity.
DPR (DOCX) + Bank Proposal (DOCX) + Investor Pitch (PPTX) + Financial Model (XLSX) + Quotation (PDF)
ALL use current dashboard config — change anything, documents auto-update.
"""
import sys, os, io
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from state_manager import get_config, init_state
from database import init_db, get_all_customers, get_customer, insert_report_generation
from engines.dynamic_doc_generator import (
    generate_dpr_docx, generate_bank_proposal_docx,
    generate_investor_pptx, generate_financial_xlsx,
    generate_all_documents,
)
from engines.report_generator_engine import generate_dpr_pdf, generate_financial_report_pdf
from config import COMPANY

st.set_page_config(page_title="Document Generator", page_icon="📄", layout="wide")
init_db()
init_state()
st.title("Document Generator (Auto-Updated)")
st.markdown("**One-click generation for ANY capacity — ALL documents use current config**")
st.markdown("---")

cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass


# ── Current Config Display ────────────────────────────────────────────
st.info(
    f"**Current Config:** {cfg['capacity_tpd']:.0f} MT/Day | "
    f"Rs {cfg['investment_cr']:.2f} Cr | "
    f"ROI {cfg['roi_pct']:.1f}% | "
    f"IRR {cfg['irr_pct']:.1f}% | "
    f"DSCR {cfg['dscr_yr3']:.2f}x | "
    f"{cfg.get('state', '')} | "
    f"{'Bitumen' if cfg['product_model'] == 'bitumen' else 'Oil+Char'}"
)
st.caption("Change any input in Plant Design or Financial Model → documents auto-reflect new values")

# ── Customer Selection ────────────────────────────────────────────────
customers = get_all_customers()
customer = None
if customers:
    cust_map = {c["id"]: f"{c['name']} ({c.get('company', '')})" for c in customers}
    cust_id = st.selectbox("Generate for Customer", [None] + list(cust_map.keys()),
                            format_func=lambda x: cust_map.get(x, "General (no specific customer)"))
    if cust_id:
        customer = get_customer(cust_id)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# INDIVIDUAL DOCUMENT GENERATION
# ═══════════════════════════════════════════════════════════════════
st.subheader("Generate Individual Documents")

col1, col2, col3 = st.columns(3)

# ── DPR (DOCX) ────────────────────────────────────────────────────
with col1:
    st.markdown("### DPR (Word)")
    st.markdown("Complete Detailed Project Report")
    if st.button("Generate DPR", type="primary", key="gen_dpr"):
        with st.spinner("Generating DPR..."):
            doc = generate_dpr_docx(cfg, COMPANY)
            buf = io.BytesIO()
            doc.save(buf)
            st.download_button("Download DPR.docx", buf.getvalue(),
                                f"DPR_{cfg['capacity_tpd']:.0f}MT.docx",
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            insert_report_generation({"report_type": "DPR_DOCX", "capacity_tpd": cfg["capacity_tpd"],
                                       "customer_id": customer["id"] if customer else None})

    st.markdown("### DPR (PDF)")
    if st.button("Generate DPR PDF", key="gen_dpr_pdf"):
        with st.spinner("Generating PDF..."):
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data",
                                 f"DPR_{cfg['capacity_tpd']:.0f}MT.pdf")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            generate_dpr_pdf(path, cfg, COMPANY)
            with open(path, "rb") as f:
                st.download_button("Download DPR.pdf", f.read(),
                                    f"DPR_{cfg['capacity_tpd']:.0f}MT.pdf", "application/pdf")

# ── Bank Proposal (DOCX) ─────────────────────────────────────────
with col2:
    st.markdown("### Bank Proposal (Word)")
    st.markdown("Term loan proposal with security details")
    if st.button("Generate Bank Proposal", type="primary", key="gen_bank"):
        with st.spinner("Generating..."):
            doc = generate_bank_proposal_docx(cfg, COMPANY, customer)
            buf = io.BytesIO()
            doc.save(buf)
            st.download_button("Download Bank_Proposal.docx", buf.getvalue(),
                                f"Bank_Proposal_{cfg['capacity_tpd']:.0f}MT.docx",
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    st.markdown("### Financial Report (PDF)")
    if st.button("Generate Financial PDF", key="gen_fin_pdf"):
        with st.spinner("Generating..."):
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data",
                                 f"Financial_{cfg['capacity_tpd']:.0f}MT.pdf")
            generate_financial_report_pdf(path, cfg, COMPANY)
            with open(path, "rb") as f:
                st.download_button("Download Financial.pdf", f.read(),
                                    f"Financial_{cfg['capacity_tpd']:.0f}MT.pdf", "application/pdf")

# ── Investor Pitch (PPTX) + Financial Model (XLSX) ───────────────
with col3:
    st.markdown("### Investor Pitch (PPT)")
    st.markdown("8-slide pitch deck with financials")
    if st.button("Generate Pitch Deck", type="primary", key="gen_pptx"):
        with st.spinner("Generating..."):
            pptx = generate_investor_pptx(cfg, COMPANY)
            buf = io.BytesIO()
            pptx.save(buf)
            st.download_button("Download Pitch.pptx", buf.getvalue(),
                                f"Investor_Pitch_{cfg['capacity_tpd']:.0f}MT.pptx",
                                "application/vnd.openxmlformats-officedocument.presentationml.presentation")

    st.markdown("### Financial Model (Excel)")
    st.markdown("5-sheet workbook with P&L, costs, sensitivity")
    if st.button("Generate Excel Model", type="primary", key="gen_xlsx"):
        with st.spinner("Generating..."):
            xlsx = generate_financial_xlsx(cfg, COMPANY)
            buf = io.BytesIO()
            xlsx.save(buf)
            st.download_button("Download Model.xlsx", buf.getvalue(),
                                f"Financial_Model_{cfg['capacity_tpd']:.0f}MT.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# GENERATE ALL AT ONCE
# ═══════════════════════════════════════════════════════════════════
st.subheader("Generate COMPLETE Package (All Documents)")
st.markdown(f"**One click → DPR (DOCX) + Bank Proposal (DOCX) + Investor Pitch (PPTX) + Financial Model (XLSX) + DPR (PDF) + Financial (PDF)**")

if st.button("GENERATE ALL DOCUMENTS", type="primary", key="gen_all"):
    with st.spinner("Generating complete document package..."):
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "generated_packages",
                                   f"{cfg['capacity_tpd']:.0f}MT_{cfg.get('state', 'General')}")
        results = generate_all_documents(cfg, COMPANY, customer, output_dir)

        # Also generate PDFs
        pdf_dpr = os.path.join(output_dir, f"DPR_{cfg['capacity_tpd']:.0f}MT.pdf")
        generate_dpr_pdf(pdf_dpr, cfg, COMPANY)
        results[f"DPR_{cfg['capacity_tpd']:.0f}MT.pdf"] = pdf_dpr

        pdf_fin = os.path.join(output_dir, f"Financial_{cfg['capacity_tpd']:.0f}MT.pdf")
        generate_financial_report_pdf(pdf_fin, cfg, COMPANY)
        results[f"Financial_{cfg['capacity_tpd']:.0f}MT.pdf"] = pdf_fin

        from utils.page_helpers import safe_path
        st.success(f"Generated **{len(results)} documents** in: {safe_path(output_dir)}")

        for fname, path in results.items():
            if isinstance(path, str) and os.path.exists(path):
                with open(path, "rb") as f:
                    mime = "application/pdf" if fname.endswith(".pdf") else "application/octet-stream"
                    st.download_button(f"Download {fname}", f.read(), fname, mime, key=f"dl_{fname}")

        insert_report_generation({
            "report_type": "COMPLETE_PACKAGE", "capacity_tpd": cfg["capacity_tpd"],
            "file_path": output_dir, "customer_id": customer["id"] if customer else None,
        })

st.markdown("---")

# ── Recent Generations ────────────────────────────────────────────
st.subheader("Recent Document Generations")
from database import get_report_generations
reports = get_report_generations(limit=10)
if reports:
    for r in reports:
        st.markdown(f"- **{r['report_type']}** — {r.get('capacity_tpd', 0):.0f} MT — {r['created_at']}")
else:
    st.info("No documents generated yet. Click any button above to start.")


# ── AI Skill: DPR Section Writer ──────────────────────────────────────
st.markdown("---")
try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("🤖 AI: DPR Section Writer"):
            if st.button("Generate", type="primary", key="ai_44DPRG"):
                with st.spinner("AI working..."):
                    _p = f"As a senior bio-bitumen consultant, generate: DPR Section Writer. "
                    _p += f"Plant: {cfg.get('capacity_tpd',20):.0f} TPD, Investment: Rs {cfg.get('investment_cr',8):.2f} Cr, "
                    _p += f"Location: {cfg.get('location','')}, {cfg.get('state','')}. "
                    _p += "Be specific with numbers. Professional format."
                    _r, _pv = ask_ai(_p, "Senior industrial consultant.", 1000)
                if _r:
                    st.markdown(_r)
except Exception:
    pass

# Print
if st.sidebar.button("Print", key="prt_44DPR"):
    import streamlit.components.v1 as _stc
    _stc.html("<script>window.print();</script>", height=0)
