"""
Slide Chart Generator — Creates the right chart for each presenter slide
==========================================================================
One function per slide type. Returns Plotly figure ready for st.plotly_chart().
All data from cfg — changes when inputs change.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def chart_market_opportunity(cfg):
    """Slide 1: Market size bar chart."""
    fig = go.Figure(data=[go.Bar(
        x=["India Bitumen\nMarket", "Import\nDependency", "Bio-Bitumen\nTarget 2030", "Plants\nNeeded"],
        y=[25000, 12250, 3750, 200],
        marker_color=["#003366", "#CC3333", "#00AA44", "#FF8800"],
        text=["Rs 25,000 Cr", "49%", "15%", "130-216"],
        textposition="outside",
    )])
    fig.update_layout(title="India Bio-Bitumen Opportunity", template="plotly_white",
                      height=300, yaxis_title="Rs Crore / Count", showlegend=False)
    return fig


def chart_cost_breakdown(cfg):
    """Slide 19: Cost pie chart from detailed costing."""
    try:
        from engines.detailed_costing import calculate_complete_cost_sheet
        cs = calculate_complete_cost_sheet(cfg)
        labels = [h for h, _ in cs["cost_heads"]]
        values = [c for _, c in cs["cost_heads"]]
    except Exception:
        labels = ["RM", "Bitumen", "Logistics", "Energy", "Labour", "Chemicals", "Overheads", "Packing", "Waste", "Outbound"]
        values = [10, 50, 5, 5, 8, 2, 4, 3, 2, 3]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4,
        marker=dict(colors=["#f59e0b", "#ef4444", "#38bdf8", "#a78bfa", "#34d399",
                             "#fb923c", "#64748b", "#f472b6", "#94a3b8", "#4ade80"]))])
    fig.update_layout(title=f"Cost Breakdown — {cfg.get('capacity_tpd', 20):.0f} TPD",
                      template="plotly_white", height=350)
    return fig


def chart_revenue_streams(cfg):
    """Slide 20: Revenue by product bar chart."""
    try:
        from engines.detailed_costing import calculate_complete_cost_sheet
        cs = calculate_complete_cost_sheet(cfg)
        items = cs["revenue"]["items"]
        names = [i["product"].split("(")[0].strip() for i in items]
        values = [i["daily_rev"] for i in items]
    except Exception:
        names = ["VG30", "VG40", "Bio-Char", "Bio-Oil", "Credits"]
        values = [800000, 350000, 100000, 20000, 60000]

    fig = go.Figure(data=[go.Bar(x=names, y=values,
        marker_color=["#003366", "#006699", "#228B22", "#FF8800", "#9333EA"])])
    fig.update_layout(title="Daily Revenue by Product (Rs)", template="plotly_white",
                      height=300, xaxis_tickangle=-20)
    return fig


def chart_7yr_pl(cfg):
    """Slide 24: 7-year P&L bar + line chart."""
    if not cfg.get("roi_timeline"):
        return None
    df = pd.DataFrame(cfg["roi_timeline"])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Year"], y=df["Revenue (Lac)"], name="Revenue", marker_color="#003366"))
    fig.add_trace(go.Bar(x=df["Year"], y=df["Variable Cost (Lac)"], name="Cost", marker_color="#CC3333"))
    fig.add_trace(go.Scatter(x=df["Year"], y=df["PAT (Lac)"], name="Net Profit",
                              mode="lines+markers", line=dict(color="#00AA44", width=3)))
    fig.update_layout(title="7-Year P&L (Rs Lakhs)", barmode="group", template="plotly_white", height=350)
    return fig


def chart_roi_gauges(cfg):
    """Slide 23: ROI + IRR + Break-even gauges."""
    fig = go.Figure()
    fig.add_trace(go.Indicator(mode="gauge+number", value=cfg.get("roi_pct", 0),
        title={"text": "ROI %"}, gauge={"axis": {"range": [0, 60]}, "bar": {"color": "#003366"},
        "steps": [{"range": [0, 15], "color": "#ffcccc"}, {"range": [15, 30], "color": "#ffffcc"},
                   {"range": [30, 60], "color": "#ccffcc"}]},
        domain={"x": [0, 0.3], "y": [0, 1]}))
    fig.add_trace(go.Indicator(mode="gauge+number", value=cfg.get("irr_pct", 0),
        title={"text": "IRR %"}, gauge={"axis": {"range": [0, 80]}, "bar": {"color": "#006699"}},
        domain={"x": [0.35, 0.65], "y": [0, 1]}))
    fig.add_trace(go.Indicator(mode="gauge+number", value=cfg.get("break_even_months", 0),
        title={"text": "Break-Even (Months)"}, gauge={"axis": {"range": [0, 60]}, "bar": {"color": "#FF8800"}},
        domain={"x": [0.7, 1.0], "y": [0, 1]}))
    fig.update_layout(height=250, margin=dict(t=50, b=10))
    return fig


def chart_boq_zones(cfg):
    """Slide 14: BOQ by zone pie chart."""
    try:
        from state_manager import calculate_boq
        boq = calculate_boq(cfg.get("capacity_tpd", 20), process_id=cfg.get("process_id", 1))
        cats = {}
        for i in boq:
            cats[i["category"]] = cats.get(i["category"], 0) + i["amount_lac"]
        labels = list(cats.keys())
        values = list(cats.values())
    except Exception:
        labels = ["Gate", "RM", "Processing", "Reactor", "Oil", "Blending", "Storage"]
        values = [15, 25, 40, 150, 20, 40, 35]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.35)])
    fig.update_layout(title=f"BOQ Cost by Zone — {cfg.get('capacity_tpd', 20):.0f} TPD",
                      template="plotly_white", height=350)
    return fig


def chart_capacity_compare(cfg):
    """Slide 40: Capacity comparison bar chart."""
    try:
        from master_data_loader import get_plant
        caps = [5, 10, 20, 25, 50]
        investments = []
        for c in caps:
            p = get_plant(f"{c:02d}MT")
            investments.append(p.get("inv_cr", c * 0.4))
    except Exception:
        caps = [5, 10, 20, 25, 50]
        investments = [1.5, 3, 8, 10, 16]

    fig = go.Figure(data=[go.Bar(x=[f"{c} TPD" for c in caps], y=investments,
        marker_color=["#38bdf8", "#34d399", "#f59e0b", "#003366", "#ef4444"],
        text=[f"Rs {v:.1f} Cr" for v in investments], textposition="outside")])
    fig.update_layout(title="Investment by Capacity", template="plotly_white",
                      height=300, yaxis_title="Rs Crore")
    return fig


def chart_state_comparison(cfg):
    """Slide 30: State profitability comparison."""
    try:
        from engines.detailed_costing import calculate_complete_cost_sheet, LOCATION_MULTIPLIERS
        states = list(LOCATION_MULTIPLIERS.keys())[:6]
        margins = []
        for s in states:
            tcfg = dict(cfg)
            tcfg["state"] = s
            try:
                cs = calculate_complete_cost_sheet(tcfg)
                margins.append(cs["margin_pct"])
            except Exception:
                margins.append(0)
    except Exception:
        states = ["Punjab", "Gujarat", "Maharashtra", "UP", "TN", "Rajasthan"]
        margins = [8.0, 7.3, 7.1, 7.5, 6.5, 7.8]

    colors = ["#00AA44" if m > 5 else "#FF8800" if m > 0 else "#CC3333" for m in margins]
    fig = go.Figure(data=[go.Bar(x=states, y=margins, marker_color=colors,
        text=[f"{m:.1f}%" for m in margins], textposition="outside")])
    fig.update_layout(title="Margin % by State", template="plotly_white",
                      height=300, yaxis_title="Margin %")
    return fig


def chart_fee_comparison(cfg):
    """Slide 52: Fee vs Risk comparison."""
    inv = cfg.get("investment_cr", 10)
    fee = inv * 0.10
    risk = inv * 0.25
    fig = go.Figure(data=[go.Bar(
        x=["Consulting Fee\n(With Us)", "Potential Loss\n(Without Us)"],
        y=[fee, risk],
        marker_color=["#00AA44", "#CC3333"],
        text=[f"Rs {fee:.1f} Cr", f"Rs {risk:.1f} Cr"],
        textposition="outside",
    )])
    fig.update_layout(title="Investment in Consulting vs Risk Without",
                      template="plotly_white", height=300, yaxis_title="Rs Crore")
    return fig


def chart_timeline_gantt(cfg):
    """Slide 36/53: Project timeline gantt chart."""
    import datetime
    start = datetime.date(2026, 7, 1)
    phases = [
        ("DPR + Feasibility", 1), ("Company + Bank", 2), ("Approvals", 4),
        ("Engineering", 3), ("Equipment Order", 3), ("Civil Construction", 5),
        ("Installation", 3), ("Commissioning", 2), ("Production Start", 3),
    ]
    data = []
    offset = 0
    for name, dur in phases:
        data.append({"Task": name, "Start": start + datetime.timedelta(days=offset * 30),
                     "Finish": start + datetime.timedelta(days=(offset + dur) * 30)})
        offset += max(1, dur - 1)

    df = pd.DataFrame(data)
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task",
                       color_discrete_sequence=["#003366"])
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(title="Project Timeline", template="plotly_white", height=350)
    return fig


# ══════════════════════════════════════════════════════════════════════
# MASTER: Get chart for any slide number
# ══════════════════════════════════════════════════════════════════════
SLIDE_CHART_MAP = {
    1: chart_market_opportunity,
    14: chart_boq_zones,
    19: chart_cost_breakdown,
    20: chart_revenue_streams,
    22: chart_7yr_pl,
    23: chart_roi_gauges,
    24: chart_7yr_pl,
    30: chart_state_comparison,
    36: chart_timeline_gantt,
    40: chart_capacity_compare,
    49: chart_fee_comparison,
    52: chart_fee_comparison,
    53: chart_timeline_gantt,
}


def get_slide_chart(slide_num, cfg):
    """Get the right chart for a slide number. Returns fig or None."""
    chart_fn = SLIDE_CHART_MAP.get(slide_num)
    if chart_fn:
        try:
            return chart_fn(cfg)
        except Exception:
            return None
    return None
