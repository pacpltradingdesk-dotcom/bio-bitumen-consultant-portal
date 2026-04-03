"""
Meeting Planner — Auto-Generated Briefs, Agenda, Notes, Follow-ups
====================================================================
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import datetime
from database import (init_db, get_all_customers, get_customer,
                       insert_meeting, get_meetings, get_milestones,
                       get_compliance_items, get_all_communications)
from state_manager import get_config, init_state
from config import COMPANY

st.set_page_config(page_title="Meeting Planner", page_icon="📋", layout="wide")
init_db()
init_state()
cfg = get_config()

st.title("Meeting Planner & Contact Hub")
st.markdown("**Auto-Generated Briefs | Agenda Templates | Notes & Follow-ups**")
st.markdown("---")

customers = get_all_customers()

if not customers:
    st.warning("No customers in CRM. Add customers first.")
    st.page_link("pages/12_Customers.py", label="Go to Customer Manager", icon="👥")
    st.stop()

tab_brief, tab_schedule, tab_history = st.tabs(["Meeting Brief", "Schedule Meeting", "Meeting History"])

# ══════════════════════════════════════════════════════════════════════
# TAB 1: AUTO-GENERATED MEETING BRIEF
# ══════════════════════════════════════════════════════════════════════
with tab_brief:
    st.subheader("Auto-Generated Meeting Brief")

    cust_names = {c["id"]: f"{c['name']} ({c.get('company', '')})" for c in customers}
    selected_id = st.selectbox("Select Customer", list(cust_names.keys()),
                                format_func=lambda x: cust_names[x], key="brief_cust")

    cust = next(c for c in customers if c["id"] == selected_id)

    if st.button("Generate Meeting Brief", type="primary", key="gen_brief"):
        # Gather all customer data
        milestones = get_milestones(selected_id)
        compliance = get_compliance_items(selected_id)
        comms = get_all_communications()
        cust_comms = [c for c in comms if c.get("customer_id") == selected_id]

        brief = f"""
{'='*60}
MEETING BRIEF — {cust['name']}
{'='*60}
Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
Prepared by: {COMPANY['trade_name']} Consulting System

CUSTOMER PROFILE
{'─'*40}
Name:           {cust['name']}
Company:        {cust.get('company', 'N/A')}
Phone:          {cust.get('phone', 'N/A')}
Email:          {cust.get('email', 'N/A')}
State:          {cust.get('state', 'N/A')}
City:           {cust.get('city', 'N/A')}
Interest:       {cust.get('interested_capacity', 'N/A')}
Budget:         Rs {cust.get('budget_cr', 0)} Crore
Pipeline Stage: {cust.get('status', 'New')}
Notes:          {cust.get('notes', 'None')}

CURRENT CONFIGURATION
{'─'*40}
Capacity:       {cfg['capacity_tpd']:.0f} TPD
Investment:     Rs {cfg['investment_cr']:.2f} Cr
ROI:            {cfg['roi_pct']:.1f}%
Break-Even:     {cfg['break_even_months']} months
Monthly Profit: Rs {cfg['monthly_profit_lac']:.1f} Lac
"""

        if milestones:
            completed = sum(1 for m in milestones if m["status"] == "Completed")
            brief += f"\nPROJECT STATUS ({completed}/{len(milestones)} milestones done)\n{'─'*40}\n"
            for m in milestones:
                icon = "✓" if m["status"] == "Completed" else ("►" if m["status"] == "In Progress" else "○")
                brief += f"  {icon} {m['milestone_name']} — {m['status']}\n"

        if compliance:
            received = sum(1 for c in compliance if c["status"] == "Received")
            brief += f"\nCOMPLIANCE ({received}/{len(compliance)} licenses)\n{'─'*40}\n"
            for c in compliance[:10]:
                brief += f"  {'✓' if c['status']=='Received' else '○'} {c['license_name']} — {c['status']}\n"

        if cust_comms:
            brief += f"\nLAST COMMUNICATIONS ({len(cust_comms)} total)\n{'─'*40}\n"
            for c in cust_comms[:5]:
                brief += f"  [{c.get('channel','Email')}] {c.get('subject','')} — {c.get('sent_at','')[:10]}\n"

        brief += f"""
SUGGESTED AGENDA
{'─'*40}
1. Review project status and current configuration
2. Discuss financial model (Rs {cfg['investment_cr']:.2f} Cr / {cfg['roi_pct']:.1f}% ROI)
3. Address any compliance/regulatory concerns
4. Next steps and timeline
5. Action items

{'='*60}
{COMPANY['name']} | {COMPANY['phone']}
"""

        st.text_area("Meeting Brief", brief, height=500)
        st.download_button("Download Brief", brief,
                            f"Meeting_Brief_{cust['name'].replace(' ', '_')}.txt", "text/plain")

# ══════════════════════════════════════════════════════════════════════
# TAB 2: SCHEDULE NEW MEETING
# ══════════════════════════════════════════════════════════════════════
with tab_schedule:
    st.subheader("Schedule New Meeting")

    sch1, sch2 = st.columns(2)
    with sch1:
        sch_cust = st.selectbox("Customer", list(cust_names.keys()),
                                 format_func=lambda x: cust_names[x], key="sch_cust")
        sch_date = st.date_input("Meeting Date", datetime.date.today(), key="sch_date")
        sch_type = st.selectbox("Meeting Type",
                                 ["In-Person", "Video Call", "Phone Call", "Site Visit", "Bank Meeting"],
                                 key="sch_type")

    with sch2:
        # Agenda templates
        agenda_templates = {
            "Initial Consultation": "1. Understand client needs\n2. Present bio-bitumen opportunity\n3. Show capacity options\n4. Discuss investment range\n5. Schedule site visit",
            "Financial Discussion": "1. Review DPR and financials\n2. Discuss funding options\n3. EMI and loan structure\n4. Subsidy opportunities\n5. Next steps for bank submission",
            "Site Visit": "1. Inspect proposed site\n2. Assess land suitability\n3. Check utility availability\n4. Discuss layout options\n5. Measure and document",
            "Bank Presentation": "1. Present DPR to bank\n2. Review CMA data\n3. Discuss collateral\n4. CGTMSE eligibility\n5. Timeline for sanction",
            "Custom": "",
        }
        template = st.selectbox("Agenda Template", list(agenda_templates.keys()), key="sch_template")
        agenda = st.text_area("Agenda", value=agenda_templates[template], height=150, key="sch_agenda")

    notes = st.text_area("Pre-Meeting Notes", placeholder="Any specific points to prepare...", key="sch_notes")

    if st.button("Schedule Meeting", type="primary", key="save_meeting"):
        insert_meeting(sch_cust, sch_date.strftime("%Y-%m-%d"), sch_type, agenda, notes)
        st.success(f"Meeting scheduled for {sch_date} with {cust_names[sch_cust]}")
        st.rerun()

# ══════════════════════════════════════════════════════════════════════
# TAB 3: MEETING HISTORY
# ══════════════════════════════════════════════════════════════════════
with tab_history:
    st.subheader("Meeting History")

    hist_cust = st.selectbox("Filter by Customer",
                              [0] + list(cust_names.keys()),
                              format_func=lambda x: "All Customers" if x == 0 else cust_names[x],
                              key="hist_cust")

    meetings = get_meetings(hist_cust if hist_cust != 0 else None, limit=50)

    if meetings:
        for m in meetings:
            cust = next((c for c in customers if c["id"] == m.get("customer_id")), None)
            cust_name = cust["name"] if cust else "Unknown"

            type_icon = {"In-Person": "🤝", "Video Call": "💻", "Phone Call": "📞",
                          "Site Visit": "🏗️", "Bank Meeting": "🏦"}.get(m.get("meeting_type", ""), "📋")

            with st.expander(f"{type_icon} {m.get('meeting_date', '')} — {cust_name} ({m.get('meeting_type', '')})"):
                mc1, mc2 = st.columns(2)
                with mc1:
                    st.markdown(f"**Agenda:**\n{m.get('agenda', 'No agenda recorded')}")
                with mc2:
                    st.markdown(f"**Notes:**\n{m.get('notes', 'No notes')}")
                    if m.get("action_items"):
                        st.markdown(f"**Action Items:**\n{m['action_items']}")

                # Add post-meeting notes
                post_notes = st.text_area("Add Post-Meeting Notes", key=f"post_{m['id']}")
                action_items = st.text_area("Action Items", key=f"action_{m['id']}")
                if st.button("Save Notes", key=f"save_notes_{m['id']}"):
                    from database import get_connection
                    with get_connection() as conn:
                        conn.execute("UPDATE meetings SET notes=?, action_items=? WHERE id=?",
                                      (post_notes, action_items, m["id"]))
                    st.success("Notes saved!")
                    st.rerun()
    else:
        st.info("No meetings recorded yet. Schedule your first meeting above.")

    # Calendar-style overview
    if meetings:
        st.markdown("---")
        st.subheader("Meeting Calendar")
        cal_df = pd.DataFrame([{
            "Date": m.get("meeting_date", ""),
            "Customer": next((c["name"] for c in customers if c["id"] == m.get("customer_id")), "Unknown"),
            "Type": m.get("meeting_type", ""),
        } for m in meetings])
        st.dataframe(cal_df, width="stretch", hide_index=True)

st.markdown("---")
st.caption(f"{COMPANY['name']} | Meeting Management")
