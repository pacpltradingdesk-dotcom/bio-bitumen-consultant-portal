"""
AI Skills Engine — 5 Specialized AI Capabilities
==================================================
Each skill is a focused AI function that can be called from any page.
Skills use OpenAI + Claude APIs via ai_engine.py.

1. Document Reader (Vision) — upload image/PDF, extract data
2. Local Law Expert (RAG) — Gujarat/India specific compliance
3. Financial Excel Generator — structured JSON → Excel
4. Voice Report (Whisper) — speech to site progress report
5. Presentation Maker — Claude text + DALL-E images → deck
"""
from engines.ai_engine import ask_ai, is_ai_available, _call_openai, _call_claude
import json


# ══════════════════════════════════════════════════════════════════════
# SKILL 1: DOCUMENT READER — Extract data from vendor quotes, sketches
# ══════════════════════════════════════════════════════════════════════
def read_vendor_quotation(quote_text, cfg):
    """AI reads vendor quotation text and generates comparison table."""
    prompt = f"""You are a procurement specialist for a {cfg['capacity_tpd']:.0f} TPD bio-bitumen plant.

Analyze this vendor quotation and extract:
1. Vendor name and location
2. Equipment offered (name, model, capacity)
3. Price (Rs) — break down if multiple items
4. Delivery timeline
5. Warranty terms
6. Payment terms
7. Any hidden costs (GST, freight, installation)

Then rate this quotation: Good / Average / Expensive compared to market.
Market reference: Pyrolysis reactor Rs 35-75 Lac, Shredder Rs 8-12 Lac, Dryer Rs 18-25 Lac.

QUOTATION TEXT:
{quote_text}

Output as a structured comparison table in markdown format."""

    result, provider = ask_ai(prompt, "You are an industrial procurement expert.", 1500)
    return result, provider


def generate_bom_from_description(description, cfg):
    """AI generates Bill of Materials from equipment description."""
    prompt = f"""Generate a Bill of Materials (BOM) for a {cfg['capacity_tpd']:.0f} TPD bio-bitumen plant
based on this description:

{description}

Output a table with columns:
| Sr | Item | Specification | Qty | Unit | Estimated Rate (Rs) | Amount (Rs) |

Include: piping, valves, fittings, supports, gaskets, bolts.
Use Indian standard sizes (DN/NB) and IS material grades.
Be specific — no generic entries."""

    result, provider = ask_ai(prompt, "You are a mechanical engineer creating a BOM.", 2000)
    return result, provider


# ══════════════════════════════════════════════════════════════════════
# SKILL 2: LOCAL LAW EXPERT — Gujarat/India specific compliance
# ══════════════════════════════════════════════════════════════════════
def draft_gpcb_application(cfg):
    """Draft GPCB Consent to Establish application."""
    prompt = f"""Draft a formal application letter to the Gujarat Pollution Control Board (GPCB)
for Consent to Establish (CTE) for the following project:

Applicant: {cfg.get('client_name', 'The Promoter')} / {cfg.get('client_company', '')}
Project: Bio-Modified Bitumen Plant using agricultural waste pyrolysis
Location: {cfg.get('site_address', cfg.get('location', ''))}, {cfg.get('state', 'Gujarat')}
Capacity: {cfg['capacity_tpd']:.0f} MT/Day
Investment: Rs {cfg['investment_cr']:.2f} Crore
Employment: {cfg.get('staff', 18)} persons

Pollution Control Measures:
- Bag filter + Gas scrubber for air emissions
- Chimney stack height: 20m (minimum as per GPCB norms)
- Zero liquid discharge — closed loop cooling
- Biochar stored in covered shed, not open dumping
- Green belt: 33% of total plot area with native species

Write in formal government application format with:
- To: Member Secretary, GPCB, Gandhinagar
- Subject line
- Reference to Environment Protection Act 1986
- Reference to Air (Prevention & Control) Act 1981
- List of enclosed documents
- Prayer clause requesting CTE

Use formal Indian government letter format."""

    result, provider = ask_ai(prompt, "You are an environmental compliance consultant in Gujarat, India.", 2000)
    return result, provider


def draft_factory_license(cfg):
    """Draft Factory License application."""
    prompt = f"""Draft a formal application for Factory License under the Factories Act 1948
for {cfg.get('state', 'Gujarat')} state.

Factory Details:
- Name: {cfg.get('client_company', cfg.get('client_name', 'Bio-Bitumen Plant'))}
- Location: {cfg.get('site_address', cfg.get('location', ''))}, {cfg.get('state', '')}
- Product: Bio-Modified Bitumen
- Capacity: {cfg['capacity_tpd']:.0f} MT/Day
- Workers: {cfg.get('staff', 18)} persons
- Power: {cfg.get('power_kw', 100)} kW
- Working Hours: 16 hrs/day (2 shifts)
- Hazardous Process: Pyrolysis (400-600°C)

Include: Form 2 details, safety measures, welfare facilities
(canteen, restrooms, first aid, drinking water).
Formal government application format."""

    result, provider = ask_ai(prompt, "You are a factory compliance consultant.", 1500)
    return result, provider


def get_compliance_checklist(cfg):
    """Generate state-specific compliance checklist."""
    state = cfg.get("state", "Gujarat")
    prompt = f"""Generate a complete compliance checklist for setting up a bio-bitumen plant
in {state}, India.

For EACH license/approval, provide:
| Sr | License/Approval | Authority | Timeline | Fee (approx) | Documents Required |

Include ALL of these:
1. GST Registration
2. Udyam (MSME) Registration
3. Factory License ({state} specific)
4. Consent to Establish (CTE) from {'GPCB' if state == 'Gujarat' else 'State PCB'}
5. Consent to Operate (CTO)
6. Fire NOC
7. PESO License (petroleum storage)
8. Building Plan Approval
9. HT Electricity Connection
10. Water Connection
11. EPF/ESI Registration
12. Professional Tax
13. Trade License
14. Labour License
15. Shops & Establishment

Add {state}-specific requirements if any.
Mark mandatory vs optional."""

    result, provider = ask_ai(prompt, f"You are a regulatory compliance expert for {state}, India.", 2000)
    return result, provider


# ══════════════════════════════════════════════════════════════════════
# SKILL 3: FINANCIAL GENERATOR — Structured output for Excel
# ══════════════════════════════════════════════════════════════════════
def generate_financial_projection_json(cfg):
    """Generate 5-year financial projection as structured JSON for Excel."""
    prompt = f"""Generate a 5-year financial projection for a bio-bitumen plant.

INPUT PARAMETERS (USE EXACTLY THESE — DO NOT GUESS):
- Capacity: {cfg['capacity_tpd']:.0f} TPD
- Investment: Rs {cfg['investment_cr']:.2f} Crore
- Selling Price: Rs {cfg['selling_price_per_mt']:,}/MT
- Variable Cost: Rs {cfg.get('total_variable_cost_per_mt', 14500):,}/MT
- Working Days: {cfg['working_days']}/year
- Interest Rate: {cfg['interest_rate']*100:.1f}%
- Equity: {cfg['equity_ratio']*100:.0f}%
- Oil Yield: 40% of biomass input

OUTPUT AS JSON (exactly this structure):
{{
  "summary": {{
    "investment_lac": number,
    "annual_revenue_yr5_lac": number,
    "roi_pct": number,
    "irr_pct": number,
    "payback_months": number
  }},
  "yearly": [
    {{"year": 1, "utilization_pct": 40, "production_mt": number, "revenue_lac": number,
      "variable_cost_lac": number, "fixed_cost_lac": number, "ebitda_lac": number,
      "depreciation_lac": number, "interest_lac": number, "pbt_lac": number,
      "tax_lac": number, "pat_lac": number, "dscr": number}}
  ]
}}

Return ONLY the JSON. No explanation text."""

    result, provider = ask_ai(prompt, "You are a CA generating financial projections. Output ONLY valid JSON.", 2000)

    # Try to parse JSON
    try:
        # Find JSON in response
        json_start = result.find('{')
        json_end = result.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            data = json.loads(result[json_start:json_end])
            return data, provider
    except Exception:
        pass

    return None, provider


# ══════════════════════════════════════════════════════════════════════
# SKILL 4: SITE REPORT GENERATOR — Text to formatted report
# ══════════════════════════════════════════════════════════════════════
def format_site_report(raw_notes, cfg):
    """Convert raw site notes/voice transcript into formal progress report."""
    prompt = f"""Convert these raw site notes into a professional Daily Site Progress Report.

PROJECT: {cfg.get('project_name', 'Bio-Bitumen Plant')}
CLIENT: {cfg.get('client_name', '')}
LOCATION: {cfg.get('location', '')}, {cfg.get('state', '')}

RAW NOTES:
{raw_notes}

Format as:
## Daily Site Progress Report
**Date:** [today]
**Project:** [name]
**Prepared by:** Site Engineer

### Work Completed Today
- [bullet points]

### Issues / Delays
- [if any mentioned]

### Tomorrow's Plan
- [if mentioned]

### Safety Observations
- [any safety items]

### Material Received
- [if mentioned]

### Manpower Present
- [if mentioned]

### Photos Required
- [list areas needing documentation]

Use professional construction report language."""

    result, provider = ask_ai(prompt, "You are a construction site manager writing a formal daily report.", 1500)
    return result, provider


# ══════════════════════════════════════════════════════════════════════
# SKILL 5: PRESENTATION MAKER — Generate slide content
# ══════════════════════════════════════════════════════════════════════
def generate_investor_deck_content(cfg, company):
    """Generate 10-slide investor presentation content."""
    prompt = f"""Create content for a 10-slide investor presentation for a bio-bitumen plant.

PROJECT DATA (use EXACTLY these numbers):
- Client: {cfg.get('client_name', 'Investor')}
- Capacity: {cfg['capacity_tpd']:.0f} TPD
- Investment: Rs {cfg['investment_cr']:.2f} Crore
- ROI: {cfg['roi_pct']:.1f}%
- IRR: {cfg['irr_pct']:.1f}%
- Break-Even: {cfg['break_even_months']} months
- Revenue Year 5: Rs {cfg.get('revenue_yr5_lac', 0):.0f} Lac
- Monthly Profit: Rs {cfg.get('monthly_profit_lac', 0):.1f} Lac
- Location: {cfg.get('location', '')}, {cfg.get('state', '')}

CONSULTANT: {company.get('trade_name', 'PPS Anantams')} | {company.get('owner', '')}
Experience: {company.get('experience', '25 years')}

Generate for each slide:
SLIDE 1: Title + Tagline
SLIDE 2: The Problem (India's bitumen import dependency)
SLIDE 3: The Solution (Bio-modified bitumen from agro waste)
SLIDE 4: Market Opportunity (Rs 25,000 Cr market)
SLIDE 5: Technology (CSIR-CRRI, 4-stage process)
SLIDE 6: Financial Summary (key metrics table)
SLIDE 7: Revenue Model (how money is made)
SLIDE 8: Competitive Advantage (why PPS Anantams)
SLIDE 9: Team & Track Record
SLIDE 10: The Ask & Next Steps

For each slide provide: Title, 4-5 bullet points, 1 key number to highlight.
Professional investor deck language — compelling but factual."""

    result, provider = ask_ai(prompt, "You are creating a VC-quality investor presentation.", 2500)
    return result, provider


# ══════════════════════════════════════════════════════════════════════
# SKILL REGISTRY — For dashboard integration
# ══════════════════════════════════════════════════════════════════════
AI_SKILLS = [
    {
        "id": "vendor_reader",
        "name": "Vendor Quote Analyzer",
        "icon": "📋",
        "description": "Paste vendor quotation → get comparison table + rating",
        "available_on": ["Procurement", "Financial"],
    },
    {
        "id": "bom_generator",
        "name": "Bill of Materials Generator",
        "icon": "📦",
        "description": "Describe equipment → get complete BOM with quantities and costs",
        "available_on": ["Procurement", "Plant Design"],
    },
    {
        "id": "gpcb_drafter",
        "name": "GPCB Application Drafter",
        "icon": "📄",
        "description": "Auto-draft Consent to Establish application for Gujarat PCB",
        "available_on": ["Compliance", "Document Hub"],
    },
    {
        "id": "factory_license",
        "name": "Factory License Drafter",
        "icon": "🏭",
        "description": "Auto-draft Factory License application",
        "available_on": ["Compliance", "Document Hub"],
    },
    {
        "id": "compliance_checklist",
        "name": "State Compliance Checklist",
        "icon": "✅",
        "description": "Generate state-specific license checklist with timelines",
        "available_on": ["Compliance"],
    },
    {
        "id": "financial_json",
        "name": "AI Financial Projection",
        "icon": "📊",
        "description": "AI generates 5-year projection → downloadable Excel",
        "available_on": ["Financial", "Document Hub", "Export Center"],
    },
    {
        "id": "site_report",
        "name": "Site Progress Report",
        "icon": "🏗️",
        "description": "Paste raw notes → get formal daily site report",
        "available_on": ["Meeting Planner", "Project Gantt"],
    },
    {
        "id": "investor_deck",
        "name": "Investor Deck Generator",
        "icon": "💼",
        "description": "Generate 10-slide investor presentation content",
        "available_on": ["Document Hub", "Presenter"],
    },
]
