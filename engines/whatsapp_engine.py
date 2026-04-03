"""
Bio Bitumen Consultant Portal — WhatsApp Engine
Generate WhatsApp messages and wa.me links for sending to customers.
"""
import urllib.parse
import webbrowser


def generate_whatsapp_message(customer, plant, company):
    """Generate a professional WhatsApp message for a customer."""
    msg = f"""*{company['trade_name']}*
{company['tagline']}
{'='*30}

Dear {customer.get('name', 'Sir/Madam')},

Thank you for your interest in our *Bio-Modified Bitumen* project. Here are the key details for the *{plant['label']}* plant:

*Project Summary:*
- Total Investment: Rs {plant['inv_cr']} Crore
- Bank Loan (60%): Rs {plant['loan_cr']} Crore
- Equity Required: Rs {plant['equity_cr']} Crore
- Revenue Year 1: Rs {plant['rev_yr1_cr']} Crore
- Revenue Year 5: Rs {plant['rev_yr5_cr']} Crore
- Monthly EMI: Rs {plant['emi_lac_mth']} Lakhs
- IRR: {plant['irr_pct']}%
- DSCR (Yr 3): {plant['dscr_yr3']}x

*Operations:*
- Staff Required: {plant['staff']}
- Daily Output: {plant['oil_ltr_day']:,} Ltrs Oil + {plant['char_kg_day']:,} Kg Char
- Power: {plant['power_kw']} kW

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
    webbrowser.open(link)
    return link
