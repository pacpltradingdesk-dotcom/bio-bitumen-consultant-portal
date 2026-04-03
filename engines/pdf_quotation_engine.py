"""
Bio Bitumen Consultant Portal — PDF Quotation Engine
Generate professional pricing quotation PDFs using ReportLab.
"""
import os
from datetime import datetime, timezone, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, PageBreak, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

IST = timezone(timedelta(hours=5, minutes=30))

# Colors
NAVY = colors.HexColor("#003366")
TEAL = colors.HexColor("#006699")
LIGHT_BG = colors.HexColor("#E6F2FF")
WHITE = colors.white


def generate_quotation_pdf(output_path, customer, plant, roi_df=None, company=None):
    """
    Generate a professional pricing quotation PDF.

    Args:
        output_path: Path to save the PDF
        customer: dict with customer details
        plant: dict with plant data from MASTER_DATA
        roi_df: DataFrame with ROI timeline (optional)
        company: dict with PACPL company details (optional)
    """
    from config import COMPANY as DEFAULT_COMPANY
    company = company or DEFAULT_COMPANY

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                             leftMargin=2 * cm, rightMargin=2 * cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CompanyName", parent=styles["Title"],
                               fontSize=18, textColor=NAVY, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="SubTitle", parent=styles["Normal"],
                               fontSize=12, textColor=TEAL, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="SectionHead", parent=styles["Heading2"],
                               fontSize=14, textColor=NAVY, spaceAfter=8))
    styles.add(ParagraphStyle(name="NormalLeft", parent=styles["Normal"],
                               fontSize=10, alignment=TA_LEFT, spaceAfter=4))
    styles.add(ParagraphStyle(name="Footer", parent=styles["Normal"],
                               fontSize=8, textColor=colors.grey, alignment=TA_CENTER))

    now = datetime.now(IST)
    elements = []

    # ── Header ────────────────────────────────────────────────────────
    elements.append(Paragraph(company["trade_name"], styles["CompanyName"]))
    elements.append(Paragraph(company["tagline"], styles["SubTitle"]))
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=2, color=NAVY))
    elements.append(Spacer(1, 12))

    # ── Quotation Title ───────────────────────────────────────────────
    elements.append(Paragraph("PRICING QUOTATION", ParagraphStyle(
        "QuoteTitle", parent=styles["Title"], fontSize=16, textColor=TEAL)))
    elements.append(Spacer(1, 6))

    # ── Customer & Date Info ──────────────────────────────────────────
    info_data = [
        ["Date:", now.strftime("%d %B %Y")],
        ["Reference:", f"PQ/{now.strftime('%Y%m%d')}/{customer.get('name', 'N/A')[:10]}"],
        ["To:", customer.get("name", "N/A")],
        ["Company:", customer.get("company", "N/A")],
        ["Location:", f"{customer.get('city', '')}, {customer.get('state', '')}"],
        ["Plant Capacity:", plant.get("label", "N/A")],
    ]
    info_table = Table(info_data, colWidths=[3 * cm, 13 * cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 16))

    # ── Plant Summary ─────────────────────────────────────────────────
    elements.append(Paragraph("PROJECT SUMMARY", styles["SectionHead"]))
    summary_data = [
        ["Parameter", "Value"],
        ["Total Project Investment", f"Rs {plant['inv_cr']} Crore"],
        ["Bank Loan (60%)", f"Rs {plant['loan_cr']} Crore"],
        ["Equity Required (40%)", f"Rs {plant['equity_cr']} Crore"],
        ["Revenue — Year 1", f"Rs {plant['rev_yr1_cr']} Crore"],
        ["Revenue — Year 5 (90% util.)", f"Rs {plant['rev_yr5_cr']} Crore"],
        ["Monthly EMI", f"Rs {plant['emi_lac_mth']} Lakhs"],
        ["DSCR (Year 3)", f"{plant['dscr_yr3']}x"],
        ["IRR (Equity)", f"{plant['irr_pct']}%"],
        ["Total Staff", f"{plant['staff']}"],
        ["Daily Output — Pyrolysis Oil", f"{plant['oil_ltr_day']:,} Litres"],
        ["Daily Output — Biochar", f"{plant['char_kg_day']:,} Kg"],
        ["Power Requirement", f"{plant['power_kw']} kW"],
        ["Biomass Required", f"{plant['biomass_mt_day']} MT/day ({plant['biomass_mt_yr']:,} MT/yr)"],
    ]
    summary_table = Table(summary_data, colWidths=[8 * cm, 8 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, -1), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 16))

    # ── Cost Breakdown ────────────────────────────────────────────────
    elements.append(Paragraph("INVESTMENT BREAKDOWN", styles["SectionHead"]))
    cost_data = [
        ["Component", "Amount (Lakhs)"],
        ["Civil & Building", f"{plant['civil_lac']}"],
        ["Machinery & Equipment", f"{plant['mach_lac']}"],
        ["GST on Machinery", f"{plant['gst_mach_lac']}"],
        ["Working Capital", f"{plant['wc_lac']}"],
        ["Interest During Construction", f"{plant['idc_lac']}"],
        ["Pre-operative Expenses", f"{plant['preop_lac']}"],
        ["Contingency", f"{plant['cont_lac']}"],
        ["Security Deposit", f"{plant['sec_lac']}"],
    ]
    total_lac = (plant['civil_lac'] + plant['mach_lac'] + plant['gst_mach_lac'] +
                 plant['wc_lac'] + plant['idc_lac'] + plant['preop_lac'] +
                 plant['cont_lac'] + plant['sec_lac'])
    cost_data.append(["TOTAL", f"{total_lac:.1f}"])

    cost_table = Table(cost_data, colWidths=[10 * cm, 6 * cm])
    cost_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT_BG),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [WHITE, LIGHT_BG]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(cost_table)
    elements.append(Spacer(1, 16))

    # ── ROI Timeline (if provided) ───────────────────────────────────
    if roi_df is not None and not roi_df.empty:
        elements.append(Paragraph("FINANCIAL PROJECTION (7 YEARS)", styles["SectionHead"]))
        roi_data = [list(roi_df.columns)]
        for _, row in roi_df.iterrows():
            roi_data.append([str(v) for v in row.values])

        col_widths = [1.5 * cm] + [2.2 * cm] * (len(roi_df.columns) - 1)
        roi_table = Table(roi_data, colWidths=col_widths)
        roi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(roi_table)
        elements.append(Spacer(1, 16))

    # ── Terms & Conditions ────────────────────────────────────────────
    elements.append(Paragraph("TERMS & CONDITIONS", styles["SectionHead"]))
    terms = [
        "This quotation is valid for 15 days from the date of issue.",
        "All prices are exclusive of GST (18%) unless otherwise stated.",
        "Payment terms: As per mutual agreement.",
        "Project timeline: 12-18 months from date of order confirmation.",
        "All figures are based on current market rates and subject to revision.",
        "This is a preliminary estimate. Detailed project report available on request.",
        f"For queries, contact: {company['owner']} | {company['phone']}",
    ]
    for i, term in enumerate(terms, 1):
        elements.append(Paragraph(f"{i}. {term}", styles["NormalLeft"]))
    elements.append(Spacer(1, 20))

    # ── Footer ────────────────────────────────────────────────────────
    elements.append(HRFlowable(width="100%", thickness=1, color=NAVY))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        f"{company['name']} | GST: {company['gst']} | {company['hq']}",
        styles["Footer"]))
    elements.append(Paragraph("CONFIDENTIAL — For Private Circulation Only", styles["Footer"]))

    doc.build(elements)
    return output_path
