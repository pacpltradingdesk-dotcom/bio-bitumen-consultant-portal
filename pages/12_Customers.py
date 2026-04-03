"""
Bio Bitumen Consultant Portal — Customer Manager (CRM)
Add, edit, delete, and track customers through the sales pipeline.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from state_manager import init_state, get_config
import pandas as pd
from database import (init_db, insert_customer, update_customer, delete_customer,
                       get_all_customers, search_customers, get_customer,
                       get_customer_count_by_status)
from config import CAPACITY_KEYS, CAPACITY_LABELS, STATES, CUSTOMER_STATUSES

st.set_page_config(page_title="Customer Manager", page_icon="👥", layout="wide")
init_state()
cfg = get_config()
init_db()
st.title("Customer Manager")

# ── Pipeline Summary ──────────────────────────────────────────────────
status_counts = get_customer_count_by_status()
if status_counts:
    cols = st.columns(len(CUSTOMER_STATUSES))
    for i, status in enumerate(CUSTOMER_STATUSES):
        count = status_counts.get(status, 0)
        cols[i].metric(status, count)
    st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────
tab_list, tab_add = st.tabs(["Customer List", "Add New Customer"])

# ══════════════════════════════════════════════════════════════════════
# TAB: CUSTOMER LIST
# ══════════════════════════════════════════════════════════════════════
with tab_list:
    search_q = st.text_input("Search customers", placeholder="Search by name, company, email, phone, state...")

    if search_q:
        customers = search_customers(search_q)
    else:
        customers = get_all_customers()

    st.markdown(f"**{len(customers)} customers**")

    if customers:
        # Display as table
        display_data = []
        for c in customers:
            display_data.append({
                "ID": c["id"],
                "Name": c["name"],
                "Company": c.get("company", ""),
                "Phone": c.get("phone", ""),
                "State": c.get("state", ""),
                "Capacity": c.get("interested_capacity", ""),
                "Status": c["status"],
                "Budget (Cr)": c.get("budget_cr", 0),
            })
        st.dataframe(pd.DataFrame(display_data), width="stretch", hide_index=True)

        # Edit / Delete Section
        st.markdown("---")
        st.subheader("Edit / Delete Customer")

        customer_options = {c["id"]: f"{c['name']} ({c.get('company', 'N/A')})" for c in customers}
        selected_id = st.selectbox("Select customer to edit", options=list(customer_options.keys()),
                                    format_func=lambda x: customer_options[x])

        if selected_id:
            cust = get_customer(selected_id)
            if cust:
                with st.form(f"edit_customer_{selected_id}"):
                    st.markdown(f"**Editing: {cust['name']}**")
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        e_name = st.text_input("Name", value=cust.get("name", ""))
                        e_company = st.text_input("Company", value=cust.get("company", ""))
                        e_email = st.text_input("Email", value=cust.get("email", ""))
                        e_phone = st.text_input("Phone", value=cust.get("phone", ""))
                        e_whatsapp = st.text_input("WhatsApp", value=cust.get("whatsapp", ""))
                    with ec2:
                        e_state = st.selectbox("State", options=[""] + STATES,
                                                index=(STATES.index(cust["state"]) + 1) if cust.get("state") in STATES else 0)
                        e_city = st.text_input("City", value=cust.get("city", ""))
                        e_capacity = st.selectbox("Interested Capacity",
                                                   options=[""] + CAPACITY_KEYS,
                                                   format_func=lambda x: CAPACITY_LABELS.get(x, "Select...") if x else "Select...",
                                                   index=(CAPACITY_KEYS.index(cust["interested_capacity"]) + 1)
                                                   if cust.get("interested_capacity") in CAPACITY_KEYS else 0)
                        e_budget = st.number_input("Budget (Crores)", value=float(cust.get("budget_cr", 0)),
                                                    min_value=0.0, step=0.5)
                        e_status = st.selectbox("Status", options=CUSTOMER_STATUSES,
                                                 index=CUSTOMER_STATUSES.index(cust["status"])
                                                 if cust.get("status") in CUSTOMER_STATUSES else 0)
                    e_notes = st.text_area("Notes", value=cust.get("notes", ""), height=80)

                    bcol1, bcol2 = st.columns(2)
                    submitted = bcol1.form_submit_button("Update Customer", type="primary")
                    if submitted:
                        update_customer(selected_id, {
                            "name": e_name, "company": e_company, "email": e_email,
                            "phone": e_phone, "whatsapp": e_whatsapp, "state": e_state,
                            "city": e_city, "interested_capacity": e_capacity,
                            "budget_cr": e_budget, "status": e_status, "notes": e_notes,
                        })
                        st.success(f"Updated {e_name}!")
                        st.rerun()

                if st.button(f"Delete {cust['name']}", type="secondary"):
                    delete_customer(selected_id)
                    st.warning(f"Deleted {cust['name']}")
                    st.rerun()
    else:
        st.info("No customers found. Add your first customer using the 'Add New Customer' tab.")


# ══════════════════════════════════════════════════════════════════════
# TAB: ADD NEW CUSTOMER
# ══════════════════════════════════════════════════════════════════════
with tab_add:
    st.subheader("Add New Customer")

    with st.form("add_customer_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name *", placeholder="Customer full name")
            company = st.text_input("Company", placeholder="Company name")
            email = st.text_input("Email", placeholder="email@example.com")
            phone = st.text_input("Phone", placeholder="+91 XXXXX XXXXX")
            whatsapp = st.text_input("WhatsApp", placeholder="+91 XXXXX XXXXX")
        with c2:
            # Pincode auto-fill
            pincode = st.text_input("Pincode (auto-fills State/City)", placeholder="e.g. 390001", key="new_cust_pin")
            auto_state = ""
            auto_city = ""
            if pincode and len(pincode) == 6 and pincode.isdigit():
                try:
                    from engines.free_apis import lookup_pincode
                    pin_data = lookup_pincode(pincode)
                    if "error" not in pin_data:
                        auto_state = pin_data.get("state", "")
                        auto_city = pin_data.get("district", pin_data.get("city", ""))
                        st.caption(f"Auto-detected: {auto_city}, {auto_state}")
                except Exception:
                    pass

            state_default = STATES.index(auto_state) + 1 if auto_state in STATES else 0
            state = st.selectbox("State", options=[""] + STATES, index=state_default)
            city = st.text_input("City", value=auto_city, placeholder="City name")
            capacity = st.selectbox("Interested Capacity",
                                     options=[""] + CAPACITY_KEYS,
                                     format_func=lambda x: CAPACITY_LABELS.get(x, "Select...") if x else "Select...")
            budget = st.number_input("Budget (Crores)", min_value=0.0, step=0.5)
            status = st.selectbox("Status", options=CUSTOMER_STATUSES)
        notes = st.text_area("Notes", placeholder="Any additional details...", height=80)

        submitted = st.form_submit_button("Add Customer", type="primary")
        if submitted:
            if not name:
                st.error("Name is required!")
            else:
                cid = insert_customer({
                    "name": name, "company": company, "email": email,
                    "phone": phone, "whatsapp": whatsapp, "state": state,
                    "city": city, "interested_capacity": capacity,
                    "budget_cr": budget, "status": status, "notes": notes,
                })
                st.success(f"Added **{name}** (ID: {cid})")
                st.rerun()
