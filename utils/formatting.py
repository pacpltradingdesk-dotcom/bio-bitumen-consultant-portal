"""
Shared Formatting — EVERY page must use these for consistent, non-truncated display.
"""


def fmt_lac(v):
    """Format Lac amount compactly — NEVER truncates in st.metric().
    Input: value in Lakhs. Output: ₹6.4Cr or ₹23.7L or ₹0
    """
    if v is None or v == 0:
        return "₹0"
    neg = "-" if v < 0 else ""
    a = abs(v)
    if a >= 100:
        return f"{neg}₹{a/100:.1f}Cr"
    if a >= 10:
        return f"{neg}₹{a:.0f}L"
    return f"{neg}₹{a:.1f}L"


def fmt_rs(v):
    """Format raw rupees compactly. Input: raw Rs. Output: ₹1.5Cr or ₹85K or ₹500"""
    if v is None or v == 0:
        return "₹0"
    neg = "-" if v < 0 else ""
    a = abs(v)
    if a >= 10000000:
        return f"{neg}₹{a/10000000:.1f}Cr"
    if a >= 100000:
        return f"{neg}₹{a/100000:.1f}L"
    if a >= 1000:
        return f"{neg}₹{a/1000:.0f}K"
    return f"{neg}₹{a:.0f}"


def fmt_pct(v):
    """Format percentage — never truncated."""
    if v is None:
        return "0%"
    return f"{v:.1f}%"


def fmt_mo(v):
    """Format months."""
    if v is None or v == 0:
        return "0 mo"
    return f"{int(v)} mo"


def fmt_x(v):
    """Format ratio (DSCR etc.)."""
    if v is None:
        return "0x"
    return f"{v:.2f}x"


def fmt_num(v):
    """Format number with commas."""
    if v is None or v == 0:
        return "0"
    return f"{v:,.0f}"


def fmt_full_lac(v):
    """Full format: ₹ 23.7 Lac or ₹ 6.40 Cr (with spaces, for documents)."""
    if v is None or v == 0:
        return "₹ 0"
    if abs(v) >= 100:
        return f"₹ {v/100:.2f} Cr"
    return f"₹ {v:.1f} Lac"


def color_val(v, threshold=0):
    """CSS color: green if >= threshold, red if below."""
    if v is None:
        return "#666"
    return "#00AA44" if v >= threshold else "#CC3333"


def dscr_color(v):
    """DSCR-specific color: green >= 1.5, orange 1.0-1.5, red < 1.0"""
    if v is None or v == 0:
        return "#CC3333"
    if v >= 1.5:
        return "#00AA44"
    if v >= 1.0:
        return "#FF8800"
    return "#CC3333"


def dscr_html(year, value):
    """Single DSCR year as colored HTML span."""
    color = dscr_color(value)
    return f'<span style="color:{color};font-weight:bold;">Yr{year}: {value:.2f}x</span>'


def print_js():
    """JavaScript for browser print — use with st.components.v1.html()"""
    return "<script>window.print();</script>"


TOOLTIPS = {
    "ROI": "Return on Investment — Annual Profit ÷ Total Investment × 100",
    "IRR": "Internal Rate of Return — Discount rate where NPV equals zero. Higher = better",
    "DSCR": "Debt Service Coverage Ratio — Cash available ÷ Annual EMI. Bank minimum: 1.5x",
    "NPV": "Net Present Value — Today's worth of all future profits. Positive = good investment",
    "EBITDA": "Earnings Before Interest, Tax, Depreciation — Operating profit measure",
    "PAT": "Profit After Tax — Final net profit after all deductions",
    "CAPEX": "Capital Expenditure — Total one-time investment (Plant + WC + Pre-operative)",
    "EMI": "Equated Monthly Installment — Fixed monthly loan repayment to bank",
    "Break-Even": "Months needed to recover total investment from net profits",
    "Margin": "Profit as % of selling price — higher margin = more room for price drops",
    "D/E": "Debt-Equity Ratio — Loan ÷ Equity. Lower = safer for lender",
    "Current Ratio": "Current Assets ÷ Current Liabilities — measures short-term liquidity",
    "Net Worth": "Total equity + retained profits built up over time",
    "Carbon Credits": "Annual revenue from selling CO2 offset certificates on carbon market",
    "Working Capital": "Cash needed for daily operations — typically 2-3 months of costs",
}
