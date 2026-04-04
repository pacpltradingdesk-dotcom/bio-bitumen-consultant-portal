"""
Shared Formatting Utilities — Used by ALL pages for consistent display.
Indian number format, compact metrics, color coding.
"""


def fmt_inr(amount, unit="rs"):
    """Format in Indian Rupee system. Never truncated.
    unit='rs': raw rupees → auto Cr/Lac/Rs
    unit='lac': amount already in Lakhs
    unit='cr': amount already in Crores
    """
    if amount is None or amount == 0:
        return "₹ 0"
    neg = "-" if amount < 0 else ""
    a = abs(amount)

    if unit == "cr":
        return f"{neg}₹ {a:.2f} Cr"
    if unit == "lac":
        if a >= 100:
            return f"{neg}₹ {a/100:.2f} Cr"
        return f"{neg}₹ {a:.1f} Lac"

    # unit == "rs" — raw rupees
    if a >= 10000000:
        return f"{neg}₹ {a/10000000:.2f} Cr"
    if a >= 100000:
        return f"{neg}₹ {a/100000:.1f} Lac"
    if a >= 1000:
        return f"{neg}₹ {a:,.0f}"
    return f"{neg}₹ {a:.0f}"


def fmt_inr_compact(amount, unit="rs"):
    """Compact format for st.metric() cards — never truncated.
    Returns short string like ₹6.4Cr, ₹23.7L, ₹35,000
    """
    if amount is None or amount == 0:
        return "₹0"
    neg = "-" if amount < 0 else ""
    a = abs(amount)

    if unit == "cr":
        return f"{neg}₹{a:.1f}Cr"
    if unit == "lac":
        if a >= 100:
            return f"{neg}₹{a/100:.1f}Cr"
        return f"{neg}₹{a:.1f}L"

    if a >= 10000000:
        return f"{neg}₹{a/10000000:.1f}Cr"
    if a >= 100000:
        return f"{neg}₹{a/100000:.1f}L"
    if a >= 1000:
        return f"{neg}₹{a:,.0f}"
    return f"{neg}₹{a:.0f}"


def fmt_lac(lac_amount):
    """Format Lac amount: ₹23.7 Lac or ₹6.40 Cr"""
    if lac_amount is None or lac_amount == 0:
        return "₹ 0"
    if abs(lac_amount) >= 100:
        return f"₹ {lac_amount/100:.2f} Cr"
    return f"₹ {lac_amount:.1f} Lac"


def fmt_pct(value):
    """Format percentage — never truncated."""
    if value is None:
        return "0%"
    return f"{value:.1f}%"


def fmt_num(value):
    """Format number with Indian commas."""
    if value is None or value == 0:
        return "0"
    return f"{value:,.0f}"


def color_value(value, threshold=0):
    """Return CSS color based on positive/negative."""
    if value is None:
        return "#666"
    return "#00AA44" if value >= threshold else "#CC3333"


def print_button_js():
    """Return JavaScript to trigger browser print dialog."""
    return '<script>window.print();</script>'


HELP_TEXTS = {
    "ROI": "Return on Investment — Annual Profit divided by Total Investment, shown as percentage",
    "IRR": "Internal Rate of Return — The discount rate at which NPV of all cash flows equals zero",
    "DSCR": "Debt Service Coverage Ratio — Cash available to pay annual loan EMI. Bank minimum is 1.5x",
    "NPV": "Net Present Value — Total value of future cash flows discounted to today's value",
    "EBITDA": "Earnings Before Interest, Tax, Depreciation & Amortization — Operating profit",
    "PAT": "Profit After Tax — Net profit after all deductions",
    "CAPEX": "Capital Expenditure — Total one-time investment in plant, machinery, and setup",
    "EMI": "Equated Monthly Installment — Fixed monthly loan repayment amount",
    "Break-Even": "Number of months to recover total investment from net profits",
    "Margin": "Gross Profit as percentage of Selling Price",
    "D/E Ratio": "Debt-Equity Ratio — Total loan divided by promoter equity. Lower is safer",
    "Current Ratio": "Current Assets / Current Liabilities — Measures short-term liquidity",
    "Working Capital": "Funds needed to run daily operations — typically 2-3 months of costs",
}
