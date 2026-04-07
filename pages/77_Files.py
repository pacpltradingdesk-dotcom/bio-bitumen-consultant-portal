"""
Bio Bitumen Consultant Portal — Document Library
Browse, search, filter, and download all 3,085+ project documents.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from state_manager import init_state, get_config
from document_index import build_index, search_index
from config import (CAPACITY_KEYS, CAPACITY_LABELS, FILE_TYPES,
                    DOCUMENT_SECTIONS, SUBMISSION_CATEGORIES, STATES)

st.set_page_config(page_title="Document Library", page_icon="📚", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.title("Document Library")

# Load index
doc_df = build_index()
st.markdown(f"**{len(doc_df):,}** documents indexed from the Bio Bitumen project suite.")
st.markdown("---")

# ── Filters (Sidebar) ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    if st.button("Print Page", key="print_pg"):
        import streamlit.components.v1 as _stc
        _stc.html("<script>window.print();</script>", height=0)

    st.header("Filters")

    search = st.text_input("Search filename", placeholder="e.g. DPR, Bank Loan, Safety...")

    ext_options = sorted(doc_df["extension"].dropna().unique().tolist())
    ext_labels = [f".{e} ({FILE_TYPES.get(e, e)})" for e in ext_options]
    selected_exts = st.multiselect("File Type", options=ext_options,
                                    format_func=lambda x: f".{x} ({FILE_TYPES.get(x, x)})")

    selected_caps = st.multiselect("Plant Capacity", options=CAPACITY_KEYS,
                                    format_func=lambda x: CAPACITY_LABELS.get(x, x))

    section_options = sorted(doc_df["section"].dropna().unique().tolist())
    selected_sections = st.multiselect("Document Section", options=section_options,
                                        format_func=lambda x: DOCUMENT_SECTIONS.get(x, x))

    sub_options = sorted(doc_df["submission_category"].dropna().unique().tolist())
    selected_subs = st.multiselect("Submission Category", options=sub_options,
                                    format_func=lambda x: SUBMISSION_CATEGORIES.get(x, x))

    state_options = sorted(doc_df["state"].dropna().unique().tolist())
    selected_states = st.multiselect("State", options=state_options)

    top_folders = sorted(doc_df["top_folder"].dropna().unique().tolist())
    selected_tops = st.multiselect("Top-level Folder", options=top_folders)

# ── Apply Filters ─────────────────────────────────────────────────────
filters = {}
if selected_exts:
    filters["extensions"] = selected_exts
if selected_caps:
    filters["capacities"] = selected_caps
if selected_sections:
    filters["sections"] = selected_sections
if selected_subs:
    filters["submission_categories"] = selected_subs
if selected_states:
    filters["states"] = selected_states
if selected_tops:
    filters["top_folders"] = selected_tops

filtered = search_index(doc_df, query=search, filters=filters if filters else None)

# ── Results ───────────────────────────────────────────────────────────
st.markdown(f"### Showing **{len(filtered):,}** of {len(doc_df):,} documents")

if not filtered.empty:
    # Sort options
    sort_col = st.selectbox("Sort by", ["filename", "size_bytes", "extension", "capacity"],
                             index=0, label_visibility="collapsed")
    sort_asc = st.toggle("Ascending", value=True)
    sorted_df = filtered.sort_values(sort_col, ascending=sort_asc)

    # Display
    display_cols = ["filename", "extension", "size_display", "capacity", "section", "top_folder", "relative_path"]
    display_labels = ["Filename", "Type", "Size", "Capacity", "Section", "Folder", "Path"]
    show_df = sorted_df[display_cols].head(100).copy()
    show_df.columns = display_labels
    st.dataframe(show_df, width="stretch", hide_index=True)

    if len(filtered) > 100:
        st.caption(f"Showing first 100. Narrow your search to see more specific results.")

    # ── Download Section ──────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Download Files")
    st.markdown("Select a file from the results above and enter its filename below to download.")

    download_query = st.text_input("Enter exact filename to download", key="download_input")
    if download_query:
        match = filtered[filtered["filename"] == download_query]
        if not match.empty:
            file_path = match.iloc[0]["absolute_path"]
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                st.download_button(
                    label=f"Download {download_query}",
                    data=file_bytes,
                    file_name=download_query,
                    mime="application/octet-stream",
                )
            else:
                st.error("File not found on disk.")
        else:
            st.warning("No exact match found. Check the filename.")

else:
    st.info("No documents match your current filters. Try adjusting your search.")

# ── Stats ─────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Library Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**By File Type**")
    type_counts = doc_df["extension"].value_counts().head(10)
    st.dataframe(type_counts.reset_index().rename(
        columns={"index": "Type", "extension": "Type", "count": "Count"}),
        hide_index=True, width="stretch")

with col2:
    st.markdown("**By Capacity**")
    cap_counts = doc_df["capacity"].dropna().value_counts()
    st.dataframe(cap_counts.reset_index().rename(
        columns={"capacity": "Capacity", "count": "Count"}),
        hide_index=True, width="stretch")

with col3:
    st.markdown("**By Top Folder**")
    folder_counts = doc_df["top_folder"].value_counts().head(10)
    st.dataframe(folder_counts.reset_index().rename(
        columns={"top_folder": "Folder", "count": "Count"}),
        hide_index=True, width="stretch")


# ── AI Assist ────────────────────────────────────────────────────
try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("AI Assist"):
            if st.button("Generate AI Summary", type="primary", key="ai_41Fil"):
                with st.spinner("AI working..."):
                    _p = f"Summarize this section for a {cfg.get('capacity_tpd',20):.0f} TPD bio-bitumen plant in {cfg.get('state','')}. Investment Rs {cfg.get('investment_cr',8):.2f} Cr. Professional consultant format."
                    _r, _pv = ask_ai(_p, "Senior industrial consultant.", 800)
                if _r:
                    st.markdown(_r)
except Exception:
    pass


# ── Next Steps Navigation ──
try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "77")
except Exception:
    pass
