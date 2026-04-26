"""
Vendor Emails — Copy-paste RFQ emails + status tracker for all 80 vendors
Source: VENDOR_ENQUIRY_PACK_2026-04-21 | YUGA PMC
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import re
from database import get_connection
from state_manager import init_state, get_config

st.set_page_config(page_title="Vendor Emails", page_icon="📧", layout="wide")
init_state()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.sidebar.markdown("---")
if st.sidebar.button("Print This Page", key="print_page"):
    import streamlit.components.v1 as _c; _c.html('<script>window.print();</script>', height=0)

st.title("Vendor RFQ Emails & Tracker")
st.markdown("**80 vendors — copy-paste ready email templates + live status tracker**")
st.markdown("---")

# ── Data paths ────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vendor_emails")

CATEGORY_MAP = {
    "A_PLANT_MACHINERY":       "A — Plant & Machinery (Sr 1-39)",
    "B_RAW_MATERIAL":          "B — Raw Material Suppliers (Sr 40-53)",
    "C_CIVIL_LOGISTICS":       "C — Civil, Utilities & Logistics (Sr 54-63)",
    "D_APPROVALS":             "D — Approvals & Consultants (Sr 64-68)",
    "E_FINANCE_AUDIT":         "E — Finance, Audit & Banking (Sr 69-74)",
    "F_TESTING_CERTIFICATION": "F — Testing & Certification (Sr 75-80)",
}

EMAIL_FILES = {
    "A_PLANT_MACHINERY":       "A_PLANT_MACHINERY_EMAILS.md",
    "B_RAW_MATERIAL":          "B_RAW_MATERIAL_EMAILS.md",
    "C_CIVIL_LOGISTICS":       "C_CIVIL_UTILITIES_LOGISTICS_EMAILS.md",
    "D_APPROVALS":             "D_APPROVALS_CONSULTANT_EMAILS.md",
    "E_FINANCE_AUDIT":         "E_FINANCE_AUDIT_EMAILS.md",
    "F_TESTING_CERTIFICATION": "F_TESTING_CERTIFICATION_EMAILS.md",
}

STATUS_COLORS = {
    "TO_SEND":    "#e74c3c",
    "SENT":       "#f39c12",
    "ACK":        "#3498db",
    "QUOTE_RCD":  "#27ae60",
    "REVISED":    "#8e44ad",
    "SHORTLISTED":"#1abc9c",
    "PO":         "#2ecc71",
    "CLOSED":     "#888888",
}

STATUSES = list(STATUS_COLORS.keys())

SIGNATURE_BLOCK = """------------------------------------------------------------

With regards,

Prince Pratap Shah
Lead Consultant
YUGA PMC (Vision · Strategy · Execution)
A brand of PPS Anantams Corporation Pvt. Ltd.

Project: 5 TPD PMB-40 Bio-Bitumen Plant, Bahadurgarh, Haryana
Client (Buyer): REX FUELS MANAGEMENT PVT LTD

Mobile:    +91 7795242424
Corporate: +91 94482 81224
Email:     sales.ppsanantams@gmail.com

Reg. Office: 04, Signet Plaza Tower-B, 3rd Floor,
             Kunal Cross Road, Gotri, Vadodara 390021, Gujarat
Mumbai Ops:  1/12 D.N. Estate, Station Road,
             Bhandup (West), Mumbai 400078

This enquiry is part of an RFQ process. Three vendors per line
are being evaluated on technical-qualified lowest-bid principle.
Quote validity requested: 90 days.

------------------------------------------------------------"""

FOLLOW_UP_TEMPLATE = """Dear Sir / Madam,

Gentle follow-up on our RFQ dated [DATE OF FIRST EMAIL] for
[ITEM NAME]. We have not yet received your acknowledgement /
quotation.

Kindly confirm receipt and share the budgetary offer at your
earliest. Our target timeline for vendor shortlist is
[DATE + 14 DAYS].

Looking forward to your reply.

{signature}""".format(signature=SIGNATURE_BLOCK)


# ── Load vendors from DB ──────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_vendors():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, vendor_name, equipment, category, city, email,
                   rfq_status, price_lac, contact
            FROM vendor_quotes
            ORDER BY id
        """).fetchall()
    return [dict(r) for r in rows]


def update_status(vendor_id: int, new_status: str):
    with get_connection() as conn:
        conn.execute("UPDATE vendor_quotes SET rfq_status=? WHERE id=?",
                     (new_status, vendor_id))
        conn.commit()
    st.cache_data.clear()


def load_email_template(category: str) -> str:
    fname = EMAIL_FILES.get(category, "")
    if not fname:
        return ""
    fpath = os.path.join(DATA_DIR, fname)
    if os.path.exists(fpath):
        with open(fpath, encoding="utf-8") as f:
            return f.read()
    return ""


def find_vendor_block(md_content: str, vendor_name: str) -> str:
    """Extract the email block for a specific vendor from the MD file."""
    if not md_content:
        return ""
    # Try to find vendor section by name
    short = vendor_name.replace(" (India Agent)", "").replace(" INDIA", "").split("(")[0].strip()
    short_upper = short.upper()

    # Find heading lines that contain the vendor name
    lines = md_content.split("\n")
    start_idx = None
    for i, line in enumerate(lines):
        if short_upper in line.upper() and line.startswith("###"):
            start_idx = i
            break

    if start_idx is None:
        # Fallback: search for vendor name anywhere in a heading
        for i, line in enumerate(lines):
            parts = vendor_name.upper().split()
            if len(parts) >= 2 and parts[0] in line.upper() and line.startswith("#"):
                start_idx = i
                break

    if start_idx is None:
        return ""

    # Collect until next ### heading or end of vendor blocks
    block_lines = []
    for line in lines[start_idx:]:
        if block_lines and line.startswith("### Vendor") and len(block_lines) > 2:
            break
        if block_lines and line.startswith("## ") and len(block_lines) > 2:
            break
        block_lines.append(line)

    return "\n".join(block_lines)


def extract_subject_body(block: str):
    """Pull SUBJECT and BODY from a vendor block."""
    subject = ""
    body = ""

    # Extract SUBJECT
    sm = re.search(r"\*\*SUBJECT:\*\*\s*(.+)", block)
    if sm:
        subject = sm.group(1).strip()

    # Extract BODY between ``` fences
    bm = re.search(r"```\n(.*?)\n```", block, re.DOTALL)
    if bm:
        body = bm.group(1).strip()
    else:
        # Try to get everything after BODY: marker
        bm2 = re.search(r"\*\*BODY:\*\*\n?(.*)", block, re.DOTALL)
        if bm2:
            body = bm2.group(1).strip()

    return subject, body


# ── Main UI ───────────────────────────────────────────────────────────
vendors = load_vendors()

# Summary metrics
col_m = st.columns(len(STATUS_COLORS) + 1)
with col_m[0]:
    st.metric("Total Vendors", len(vendors))
for i, (s, clr) in enumerate(STATUS_COLORS.items()):
    cnt = sum(1 for v in vendors if v.get("rfq_status") == s)
    with col_m[i+1]:
        st.metric(s, cnt)

st.markdown("---")

TAB_TRACKER, TAB_EMAILS, TAB_SIGNATURE = st.tabs([
    "Tracker — All 80 Vendors",
    "Email Templates",
    "Signature Block & Follow-up",
])


# ══════════════════════════════════════════════════════════════════════
# TAB 1 — TRACKER
# ══════════════════════════════════════════════════════════════════════
with TAB_TRACKER:
    st.subheader("RFQ Tracker — All 80 Vendors")
    st.caption("Update status live; data saved to portal database instantly.")

    # Filters
    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        cat_options = ["ALL"] + list(CATEGORY_MAP.keys())
        sel_cat = st.selectbox("Category", cat_options,
                               format_func=lambda x: "ALL" if x == "ALL" else CATEGORY_MAP.get(x, x))
    with f2:
        sel_status = st.selectbox("Status", ["ALL"] + STATUSES)
    with f3:
        search_txt = st.text_input("Search vendor / item", "")

    filtered = vendors
    if sel_cat != "ALL":
        filtered = [v for v in filtered if v.get("category") == sel_cat]
    if sel_status != "ALL":
        filtered = [v for v in filtered if v.get("rfq_status") == sel_status]
    if search_txt:
        q = search_txt.lower()
        filtered = [v for v in filtered
                    if q in v.get("vendor_name","").lower()
                    or q in v.get("equipment","").lower()
                    or q in v.get("city","").lower()]

    st.markdown(f"**Showing {len(filtered)} of {len(vendors)} vendors**")

    # Per-vendor cards with inline status update
    for v in filtered:
        status = v.get("rfq_status", "TO_SEND") or "TO_SEND"
        cat_label = CATEGORY_MAP.get(v.get("category",""), v.get("category",""))
        clr = STATUS_COLORS.get(status, "#888")

        with st.expander(
            f"**{v['vendor_name']}** — {v['equipment'][:60]}  "
            f"| {v.get('city','')} | :{status}:",
            expanded=False
        ):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            with c1:
                st.markdown(f"**Vendor:** {v['vendor_name']}")
                st.markdown(f"**Item:** {v['equipment']}")
                st.markdown(f"**Category:** {cat_label}")
                if v.get("city"):
                    st.markdown(f"**City:** {v['city']}")
            with c2:
                if v.get("email"):
                    st.markdown(f"**Email:** `{v['email']}`")
                if v.get("price_lac") and v["price_lac"] > 0:
                    st.markdown(f"**Budget:** Rs {v['price_lac']:.2f} L")
                if v.get("contact"):
                    st.caption(v["contact"])
            with c3:
                new_status = st.selectbox(
                    "Update Status",
                    STATUSES,
                    index=STATUSES.index(status) if status in STATUSES else 0,
                    key=f"status_{v['id']}"
                )
            with c4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Save", key=f"save_{v['id']}", type="primary"):
                    update_status(v["id"], new_status)
                    st.success("Updated!")
                    st.rerun()

    # Download tracker as CSV
    st.markdown("---")
    if vendors:
        df = pd.DataFrame([{
            "Sr": i+1,
            "Vendor": v["vendor_name"],
            "Item": v["equipment"],
            "Category": CATEGORY_MAP.get(v.get("category",""), ""),
            "City": v.get("city",""),
            "Email": v.get("email",""),
            "Budget (L)": v.get("price_lac",""),
            "Status": v.get("rfq_status","TO_SEND"),
        } for i, v in enumerate(vendors)])
        csv_data = df.to_csv(index=False)
        st.download_button("Download Tracker as CSV", csv_data,
                           "vendor_rfq_tracker.csv", "text/csv",
                           key="dl_tracker_csv")


# ══════════════════════════════════════════════════════════════════════
# TAB 2 — EMAIL TEMPLATES
# ══════════════════════════════════════════════════════════════════════
with TAB_EMAILS:
    st.subheader("Copy-Paste Email Templates")
    st.caption(
        "Select category → select vendor → copy the Subject and Body into Gmail / Outlook."
        " Paste the Signature Block (Tab 3) at the end of every email."
    )

    tc1, tc2 = st.columns([2, 3])
    with tc1:
        email_cat = st.selectbox(
            "Category",
            list(CATEGORY_MAP.keys()),
            format_func=lambda x: CATEGORY_MAP.get(x, x),
            key="email_cat_sel"
        )
    with tc2:
        cat_vendors = [v for v in vendors if v.get("category") == email_cat]
        vendor_labels = [f"{v['vendor_name']} — {v['equipment'][:50]}" for v in cat_vendors]
        sel_vendor_idx = st.selectbox("Select Vendor", range(len(cat_vendors)),
                                      format_func=lambda i: vendor_labels[i] if vendor_labels else "",
                                      key="email_vendor_sel") if cat_vendors else None

    if sel_vendor_idx is not None and cat_vendors:
        sel_vendor = cat_vendors[sel_vendor_idx]
        md_content = load_email_template(email_cat)
        block = find_vendor_block(md_content, sel_vendor["vendor_name"])
        subject, body = extract_subject_body(block)

        st.markdown("---")
        ea, eb = st.columns([1, 2])

        with ea:
            st.markdown("**Vendor Details**")
            st.info(
                f"**{sel_vendor['vendor_name']}**\n\n"
                f"City: {sel_vendor.get('city','—')}\n\n"
                f"Email: {sel_vendor.get('email','—')}\n\n"
                f"Category: {CATEGORY_MAP.get(sel_vendor.get('category',''),'')}\n\n"
                f"Status: **{sel_vendor.get('rfq_status','TO_SEND')}**"
            )
            # Quick status update
            new_s = st.selectbox("Update Status", STATUSES,
                                 index=STATUSES.index(sel_vendor.get("rfq_status","TO_SEND"))
                                 if sel_vendor.get("rfq_status","TO_SEND") in STATUSES else 0,
                                 key="email_status_update")
            if st.button("Save Status", key="email_save_status"):
                update_status(sel_vendor["id"], new_s)
                st.success("Status updated!")
                st.rerun()

        with eb:
            if subject:
                st.markdown("**SUBJECT LINE** (copy this into your email subject):")
                st.code(subject, language=None)
            else:
                st.info("Subject not found in template — see full MD below.")

            if body:
                # Append signature placeholder note
                full_body = body
                if "[PASTE SIGNATURE BLOCK HERE]" in full_body or "[PASTE SIGNATURE BLOCK]" in full_body:
                    full_body = full_body.replace(
                        "[PASTE SIGNATURE BLOCK HERE]", SIGNATURE_BLOCK
                    ).replace("[PASTE SIGNATURE BLOCK]", SIGNATURE_BLOCK)

                st.markdown("**EMAIL BODY** (copy this into your email body):")
                st.text_area("", full_body, height=420, key=f"body_{sel_vendor['id']}")
                st.caption("Click inside the box and press Ctrl+A then Ctrl+C to copy all.")
            else:
                st.warning(
                    "Detailed template not parsed for this vendor. "
                    "See the full MD file below for the email body."
                )

        # Show raw MD section as reference
        if block:
            with st.expander("Raw Template (from MD file)", expanded=False):
                st.markdown(block)
        elif md_content:
            with st.expander(f"Full {CATEGORY_MAP.get(email_cat,'')} email file", expanded=False):
                st.markdown(md_content[:8000] + ("\n\n[...truncated...]" if len(md_content) > 8000 else ""))

    # ── View full category file ──
    st.markdown("---")
    with st.expander("View / Download Full Email File for Selected Category", expanded=False):
        md_full = load_email_template(email_cat)
        if md_full:
            st.markdown(md_full)
            fname = EMAIL_FILES.get(email_cat, "emails.md")
            st.download_button("Download MD File", md_full.encode(), fname,
                               "text/markdown", key="dl_email_md")
        else:
            st.warning("Email template file not found in data/vendor_emails/")


# ══════════════════════════════════════════════════════════════════════
# TAB 3 — SIGNATURE BLOCK
# ══════════════════════════════════════════════════════════════════════
with TAB_SIGNATURE:
    st.subheader("Universal Email Signature Block")
    st.caption("Paste at the bottom of every RFQ email after the body.")

    sig_path = os.path.join(DATA_DIR, "01_SIGNATURE_BLOCK.md")
    if os.path.exists(sig_path):
        with open(sig_path, encoding="utf-8") as f:
            sig_md = f.read()
        st.markdown(sig_md)
    else:
        st.text_area("Signature Block (copy this):", SIGNATURE_BLOCK, height=300,
                     key="sig_block_main")

    st.markdown("---")
    st.subheader("Follow-up Email Template")
    st.caption("Use this on Day 4 (no ACK) or Day 10 (no quote) after sending RFQ.")
    st.text_area("Follow-up Template:", FOLLOW_UP_TEMPLATE, height=300, key="followup_template")

    st.markdown("---")
    st.subheader("Sending Workflow")
    st.markdown("""
| Day | Action |
|-----|--------|
| **Day 1** | Open each category email file → paste Subject + Body into Gmail → find vendor email from their website |
| **Day 1-3** | Send all 80 RFQs → update status to `SENT` in Tracker tab |
| **Day 4-5** | Acknowledgements received → update status to `ACK` |
| **Day 10-14** | First quotes arriving → update to `QUOTE_RCD` + note price |
| **Day 15** | Follow-up to non-responders using template above |
| **Week 3** | Shortlist — update to `SHORTLISTED` |
| **Week 4-6** | Revised quotes, PO placement → `PO` then `CLOSED` |
    """)

    st.markdown("---")
    st.subheader("Status Legend")
    cols = st.columns(4)
    for i, (s, clr) in enumerate(STATUS_COLORS.items()):
        with cols[i % 4]:
            st.markdown(
                f'<span style="background:{clr};color:white;padding:3px 10px;border-radius:4px;font-weight:bold">'
                f'{s}</span>', unsafe_allow_html=True
            )
            st.caption({
                "TO_SEND":    "Not sent yet",
                "SENT":       "Email sent, awaiting ACK",
                "ACK":        "Vendor acknowledged receipt",
                "QUOTE_RCD":  "Quote / offer received",
                "REVISED":    "Revised quote after negotiation",
                "SHORTLISTED":"Technically shortlisted",
                "PO":         "Purchase Order placed",
                "CLOSED":     "Finalized or not selected",
            }.get(s, ""))

# ── Next Steps ────────────────────────────────────────────────────────
try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "60")
except Exception:
    pass
