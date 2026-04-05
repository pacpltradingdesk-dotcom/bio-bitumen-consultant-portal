"""
Bio Bitumen Consultant Portal — Package Builder
Build customer-specific document packages from the 12 submission categories.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from state_manager import init_state, get_config
from database import (init_db, get_all_customers, get_customer, insert_package)
from master_data_loader import get_plant
from config import CAPACITY_KEYS, CAPACITY_LABELS

st.set_page_config(page_title="Package Builder", page_icon="📦", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

init_db()
st.title("Package Builder")
st.markdown("Build customized document packages for your customers.")
st.markdown("---")

# ── Step 1: Select Customer ──────────────────────────────────────────
st.subheader("Step 1: Select Customer")
customers = get_all_customers()
if not customers:
    st.warning("No customers found. Please add customers in the **Customer Manager** first.")
    st.stop()

customer_map = {}
for c in customers:
    state_str = c.get('state', '')
    cap_str = CAPACITY_LABELS.get(c.get('interested_capacity', ''), '')
    label_parts = [c['name']]
    if c.get('company'):
        label_parts.append(f"({c['company']})")
    if state_str:
        label_parts.append(f"— {state_str}")
    if cap_str:
        label_parts.append(f"| {cap_str}")
    customer_map[c["id"]] = " ".join(label_parts)

selected_cust_id = st.selectbox("Customer", options=list(customer_map.keys()),
                                 format_func=lambda x: customer_map[x])
customer = get_customer(selected_cust_id)
st.success(f"Selected: **{customer['name']}** | {customer.get('company', '')} | "
           f"{customer.get('state', 'N/A')} | Interest: {CAPACITY_LABELS.get(customer.get('interested_capacity', ''), 'N/A')}")

# ── Step 2: Select Capacity ──────────────────────────────────────────
st.markdown("---")
st.subheader("Step 2: Select Plant Capacity")

# Default to customer's interested capacity, then session cfg, then 20MT
default_cap = customer.get("interested_capacity", "")
if not default_cap or default_cap not in CAPACITY_KEYS:
    cfg_cap = f"{int(cfg.get('capacity_tpd', 20)):02d}MT"
    default_cap = cfg_cap if cfg_cap in CAPACITY_KEYS else "20MT"
default_idx = CAPACITY_KEYS.index(default_cap) if default_cap in CAPACITY_KEYS else 3

selected_capacity = st.selectbox("Capacity", options=CAPACITY_KEYS,
                                  format_func=lambda x: CAPACITY_LABELS.get(x, x),
                                  index=default_idx)
plant = get_plant(selected_capacity)
st.info(f"**{plant['label']}** — Rs {plant.get('inv_cr', 'N/A')} Cr | "
        f"IRR: {plant.get('irr_pct', 'N/A')}% | Revenue Yr5: Rs {plant.get('rev_yr5_cr', 'N/A')} Cr")

# ── Step 3: Select Recipient Type ────────────────────────────────────
st.markdown("---")
st.subheader("Step 3: Select Document Package Type")

try:
    from engines.package_engine import (get_suggested_documents, get_state_forms,
                                         build_package, zip_package,
                                         get_available_recipient_types)
    recipient_types = get_available_recipient_types()
    package_engine_available = True
except Exception as e:
    st.error(f"Package engine error: {e}")
    from config import SUBMISSION_CATEGORIES
    recipient_types = SUBMISSION_CATEGORIES
    package_engine_available = False

selected_type_key = st.selectbox("Recipient Type", options=list(recipient_types.keys()),
                                  format_func=lambda x: recipient_types[x])
selected_type_label = recipient_types[selected_type_key]

# ── Step 4: Document Selection ────────────────────────────────────────
st.markdown("---")
st.subheader("Step 4: Select Documents")

# Auto-suggest documents
suggested_docs = []
if package_engine_available:
    try:
        suggested_docs = get_suggested_documents(selected_capacity, selected_type_key)
    except Exception:
        pass

if not suggested_docs:
    st.warning(f"No pre-packaged documents found for {CAPACITY_LABELS.get(selected_capacity, selected_capacity)} / "
               f"{selected_type_label}. You can add documents manually below.")

# Initialize session state for selected docs
session_key = f"pkg_docs_{selected_cust_id}_{selected_capacity}_{selected_type_key}"
if session_key not in st.session_state:
    st.session_state[session_key] = [d["absolute_path"] for d in suggested_docs]

# Show suggested documents with checkboxes
if suggested_docs:
    st.markdown(f"**{len(suggested_docs)} suggested documents** for {selected_type_label}:")
    for doc in suggested_docs:
        checked = doc["absolute_path"] in st.session_state[session_key]
        size_mb = doc["size"] / (1024 * 1024)
        if st.checkbox(f"{doc['filename']} ({size_mb:.1f} MB)", value=checked, key=f"chk_{doc['filename']}"):
            if doc["absolute_path"] not in st.session_state[session_key]:
                st.session_state[session_key].append(doc["absolute_path"])
        else:
            if doc["absolute_path"] in st.session_state[session_key]:
                st.session_state[session_key].remove(doc["absolute_path"])

# Add state forms
if customer.get("state"):
    with st.expander(f"Add State Forms ({customer['state']})"):
        try:
            state_docs = get_state_forms(customer["state"], selected_capacity)
            if state_docs:
                for doc in state_docs:
                    if st.checkbox(f"[State] {doc['filename']}", key=f"state_{doc['filename']}"):
                        if doc["absolute_path"] not in st.session_state[session_key]:
                            st.session_state[session_key].append(doc["absolute_path"])
            else:
                st.info(f"No state forms found for {customer['state']} / {selected_capacity}")
        except Exception:
            st.info(f"No state forms available for {customer['state']}")

# Add more from full library
with st.expander("Add More Documents from Library"):
    search_q = st.text_input("Search all documents", key="pkg_search")
    if search_q:
        try:
            from document_index import build_index, search_index
            doc_df = build_index()
            results = search_index(doc_df, query=search_q)
            if not results.empty:
                for _, row in results.head(20).iterrows():
                    if st.checkbox(f"{row['filename']} ({row['size_display']})",
                                  key=f"lib_{row['filename']}_{row['relative_path'][:20]}"):
                        if row["absolute_path"] not in st.session_state[session_key]:
                            st.session_state[session_key].append(row["absolute_path"])
            else:
                st.info("No documents found matching your search.")
        except Exception as e:
            st.info(f"Document search unavailable: {e}")

# ── Package Summary ───────────────────────────────────────────────────
st.markdown("---")
st.subheader("Step 5: Review & Generate")
selected_paths = st.session_state[session_key]

# Filter out non-existent files
valid_paths = [p for p in selected_paths if os.path.exists(p)]
if len(valid_paths) < len(selected_paths):
    missing = len(selected_paths) - len(valid_paths)
    st.warning(f"{missing} file(s) not found on disk and will be skipped.")
    st.session_state[session_key] = valid_paths
    selected_paths = valid_paths

total_size = sum(os.path.getsize(p) for p in selected_paths)
st.markdown(f"**{len(selected_paths)} documents selected** | Total size: **{total_size / (1024 * 1024):.1f} MB**")

# Customization toggle
customize = st.toggle("Customize DOCX files with customer details (replace names, dates, capacity)", value=True)

# Generate Package — with proper error handling and ZIP download
if st.button("Generate Package", type="primary", disabled=len(selected_paths) == 0):
    if not package_engine_available:
        st.error("Package engine not available. Check engines/package_engine.py")
    elif len(selected_paths) == 0:
        st.error("No documents selected. Please select at least one document.")
    else:
        try:
            with st.spinner(f"Building package with {len(selected_paths)} documents..."):
                pkg_folder = build_package(
                    customer=customer,
                    capacity=selected_capacity,
                    document_paths=selected_paths,
                    customize=customize,
                    plant=plant,
                )

                # Save to database
                pkg_id = insert_package({
                    "customer_id": customer["id"],
                    "capacity": selected_capacity,
                    "recipient_type": selected_type_label,
                    "documents": [os.path.basename(p) for p in selected_paths],
                    "output_folder": pkg_folder,
                    "customized": 1 if customize else 0,
                })

                st.session_state["last_package_folder"] = pkg_folder
                st.success(f"Package created! Package ID: {pkg_id} | {len(selected_paths)} documents")

                # Immediately create ZIP and offer download
                zip_path = zip_package(pkg_folder)
                with open(zip_path, "rb") as f:
                    zip_data = f.read()

                customer_name = (customer.get("name", "Customer")).replace(" ", "_")
                st.download_button(
                    label=f"Download ZIP ({len(selected_paths)} files, {len(zip_data)/(1024*1024):.1f} MB)",
                    data=zip_data,
                    file_name=f"Package_{customer_name}_{selected_capacity}.zip",
                    mime="application/zip",
                    type="primary",
                )
        except Exception as e:
            st.error(f"Package generation failed: {e}")
            st.info("Check that the package output directory exists and documents are accessible.")

# Also show ZIP download for previously generated package
if "last_package_folder" in st.session_state and os.path.exists(st.session_state.get("last_package_folder", "")):
    pkg_folder = st.session_state["last_package_folder"]
    zip_path = f"{pkg_folder}.zip"
    if os.path.exists(zip_path):
        with open(zip_path, "rb") as f:
            zip_data = f.read()
        st.download_button(
            label="Re-download Last Package ZIP",
            data=zip_data,
            file_name=os.path.basename(zip_path),
            mime="application/zip",
            key="redownload_zip",
        )


# ── AI Assist ────────────────────────────────────────────────────
try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("AI Assist"):
            if st.button("Generate AI Summary", type="primary", key="ai_42Pac"):
                with st.spinner("AI working..."):
                    _p = (f"Summarize document package for {customer.get('name', 'client')} at "
                          f"{customer.get('company', 'their company')}. "
                          f"{cfg.get('capacity_tpd',20):.0f} TPD bio-bitumen plant in {cfg.get('state','')}. "
                          f"Investment Rs {cfg.get('investment_cr',8):.2f} Cr. "
                          f"Package type: {selected_type_label}. Professional consultant format.")
                    _r, _pv = ask_ai(_p, "Senior industrial consultant.", 800)
                if _r:
                    st.markdown(_r)
except Exception:
    pass

# Print
st.markdown("---")
if st.button("Print", key="prt_42Pac"):
    import streamlit.components.v1 as _stc
    _stc.html("<script>window.print();</script>", height=0)
