"""
QR Code Engine — Generate QR codes for document verification.
Embeds QR in PDFs/DOCXs linking to live dashboard.
Uses qrcode library (pure Python, no external API needed).
"""
import io
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


def generate_qr_code(data, size=200):
    """Generate QR code image as bytes.
    data: URL or text to encode
    size: pixel size of QR image
    Returns: PNG bytes or None
    """
    if not QR_AVAILABLE:
        return None

    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Resize
    img = img.resize((size, size))

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()


def generate_project_qr(cfg):
    """Generate QR code with project verification data."""
    project_info = (
        f"Bio-Bitumen Project Verification\n"
        f"Client: {cfg.get('client_name', 'N/A')}\n"
        f"Capacity: {cfg.get('capacity_tpd', 20)} TPD\n"
        f"Investment: Rs {cfg.get('investment_cr', 0):.2f} Cr\n"
        f"ROI: {cfg.get('roi_pct', 0):.1f}%\n"
        f"Location: {cfg.get('location', '')}, {cfg.get('state', '')}\n"
        f"Consultant: PPS Anantams | +91 7795242424\n"
        f"Ref: {cfg.get('project_id', 'PPS/2026/BIO')}"
    )
    return generate_qr_code(project_info, 200)


def get_qr_for_document(cfg, doc_type="DPR"):
    """Generate QR for a specific document type."""
    data = (
        f"{doc_type} - {cfg.get('client_name', 'Client')}\n"
        f"{cfg.get('capacity_tpd', 20)} TPD | Rs {cfg.get('investment_cr', 0):.2f} Cr\n"
        f"PPS Anantams | {cfg.get('project_id', '')}"
    )
    return generate_qr_code(data, 150)
