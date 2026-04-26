"""
Client Manager — Multi-Client Project Management
=================================================
Add, edit, switch, and manage multiple client projects.
Each client has their own complete config — capacity, financials, location, etc.
Switching client loads ALL their data into every page automatically.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from state_manager import (init_state, get_config, update_fields,
                             set_active_client, get_active_client_id,
                             save_current_as_client, get_client_display_name, DEFAULTS)
from database import (init_db, get_all_client_profiles, get_all_customers,
                       insert_customer, update_customer, delete_customer,
                       save_client_config, load_client_config, get_customer,
                       seed_client_if_missing)
from config import COMPANY, STATES

st.set_page_config(page_title="Client Manager", page_icon="👥", layout="wide")
init_db()
init_state()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.title("Client Manager")
st.markdown("**Manage multiple client projects — switch client to auto-load all their data everywhere**")
st.markdown("---")

active_cid = get_active_client_id()
profiles = get_all_client_profiles()

# ══════════════════════════════════════════════════════════════════════
# TOP — Active client banner
# ══════════════════════════════════════════════════════════════════════
if active_cid:
    cust = get_customer(active_cid)
    cfg = get_config()
    if cust:
        st.success(f"**Active Client: {cust.get('name','')} | {cust.get('company','')}** | "
                   f"{cfg.get('capacity_tpd',0):.0f} TPD | {cust.get('state','')} | "
                   f"₹{cfg.get('investment_cr',0):.2f} Cr")
else:
    st.warning("No client selected. Select or add a client below.")

st.markdown("---")

tab_list, tab_add, tab_edit, tab_switch = st.tabs([
    "All Clients", "Add New Client", "Edit / Update", "Switch & Load"
])

# ══════════════════════════════════════════════════════════════════════
# TAB 1 — CLIENT LIST
# ══════════════════════════════════════════════════════════════════════
with tab_list:
    st.subheader(f"All Clients ({len(profiles)} total)")

    if not profiles:
        st.info("No clients yet. Use **Add New Client** tab to add your first client.")
    else:
        import pandas as pd
        rows = []
        for p in profiles:
            rows.append({
                "ID": p["id"],
                "Client Name": p.get("name", ""),
                "Company": p.get("company", ""),
                "State": p.get("state", ""),
                "City": p.get("city", ""),
                "Capacity (TPD)": f"{p.get('capacity_tpd', 0):.0f}",
                "Investment (Cr)": f"₹{p.get('investment_cr', 0):.2f}",
                "Project": p.get("project_name", ""),
                "Status": p.get("status", ""),
                "Active": "✅" if p["id"] == active_cid else "",
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Quick Switch")
        cols = st.columns(min(4, len(profiles)))
        for i, p in enumerate(profiles):
            with cols[i % 4]:
                is_active = p["id"] == active_cid
                btn_label = f"{'✅ ' if is_active else ''}{p.get('name','Client')[:20]}"
                btn_detail = f"{p.get('capacity_tpd',0):.0f} TPD | {p.get('city','') or p.get('state','')}"
                if st.button(btn_label, help=btn_detail, key=f"qs_{p['id']}",
                             type="primary" if is_active else "secondary"):
                    if set_active_client(p["id"]):
                        st.success(f"Switched to: {p.get('name','')}")
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════
# TAB 2 — ADD NEW CLIENT
# ══════════════════════════════════════════════════════════════════════
with tab_add:
    st.subheader("Add New Client Project")
    st.caption("Fill client info + project config → all pages auto-populate for this client")

    with st.form("add_client_form"):
        st.markdown("#### Client Information")
        ac1, ac2 = st.columns(2)
        with ac1:
            nc_name = st.text_input("Contact Person Name *", placeholder="e.g., Rajesh Kumar")
            nc_company = st.text_input("Company / Legal Entity *", placeholder="e.g., Raj Bio-Bitumen Pvt Ltd")
            nc_gstin = st.text_input("GSTIN", placeholder="e.g., 27AABCR1234Z1ZY")
            nc_phone = st.text_input("Phone *", placeholder="+91 98765 43210")
        with ac2:
            nc_email = st.text_input("Email", placeholder="contact@company.com")
            nc_whatsapp = st.text_input("WhatsApp", placeholder="+91 98765 43210")
            nc_state = st.selectbox("State", STATES, key="nc_state")
            nc_city = st.text_input("City / Location", placeholder="e.g., Pune")

        nc_address = st.text_area("Registered Address", height=60,
                                   placeholder="Full address with pincode")
        nc_status = st.selectbox("Lead Status", ["New", "Prospect", "Active", "On Hold", "Completed"])
        nc_notes = st.text_area("Notes", height=60,
                                 placeholder="Any additional notes about this client")

        st.markdown("---")
        st.markdown("#### Project Configuration")
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            nc_project_name = st.text_input("Project Name",
                                             placeholder="e.g., Pune 20 TPD Bio-Bitumen Plant")
            nc_capacity = st.number_input("Capacity (TPD)", min_value=5.0, max_value=100.0, value=20.0, step=5.0)
            nc_investment = st.number_input("Total Investment (Cr)", min_value=1.0, max_value=50.0, value=8.0, step=0.5)
        with pc2:
            nc_product = st.selectbox("Primary Product",
                ["VG30 Bio-Bitumen", "PMB-40", "VG40 Bio-Bitumen", "CRMB", "Bio-Oil + Bio-Char"])
            nc_process = st.selectbox("Process Type", [1, 2, 3],
                format_func=lambda x: {1: "Full Chain (Pyrolysis→Blend)", 2: "Blending Only", 3: "Raw Output"}[x])
            nc_working_days = st.number_input("Working Days/Year", 200, 365, 300)
        with pc3:
            nc_plot_l = st.number_input("Plot Length (m)", 30, 300, 120)
            nc_plot_w = st.number_input("Plot Width (m)", 20, 200, 80)
            nc_equity_ratio = st.slider("Equity Ratio (%)", 20, 80, 40) / 100

        nc_site_address = st.text_area("Site / Plant Address", height=60,
                                        placeholder="Location where plant will be set up")

        submitted = st.form_submit_button("Add Client & Save Project Config", type="primary")

    if submitted:
        if not nc_name or not nc_company:
            st.error("Client Name and Company are required.")
        else:
            customer_data = {
                "name": nc_name, "company": nc_company,
                "email": nc_email, "phone": nc_phone, "whatsapp": nc_whatsapp,
                "state": nc_state, "city": nc_city,
                "interested_capacity": f"{nc_capacity:.0f} TPD",
                "budget_cr": nc_investment, "status": nc_status,
                "notes": f"GSTIN: {nc_gstin}\nAddress: {nc_address}\n{nc_notes}",
            }
            cid = insert_customer(customer_data)

            project_config = {
                "client_name": nc_name, "client_company": nc_company,
                "client_email": nc_email, "client_phone": nc_phone,
                "client_gst": nc_gstin, "project_name": nc_project_name,
                "state": nc_state, "location": nc_city,
                "site_address": nc_site_address,
                "capacity_tpd": nc_capacity, "investment_cr": nc_investment,
                "process_id": nc_process, "working_days": nc_working_days,
                "equity_ratio": nc_equity_ratio,
                "plot_length_m": nc_plot_l, "plot_width_m": nc_plot_w,
            }
            save_client_config(cid, project_config)

            st.success(f"Client **{nc_name}** ({nc_company}) added successfully! ID: {cid}")
            if st.button("Switch to This Client Now", key="switch_new"):
                set_active_client(cid)
                st.rerun()
            st.rerun()


# ══════════════════════════════════════════════════════════════════════
# TAB 3 — EDIT / UPDATE
# ══════════════════════════════════════════════════════════════════════
with tab_edit:
    st.subheader("Edit Existing Client")

    all_customers = get_all_customers()
    if not all_customers:
        st.info("No clients to edit.")
    else:
        edit_map = {c["id"]: f"{c['name']} | {c.get('company','')}" for c in all_customers}
        edit_id = st.selectbox("Select client to edit", list(edit_map.keys()),
                                format_func=lambda x: edit_map[x], key="edit_sel")

        if edit_id:
            ec = get_customer(edit_id)
            ec_cfg = load_client_config(edit_id) or {}

            with st.form("edit_client_form"):
                st.markdown("#### Client Info")
                ee1, ee2 = st.columns(2)
                with ee1:
                    e_name = st.text_input("Contact Name", value=ec.get("name", ""))
                    e_company = st.text_input("Company", value=ec.get("company", ""))
                    e_phone = st.text_input("Phone", value=ec.get("phone", ""))
                    e_gstin = st.text_input("GSTIN", value=ec.get("notes","").split("GSTIN:")[1].split("\n")[0].strip() if "GSTIN:" in ec.get("notes","") else "")
                with ee2:
                    e_email = st.text_input("Email", value=ec.get("email", ""))
                    e_state = st.selectbox("State", STATES,
                                           index=STATES.index(ec.get("state", STATES[0])) if ec.get("state") in STATES else 0)
                    e_city = st.text_input("City", value=ec.get("city", ""))
                    e_status = st.selectbox("Status",
                                            ["New", "Prospect", "Active", "On Hold", "Completed"],
                                            index=["New","Prospect","Active","On Hold","Completed"].index(
                                                ec.get("status","New")) if ec.get("status") in ["New","Prospect","Active","On Hold","Completed"] else 0)

                st.markdown("#### Project Config")
                ep1, ep2 = st.columns(2)
                with ep1:
                    e_proj = st.text_input("Project Name", value=ec_cfg.get("project_name", ""))
                    e_cap = st.number_input("Capacity (TPD)", 5.0, 100.0,
                                             float(ec_cfg.get("capacity_tpd", 20)), 5.0)
                    e_inv = st.number_input("Investment (Cr)", 1.0, 50.0,
                                             float(ec_cfg.get("investment_cr", 8)), 0.5)
                with ep2:
                    e_site = st.text_area("Site Address", value=ec_cfg.get("site_address", ""), height=80)
                    e_notes = st.text_area("Notes", value=ec.get("notes",""), height=80)

                update_submitted = st.form_submit_button("Update Client", type="primary")

            if update_submitted:
                update_customer(edit_id, {
                    "name": e_name, "company": e_company,
                    "email": e_email, "phone": e_phone,
                    "state": e_state, "city": e_city,
                    "status": e_status, "notes": e_notes,
                    "budget_cr": e_inv,
                    "interested_capacity": f"{e_cap:.0f} TPD",
                    "whatsapp": ec.get("whatsapp", ""),
                })
                updated_cfg = dict(ec_cfg)
                updated_cfg.update({
                    "client_name": e_name, "client_company": e_company,
                    "client_email": e_email, "client_phone": e_phone,
                    "client_gst": e_gstin, "project_name": e_proj,
                    "state": e_state, "location": e_city,
                    "site_address": e_site,
                    "capacity_tpd": e_cap, "investment_cr": e_inv,
                })
                save_client_config(edit_id, updated_cfg)
                st.success(f"Updated: {e_name}")
                if active_cid == edit_id:
                    set_active_client(edit_id)
                st.rerun()

            st.markdown("---")
            st.markdown("**Danger Zone**")
            if st.button(f"Delete Client: {ec.get('name','')}", type="secondary", key="del_client"):
                st.warning("Are you sure? This will delete all data for this client.")
                if st.button("YES, DELETE", type="primary", key="confirm_del"):
                    delete_customer(edit_id)
                    if active_cid == edit_id:
                        st.session_state["active_client_id"] = None
                    st.success("Client deleted.")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════
# TAB 4 — SWITCH & LOAD
# ══════════════════════════════════════════════════════════════════════
with tab_switch:
    st.subheader("Switch Active Client")
    st.markdown("Switching client loads **ALL their project data** into every page — "
                "drawings, financials, documents, compliance, everything.")

    if not profiles:
        st.info("No clients yet.")
    else:
        for p in profiles:
            is_active = p["id"] == active_cid
            ec = st.expander(
                f"{'🟢 ACTIVE — ' if is_active else ''}{p.get('name','')} | "
                f"{p.get('company','')} | {p.get('capacity_tpd',0):.0f} TPD | "
                f"{p.get('city','') or p.get('state','')}",
                expanded=is_active
            )
            with ec:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**Company:** {p.get('company','')}")
                    st.markdown(f"**State:** {p.get('state','')}")
                    st.markdown(f"**City:** {p.get('city','')}")
                with c2:
                    st.markdown(f"**Capacity:** {p.get('capacity_tpd',0):.0f} TPD")
                    st.markdown(f"**Investment:** ₹{p.get('investment_cr',0):.2f} Cr")
                    st.markdown(f"**Project:** {p.get('project_name','')[:40]}")
                with c3:
                    st.markdown(f"**Status:** {p.get('status','')}")
                    if not is_active:
                        if st.button(f"Load This Client", key=f"load_{p['id']}", type="primary"):
                            if set_active_client(p["id"]):
                                st.success(f"Switched to: {p.get('name','')}")
                                st.rerun()
                    else:
                        st.success("Currently Active")
                        cfg = get_config()
                        if st.button("Save Current Changes to This Client", key=f"save_{p['id']}"):
                            if save_current_as_client(p["id"]):
                                st.success("Saved!")

    st.markdown("---")
    st.subheader("Save Current Session as New Client")
    st.caption("If you've set up a config on Project Setup page, save it here under a client name.")
    cfg = get_config()
    st.info(f"Current session: {cfg.get('capacity_tpd',0):.0f} TPD | "
            f"₹{cfg.get('investment_cr',0):.2f} Cr | {cfg.get('state','')} | "
            f"Client: {cfg.get('client_name','(not set)')}")

    save_name = st.text_input("Client name to save as", value=cfg.get("client_name", ""), key="save_as_name")
    save_company = st.text_input("Company", value=cfg.get("client_company", ""), key="save_as_company")
    if st.button("Save Session as Client", type="primary", key="save_session"):
        if save_name:
            from database import seed_client_if_missing
            inputs_only = {k: v for k, v in cfg.items() if k in DEFAULTS or k in ("capacity_key",)}
            cid = seed_client_if_missing(save_name, save_company or save_name, inputs_only,
                                          {"state": cfg.get("state",""), "city": cfg.get("location",""),
                                           "status": "Active"})
            st.session_state["active_client_id"] = cid
            st.success(f"Saved as client: {save_name} (ID: {cid})")
            st.rerun()
        else:
            st.warning("Enter client name first.")


st.markdown("---")
st.caption(f"{COMPANY['name']} | Client Manager | Multi-client project system")

try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "09")
except Exception:
    pass
