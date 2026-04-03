"""
Bio Bitumen Consultant Portal — Email Engine
SMTP-based email sender with attachment support.
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import streamlit as st


def get_email_config():
    """Get email configuration from session state."""
    return {
        "smtp_server": st.session_state.get("smtp_server", "smtp.gmail.com"),
        "smtp_port": st.session_state.get("smtp_port", 587),
        "sender_email": st.session_state.get("sender_email", ""),
        "sender_password": st.session_state.get("sender_password", ""),
        "sender_name": st.session_state.get("sender_name", "PPS Anantams"),
    }


def send_email(to_email, subject, body_html, attachments=None, config=None):
    """
    Send an email with optional attachments.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body_html: HTML body content
        attachments: List of file paths to attach
        config: Email config dict (optional, uses session state if not provided)

    Returns:
        (success: bool, message: str)
    """
    config = config or get_email_config()

    if not config["sender_email"] or not config["sender_password"]:
        return False, "Email not configured. Please set up email credentials in Settings."

    try:
        msg = MIMEMultipart()
        msg["From"] = f"{config['sender_name']} <{config['sender_email']}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body_html, "html"))

        # Attach files
        if attachments:
            for filepath in attachments:
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        part = MIMEApplication(f.read(), Name=os.path.basename(filepath))
                        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(filepath)}"'
                        msg.attach(part)

        with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
            server.starttls()
            server.login(config["sender_email"], config["sender_password"])
            server.send_message(msg)

        return True, f"Email sent successfully to {to_email}"

    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed. Check email credentials."
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"


def generate_email_body(customer, plant, company):
    """Generate a professional HTML email body for a customer."""
    return f"""
    <html>
    <body style="font-family: Calibri, Arial, sans-serif; color: #333;">
        <div style="background: #003366; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">{company['trade_name']}</h1>
            <p style="margin: 5px 0 0;">{company['tagline']}</p>
        </div>

        <div style="padding: 20px;">
            <p>Dear <strong>{customer.get('name', 'Sir/Madam')}</strong>,</p>

            <p>Thank you for your interest in our Bio-Modified Bitumen project.
            Please find below the key details for the <strong>{plant['label']}</strong> plant capacity:</p>

            <table style="border-collapse: collapse; width: 100%; margin: 15px 0;">
                <tr style="background: #006699; color: white;">
                    <th style="padding: 10px; text-align: left;">Parameter</th>
                    <th style="padding: 10px; text-align: right;">Value</th>
                </tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">Total Investment</td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">Rs {plant['inv_cr']} Crore</td></tr>
                <tr style="background: #f5f5f5;"><td style="padding: 8px; border-bottom: 1px solid #ddd;">Bank Loan</td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">Rs {plant['loan_cr']} Crore</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">Equity Required</td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">Rs {plant['equity_cr']} Crore</td></tr>
                <tr style="background: #f5f5f5;"><td style="padding: 8px; border-bottom: 1px solid #ddd;">Revenue (Year 5)</td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">Rs {plant['rev_yr5_cr']} Crore</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">IRR</td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{plant['irr_pct']}%</td></tr>
                <tr style="background: #f5f5f5;"><td style="padding: 8px;">DSCR (Year 3)</td>
                    <td style="padding: 8px; text-align: right;">{plant['dscr_yr3']}x</td></tr>
            </table>

            <p>Please find attached the detailed project documentation for your review.
            We would be happy to arrange a detailed presentation at your convenience.</p>

            <p>Best regards,<br>
            <strong>{company['owner']}</strong><br>
            {company['trade_name']}<br>
            {company['phone']} | {company.get('email', '')}<br>
            {company['hq']}</p>
        </div>

        <div style="background: #f0f0f0; padding: 10px; text-align: center; font-size: 11px; color: #666;">
            CONFIDENTIAL — For Private Circulation Only | {company['name']} | GST: {company['gst']}
        </div>
    </body>
    </html>
    """
