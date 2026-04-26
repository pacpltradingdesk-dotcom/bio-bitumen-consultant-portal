"""
Master Context Engine — Anti-Hallucination Data Layer
======================================================
Collects ALL project parameters BEFORE any AI generation.
If ANY required field is missing, blocks generation and asks user to fill it.
Every AI prompt gets this context prepended — no guessing allowed.
"""


def build_master_context(cfg):
    """
    Build the Master Context Document from current config.
    Returns: (context_text, missing_fields_list)

    If missing_fields is not empty, AI generation MUST be blocked
    until user fills all required fields.
    """
    missing = []

    # ── 1. SITE & LOCATION ───────────────────────────────────────
    client_name = cfg.get("client_name", "")
    if not client_name: missing.append("Client Name (Project Setup → Client Name)")

    client_company = cfg.get("client_company", "")
    state = cfg.get("state", "")
    if not state: missing.append("State (Project Setup → State)")

    city = cfg.get("location", "")
    if not city: missing.append("City (Project Setup → City)")

    site_address = cfg.get("site_address", "")
    site_area = cfg.get("site_area_acres", 0)
    site_pincode = cfg.get("site_pincode", "")

    # ── 2. PROCESS & CAPACITY ────────────────────────────────────
    capacity = cfg.get("capacity_tpd", 0)
    if capacity <= 0: missing.append("Plant Capacity TPD (Project Setup → Capacity)")

    working_days = cfg.get("working_days", 300)
    biomass_source = cfg.get("biomass_source", "")
    if not biomass_source: missing.append("Primary Biomass Source (Project Setup → Biomass)")

    # ── 3. FINANCIAL ─────────────────────────────────────────────
    investment_cr = cfg.get("investment_cr", 0)
    if investment_cr <= 0: missing.append("Investment Amount (Financial Model → auto-calculated)")

    selling_price = cfg.get("selling_price_per_mt", 0)
    if selling_price <= 0: missing.append("Selling Price per MT (Financial Model)")

    roi = cfg.get("roi_pct", 0)
    irr = cfg.get("irr_pct", 0)
    dscr = cfg.get("dscr_yr3", 0)
    break_even = cfg.get("break_even_months", 0)
    emi = cfg.get("emi_lac_mth", 0)
    loan_cr = cfg.get("loan_cr", 0)
    equity_cr = cfg.get("equity_cr", 0)
    monthly_profit = cfg.get("monthly_profit_lac", 0)
    profit_per_mt = cfg.get("profit_per_mt", 0)

    # ── 4. OPERATIONS ────────────────────────────────────────────
    staff = cfg.get("staff", 0)
    power_kw = cfg.get("power_kw", 0)
    interest_rate = cfg.get("interest_rate", 0.115)
    equity_ratio = cfg.get("equity_ratio", 0.4)

    # ── 5. DERIVED ───────────────────────────────────────────────
    oil_yield_pct = cfg.get("bio_oil_yield_pct", 32)
    annual_output = capacity * (oil_yield_pct / 100) * working_days
    daily_biomass = capacity * 2.5  # Input ratio
    water_kld = max(5, int(capacity * 1.5))

    # ── 6. PLANT ENGINEERING DATA ────────────────────────────────
    try:
        from engines.plant_engineering import get_plant_engineering
        eng_data = get_plant_engineering(cfg)
        eng_comp = eng_data.get("computed", {})
    except Exception:
        eng_data = {"safety_clearances": {}, "total_motor_kw": 0, "machinery_count": 15}
        eng_comp = {}

    # ── 7. BOQ DATA (82 items, 15 zones) ─────────────────────────
    try:
        from state_manager import calculate_boq
        boq_items = calculate_boq(capacity)
        boq_total_lac = sum(i["amount_lac"] for i in boq_items)
        # Zone summary
        zone_cats = {}
        for item in boq_items:
            cat = item["category"]
            zone_cats[cat] = zone_cats.get(cat, 0) + item["amount_lac"]
        zone_summary = "\n".join(f"  {cat}: Rs {cost:.1f} Lac ({len([i for i in boq_items if i['category']==cat])} items)"
                                  for cat, cost in sorted(zone_cats.items()))
    except Exception:
        boq_items = []
        boq_total_lac = 0
        zone_summary = "BOQ not available"

    # ── BUILD CONTEXT TEXT ───────────────────────────────────────
    context = f"""
═══════════════════════════════════════════════════════════════
MASTER PROJECT CONTEXT — ABSOLUTE FACTS (DO NOT GUESS)
═══════════════════════════════════════════════════════════════

ANTI-HALLUCINATION RULE:
You are acting as a Senior Lead Engineer for PPS Anantams Corporation.
Use the parameters below as ABSOLUTE FACTS. If any required value is
marked as "NOT SET" or is missing, output "MISSING DATA:" followed by
exactly what information is needed. NEVER invent, guess, or use
generic web data for any specific number.

═══ 1. CLIENT & SITE ═══
Client Name:        {client_name or 'NOT SET'}
Company:            {client_company or 'NOT SET'}
State:              {state or 'NOT SET'}
City:               {city or 'NOT SET'}
Site Address:       {site_address or 'NOT SET'}
Site Area:          {site_area} acres
Pincode:            {site_pincode or 'NOT SET'}

Regulatory Bodies:  {'GPCB' if state == 'Gujarat' else 'MPCB' if state == 'Maharashtra' else 'State PCB'} (Pollution Control)
                    {'GUVNL' if state == 'Gujarat' else 'State DISCOM'} (Electricity)

═══ 2. PROCESS & CAPACITY ═══
Plant Type:         Bio-Modified Bitumen (Pyrolysis + VG-30 Blending)
Capacity:           {capacity:.0f} MT/Day (biomass input)
Bio-Oil Yield:      {cfg.get('bio_oil_yield_pct', 32)}% = {capacity * cfg.get('bio_oil_yield_pct', 32)/100:.1f} MT/Day
Bio-Char Yield:     {cfg.get('bio_char_yield_pct', 28)}% = {capacity * cfg.get('bio_char_yield_pct', 28)/100:.1f} MT/Day
Syngas Yield:       {cfg.get('syngas_yield_pct', 22)}% = {capacity * cfg.get('syngas_yield_pct', 22)/100:.1f} MT/Day (captive fuel)
Process Loss:       {cfg.get('process_loss_pct', 18)}%
Working Days:       {working_days}/year
Operating Hours:    16 hrs/day (2 shifts)
Biomass Source:     {biomass_source or 'NOT SET'}
Daily Biomass Need: {daily_biomass:.0f} MT/day (at 2.5x input ratio)
Annual Production:  {annual_output:.0f} MT of bio-bitumen output
BOQ:                {len(boq_items)} items across 15 zones (gate to gate)
BOQ Total Cost:     Rs {boq_total_lac:.1f} Lac ({boq_total_lac/100:.2f} Cr)

═══ 3. PLANT ZONES (15 areas) ═══
{zone_summary}

═══ 4. UTILITIES ═══
Connected Load:     {power_kw} kW
Water Requirement:  {water_kld} KLD (cooling + process + domestic)
Fuel Source:        Syngas (captive) + DG backup
Power Source:       {'GUVNL' if state == 'Gujarat' else 'State DISCOM'} HT Connection + {max(50, power_kw)} kVA DG
Compressed Air:     {max(50, int(capacity * 5))} CFM

═══ 4. PLOT DIMENSIONS ═══
Plot Area:          {int(site_area * 43560)} sq ft ({site_area} acres)
Estimated Layout:   {int((site_area * 43560) ** 0.5 * 1.2):.0f}m x {int((site_area * 43560) ** 0.5 / 1.2):.0f}m (approx)
Internal Road:      6m wide
Equipment Clearance: 2m all sides
Pipe Rack Height:   4.5m
Reactor Safety Zone: {eng_data.get('safety_clearances',{}).get('reactor_to_boundary_m',15)}m to boundary
Fire Spacing:       {eng_data.get('safety_clearances',{}).get('bio_oil_tank_to_building_m',7.5)}m tanks-to-building (OISD-118)
Green Belt:         {eng_data.get('safety_clearances',{}).get('green_belt_min_m',5)}m boundary
Total Motor Load:   {eng_data.get('total_motor_kw',0)} kW ({eng_data.get('machinery_count',15)} major equipment)
Key Equipment:      Reactor {eng_comp.get('reactor_dia_m',1.5)}m dia × {eng_comp.get('reactor_ht_m',4.5)}m | Dryer {eng_comp.get('dryer_dia_m',1.2)}m × {eng_comp.get('dryer_len_m',6)}m
Standards:          IS 2825 (vessels), IS 732 (electrical), NBC 2016 (fire), IS 14489 (safety)

═══ 5. FINANCIAL (VERIFIED CALCULATIONS) ═══
Total Investment:   Rs {investment_cr:.2f} Crore (Rs {investment_cr*100:.0f} Lac)
Bank Loan:          Rs {loan_cr:.2f} Crore ({(1-equity_ratio)*100:.0f}%)
Promoter Equity:    Rs {equity_cr:.2f} Crore ({equity_ratio*100:.0f}%)
Interest Rate:      {interest_rate*100:.1f}% p.a.
EMI:                Rs {emi:.2f} Lac/month
Selling Price:      Rs {selling_price:,}/MT
Variable Cost:      Rs {cfg.get('total_variable_cost_per_mt', 0):,}/MT
Profit per MT:      Rs {profit_per_mt:,}/MT
ROI:                {roi:.1f}%
IRR:                {irr:.1f}%
DSCR Year 3:        {dscr:.2f}x
Break-Even:         {break_even} months
Monthly Profit:     Rs {monthly_profit:.1f} Lac (Year 5 at 85% util)
Revenue Year 5:     Rs {cfg.get('revenue_yr5_lac', 0):.0f} Lac

═══ 6. STAFFING ═══
Total Staff:        {staff} persons
Plant Manager:      1 (Rs 60-80K/month)
Shift Supervisors:  2 (Rs 30-40K/month)
Operators:          {max(4, int(capacity * 0.3))} (Rs 18-25K/month)
Lab Technician:     1-2 (Rs 20-30K/month)
Helpers:            {max(6, int(capacity * 0.5))} (Rs 12-15K/month)

═══ 7. CONSULTANT ═══
Consultant:         PPS Anantams Corporation Pvt Ltd (CIN U46632GJ2019PTC110676)
Owner:              Prince Pratap Shah — DIN 06680837 (MCA-registered director since 2009)
Experience:         25 years hands-on bitumen industry (since 2001) | 17+ years as Director | 9 plants commissioned
Group Companies:    Omnipotent Industries Limited (CIN L74999MH2016PLC285902) — incorporated 2016, IPO 2020, BSE-LISTED
                    Global Enterprises (prop., since 2004) — AMT Techno Worldwide Marketing Rep (Ref L-012/2015-16)
                    PS Enterprises (prop., since 2023) — 1.2 Lakh MT UK bitumen contract
Business scale:     3 Omnipotent plants (Panvel/Kandala/Karjan) | 11 JVs | 2.4 Lakh MT/yr VG-30 import capacity (Getka USA)
Signature firsts:   1st automatic emulsion plant in Karnataka (2013) | 1st decanter plant Panvel (2016) | 1st drum-bitumen supplier West+South India (2019)
Innovations:        9 documented on-plant engineering improvements 2001-2010
Network:            150,000-contact pan-India database (125K petroleum verified + 25K bitumen-specific)
Awards:             Pride of India Icon 2021 — Best Fast-Growing Business
Phone:              +91 7795242424  (Secondary: +91 7506941655)
Email:              princepshah@gmail.com  (Business: sales@princeshah.com)
Website:            www.princeshah.com
GST:                24AAHCV1611L2ZD
PAN:                AAHCV1611L
HQ:                 Vadodara, Gujarat (Operations) | Bhandup West, Mumbai (Registered)

═══════════════════════════════════════════════════════════════
END OF MASTER CONTEXT — ALL AI OUTPUTS MUST USE THESE VALUES
═══════════════════════════════════════════════════════════════
"""
    return context.strip(), missing


def get_missing_fields_popup(missing):
    """Generate Streamlit popup content for missing fields."""
    if not missing:
        return None

    lines = ["**The following information is required before generating professional output:**\n"]
    for i, field in enumerate(missing, 1):
        lines.append(f"{i}. {field}")
    lines.append("\n**Go to Project Setup page to fill these fields.**")
    return "\n".join(lines)


def validate_before_generation(cfg):
    """
    Call this BEFORE any AI generation or document export.
    Returns (is_valid, context_text, missing_popup_text)
    """
    context, missing = build_master_context(cfg)

    if missing:
        popup = get_missing_fields_popup(missing)
        return False, context, popup

    return True, context, None


# ═══════════════════════════════════════════════════════════════
# PARAMETER EXPLANATION POPUPS — Show what each input means
# ═══════════════════════════════════════════════════════════════
PARAMETER_EXPLANATIONS = {
    "capacity_tpd": {
        "label": "Plant Capacity (TPD)",
        "explanation": "Tonnes Per Day of biomass INPUT to the pyrolysis reactor. "
                       "At 40% oil yield, a 20 TPD plant produces 8 MT/day of bio-oil.",
        "affects": ["Investment amount", "Equipment sizing", "Staff count", "Power load",
                     "Revenue", "ROI", "All drawings and layouts"],
        "typical_range": "5-50 TPD for bio-bitumen",
    },
    "selling_price_per_mt": {
        "label": "Selling Price (Rs/MT)",
        "explanation": "Price at which bio-modified bitumen is sold to NHAI/PWD contractors. "
                       "Includes bio-oil value + biochar revenue + syngas savings.",
        "affects": ["Revenue", "Profit per MT", "ROI", "Break-Even", "All financial documents"],
        "typical_range": "Rs 30,000-55,000/MT depending on VG30 market price",
    },
    "raw_material_cost_per_mt": {
        "label": "Raw Material Cost (Rs/MT output)",
        "explanation": "Cost per MT of BITUMEN OUTPUT (not raw biomass). "
                       "Includes 2.5x input ratio: actual biomass cost × 2.5 = this value. "
                       "Example: Rs 3,000/MT biomass × 2.5 = Rs 7,500/MT output.",
        "affects": ["Variable cost", "Profit margin", "Break-Even", "Sensitivity analysis"],
        "typical_range": "Rs 5,000-12,000/MT output (Rs 2,000-5,000/MT raw biomass)",
    },
    "interest_rate": {
        "label": "Interest Rate (%)",
        "explanation": "Annual interest rate on term loan from bank. "
                       "SBI MCLR (2026): 9.5% + 200 bps spread = 11.5% typical for MSME.",
        "affects": ["EMI amount", "Total interest paid", "DSCR", "Cash flow"],
        "typical_range": "9.5-13% for MSME term loans in India",
    },
    "equity_ratio": {
        "label": "Equity Percentage (%)",
        "explanation": "Promoter's own contribution as percentage of total investment. "
                       "Bank typically requires 25-40% equity. Higher equity = lower EMI but more upfront cash.",
        "affects": ["Loan amount", "EMI", "DSCR", "Debt-Equity ratio"],
        "typical_range": "25-40% (banks prefer 30%+ for new promoters)",
    },
    "working_days": {
        "label": "Working Days per Year",
        "explanation": "Actual production days after deducting Sundays, holidays, monsoon, maintenance. "
                       "Weather page can calculate this automatically for your location.",
        "affects": ["Annual production", "Revenue", "All financial projections"],
        "typical_range": "270-300 days (varies by state — monsoon impact)",
    },
}


def get_parameter_popup(param_key):
    """Get explanation popup for a parameter."""
    info = PARAMETER_EXPLANATIONS.get(param_key)
    if not info:
        return None

    text = f"**{info['label']}**\n\n"
    text += f"{info['explanation']}\n\n"
    text += f"**Typical Range:** {info['typical_range']}\n\n"
    text += "**This value affects:**\n"
    for item in info['affects']:
        text += f"- {item}\n"

    return text
