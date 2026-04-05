"""Shared export helpers for calculator pages — Excel, Print."""
import io
import streamlit as st


def add_excel_export(dataframe, filename, sheet_name="Data"):
    """Add Excel download button for any DataFrame."""
    try:
        buffer = io.BytesIO()
        dataframe.to_excel(buffer, index=False, sheet_name=sheet_name)
        buffer.seek(0)
        st.download_button(
            "Download Excel", buffer.getvalue(), filename,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    except Exception as e:
        st.error(f"Excel export failed: {e}")


def add_csv_export(dataframe, filename):
    """Add CSV download button for any DataFrame."""
    csv = dataframe.to_csv(index=False)
    st.download_button("Download CSV", csv, filename, "text/csv")


def add_print_button(key="print_calc"):
    """Add browser print button."""
    if st.button("Print", key=key):
        import streamlit.components.v1 as stc
        stc.html("<script>window.print();</script>", height=0)
