"""
Bio Bitumen Consultant Portal — DOCX Customizer
Find-and-replace placeholders in Word documents with customer-specific details.
"""
import os
import copy
from docx import Document


# Common placeholder patterns found in the document suite
DEFAULT_PLACEHOLDERS = [
    "Customer Name", "[Customer Name]", "<<Customer Name>>",
    "CUSTOMER NAME", "INVESTOR NAME", "[Investor Name]",
    "[Client Name]", "CLIENT NAME", "Client Name",
    "[Company Name]", "COMPANY NAME", "Company Name",
    "[Party Name]", "PARTY NAME", "Party Name",
]


def get_default_replacements(customer, plant=None):
    """Build a replacement dict from customer and plant data."""
    replacements = {}

    # Customer name replacements
    cust_name = customer.get("name", "")
    cust_company = customer.get("company", "") or cust_name

    for pattern in DEFAULT_PLACEHOLDERS:
        if "investor" in pattern.lower() or "client" in pattern.lower() or "customer" in pattern.lower():
            replacements[pattern] = cust_name
        elif "company" in pattern.lower() or "party" in pattern.lower():
            replacements[pattern] = cust_company

    # Additional replacements
    replacements["[Customer Email]"] = customer.get("email", "")
    replacements["[Customer Phone]"] = customer.get("phone", "")
    replacements["[Customer State]"] = customer.get("state", "")
    replacements["[Customer City]"] = customer.get("city", "")

    # Date replacement
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(IST).strftime("%d %B %Y")
    replacements["[DATE]"] = today
    replacements["[Date]"] = today
    replacements["<<DATE>>"] = today

    # Plant-specific replacements
    if plant:
        replacements["[Capacity]"] = plant.get("label", "")
        replacements["[Investment]"] = f"Rs {plant.get('inv_cr', '')} Crore"
        replacements["[Location]"] = plant.get("location", "")

    return replacements


def _replace_in_runs(paragraph, replacements):
    """Replace text in paragraph runs while preserving formatting."""
    full_text = paragraph.text
    changed = False

    for old_text, new_text in replacements.items():
        if old_text in full_text:
            full_text = full_text.replace(old_text, new_text)
            changed = True

    if changed and paragraph.runs:
        # Rebuild runs: put all text in first run, clear rest
        for i, run in enumerate(paragraph.runs):
            if i == 0:
                run.text = full_text
            else:
                run.text = ""


def customize_docx(source_path, output_path, replacements):
    """
    Open a DOCX file, replace all placeholder text, and save to output_path.
    Handles paragraphs, tables, headers, and footers.
    """
    doc = Document(source_path)

    # Replace in body paragraphs
    for paragraph in doc.paragraphs:
        _replace_in_runs(paragraph, replacements)

    # Replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    _replace_in_runs(paragraph, replacements)

    # Replace in headers and footers
    for section in doc.sections:
        for header in [section.header, section.first_page_header]:
            if header and header.paragraphs:
                for paragraph in header.paragraphs:
                    _replace_in_runs(paragraph, replacements)
        for footer in [section.footer, section.first_page_footer]:
            if footer and footer.paragraphs:
                for paragraph in footer.paragraphs:
                    _replace_in_runs(paragraph, replacements)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path
