"""
Project Timeline — 10-Phase Implementation with Gantt Chart
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Project Timeline", page_icon="📅", layout="wide")
st.title("Project Implementation Timeline")
st.markdown("**10-Phase: Pre-Feasibility → Commercial Production (12-18 months)**")
st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# 10-PHASE TIMELINE
# ═══════════════════════════════════════════════════════════════════
phases = pd.DataFrame([
    {"Phase": "1. Pre-Feasibility", "Start Month": 0, "Duration": 1, "Activities": "Site selection, feasibility study, DPR preparation", "Responsible": "Consultant"},
    {"Phase": "2. Company Setup", "Start Month": 1, "Duration": 1, "Activities": "ROC incorporation, PAN, TAN, GST, Udyam registration", "Responsible": "Legal/CA"},
    {"Phase": "3. Land & Approvals", "Start Month": 1, "Duration": 3, "Activities": "Land purchase/lease, building plan, zoning approval", "Responsible": "Owner + Legal"},
    {"Phase": "4. Environmental", "Start Month": 2, "Duration": 5, "Activities": "CTE from PCB, EIA, fire NOC, PESO license", "Responsible": "Consultant + PCB"},
    {"Phase": "5. Bank Loan", "Start Month": 2, "Duration": 3, "Activities": "DPR submission, CMA data, bank appraisal, sanction", "Responsible": "CA + Bank"},
    {"Phase": "6. Design & Engineering", "Start Month": 3, "Duration": 3, "Activities": "Detailed engineering, P&ID, civil design, electrical SLD", "Responsible": "Engineer"},
    {"Phase": "7. Procurement", "Start Month": 4, "Duration": 4, "Activities": "Equipment ordering, vendor finalization, delivery tracking", "Responsible": "Procurement"},
    {"Phase": "8. Civil & Construction", "Start Month": 5, "Duration": 5, "Activities": "Foundation, structure, building, roads, bund walls", "Responsible": "Contractor"},
    {"Phase": "9. Installation & Commissioning", "Start Month": 9, "Duration": 3, "Activities": "Equipment erection, piping, electrical, testing, trial run", "Responsible": "Vendor + Engineer"},
    {"Phase": "10. Commercial Production", "Start Month": 12, "Duration": 6, "Activities": "CTO from PCB, ramp-up: 40% → 85% utilization over 18 months", "Responsible": "Operations"},
])

# ── Gantt Chart ──────────────────────────────────────────────────
fig = px.timeline(
    phases,
    x_start=phases["Start Month"].apply(lambda x: f"2026-{(x % 12) + 1:02d}-01"),
    x_end=phases.apply(lambda r: f"2026-{((r['Start Month'] + r['Duration']) % 12) + 1:02d}-01", axis=1),
    y="Phase",
    color="Duration",
    color_continuous_scale="Blues",
    title="Project Implementation Gantt Chart (12-18 Months)",
)
fig.update_layout(height=500, template="plotly_white", yaxis_autorange="reversed")
st.plotly_chart(fig, width="stretch")

# ── Phase Details Table ──────────────────────────────────────────
st.dataframe(phases, width="stretch", hide_index=True)

st.markdown("---")

# ── Key Milestones ───────────────────────────────────────────────
st.subheader("Key Milestones")
milestones = pd.DataFrame([
    {"Month": "Month 0", "Milestone": "Project GO decision", "Deliverable": "Signed DPR + Feasibility Report"},
    {"Month": "Month 1", "Milestone": "Company incorporated", "Deliverable": "ROC certificate, PAN, GST"},
    {"Month": "Month 3", "Milestone": "Land secured + Bank sanction", "Deliverable": "Land documents + Loan sanction letter"},
    {"Month": "Month 5", "Milestone": "CTE from PCB obtained", "Deliverable": "Consent to Establish"},
    {"Month": "Month 6", "Milestone": "All equipment ordered", "Deliverable": "POs + delivery schedule"},
    {"Month": "Month 10", "Milestone": "Construction complete", "Deliverable": "Civil completion certificate"},
    {"Month": "Month 12", "Milestone": "Trial run successful", "Deliverable": "Product samples + test reports"},
    {"Month": "Month 13", "Milestone": "CTO from PCB", "Deliverable": "Consent to Operate"},
    {"Month": "Month 14", "Milestone": "Commercial production starts", "Deliverable": "First sales invoice"},
    {"Month": "Month 18", "Milestone": "85% utilization achieved", "Deliverable": "Steady-state operations"},
])
st.dataframe(milestones, width="stretch", hide_index=True)

st.markdown("---")

# ── License Timeline (parallel tracks) ────────────────────────────
st.subheader("License/Approval Timeline (Parallel Tracks)")
licenses = pd.DataFrame([
    {"License": "Company Incorporation (ROC)", "Start": 1, "Duration": 1, "Authority": "ROC/MCA"},
    {"License": "GST + PAN + TAN", "Start": 1, "Duration": 1, "Authority": "IT Dept / GST Portal"},
    {"License": "Udyam (MSME)", "Start": 1, "Duration": 1, "Authority": "MSME Portal"},
    {"License": "Building Plan Approval", "Start": 2, "Duration": 2, "Authority": "Municipal/Nagar Palika"},
    {"License": "CTE (Pollution Board)", "Start": 2, "Duration": 5, "Authority": "State PCB"},
    {"License": "Factory License", "Start": 3, "Duration": 2, "Authority": "Dir. of Factories"},
    {"License": "Fire NOC", "Start": 3, "Duration": 3, "Authority": "State Fire Services"},
    {"License": "PESO License", "Start": 3, "Duration": 4, "Authority": "PESO Nagpur"},
    {"License": "Electricity HT Connection", "Start": 4, "Duration": 3, "Authority": "State DISCOM"},
    {"License": "NHAI Material Approval", "Start": 6, "Duration": 8, "Authority": "NHAI/IRC"},
    {"License": "CTO (Pollution Board)", "Start": 12, "Duration": 2, "Authority": "State PCB"},
])
st.dataframe(licenses, width="stretch", hide_index=True)

total_calendar = max(l["Start"] + l["Duration"] for _, l in licenses.iterrows())
st.info(f"**Total calendar time for all licenses:** ~{total_calendar} months (many run in parallel, so effective time is 12-14 months)")

st.caption("Timeline based on actual project experience. Durations may vary by state.")
