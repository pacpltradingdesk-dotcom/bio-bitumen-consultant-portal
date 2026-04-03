"""
AI Engine — OpenAI + Claude API Integration with Smart Fallback
=================================================================
Supports: GPT-4o, GPT-4o-mini, Claude Sonnet, Claude Haiku
Falls back to built-in knowledge base if no API key configured.

API keys stored in: data/ai_config.json (gitignored, never committed)
"""
import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "data" / "ai_config.json"


def load_ai_config():
    """Load API keys from secure config file."""
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"openai_key": "", "claude_key": "", "preferred_provider": "openai",
            "openai_model": "gpt-4o-mini", "claude_model": "claude-sonnet-4-20250514"}


def save_ai_config(config):
    """Save API keys to secure config file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")


def is_ai_available():
    """Check if any AI API is configured and ready."""
    cfg = load_ai_config()
    return bool(cfg.get("openai_key") or cfg.get("claude_key"))


def get_active_provider():
    """Return which AI provider is active."""
    cfg = load_ai_config()
    if cfg.get("preferred_provider") == "claude" and cfg.get("claude_key"):
        return "claude"
    if cfg.get("openai_key"):
        return "openai"
    if cfg.get("claude_key"):
        return "claude"
    return None


# ══════════════════════════════════════════════════════════════════════
# OPENAI API CALLS
# ══════════════════════════════════════════════════════════════════════
def _call_openai(prompt, system_prompt="", max_tokens=2000):
    """Call OpenAI API (GPT-4o / GPT-4o-mini)."""
    cfg = load_ai_config()
    api_key = cfg.get("openai_key", "")
    model = cfg.get("openai_model", "gpt-4o-mini")

    if not api_key:
        return None

    try:
        import requests
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        resp = requests.post("https://api.openai.com/v1/chat/completions",
                              headers=headers, timeout=60,
                              json={"model": model, "messages": messages,
                                    "max_tokens": max_tokens, "temperature": 0.7})
        data = resp.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        if "error" in data:
            return f"OpenAI Error: {data['error'].get('message', 'Unknown error')}"
        return None
    except Exception as e:
        return f"OpenAI connection error: {e}"


# ══════════════════════════════════════════════════════════════════════
# CLAUDE API CALLS
# ══════════════════════════════════════════════════════════════════════
def _call_claude(prompt, system_prompt="", max_tokens=2000):
    """Call Anthropic Claude API (Sonnet / Haiku)."""
    cfg = load_ai_config()
    api_key = cfg.get("claude_key", "")
    model = cfg.get("claude_model", "claude-sonnet-4-20250514")

    if not api_key:
        return None

    try:
        import requests
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        body = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            body["system"] = system_prompt

        resp = requests.post("https://api.anthropic.com/v1/messages",
                              headers=headers, timeout=60, json=body)
        data = resp.json()
        if "content" in data:
            return data["content"][0]["text"]
        if "error" in data:
            return f"Claude Error: {data['error'].get('message', 'Unknown error')}"
        return None
    except Exception as e:
        return f"Claude connection error: {e}"


# ══════════════════════════════════════════════════════════════════════
# UNIFIED AI CALL — Auto-selects best available provider
# ══════════════════════════════════════════════════════════════════════
def ask_ai(prompt, system_prompt="", max_tokens=2000):
    """
    Ask AI using best available provider. Falls back gracefully.
    Priority: preferred_provider → other provider → None (use built-in)
    """
    provider = get_active_provider()

    if provider == "openai":
        result = _call_openai(prompt, system_prompt, max_tokens)
        if result and not result.startswith("OpenAI Error"):
            return result, "openai"
        # Fallback to Claude
        result2 = _call_claude(prompt, system_prompt, max_tokens)
        if result2 and not result2.startswith("Claude Error"):
            return result2, "claude"
        return result or "AI unavailable", "error"

    elif provider == "claude":
        result = _call_claude(prompt, system_prompt, max_tokens)
        if result and not result.startswith("Claude Error"):
            return result, "claude"
        # Fallback to OpenAI
        result2 = _call_openai(prompt, system_prompt, max_tokens)
        if result2 and not result2.startswith("OpenAI Error"):
            return result2, "openai"
        return result or "AI unavailable", "error"

    return None, "none"


# ══════════════════════════════════════════════════════════════════════
# SPECIALIZED AI FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_BASE = """You are a senior industrial consultant for PPS Anantams Corporation,
specializing in Bio-Modified Bitumen plant setup in India. You have 25 years of experience
in the bitumen industry. You provide professional, accurate, bank-ready advice.
Always use specific numbers, reference IS standards, and give actionable recommendations.
Format responses with clear headings, bullet points, and tables where appropriate."""


def ai_write_dpr_section(section_name, cfg, company):
    """AI writes a professional DPR section using project data."""
    prompt = f"""Write a professional DPR (Detailed Project Report) section: "{section_name}"

Project Details:
- Client: {cfg.get('client_name', 'The Promoter')} | {cfg.get('client_company', '')}
- Project: {cfg.get('project_name', 'Bio-Modified Bitumen Plant')}
- Location: {cfg.get('site_address', cfg.get('location', ''))} , {cfg.get('state', '')}
- Capacity: {cfg['capacity_tpd']:.0f} MT/Day
- Investment: Rs {cfg['investment_cr']:.2f} Crore
- ROI: {cfg['roi_pct']:.1f}% | IRR: {cfg['irr_pct']:.1f}%
- DSCR Year 3: {cfg['dscr_yr3']:.2f}x
- Break-Even: {cfg['break_even_months']} months
- Revenue Year 5: Rs {cfg['revenue_yr5_lac']:.0f} Lakhs

Write 300-500 words, professional tone, suitable for bank submission.
Include specific numbers from the data above. Use proper formatting."""

    system = SYSTEM_PROMPT_BASE + "\nYou are writing a bank-ready DPR section. Be precise and professional."
    result, provider = ask_ai(prompt, system, max_tokens=1500)
    return result, provider


def ai_financial_analysis(cfg):
    """AI analyzes financials and provides professional commentary."""
    timeline_str = ""
    if cfg.get("roi_timeline"):
        for row in cfg["roi_timeline"][:3]:
            timeline_str += f"Year {row['Year']}: Rev={row['Revenue (Lac)']}L, PAT={row['PAT (Lac)']}L, DSCR={row['DSCR']}\n"

    prompt = f"""Analyze this bio-bitumen plant financial model and provide professional commentary:

Investment: Rs {cfg['investment_cr']:.2f} Crore (Loan: Rs {cfg.get('loan_cr', 0):.2f} Cr, Equity: Rs {cfg.get('equity_cr', 0):.2f} Cr)
Capacity: {cfg['capacity_tpd']:.0f} MT/Day | Working Days: {cfg['working_days']}
EMI: Rs {cfg['emi_lac_mth']:.2f} Lakhs/month | Interest: {cfg['interest_rate']*100:.1f}%
ROI: {cfg['roi_pct']:.1f}% | IRR: {cfg['irr_pct']:.1f}% | DSCR Yr3: {cfg['dscr_yr3']:.2f}x
Break-Even: {cfg['break_even_months']} months | Revenue Yr5: Rs {cfg['revenue_yr5_lac']:.0f} Lac
Profit/MT: Rs {cfg['profit_per_mt']:,.0f} | Monthly Profit: Rs {cfg['monthly_profit_lac']:.1f} Lac

P&L Trend:
{timeline_str}

Provide:
1. Overall financial health assessment (2-3 sentences)
2. Bankability score (out of 10) with justification
3. Key strengths (3 points)
4. Key risks (3 points)
5. Recommendations for improving financial metrics
6. DSCR commentary (is it above bank minimum 1.5x?)

Write in professional consultant tone, suitable for bank presentation."""

    system = SYSTEM_PROMPT_BASE + "\nYou are a CA/financial analyst providing expert commentary for bank submission."
    result, provider = ask_ai(prompt, system, max_tokens=1500)
    return result, provider


def ai_chat(user_message, chat_history=None, cfg=None):
    """Smart AI chat — answers any question about bio-bitumen business."""
    context = ""
    if cfg:
        context = f"""Current project: {cfg.get('project_name', 'Bio-Bitumen Plant')}
Client: {cfg.get('client_name', 'Not set')} | {cfg.get('capacity_tpd', 20)} TPD
Investment: Rs {cfg.get('investment_cr', 8)} Cr | ROI: {cfg.get('roi_pct', 40)}%
Location: {cfg.get('location', '')}, {cfg.get('state', '')}"""

    history_str = ""
    if chat_history:
        for msg in chat_history[-6:]:  # Last 6 messages for context
            role = "User" if msg["role"] == "user" else "Consultant"
            history_str += f"{role}: {msg['content'][:200]}\n"

    prompt = f"""Project Context:
{context}

Recent Chat:
{history_str}

User Question: {user_message}

Answer as the senior consultant. Be specific, use numbers, give actionable advice.
If asked about technical specs, quote IS standards. If asked about finance, give specific calculations.
If asked about compliance, list exact licenses with timelines."""

    system = SYSTEM_PROMPT_BASE
    result, provider = ask_ai(prompt, system, max_tokens=1500)
    return result, provider


def ai_auto_report(report_type, cfg, company):
    """Generate complete professional report using AI."""
    prompts = {
        "executive_summary": f"Write a 500-word Executive Summary for a {cfg['capacity_tpd']:.0f} TPD Bio-Modified Bitumen plant DPR. Investment: Rs {cfg['investment_cr']:.2f} Cr, ROI: {cfg['roi_pct']:.1f}%, Location: {cfg.get('location', '')}, {cfg.get('state', '')}. Make it compelling for bank/investor submission.",

        "market_analysis": f"Write a 400-word Market Analysis section for bio-bitumen in India. Include: market size (Rs 25,000+ Cr), import dependency (49%), NHAI green mandate, CSIR-CRRI technology, 130-216 new plants needed. Reference for {cfg.get('state', 'India')} specifically.",

        "technical_description": f"Write a 500-word Technical Process Description for {cfg['capacity_tpd']:.0f} TPD bio-bitumen plant. Cover: 4 stages (pelletization, pyrolysis at 450-550C, bio-oil blending 15-30%, quality testing IS:73). Include equipment list and specifications.",

        "risk_assessment": f"Write a 400-word Risk Assessment for {cfg['capacity_tpd']:.0f} TPD bio-bitumen plant with Rs {cfg['investment_cr']:.2f} Cr investment in {cfg.get('state', 'India')}. Cover: market risk, technical risk, financial risk, regulatory risk, supply chain risk. Include mitigation for each.",

        "compliance_narrative": f"Write a 300-word Compliance & Regulatory section listing all licenses needed for a bio-bitumen plant in {cfg.get('state', 'India')}. Include: CTE, CTO, PESO, Factory License, Fire NOC, GST, MSME registration. With timelines.",
    }

    prompt = prompts.get(report_type, prompts["executive_summary"])
    system = SYSTEM_PROMPT_BASE + f"\nWriting for: {cfg.get('client_name', 'Client')} | {company.get('trade_name', 'PPS Anantams')}"
    result, provider = ask_ai(prompt, system, max_tokens=2000)
    return result, provider


def test_api_connection():
    """Test if API keys work — returns status for each provider."""
    results = {}

    cfg = load_ai_config()

    if cfg.get("openai_key"):
        result = _call_openai("Say 'OpenAI connected' in exactly 2 words.", max_tokens=10)
        results["openai"] = {"status": "OK" if result and "Error" not in str(result) else "FAILED",
                              "model": cfg.get("openai_model", "gpt-4o-mini"),
                              "response": str(result)[:100] if result else "No response"}
    else:
        results["openai"] = {"status": "No key", "model": "", "response": ""}

    if cfg.get("claude_key"):
        result = _call_claude("Say 'Claude connected' in exactly 2 words.", max_tokens=10)
        results["claude"] = {"status": "OK" if result and "Error" not in str(result) else "FAILED",
                              "model": cfg.get("claude_model", "claude-sonnet-4-20250514"),
                              "response": str(result)[:100] if result else "No response"}
    else:
        results["claude"] = {"status": "No key", "model": "", "response": ""}

    return results
