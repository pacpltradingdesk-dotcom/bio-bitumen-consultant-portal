"""
Page Helpers — Common functions used across ALL pages.
Import and call at top of every page that has metrics or paths.
"""
import streamlit as st
import os


def fix_metric_truncation():
    """Apply CSS to prevent st.metric() value truncation. Call once per page."""
    st.markdown("""<style>
    [data-testid="metric-container"] {
        width: 100% !important;
        overflow: visible !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }
    div[data-testid="column"] {
        overflow: visible !important;
    }
    </style>""", unsafe_allow_html=True)


def safe_path(full_path):
    """Convert Windows absolute path to safe display path. Never show C:\\Users\\..."""
    if not full_path:
        return ""
    # Get just the last 2-3 folder levels + filename
    parts = full_path.replace("\\", "/").split("/")
    if len(parts) > 3:
        return "/".join(parts[-3:])
    return "/".join(parts)


def show_missing_fields_warning(cfg):
    """Show warning if critical fields are empty — for document generation pages."""
    missing = []
    if not cfg.get("client_name"): missing.append("Client Name")
    if not cfg.get("client_phone"): missing.append("Phone")
    if not cfg.get("client_gst"): missing.append("GST Number")
    if not cfg.get("site_address"): missing.append("Site Address")
    if not cfg.get("site_pincode"): missing.append("Pincode")
    if cfg.get("site_area_acres", 0) == 0: missing.append("Site Area")

    if missing:
        st.warning(f"⚠️ Empty fields: **{', '.join(missing)}**. Documents will have blank fields. "
                    f"Fill these in Project Setup for bank-ready output.")
    return missing


def add_roi_disclaimer():
    """Add disclaimer about ROI calculation differences."""
    st.caption("📊 ROI shown here uses simplified operating-profit formula. "
               "For bank-standard ROI after full debt service, see Financial Model page.")
