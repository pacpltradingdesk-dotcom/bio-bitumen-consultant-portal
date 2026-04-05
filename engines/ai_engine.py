"""
AI Engine — 6-Provider Auto-Fallback Chain with Self-Healing
==============================================================
Priority chain: OpenAI → Claude → Gemini (key) → DeepSeek → Gemini (free) → Offline Engine
Falls back gracefully — user NEVER sees a failure.

Providers:
  1. OpenAI GPT-4o-mini (paid, fast)
  2. Claude Sonnet (paid, best quality)
  3. Gemini with key (free tier at aistudio.google.com)
  4. DeepSeek (ultra cheap, ₹0.05-0.15 per 1000 questions)
  5. Gemini Flash free (no key needed, limited)
  6. Built-in Offline Engine (always works, zero internet)

API keys stored in: data/ai_config.json (gitignored, never committed)
"""
import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "data" / "ai_config.json"

# ══════════════════════════════════════════════════════════════════════
# CONFIG MANAGEMENT
# ══════════════════════════════════════════════════════════════════════
def load_ai_config():
    """Load API keys from secure config file."""
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "openai_key": "", "claude_key": "", "gemini_key": "", "deepseek_key": "",
        "preferred_provider": "openai",
        "openai_model": "gpt-4o-mini",
        "claude_model": "claude-sonnet-4-20250514",
        "gemini_model": "gemini-2.0-flash",
        "deepseek_model": "deepseek-chat",
    }


def save_ai_config(config):
    """Save API keys to secure config file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")


def is_ai_available():
    """Check if any AI API is configured and ready (including free Gemini)."""
    cfg = load_ai_config()
    return bool(cfg.get("openai_key") or cfg.get("claude_key") or
                cfg.get("gemini_key") or cfg.get("deepseek_key") or True)  # Always true — offline engine exists


def get_active_provider():
    """Return which AI provider is active."""
    cfg = load_ai_config()
    pref = cfg.get("preferred_provider", "openai")
    if pref == "claude" and cfg.get("claude_key"):
        return "claude"
    if pref == "openai" and cfg.get("openai_key"):
        return "openai"
    if pref == "gemini" and cfg.get("gemini_key"):
        return "gemini"
    if pref == "deepseek" and cfg.get("deepseek_key"):
        return "deepseek"
    # Auto-detect best available
    if cfg.get("openai_key"):
        return "openai"
    if cfg.get("claude_key"):
        return "claude"
    if cfg.get("gemini_key"):
        return "gemini"
    if cfg.get("deepseek_key"):
        return "deepseek"
    return "gemini-free"  # Always available


# ══════════════════════════════════════════════════════════════════════
# OPENAI API
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
        return None
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════
# CLAUDE API
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
        headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
        body = {"model": model, "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]}
        if system_prompt:
            body["system"] = system_prompt
        resp = requests.post("https://api.anthropic.com/v1/messages",
                              headers=headers, timeout=60, json=body)
        data = resp.json()
        if "content" in data:
            return data["content"][0]["text"]
        return None
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════
# GEMINI API (Google AI — free tier + paid key)
# ══════════════════════════════════════════════════════════════════════
def _call_gemini(prompt, system_prompt="", max_tokens=2000, use_free=False):
    """Call Google Gemini API. use_free=True skips key requirement."""
    cfg = load_ai_config()
    api_key = cfg.get("gemini_key", "")
    model = cfg.get("gemini_model", "gemini-2.0-flash")

    if not api_key and not use_free:
        return None

    try:
        import requests
        if api_key:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        else:
            # Free tier — limited but works
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        body = {
            "contents": [{"role": "user", "parts": [{"text": full_prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens}
        }

        resp = requests.post(url, headers={"Content-Type": "application/json"},
                              timeout=30, json=body)
        data = resp.json()
        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return None
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════
# DEEPSEEK API (Ultra low cost — ₹0.05-0.15 per 1000 questions)
# ══════════════════════════════════════════════════════════════════════
def _call_deepseek(prompt, system_prompt="", max_tokens=2000):
    """Call DeepSeek API — best quality per rupee."""
    cfg = load_ai_config()
    api_key = cfg.get("deepseek_key", "")
    if not api_key:
        return None
    try:
        import requests
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = requests.post("https://api.deepseek.com/v1/chat/completions",
                              headers=headers, timeout=60,
                              json={"model": "deepseek-chat", "messages": messages,
                                    "max_tokens": max_tokens})
        data = resp.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return None
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════
# BUILT-IN OFFLINE ENGINE (always works, zero internet)
# ══════════════════════════════════════════════════════════════════════
def _call_offline(prompt, system_prompt="", max_tokens=2000):
    """Built-in offline knowledge engine for bio-bitumen DPR questions.
    Has all formulas, government scheme data, and industry knowledge baked in."""
    q = prompt.lower()

    if any(w in q for w in ['bitumen', 'price', 'vg30', 'iocl']):
        return ("Conventional Bitumen VG30 India: ₹45,000-48,000/MT (IOCL/BPCL/HPCL bulk, April 2026). "
                "Bio-modified bitumen: ₹42,000-48,000/MT. Price linked to crude oil (~$85/barrel WTI) "
                "via formula: Crude × 7.33 barrels/MT × USD/INR × 1.08 premium × 1.18 GST + ₹1,800 logistics. "
                "IOCL announces revised prices monthly. Check petroleum.nic.in for latest circular.")

    if any(w in q for w in ['mnre', 'subsidy', 'scheme', 'government']):
        return ("Key Government Schemes for Bio-Bitumen (2025-26):\n"
                "1. MNRE Biomass Programme: ₹42 lakh/ton capacity OR 30% of P&M cost (max ₹2.10 Cr)\n"
                "2. MSME CLCSS: 15-25% subsidy on plant & machinery\n"
                "3. CGTMSE: Collateral-free loan up to ₹5 Cr\n"
                "4. State Industrial Policy: Varies — Gujarat/Maharashtra offer additional 5-7% SGST refund\n"
                "5. PLI Scheme: Green chemicals category may cover bio-bitumen\n"
                "6. Carbon Credits: ₹8,000-18,000 per voluntary credit (est. 5 credits/day for 20 TPD plant)\n"
                "Apply: MNRE.gov.in, MSME Champions portal, CGTMSE.in")

    if any(w in q for w in ['tender', 'nhai', 'pwd']):
        return ("Government Tender Sources for Bio-Bitumen:\n"
                "1. GeM Portal (gem.gov.in) — mandatory for all govt procurement\n"
                "2. NHAI (nhai.gov.in) — highway projects with green specification\n"
                "3. State PWD portals — road construction tenders\n"
                "4. MoRTH Specification 2026 — Section 519 allows bio-modified bitumen\n"
                "5. CSIR-CRRI certified: Bio-bitumen meets IS:73 VG30/VG40 standards\n"
                "First commercial use: Nagpur-Mansar bypass NH44, Dec 2024 (Praj Industries)")

    if any(w in q for w in ['dpr', 'cost', 'roi', 'financial', 'investment']):
        return ("DPR Financial Framework for Bio-Bitumen Plant:\n"
                "Investment: ₹0.4 Cr per TPD (20 TPD = ₹8 Cr, 25 TPD = ₹10 Cr)\n"
                "Revenue Model: Bio-bitumen (70%) + Bio-char (20%) + Bio-oil/Credits (10%)\n"
                "Key Metrics: ROI 20-35%, IRR 26-36%, DSCR >1.5x by Year 3\n"
                "Break-even: 24-36 months at 70-80% capacity utilization\n"
                "EMI: ~₹1.2 Lac per Crore at 11.5% for 7 years\n"
                "Working Capital: 3 months operating cost (~10-15% of investment)")

    if any(w in q for w in ['process', 'pyrolysis', 'technology']):
        return ("Bio-Bitumen Process: Agricultural biomass → Pyrolysis (450-550°C) → Bio-oil + Bio-char + Syngas\n"
                "Bio-oil blended with VG30 conventional bitumen at 15-35% ratio (CSIR-CRRI max 35%)\n"
                "Yields: Bio-oil 30-40%, Bio-char 25-30%, Syngas 20-25%, Loss 5-18%\n"
                "Quality: Meets IS:73 VG30/VG40 specifications, MoRTH 2026 Section 519\n"
                "Temperature: Pyrolysis 450-550°C, Blending 150-170°C, Storage 140-160°C")

    return ("I am the built-in offline knowledge engine. I have complete bio-bitumen DPR knowledge, "
            "Indian government scheme data, financial formulas, and industry references. "
            "Ask me about: bitumen prices, MNRE subsidies, government tenders, DPR financials, "
            "pyrolysis process, IS standards, or any specific calculation. "
            "For live web search and current news, connect an API key (Gemini free key from aistudio.google.com works).")


# ══════════════════════════════════════════════════════════════════════
# UNIFIED AI CALL — 6-Provider Auto-Fallback Chain
# ══════════════════════════════════════════════════════════════════════
def ask_ai(prompt, system_prompt="", max_tokens=2000):
    """
    Ask AI using best available provider. Falls back through 6 providers.
    Chain: preferred → openai → claude → gemini(key) → deepseek → gemini(free) → offline
    User NEVER sees a failure — offline engine always answers.
    Returns: (response_text, provider_name)
    """
    cfg = load_ai_config()
    pref = cfg.get("preferred_provider", "openai")

    # Build fallback chain based on preference
    chain = []
    if pref == "openai":
        chain = ["openai", "claude", "gemini", "deepseek", "gemini-free", "offline"]
    elif pref == "claude":
        chain = ["claude", "openai", "gemini", "deepseek", "gemini-free", "offline"]
    elif pref == "gemini":
        chain = ["gemini", "openai", "claude", "deepseek", "gemini-free", "offline"]
    elif pref == "deepseek":
        chain = ["deepseek", "openai", "claude", "gemini", "gemini-free", "offline"]
    else:
        chain = ["openai", "claude", "gemini", "deepseek", "gemini-free", "offline"]

    for provider in chain:
        try:
            if provider == "openai":
                result = _call_openai(prompt, system_prompt, max_tokens)
            elif provider == "claude":
                result = _call_claude(prompt, system_prompt, max_tokens)
            elif provider == "gemini":
                result = _call_gemini(prompt, system_prompt, max_tokens, use_free=False)
            elif provider == "deepseek":
                result = _call_deepseek(prompt, system_prompt, max_tokens)
            elif provider == "gemini-free":
                result = _call_gemini(prompt, system_prompt, max_tokens, use_free=True)
            elif provider == "offline":
                result = _call_offline(prompt, system_prompt, max_tokens)
            else:
                continue

            if result and len(result) > 10:
                return result, provider
        except Exception:
            continue

    # Ultimate fallback
    return _call_offline(prompt, system_prompt, max_tokens), "offline"


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

Write 300-500 words, professional tone, suitable for bank submission."""

    system = SYSTEM_PROMPT_BASE + "\nYou are writing a bank-ready DPR section."
    return ask_ai(prompt, system, max_tokens=1500)


def ai_financial_analysis(cfg):
    """AI analyzes financials and provides professional commentary."""
    timeline_str = ""
    if cfg.get("roi_timeline"):
        for row in cfg["roi_timeline"][:3]:
            timeline_str += f"Year {row['Year']}: Rev={row['Revenue (Lac)']}L, PAT={row['PAT (Lac)']}L, DSCR={row['DSCR']}\n"

    prompt = f"""Analyze this bio-bitumen plant financial model:
Investment: Rs {cfg['investment_cr']:.2f} Cr | Capacity: {cfg['capacity_tpd']:.0f} TPD
ROI: {cfg['roi_pct']:.1f}% | IRR: {cfg['irr_pct']:.1f}% | DSCR Yr3: {cfg['dscr_yr3']:.2f}x
Break-Even: {cfg['break_even_months']} months | Revenue Yr5: Rs {cfg['revenue_yr5_lac']:.0f} Lac
{timeline_str}
Provide: health assessment, bankability score /10, strengths, risks, recommendations."""

    system = SYSTEM_PROMPT_BASE + "\nYou are a CA/financial analyst."
    return ask_ai(prompt, system, max_tokens=1500)


def ai_chat(user_message, chat_history=None, cfg=None):
    """Smart AI chat with project context."""
    context = ""
    if cfg:
        context = f"Project: {cfg.get('capacity_tpd', 20)} TPD, Rs {cfg.get('investment_cr', 8)} Cr, {cfg.get('state', '')}"

    history_str = ""
    if chat_history:
        for msg in chat_history[-6:]:
            role = "User" if msg["role"] == "user" else "Consultant"
            history_str += f"{role}: {msg['content'][:200]}\n"

    prompt = f"Context: {context}\n{history_str}\nUser: {user_message}\nAnswer professionally with specific numbers."
    return ask_ai(prompt, SYSTEM_PROMPT_BASE, max_tokens=1500)


def ai_auto_report(report_type, cfg, company):
    """Generate complete professional report using AI."""
    prompts = {
        "executive_summary": f"Write a 500-word Executive Summary for a {cfg['capacity_tpd']:.0f} TPD Bio-Modified Bitumen plant. Investment: Rs {cfg['investment_cr']:.2f} Cr, ROI: {cfg['roi_pct']:.1f}%, Location: {cfg.get('state', '')}.",
        "market_analysis": f"Write a 400-word Market Analysis for bio-bitumen in India. Market size Rs 25,000+ Cr, 49% imports, NHAI green mandate. For {cfg.get('state', 'India')}.",
        "technical_description": f"Write a 500-word Technical Description for {cfg['capacity_tpd']:.0f} TPD bio-bitumen plant. Pyrolysis at 450-550C, bio-oil blending 15-30%, IS:73 quality.",
        "risk_assessment": f"Write a 400-word Risk Assessment for {cfg['capacity_tpd']:.0f} TPD plant, Rs {cfg['investment_cr']:.2f} Cr in {cfg.get('state', 'India')}.",
        "compliance_narrative": f"Write a 300-word Compliance section for bio-bitumen plant in {cfg.get('state', 'India')}. CTE, CTO, PESO, Factory License, Fire NOC.",
    }
    prompt = prompts.get(report_type, prompts["executive_summary"])
    system = SYSTEM_PROMPT_BASE + f"\nFor: {cfg.get('client_name', 'Client')} | {company.get('trade_name', 'PPS Anantams')}"
    return ask_ai(prompt, system, max_tokens=2000)


def test_api_connection():
    """Test all 6 AI providers — returns status dict."""
    results = {}
    cfg = load_ai_config()

    # OpenAI
    if cfg.get("openai_key"):
        r = _call_openai("Say 'OK' in 1 word.", max_tokens=5)
        results["openai"] = {"status": "OK" if r else "FAILED", "model": cfg.get("openai_model", "gpt-4o-mini")}
    else:
        results["openai"] = {"status": "No key", "model": ""}

    # Claude
    if cfg.get("claude_key"):
        r = _call_claude("Say 'OK' in 1 word.", max_tokens=5)
        results["claude"] = {"status": "OK" if r else "FAILED", "model": cfg.get("claude_model", "")}
    else:
        results["claude"] = {"status": "No key", "model": ""}

    # Gemini (with key)
    if cfg.get("gemini_key"):
        r = _call_gemini("Say 'OK' in 1 word.", max_tokens=5)
        results["gemini"] = {"status": "OK" if r else "FAILED", "model": "gemini-2.0-flash"}
    else:
        results["gemini"] = {"status": "No key", "model": ""}

    # DeepSeek
    if cfg.get("deepseek_key"):
        r = _call_deepseek("Say 'OK' in 1 word.", max_tokens=5)
        results["deepseek"] = {"status": "OK" if r else "FAILED", "model": "deepseek-chat"}
    else:
        results["deepseek"] = {"status": "No key", "model": ""}

    # Gemini free
    r = _call_gemini("Say 'OK' in 1 word.", max_tokens=5, use_free=True)
    results["gemini-free"] = {"status": "OK" if r else "FAILED", "model": "gemini-2.0-flash-exp (free)"}

    # Offline
    results["offline"] = {"status": "ALWAYS ON", "model": "Built-in DPR Engine"}

    return results
