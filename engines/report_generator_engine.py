"""
Bio Bitumen Master Consulting System — Report Generator Engine
===============================================================
Generate DPR, Financial Report, Technical Report as professional PDFs.
Uses current state_manager config so reports auto-reflect latest inputs.
"""
import os
from datetime import datetime, timezone, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

IST = timezone(timedelta(hours=5, minutes=30))
NAVY = colors.HexColor("#003366")
TEAL = colors.HexColor("#006699")
LIGHT = colors.HexColor("#E6F2FF")
WHITE = colors.white
NUM_FMT = '{:,.2f}'


def _header_footer(canvas, doc, company):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(NAVY)
    canvas.drawString(2 * cm, A4[1] - 1.2 * cm, f"{company['trade_name']} | {company['tagline']}")
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1 * cm, f"CONFIDENTIAL | {company['name']} | GST: {company['gst']}")
    canvas.drawRightString(A4[0] - 2 * cm, 1 * cm, f"Page {doc.page}")
    canvas.restoreState()


def _make_table(data, col_widths=None):
    if not col_widths:
        col_widths = [8 * cm, 8 * cm]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def generate_dpr_pdf(output_path, cfg, company):
    """Generate a complete Detailed Project Report PDF from current config."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             topMargin=2 * cm, bottomMargin=2 * cm,
                             leftMargin=2 * cm, rightMargin=2 * cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("Title2", parent=styles["Title"], fontSize=20, textColor=NAVY))
    styles.add(ParagraphStyle("Sub", parent=styles["Normal"], fontSize=12, textColor=TEAL, alignment=TA_CENTER))
    styles.add(ParagraphStyle("Section", parent=styles["Heading2"], fontSize=14, textColor=NAVY, spaceAfter=8))
    styles.add(ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, spaceAfter=4))

    now = datetime.now(IST)
    elements = []

    # ── COVER PAGE (with client info) ────────────────────────────────
    client_name = cfg.get("client_name", "")
    project_name = cfg.get("project_name", f"Bio-Modified Bitumen Plant — {cfg['capacity_tpd']:.0f} MT/Day")
    site_address = cfg.get("site_address", f"{cfg.get('location', 'To be finalized')}, {cfg.get('state', '')}")

    elements.append(Spacer(1, 3 * cm))
    elements.append(Paragraph("DETAILED PROJECT REPORT (DPR)", styles["Title2"]))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph(project_name, styles["Sub"]))
    elements.append(Spacer(1, 0.5 * cm))
    if client_name:
        elements.append(Paragraph(f"Prepared for: {client_name}", styles["Sub"]))
        if cfg.get("client_company"):
            elements.append(Paragraph(f"{cfg['client_company']}", styles["Body"]))
    elements.append(Paragraph(f"Total Investment: Rs {cfg['investment_cr']:.2f} Crore", styles["Sub"]))
    elements.append(Paragraph(f"Location: {site_address}", styles["Body"]))
    elements.append(Spacer(1, 1 * cm))
    elements.append(Paragraph(f"Prepared by: {company['trade_name']}", styles["Body"]))
    elements.append(Paragraph(f"Consultant: {company['owner']} | {company['phone']}", styles["Body"]))
    elements.append(Paragraph(f"Date: {now.strftime('%d %B %Y')}", styles["Body"]))
    if cfg.get("project_id"):
        elements.append(Paragraph(f"Reference: {cfg['project_id']}", styles["Body"]))
    elements.append(Paragraph(f"CONFIDENTIAL", styles["Body"]))
    elements.append(PageBreak())

    # ── 1. PROJECT OVERVIEW ───────────────────────────────────────────
    elements.append(Paragraph("1. PROJECT OVERVIEW", styles["Section"]))
    elements.append(Paragraph(
        f"This DPR presents a {cfg['capacity_tpd']:.0f} MT/Day Bio-Modified Bitumen manufacturing plant "
        f"using agricultural biomass pyrolysis technology. The project requires a total investment of "
        f"Rs {cfg['investment_cr']:.2f} Crore with debt:equity ratio of "
        f"{int((1-cfg['equity_ratio'])*100)}:{int(cfg['equity_ratio']*100)}.", styles["Body"]))

    overview_data = [
        ["Parameter", "Value"],
        ["Plant Capacity", f"{cfg['capacity_tpd']:.0f} MT/Day"],
        ["Product", "Bio-Modified Bitumen" if cfg['product_model'] == "bitumen" else "Pyrolysis Oil + Biochar"],
        ["Total Investment", f"Rs {cfg['investment_cr']:.2f} Crore"],
        ["Bank Loan", f"Rs {cfg['loan_cr']:.2f} Crore"],
        ["Promoter Equity", f"Rs {cfg['equity_cr']:.2f} Crore"],
        ["Location", f"{cfg.get('location', 'To be finalized')}, {cfg.get('state', '')}"],
        ["Staff Requirement", f"{cfg['staff']} persons"],
        ["Power Requirement", f"{cfg['power_kw']:.0f} kW"],
        ["Working Days", f"{cfg['working_days']}/year"],
    ]
    elements.append(_make_table(overview_data))
    elements.append(Spacer(1, 0.5 * cm))

    # ── 2. INVESTMENT BREAKDOWN ───────────────────────────────────────
    elements.append(Paragraph("2. INVESTMENT BREAKDOWN", styles["Section"]))
    plant = cfg["plant_data"]
    inv_data = [
        ["Component", "Amount (Rs Lakhs)"],
        ["Civil & Building", f"{plant.get('civil_lac', 0):.1f}"],
        ["Machinery & Equipment", f"{plant.get('mach_lac', 0):.1f}"],
        ["GST on Machinery (18%)", f"{plant.get('gst_mach_lac', 0):.1f}"],
        ["Working Capital", f"{plant.get('wc_lac', 0):.1f}"],
        ["Interest During Construction", f"{plant.get('idc_lac', 0):.1f}"],
        ["Pre-operative Expenses", f"{plant.get('preop_lac', 0):.1f}"],
        ["Contingency", f"{plant.get('cont_lac', 0):.1f}"],
        ["Security Deposit", f"{plant.get('sec_lac', 0):.1f}"],
        ["TOTAL", f"{cfg['investment_lac']:.1f}"],
    ]
    elements.append(_make_table(inv_data))
    elements.append(Spacer(1, 0.5 * cm))

    # ── 3. FINANCIAL PROJECTIONS ──────────────────────────────────────
    elements.append(Paragraph("3. FINANCIAL PROJECTIONS (7 YEARS)", styles["Section"]))
    if cfg["roi_timeline"]:
        roi_header = ["Year", "Revenue", "EBITDA", "PAT", "DSCR"]
        roi_rows = [roi_header]
        for yr in cfg["roi_timeline"]:
            roi_rows.append([
                str(yr["Year"]),
                f"Rs {yr['Revenue (Lac)']:.0f} L",
                f"Rs {yr['EBITDA (Lac)']:.0f} L",
                f"Rs {yr['PAT (Lac)']:.0f} L",
                f"{yr['DSCR']:.2f}x",
            ])
        elements.append(_make_table(roi_rows, col_widths=[2 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm, 2.5 * cm]))

    elements.append(Spacer(1, 0.5 * cm))

    # ── 4. KEY METRICS ────────────────────────────────────────────────
    elements.append(Paragraph("4. KEY FINANCIAL METRICS", styles["Section"]))
    metrics_data = [
        ["Metric", "Value"],
        ["Monthly EMI", f"Rs {cfg['emi_lac_mth']:.2f} Lakhs"],
        ["Revenue Year 1", f"Rs {cfg['revenue_yr1_lac']:.0f} Lakhs"],
        ["Revenue Year 5", f"Rs {cfg['revenue_yr5_lac']:.0f} Lakhs"],
        ["DSCR (Year 3)", f"{cfg['dscr_yr3']:.2f}x"],
        ["Break-Even", f"Month {cfg.get('break_even_months', cfg.get('break_even_month', 0))}" if cfg.get('break_even_months', cfg.get('break_even_month', 0)) > 0 else "Under calculation"],
        ["Interest Rate", f"{cfg['interest_rate']*100:.1f}% p.a."],
        ["Loan Tenure", f"{cfg['emi_tenure_months']} months ({cfg['emi_tenure_months']//12} years)"],
    ]
    elements.append(_make_table(metrics_data))

    # ── 5. TERMS ──────────────────────────────────────────────────────
    elements.append(Spacer(1, 1 * cm))
    elements.append(Paragraph("DISCLAIMER", styles["Section"]))
    elements.append(Paragraph(
        "This DPR is based on current market data, verified assumptions, and standard engineering practices. "
        "All financial projections are estimates and subject to market conditions. "
        "The client should conduct independent due diligence before making investment decisions.",
        styles["Body"]))

    elements.append(Spacer(1, 1 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=NAVY))
    elements.append(Paragraph(
        f"{company['name']} | {company['owner']} | {company['phone']} | {company['hq']}",
        ParagraphStyle("Footer", fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))

    doc.build(elements, onFirstPage=lambda c, d: _header_footer(c, d, company),
              onLaterPages=lambda c, d: _header_footer(c, d, company))
    return output_path


def generate_financial_report_pdf(output_path, cfg, company):
    """Generate a financial summary report PDF."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             topMargin=2 * cm, bottomMargin=2 * cm,
                             leftMargin=2 * cm, rightMargin=2 * cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("Title2", parent=styles["Title"], fontSize=18, textColor=NAVY))
    styles.add(ParagraphStyle("Section", parent=styles["Heading2"], fontSize=14, textColor=NAVY))
    styles.add(ParagraphStyle("Body", parent=styles["Normal"], fontSize=10))

    now = datetime.now(IST)
    elements = []

    elements.append(Paragraph("FINANCIAL ANALYSIS REPORT", styles["Title2"]))
    elements.append(Paragraph(f"Bio-Modified Bitumen — {cfg['capacity_tpd']:.0f} MT/Day | {now.strftime('%d %B %Y')}", styles["Body"]))
    elements.append(HRFlowable(width="100%", thickness=2, color=NAVY))
    elements.append(Spacer(1, 0.5 * cm))

    # Investment summary
    elements.append(Paragraph("INVESTMENT SUMMARY", styles["Section"]))
    inv_tbl = [
        ["Item", "Amount"],
        ["Total Project Cost", f"Rs {cfg['investment_cr']:.2f} Crore ({cfg['investment_lac']:.0f} Lakhs)"],
        ["Bank Term Loan (60%)", f"Rs {cfg['loan_cr']:.2f} Crore"],
        ["Promoter Equity (40%)", f"Rs {cfg['equity_cr']:.2f} Crore"],
        ["Monthly EMI", f"Rs {cfg['emi_lac_mth']:.2f} Lakhs"],
        ["Interest Rate", f"{cfg['interest_rate']*100:.1f}% p.a."],
        ["Tenure", f"{cfg['emi_tenure_months']} months"],
    ]
    elements.append(_make_table(inv_tbl))
    elements.append(Spacer(1, 0.5 * cm))

    # 7-year projection
    elements.append(Paragraph("7-YEAR P&L PROJECTION", styles["Section"]))
    if cfg["roi_timeline"]:
        header = ["Yr", "Rev (L)", "Var (L)", "Fix (L)", "EBITDA (L)", "PAT (L)", "DSCR"]
        rows = [header]
        for yr in cfg["roi_timeline"]:
            rows.append([
                str(yr["Year"]), f"{yr['Revenue (Lac)']:.0f}", f"{yr['Variable Cost (Lac)']:.0f}",
                f"{yr['Fixed Cost (Lac)']:.0f}", f"{yr['EBITDA (Lac)']:.0f}",
                f"{yr['PAT (Lac)']:.0f}", f"{yr['DSCR']:.2f}x",
            ])
        elements.append(_make_table(rows, col_widths=[1.2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2*cm]))

    # Sensitivity
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph("SENSITIVITY MATRIX (EBITDA Yr5, Rs Lakhs)", styles["Section"]))
    if cfg["sensitivity_matrix"]:
        sens_header = ["Cost \\ Price", "Low Price", "Base Price", "High Price"]
        sens_rows = [sens_header]
        labels = ["Low Cost", "Base Cost", "High Cost"]
        for i, row in enumerate(cfg["sensitivity_matrix"]):
            sens_rows.append([labels[i]] + [f"{v:.0f}" for v in row])
        elements.append(_make_table(sens_rows, col_widths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm]))

    elements.append(Spacer(1, 1 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=NAVY))
    elements.append(Paragraph(f"{company['name']} | CONFIDENTIAL",
                               ParagraphStyle("F", fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))

    doc.build(elements, onFirstPage=lambda c, d: _header_footer(c, d, company),
              onLaterPages=lambda c, d: _header_footer(c, d, company))
    return output_path
