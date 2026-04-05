"""
Contradiction Alert System — Shows warnings when data is inconsistent.
Call check_contradictions(cfg) on any page to get list of alerts.
Call show_alerts(cfg) to display them in Streamlit.
"""
import streamlit as st


def check_contradictions(cfg):
    """Check for data contradictions. Returns list of alert dicts."""
    alerts = []

    # Alert 1: DSCR Year 1 below 1.0
    dscr_sched = cfg.get("dscr_schedule", [])
    if dscr_sched and len(dscr_sched) > 0 and dscr_sched[0] < 1.0:
        alerts.append({
            "level": "error",
            "title": "DSCR Year 1 Below 1.0",
            "msg": f"DSCR Year 1 = {dscr_sched[0]:.2f}x. Banks require minimum 1.0x. "
                   f"Consider: increase moratorium, reduce loan, or increase revenue.",
        })

    # Alert 2: Break-Even > 60 months
    be = cfg.get("break_even_months", 0)
    if be > 60:
        alerts.append({
            "level": "warning",
            "title": "Break-Even Exceeds 5 Years",
            "msg": f"Break-Even is {be} months ({be/12:.1f} years). Most investors expect <48 months. "
                   f"Consider adjusting capacity, price, or equity ratio.",
        })

    # Alert 3: Loan + Equity ≠ Investment (within 5%)
    loan_cr = cfg.get("loan_cr", 0)
    equity_cr = cfg.get("equity_cr", 0)
    inv_cr = cfg.get("investment_cr", 0)
    if inv_cr > 0 and abs(loan_cr + equity_cr - inv_cr) > inv_cr * 0.05:
        alerts.append({
            "level": "error",
            "title": "Loan + Equity Mismatch",
            "msg": f"Loan (Rs {loan_cr:.2f} Cr) + Equity (Rs {equity_cr:.2f} Cr) = "
                   f"Rs {loan_cr+equity_cr:.2f} Cr but Investment is Rs {inv_cr:.2f} Cr. "
                   f"This will be rejected by banks.",
        })

    # Alert 4: CGTMSE limit
    loan_lac = cfg.get("loan_cr", 0) * 100
    if loan_lac > 500:
        remain = loan_lac - 500
        alerts.append({
            "level": "info",
            "title": "CGTMSE Limit Exceeded",
            "msg": f"Loan Rs {loan_lac/100:.2f} Cr exceeds Rs 5 Cr CGTMSE limit. "
                   f"Consider: Rs 5 Cr CGTMSE (collateral-free) + Rs {remain/100:.2f} Cr with collateral.",
        })

    # Alert 5: Negative profit
    profit = cfg.get("profit_per_mt", 0)
    if profit < 0:
        alerts.append({
            "level": "error",
            "title": "Project Making Loss",
            "msg": f"Profit per MT is Rs {profit:,.0f} (NEGATIVE). "
                   f"Selling price must be increased or costs must be reduced.",
        })

    # Alert 6: ROI below 10%
    roi = cfg.get("roi_pct", 0)
    if 0 < roi < 10:
        alerts.append({
            "level": "warning",
            "title": "Low ROI",
            "msg": f"ROI is only {roi:.1f}%. Most investors expect >15%. "
                   f"Consider increasing capacity or selling price.",
        })

    # Alert 7: Biomass cost explanation
    raw_mt = cfg.get("raw_material_cost_per_mt", 0)
    if raw_mt > 0:
        raw_biomass = raw_mt / 2.5  # Input ratio
        alerts.append({
            "level": "info",
            "title": "Biomass Cost Note",
            "msg": f"Raw Material Rs {raw_mt:,}/MT is per MT of BITUMEN OUTPUT "
                   f"(not raw biomass). Actual biomass cost = Rs {raw_biomass:,.0f}/MT × 2.5 input ratio.",
        })

    # Alert 8: Working days vs weather
    days = cfg.get("working_days", 300)
    if days > 290:
        alerts.append({
            "level": "info",
            "title": "Working Days May Be High",
            "msg": f"Using {days} working days. After monsoon, holidays, and maintenance, "
                   f"effective days may be 270-290. Check Weather page for your location.",
        })

    # Alert 9: Missing client info
    if not cfg.get("client_name"):
        alerts.append({
            "level": "warning",
            "title": "Client Name Missing",
            "msg": "No client name set. Documents will show generic text. "
                   "Go to Project Setup to enter client details.",
        })

    return alerts


def show_alerts(cfg, show_info=False):
    """Display contradiction alerts on any Streamlit page.
    show_info=False hides informational alerts (only shows errors/warnings).
    """
    alerts = check_contradictions(cfg)
    errors = [a for a in alerts if a["level"] == "error"]
    warnings = [a for a in alerts if a["level"] == "warning"]
    infos = [a for a in alerts if a["level"] == "info"]

    if errors:
        for a in errors:
            st.error(f"🚨 **{a['title']}:** {a['msg']}")

    if warnings:
        for a in warnings:
            st.warning(f"⚠️ **{a['title']}:** {a['msg']}")

    if show_info and infos:
        with st.expander(f"ℹ️ {len(infos)} notes (click to see)"):
            for a in infos:
                st.info(f"**{a['title']}:** {a['msg']}")

    return len(errors), len(warnings), len(infos)


def get_readiness_score(cfg):
    """Calculate submission readiness score (0-100)."""
    score = 0
    details = []

    # Client info (10 pts)
    if cfg.get("client_name"):
        score += 10; details.append(("Client info", 10, True))
    else:
        details.append(("Client info", 0, False))

    # Financial consistent (20 pts)
    if cfg.get("roi_pct", 0) > 0 and cfg.get("investment_cr", 0) > 0:
        score += 20; details.append(("Financial model", 20, True))
    else:
        details.append(("Financial model", 0, False))

    # No contradictions (20 pts)
    alerts = check_contradictions(cfg)
    errors = len([a for a in alerts if a["level"] == "error"])
    if errors == 0:
        score += 20; details.append(("No contradictions", 20, True))
    else:
        details.append(("No contradictions", 0, False))

    # DSCR > 1.25 all years (15 pts)
    dscr = cfg.get("dscr_schedule", [])
    if dscr and all(d >= 1.25 for d in dscr):
        score += 15; details.append(("DSCR healthy", 15, True))
    elif dscr and all(d >= 1.0 for d in dscr):
        score += 8; details.append(("DSCR adequate", 8, True))
    else:
        details.append(("DSCR healthy", 0, False))

    # Break-Even < 60 months (10 pts)
    be = cfg.get("break_even_months", 0)
    if 0 < be < 60:
        score += 10; details.append(("Break-Even OK", 10, True))
    else:
        details.append(("Break-Even OK", 0, False))

    # State selected (10 pts)
    if cfg.get("state"):
        score += 10; details.append(("Location set", 10, True))
    else:
        details.append(("Location set", 0, False))

    # Process model (5 pts)
    score += 5; details.append(("Process model", 5, True))

    # Risk assessment (5 pts)
    score += 5; details.append(("Risk data", 5, True))

    # Environmental (5 pts)
    score += 5; details.append(("Environmental", 5, True))

    return score, details
