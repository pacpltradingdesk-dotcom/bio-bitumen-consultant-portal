"""
Meeting Copilot — AI-Powered Live Meeting Assistant
=====================================================
10 features for client meetings: Q&A, objections, CMA, scenarios,
meeting notes, scheme analysis, competitor comparison, investment thesis.
Works with OpenAI GPT-4o and/or Claude Sonnet via ai_engine.py.
"""
from engines.ai_engine import ask_ai, is_ai_available
from config import COMPANY, COMPETITORS, PPS_SWOT, RISK_REGISTRY, ENVIRONMENTAL_FACTORS


def _build_context(cfg):
    """Build project context string from config for AI prompts."""
    return f"""PROJECT: {cfg.get('project_name', 'Bio-Bitumen Plant')}
CLIENT: {cfg.get('client_name', 'Client')} | {cfg.get('client_company', '')}
CAPACITY: {cfg['capacity_tpd']:.0f} TPD | INVESTMENT: Rs {cfg['investment_cr']:.2f} Crore
LOCATION: {cfg.get('location', '')}, {cfg.get('state', '')}
LOAN: Rs {cfg.get('loan_cr', 0):.2f} Cr | EQUITY: Rs {cfg.get('equity_cr', 0):.2f} Cr | EMI: Rs {cfg.get('emi_lac_mth', 0):.2f} Lac/mo
ROI: {cfg['roi_pct']:.1f}% | IRR: {cfg['irr_pct']:.1f}% | DSCR Yr3: {cfg['dscr_yr3']:.2f}x
BREAK-EVEN: {cfg['break_even_months']} months | REVENUE YR5: Rs {cfg['revenue_yr5_lac']:.0f} Lac
PROFIT/MT: Rs {cfg['profit_per_mt']:,.0f} | MONTHLY PROFIT: Rs {cfg['monthly_profit_lac']:.1f} Lac
STAFF: {cfg.get('staff', 18)} | POWER: {cfg.get('power_kw', 100)} kW
CO2 SAVED: {cfg['capacity_tpd'] * 300 * 0.35:.0f} tonnes/yr | STUBBLE: {cfg['capacity_tpd'] * 300 * 2.5:.0f} MT/yr diverted"""


CONSULTANT_SYSTEM = f"""You are the AI assistant for {COMPANY['owner']}, {COMPANY['trade_name']} —
India's most experienced bio-bitumen plant consultant.
CREDENTIALS: {COMPANY['experience']} | {COMPANY['industry_contacts']:,} industry contacts |
International VG-30 supply 2.4 Lakh MT/yr | BSE-listed founder.
Use EXACT numbers from project data. Indian number format (Lac/Cr).
Be professional, confident, data-driven. Format with bold headers and bullet points."""


# ══════════════════════════════════════════════════════════════════════
# FEATURE 1: LIVE Q&A COPILOT
# ══════════════════════════════════════════════════════════════════════
def live_qa(question, stakeholder_type, cfg):
    """Answer any client question instantly with project-specific data."""
    system = CONSULTANT_SYSTEM + f"""
You are answering during a LIVE CLIENT MEETING. Stakeholder: {stakeholder_type}.
RULES:
- Answer in 4-6 bullet points maximum
- Use EXACT numbers from project data below
- For Investor: focus on returns, exit strategy, market size
- For Bank Officer: focus on DSCR, collateral, repayment, CGTMSE
- For Govt Officer: focus on jobs, CO2 saved, stubble burning, Make in India
- For Farmer: focus on biomass price, guaranteed purchase, local jobs
- End with one compelling closing statement"""

    prompt = f"{_build_context(cfg)}\n\nCLIENT QUESTION: {question}"
    result, provider = ask_ai(prompt, system, max_tokens=800)
    return result, provider


# ══════════════════════════════════════════════════════════════════════
# FEATURE 2: OBJECTION DESTROYER
# ══════════════════════════════════════════════════════════════════════
COMMON_OBJECTIONS = {
    "Investor": [
        "The ROI seems too high to be realistic",
        "Bio-bitumen is unproven technology",
        "What if crude oil prices drop?",
        "Too much competition from IOCL/BPCL",
        "I don't understand the bitumen market",
    ],
    "Bank Officer": [
        "DSCR projections seem aggressive",
        "What collateral can you offer?",
        "Bio-bitumen has no track record for bank funding",
        "The promoter has no manufacturing experience",
        "Working capital requirement seems insufficient",
    ],
    "Govt Officer": [
        "How is this different from plastic road technology?",
        "What proof of CSIR-CRRI certification?",
        "Will this actually reduce stubble burning?",
        "Why should government subsidize this?",
        "Is the technology commercially proven?",
    ],
    "Farmer": [
        "How do I know you'll actually buy my straw?",
        "The price you're offering is too low",
        "What if your plant shuts down?",
        "I've been cheated by companies before",
        "Transportation cost will eat my profit",
    ],
}


def handle_objection(objection, stakeholder_type, cfg):
    """Generate ACR (Acknowledge-Counter-Redirect) response to objection."""
    system = CONSULTANT_SYSTEM + f"""
A {stakeholder_type} has raised an OBJECTION. Use ACR method:
(A) ACKNOWLEDGE — Show understanding, never dismiss
(C) COUNTER — Data-driven rebuttal with exact project numbers
(R) REDIRECT — Pivot to PPS Anantams unique strength

Format:
**Understanding your concern:** [1 sentence]
**The data says:** [2-3 bullets with numbers]
**What sets us apart:** [1 compelling differentiator]"""

    prompt = f"{_build_context(cfg)}\n\nOBJECTION: \"{objection}\""
    result, provider = ask_ai(prompt, system, max_tokens=600)
    return result, provider


# ══════════════════════════════════════════════════════════════════════
# FEATURE 3: CMA DATA GENERATOR
# ══════════════════════════════════════════════════════════════════════
def generate_cma_narrative(cfg):
    """Generate Credit Monitoring Arrangement summary for bank officers."""
    system = CONSULTANT_SYSTEM + """
You are a Chartered Accountant preparing CMA Data narrative for a term loan application.
Use formal banking language. Include all standard CMA ratios and viability assessment."""

    prompt = f"""{_build_context(cfg)}

Generate CMA-format narrative:
1. Project Viability Summary (3 lines)
2. Key Ratios: DSCR (yr 1-5), Current Ratio, Debt-Equity, Interest Coverage
3. Strength of Proposal (4 bullets)
4. Risk Mitigation (3 bullets)
5. Promoter Background: {COMPANY['owner']} — {COMPANY['experience']}
6. Recommendation: Suitable for term loan sanction

Format as bank submission document."""

    result, provider = ask_ai(prompt, system, max_tokens=1200)
    return result, provider


# ══════════════════════════════════════════════════════════════════════
# FEATURE 4: AUDIENCE-ADAPTIVE TALKING POINTS
# ══════════════════════════════════════════════════════════════════════
def get_talking_points(slide_title, slide_data, audience_type, cfg):
    """Generate 3 audience-specific talking points for a presentation slide."""
    system = CONSULTANT_SYSTEM + f"""
Generate 3 concise talking points for audience: {audience_type}.
Rules:
- Each point: 1 sentence with a specific number
- Investor: returns, market, exit | Bank: cash flows, security | Govt: jobs, CO2 | Farmer: income, guarantee
- Mark most impactful point with a star"""

    prompt = f"SLIDE: {slide_title}\n{_build_context(cfg)}\nSLIDE DATA: {slide_data}"
    result, provider = ask_ai(prompt, system, max_tokens=400)
    return result, provider


# ══════════════════════════════════════════════════════════════════════
# FEATURE 5: COMPETITOR COMPARISON
# ══════════════════════════════════════════════════════════════════════
def compare_competitor(competitor_name, stakeholder_type, cfg):
    """Generate professional competitive comparison."""
    comp = next((c for c in COMPETITORS if competitor_name.lower() in c["name"].lower()), None)
    comp_str = str(comp) if comp else f"Unknown competitor: {competitor_name}"

    system = CONSULTANT_SYSTEM + """
Generate professional competitive comparison. Be fair — never trash-talk.
Focus on PPS strengths, not competitor weaknesses."""

    prompt = f"""{_build_context(cfg)}
COMPETITOR: {competitor_name}
COMPETITOR DATA: {comp_str}
STAKEHOLDER: {stakeholder_type}

PPS ADVANTAGES: {', '.join(PPS_SWOT['strengths'][:4])}

Generate:
1. **Competitor Profile** (2 lines, fair assessment)
2. **Comparison Table** (5 criteria: Experience, Network, Technology, Supply Chain, Track Record)
3. **3 Winning Arguments** for THIS project
4. **Diplomatic Closer** (1 sentence)"""

    result, provider = ask_ai(prompt, system, max_tokens=800)
    return result, provider


# ══════════════════════════════════════════════════════════════════════
# FEATURE 7: RISK SCENARIO NARRATOR
# ══════════════════════════════════════════════════════════════════════
def narrate_scenario(scenario_desc, base_metrics, new_metrics, stakeholder_type):
    """AI narrates the impact of a risk scenario."""
    system = CONSULTANT_SYSTEM + f"""
A risk scenario has been simulated. Explain impact to {stakeholder_type}.
Be confident but honest. Show mitigation strategies."""

    prompt = f"""SCENARIO: "{scenario_desc}"
BASE CASE: ROI {base_metrics['roi']}% | IRR {base_metrics['irr']}% | DSCR {base_metrics['dscr']}x | Payback {base_metrics['payback']}mo
NEW CASE: ROI {new_metrics['roi']}% | IRR {new_metrics['irr']}% | DSCR {new_metrics['dscr']}x | Payback {new_metrics['payback']}mo

Generate:
1. **Impact Summary** — 1 headline sentence
2. **What This Means** — 2 bullets in plain language
3. **Why It's Manageable** — 2 mitigation strategies
4. **Bottom Line** — 1 reassurance sentence with a number"""

    result, provider = ask_ai(prompt, system, max_tokens=600)
    return result, provider


# ══════════════════════════════════════════════════════════════════════
# FEATURE 8: MEETING MINUTES GENERATOR
# ══════════════════════════════════════════════════════════════════════
def generate_meeting_minutes(raw_notes, cfg, meeting_type="Client Meeting"):
    """Generate formal meeting minutes from raw notes."""
    system = CONSULTANT_SYSTEM + """
You are a professional business meeting documentation specialist.
Generate formal minutes from raw notes. Use Indian business language."""

    prompt = f"""MEETING: {meeting_type}
CONSULTANT: {COMPANY['owner']}, {COMPANY['trade_name']}
CLIENT: {cfg.get('client_name', 'Client')}, {cfg.get('client_company', '')}
PROJECT: {cfg.get('project_name', 'Bio-Bitumen Plant')} | {cfg['capacity_tpd']:.0f} TPD | {cfg.get('state', '')}
DATE: Today

RAW NOTES:
{raw_notes}

Generate:
1. **MEETING MINUTES** (formal): Attendees, Discussion Points, Decisions, Action Items with deadlines
2. **WHATSAPP SUMMARY** (under 500 chars, professional)
3. **EMAIL DRAFT** (thank you + summary + next steps)
4. **FOLLOW-UP CHECKLIST** (for internal team)"""

    result, provider = ask_ai(prompt, system, max_tokens=1500)
    return result, provider


# ══════════════════════════════════════════════════════════════════════
# FEATURE 9: GOVT SCHEME ELIGIBILITY ANALYZER
# ══════════════════════════════════════════════════════════════════════
def analyze_govt_schemes(cfg):
    """Analyze eligibility for all government schemes."""
    system = CONSULTANT_SYSTEM + """
You are an expert on Indian government industrial schemes and subsidies.
Be specific with scheme names, amounts, and application processes."""

    prompt = f"""{_build_context(cfg)}
RAW MATERIAL: Agricultural waste (biomass pyrolysis)
TECHNOLOGY: CSIR-CRRI Licensed

Analyze eligibility for:
1. MNRE Waste-to-Wealth Mission
2. State MSME Subsidy ({cfg.get('state', 'Gujarat')})
3. CGTMSE Collateral-Free Guarantee
4. Technology Development Board
5. Carbon Credits (voluntary market)
6. PM MUDRA Yojana
7. Startup India (if applicable)
8. BIRAC/DBT Bio-innovation
9. State-specific schemes for {cfg.get('state', 'Gujarat')}

For EACH: Eligibility status, Potential amount (Rs), Key documents, Timeline.
Calculate TOTAL POTENTIAL SUBSIDY as Rs Crore and % of project cost."""

    result, provider = ask_ai(prompt, system, max_tokens=1500)
    return result, provider


# ══════════════════════════════════════════════════════════════════════
# FEATURE 10: INVESTMENT THESIS
# ══════════════════════════════════════════════════════════════════════
def generate_investment_thesis(cfg, stakeholder_type="Investor"):
    """Generate comprehensive investment thesis: bio-bitumen vs alternatives."""
    system = CONSULTANT_SYSTEM + f"""
You are an investment analyst. Generate rigorous comparison for {stakeholder_type}."""

    prompt = f"""{_build_context(cfg)}

Compare 5 business options:
1. Bio-Modified Bitumen Plant (THIS proposal)
2. Conventional VG-30 Trading Business
3. Plastic-Modified Bitumen Unit
4. Bitumen Emulsion Plant
5. Pure Pyrolysis (bio-oil + biochar only)

For EACH show: Capital (Rs Cr), Revenue potential, Net Margin %, Govt Support level, Competition level, 5-Year outlook.

Then generate:
**Investment Thesis** — Why bio-bitumen is optimal for {cfg.get('state', 'India')} in 2026 (3-4 sentences)
**Key Differentiator** — 1 closing line

Use Indian number format. Be balanced but conclusive."""

    result, provider = ask_ai(prompt, system, max_tokens=1500)
    return result, provider
