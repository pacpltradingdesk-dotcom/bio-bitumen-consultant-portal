"""
Bio Bitumen Master Consulting System — Compliance & License Tracker
===================================================================
25 license types, state-wise tracking, per-customer compliance management.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from database import (init_db, get_all_customers, get_customer,
                       get_compliance_items, update_compliance_item,
                       init_compliance_for_customer)
from config import LICENSE_TYPES, STATES

st.set_page_config(page_title="Compliance Tracker", page_icon="📋", layout="wide")
init_db()
st.title("Compliance & License Tracker")
st.markdown("**Track all licenses and approvals needed for plant setup — state-wise**")
st.markdown("---")

tab_master, tab_customer = st.tabs(["Master License List", "Customer Compliance Tracking"])

# ═══════════════════════════════════════════════════════════════════
# TAB 1: MASTER LICENSE LIST
# ═══════════════════════════════════════════════════════════════════
with tab_master:
    st.subheader(f"All {len(LICENSE_TYPES)} License Types Required for Bio-Bitumen Plant")

    # Summary metrics
    mandatory = [lt for lt in LICENSE_TYPES if lt.get("mandatory")]
    optional = [lt for lt in LICENSE_TYPES if not lt.get("mandatory")]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Licenses", len(LICENSE_TYPES))
    c2.metric("Mandatory", len(mandatory))
    c3.metric("Optional", len(optional))

    # Category filter
    categories = sorted(set(lt["category"] for lt in LICENSE_TYPES))
    selected_cats = st.multiselect("Filter by Category", categories, default=categories)

    # Display table
    filtered = [lt for lt in LICENSE_TYPES if lt["category"] in selected_cats]
    license_df = pd.DataFrame(filtered)
    license_df["Mandatory"] = license_df["mandatory"].apply(lambda x: "Yes" if x else "No")
    license_df["Timeline"] = license_df["typical_days"].apply(lambda x: f"{x} days")
    display_df = license_df[["name", "authority", "category", "Mandatory", "Timeline"]].copy()
    display_df.columns = ["License", "Issuing Authority", "Category", "Mandatory", "Typical Timeline"]
    st.dataframe(display_df, width="stretch", hide_index=True)

    # Timeline Gantt-like view
    st.markdown("---")
    st.subheader("Timeline Estimate (Sequential)")
    total_days = sum(lt["typical_days"] for lt in mandatory)
    st.info(f"Total estimated time for all mandatory licenses: **{total_days} days** (~{total_days//30} months)")
    st.caption("Many licenses can be applied for in parallel, reducing actual timeline to 3-4 months.")


# ═══════════════════════════════════════════════════════════════════
# TAB 2: CUSTOMER COMPLIANCE TRACKING
# ═══════════════════════════════════════════════════════════════════
with tab_customer:
    st.subheader("Per-Customer License Tracking")

    customers = get_all_customers()
    if not customers:
        st.warning("Add customers in Customer Manager first.")
        st.stop()

    cust_map = {c["id"]: f"{c['name']} ({c.get('company', '')})" for c in customers}
    selected_id = st.selectbox("Select Customer", list(cust_map.keys()),
                                format_func=lambda x: cust_map[x])

    # Initialize compliance items for this customer
    init_compliance_for_customer(selected_id, LICENSE_TYPES)
    items = get_compliance_items(selected_id)

    # Status summary
    status_counts = {}
    for item in items:
        s = item["status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Not Started", status_counts.get("Not Started", 0))
    sc2.metric("Applied", status_counts.get("Applied", 0))
    sc3.metric("Received", status_counts.get("Received", 0))
    sc4.metric("Expired", status_counts.get("Expired", 0))

    # Editable compliance table
    st.markdown("---")
    for item in items:
        with st.expander(f"{'✅' if item['status'] == 'Received' else '⏳' if item['status'] == 'Applied' else '⬜'} {item['license_name']} — {item['status']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_status = st.selectbox("Status", ["Not Started", "Applied", "Received", "Expired"],
                                           index=["Not Started", "Applied", "Received", "Expired"].index(item["status"]),
                                           key=f"status_{item['id']}")
            with col2:
                applied = st.date_input("Applied Date", value=None, key=f"applied_{item['id']}")
                received = st.date_input("Received Date", value=None, key=f"received_{item['id']}")
            with col3:
                expiry = st.date_input("Expiry Date", value=None, key=f"expiry_{item['id']}")
                notes = st.text_input("Notes", value=item.get("notes", ""), key=f"notes_{item['id']}")

            if st.button("Update", key=f"update_{item['id']}"):
                update_compliance_item(item["id"], {
                    "status": new_status,
                    "applied_date": str(applied) if applied else None,
                    "received_date": str(received) if received else None,
                    "expiry_date": str(expiry) if expiry else None,
                    "notes": notes,
                })
                st.success(f"Updated {item['license_name']}")
                st.rerun()

        # ── Compliance Score ─────────────────────────────────────────
        st.markdown("---")
        st.subheader("Compliance Score")
        total_items = len(items)
        received_items = sum(1 for i in items if i["status"] == "Received")
        applied_items = sum(1 for i in items if i["status"] == "Applied")
        compliance_score = (received_items / total_items * 100) if total_items > 0 else 0

        cs1, cs2, cs3, cs4 = st.columns(4)
        cs1.metric("Total Licenses", total_items)
        cs2.metric("Received", received_items)
        cs3.metric("Applied", applied_items)
        cs4.metric("Compliance Score", f"{compliance_score:.0f}%")

        import plotly.express as px
        st.progress(compliance_score / 100)

        # ── Expiry Alerts ────────────────────────────────────────────
        import datetime
        today = datetime.date.today()
        expiring_soon = []
        for item in items:
            if item.get("expiry_date") and item["status"] == "Received":
                try:
                    exp_date = datetime.date.fromisoformat(item["expiry_date"])
                    days_left = (exp_date - today).days
                    if 0 < days_left <= 90:
                        expiring_soon.append((item["license_name"], days_left, item["expiry_date"]))
                except (ValueError, TypeError):
                    pass

        if expiring_soon:
            st.warning(f"**{len(expiring_soon)} licenses expiring within 90 days!**")
            for name, days, exp in sorted(expiring_soon, key=lambda x: x[1]):
                icon = "🔴" if days <= 30 else "🟡"
                st.markdown(f"{icon} **{name}** — expires {exp} ({days} days left)")

        # ── License Timeline (Gantt) ─────────────────────────────────
        st.markdown("---")
        st.subheader("License Application Timeline")

        import plotly.express as px
        gantt_data = []
        for item in items:
            if item.get("applied_date"):
                start = item["applied_date"]
                end = item.get("received_date") or item.get("expiry_date") or str(today)
                gantt_data.append({
                    "License": item["license_name"],
                    "Start": start,
                    "End": end,
                    "Status": item["status"],
                })

        if gantt_data:
            gantt_df = pd.DataFrame(gantt_data)
            gantt_df["Start"] = pd.to_datetime(gantt_df["Start"])
            gantt_df["End"] = pd.to_datetime(gantt_df["End"])
            color_map = {"Applied": "#FF8800", "Received": "#00AA44", "Expired": "#CC3333", "Not Started": "#cccccc"}
            fig_gantt = px.timeline(gantt_df, x_start="Start", x_end="End", y="License",
                                    color="Status", color_discrete_map=color_map,
                                    title="License Application Progress")
            fig_gantt.update_yaxes(autorange="reversed")
            fig_gantt.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig_gantt, width="stretch")
        else:
            st.info("Apply for licenses and add dates to see the timeline chart.")
