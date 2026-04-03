"""
Bio Bitumen Consultant Portal — Document Index
Walks the entire document suite and builds a searchable pandas DataFrame.
"""
import os
import re
import pandas as pd
import streamlit as st
from config import DOC_ROOT, EXCLUDED_DIRS, EXCLUDED_EXTENSIONS, CAPACITY_KEYS


def _parse_capacity(rel_path):
    """Extract capacity key from path (e.g. '20MT' from 'PLANT_20MT_Day_INR_8Cr/...')."""
    for cap in CAPACITY_KEYS:
        if cap in rel_path:
            return cap
    return None


def _parse_section(parts):
    """Extract document section from path parts."""
    section_pattern = re.compile(r"^\d{2}_")
    for part in parts:
        if section_pattern.match(part) and "PLANT_" not in part:
            return part
    return None


def _parse_submission_category(rel_path):
    """Extract submission category from READY_FOR_SUBMISSION paths."""
    if "READY_FOR_SUBMISSION" not in rel_path:
        return None
    match = re.search(r"READY_FOR_SUBMISSION[/\\](\d{2}_FOR_[A-Z_]+)", rel_path)
    if match:
        return match.group(1)
    return None


def _parse_state(rel_path):
    """Extract state from STATE_WISE_APPLICATION_FORMS paths."""
    match = re.search(r"STATE_WISE_APPLICATION_FORMS[/\\]([A-Za-z_]+)[/\\]", rel_path)
    if match:
        return match.group(1).replace("_", " ")
    return None


def _should_exclude(dirpath, filename):
    """Check if a file/dir should be excluded from the index."""
    parts = dirpath.replace("\\", "/").split("/")
    for part in parts:
        if part in EXCLUDED_DIRS:
            return True

    _, ext = os.path.splitext(filename)
    if ext.lower() in EXCLUDED_EXTENSIONS:
        return True

    return False


@st.cache_data(ttl=300, show_spinner="Scanning document library...")
def build_index():
    """Walk DOC_ROOT and build a DataFrame of all document files."""
    records = []
    root_str = str(DOC_ROOT)

    for dirpath, dirnames, filenames in os.walk(root_str):
        # Prune excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]

        for fname in filenames:
            if _should_exclude(dirpath, fname):
                continue

            abs_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(abs_path, root_str)
            parts = rel_path.replace("\\", "/").split("/")
            _, ext = os.path.splitext(fname)

            try:
                size = os.path.getsize(abs_path)
            except OSError:
                size = 0

            records.append({
                "filename": fname,
                "extension": ext.lower().lstrip("."),
                "size_bytes": size,
                "size_display": _format_size(size),
                "relative_path": rel_path.replace("\\", "/"),
                "absolute_path": abs_path,
                "parent_folder": parts[-2] if len(parts) > 1 else "",
                "top_folder": parts[0] if parts else "",
                "capacity": _parse_capacity(rel_path),
                "section": _parse_section(parts),
                "submission_category": _parse_submission_category(rel_path),
                "state": _parse_state(rel_path),
            })

    return pd.DataFrame(records)


def _format_size(size_bytes):
    """Format file size for display."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def search_index(df, query="", filters=None):
    """Filter the document index by keyword and filters."""
    result = df.copy()

    if query:
        query_lower = query.lower()
        result = result[result["filename"].str.lower().str.contains(query_lower, na=False)]

    if filters:
        if filters.get("extensions"):
            result = result[result["extension"].isin(filters["extensions"])]
        if filters.get("capacities"):
            result = result[result["capacity"].isin(filters["capacities"])]
        if filters.get("sections"):
            result = result[result["section"].isin(filters["sections"])]
        if filters.get("submission_categories"):
            result = result[result["submission_category"].isin(filters["submission_categories"])]
        if filters.get("states"):
            result = result[result["state"].isin(filters["states"])]
        if filters.get("top_folders"):
            result = result[result["top_folder"].isin(filters["top_folders"])]

    return result
