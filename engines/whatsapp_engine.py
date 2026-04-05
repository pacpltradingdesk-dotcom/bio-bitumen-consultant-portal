"""
Bio Bitumen Consultant Portal — WhatsApp Engine
Generate WhatsApp messages and wa.me links for sending to customers.
All financial values come from plant dict (which should be populated from cfg).
"""
import urllib.parse


def generate_whatsapp_message(customer, plant, company):
    """Generate a professional WhatsApp message for a customer.
    plant dict should contain live values from session cfg."""
    inv = plant.get('inv_cr', 8)
    loan = plant.get('loan_cr', 4.8)
    equity = plant.get('equity_cr', 3.2)
    debt_pct = round(loan / inv * 100) if inv > 0 else 60

    msg = f"""*{company['trade_name']}*
{company['tagline']}
{'='*30}

Dear {customer.get('name', 'Sir/Madam')},

Thank you for your interest in our *Bio-Modified Bitumen* project. Here are the key details for the *{plant.get('label', 'Plant')}* plant:

*Project Summary:*
- Total Investment: Rs {inv} Crore
- Bank Loan ({debt_pct}%): Rs {loan} Crore
- Equity Required: Rs {equity} Crore
- Revenue Year 1: Rs {plant.get('rev_yr1_cr', 0)} Crore
- Revenue Year 5: Rs {plant.get('rev_yr5_cr', 0)} Crore
- Monthly EMI: Rs {plant.get('emi_lac_mth', 0)} Lakhs
- IRR: {plant.get('irr_pct', 0)}%
- ROI: {plant.get('roi_pct', 0)}%
- DSCR (Yr 3): {plant.get('dscr_yr3', 0)}x

*Operations:*
- Staff Required: {plant.get('staff', 0)}
- Daily Output: {plant.get('oil_ltr_day', 0):,} Ltrs Oil + {plant.get('char_kg_day', 0):,} Kg Char
- Power: {plant.get('power_kw', 0)} kW

We have the complete project documentation ready, including DPR, financial models, engineering specs, and bank-ready packages. Shall I share the detailed documents?

Regards,
*{company['owner']}*
{company['trade_name']}
{company['phone']}
"""
    return msg


def get_whatsapp_link(phone, message):
    """
    Generate a wa.me link for sending a WhatsApp message.
    Phone should include country code (e.g., +919876543210).
    """
    # Clean phone number
    phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")
    if phone_clean.startswith("0"):
        phone_clean = "91" + phone_clean[1:]
    elif not phone_clean.startswith("91") and len(phone_clean) == 10:
        phone_clean = "91" + phone_clean

    encoded_msg = urllib.parse.quote(message)
    return f"https://wa.me/{phone_clean}?text={encoded_msg}"


def open_whatsapp(phone, message):
    """Open WhatsApp web with the pre-composed message."""
    link = get_whatsapp_link(phone, message)
    import webbrowser
    webbrowser.open(link)
    return link
