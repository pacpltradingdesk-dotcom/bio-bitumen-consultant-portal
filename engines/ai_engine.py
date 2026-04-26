"""
AI Engine — 11-Provider Auto-Fallback Chain with Health Tracking
=================================================================
FREE providers (no credit card needed):
  1. Groq          console.groq.com          Llama 3.3 70B — fastest
  2. Cerebras      cloud.cerebras.ai          Even faster than Groq
  3. Gemini (key)  aistudio.google.com        1M context, multimodal
  4. Gemini (free) No key needed              Limited but always on
  5. Mistral       console.mistral.ai         EU-hosted, privacy
  6. OpenRouter    openrouter.ai/keys         100+ free $0 models
  7. GitHub Models github.com/marketplace     Free for GitHub users
  8. Ollama        ollama.com (local)         Truly unlimited, offline

PAID (optional, best quality):
  9. OpenAI        platform.openai.com        GPT-4o-mini
 10. Claude        console.anthropic.com      Best writing quality
 11. DeepSeek      platform.deepseek.com      Cheapest paid (~₹0.10/1k)

ALWAYS ON:
 12. Built-in Offline Engine                  Zero internet needed

Features: persistent HTTP session, cooldown per provider,
          rate-limit detection (429), auto-recovery.
API keys stored in: data/ai_config.json (gitignored)
"""
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
import requests as _requests

# ── Persistent HTTP session (one connection pool, no reconnect) ───────
_session = _requests.Session()
_adapter = _requests.adapters.HTTPAdapter(
    pool_connections=10, pool_maxsize=10, max_retries=0
)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)

# ── Per-provider health / cooldown tracking ───────────────────────────
_health_lock = threading.Lock()
_health: dict = {}  # name → {"fails": int, "cooldown_until": datetime|None}


def _is_available(name: str) -> bool:
    with _health_lock:
        h = _health.get(name, {})
        until = h.get("cooldown_until")
        return until is None or datetime.now() >= until


def _mark_failed(name: str, base_cd: int = 60):
    with _health_lock:
        h = _health.setdefault(name, {"fails": 0, "cooldown_until": None})
        h["fails"] += 1
        cd = min(base_cd * (2 ** (h["fails"] - 1)), 1800)
        h["cooldown_until"] = datetime.now() + timedelta(seconds=cd)


def _mark_ok(name: str):
    with _health_lock:
        _health[name] = {"fails": 0, "cooldown_until": None}

CONFIG_PATH = Path(__file__).parent.parent / "data" / "ai_config.json"

# ══════════════════════════════════════════════════════════════════════
# CONFIG MANAGEMENT
# ══════════════════════════════════════════════════════════════════════
_CONFIG_DEFAULTS = {
    # Paid providers (optional)
    "openai_key": "", "claude_key": "", "deepseek_key": "",
    # Free providers (get these first)
    "groq_key": "",        # console.groq.com
    "cerebras_key": "",    # cloud.cerebras.ai
    "gemini_key": "",      # aistudio.google.com/apikey
    "mistral_key": "",     # console.mistral.ai
    "openrouter_key": "",  # openrouter.ai/keys
    "github_token": "",    # github.com/settings/tokens
    # Local (no key needed)
    "ollama_host": "http://localhost:11434",
    "ollama_model": "llama3.2",
    # Settings
    "preferred_provider": "groq",
    "openai_model": "gpt-4o-mini",
    "claude_model": "claude-sonnet-4-20250514",
    "gemini_model": "gemini-2.5-flash",
    "deepseek_model": "deepseek-chat",
}


def load_ai_config():
    """Load API keys from secure config file."""
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            # Merge with defaults so new keys always present
            return {**_CONFIG_DEFAULTS, **data}
        except Exception:
            pass
    return dict(_CONFIG_DEFAULTS)


def save_ai_config(config):
    """Save API keys to secure config file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")


def is_ai_available():
    """Always True — offline engine is the final fallback."""
    return True


def get_active_provider():
    """Return the best-available provider name."""
    cfg = load_ai_config()
    # Free providers first
    for name, key_field in [
        ("groq",         "groq_key"),
        ("cerebras",     "cerebras_key"),
        ("gemini",       "gemini_key"),
        ("mistral",      "mistral_key"),
        ("openrouter",   "openrouter_key"),
        ("github",       "github_token"),
        # Paid
        ("openai",       "openai_key"),
        ("claude",       "claude_key"),
        ("deepseek",     "deepseek_key"),
    ]:
        if cfg.get(key_field):
            return name
    return "gemini-free"  # No-key fallback


def get_ai_provider_summary():
    """Return list of dicts describing each provider for the settings UI."""
    cfg = load_ai_config()
    providers = [
        # (display_name, internal_name, key_field, tier, signup_url, note)
        ("Groq",          "groq",       "groq_key",       "FREE",  "console.groq.com",            "Llama 3.3 70B — fastest free LLM"),
        ("Cerebras",      "cerebras",   "cerebras_key",   "FREE",  "cloud.cerebras.ai",           "Even faster than Groq"),
        ("Gemini (key)",  "gemini",     "gemini_key",     "FREE",  "aistudio.google.com/apikey",  "1M context, multimodal, big quota"),
        ("Gemini (free)", "gemini-free","",               "FREE",  "No signup needed",            "No key — limited requests/day"),
        ("Mistral",       "mistral",    "mistral_key",    "FREE",  "console.mistral.ai",          "EU-hosted, privacy-focused"),
        ("OpenRouter",    "openrouter", "openrouter_key", "FREE",  "openrouter.ai/keys",          "100+ free $0 models as backup"),
        ("GitHub Models", "github",     "github_token",   "FREE",  "github.com/marketplace/models","Free for any GitHub account"),
        ("Ollama (local)","ollama",     "",               "LOCAL", "ollama.com",                  "Runs on your PC — truly unlimited"),
        ("OpenAI",        "openai",     "openai_key",     "PAID",  "platform.openai.com",         "GPT-4o-mini (best quality/speed)"),
        ("Claude",        "claude",     "claude_key",     "PAID",  "console.anthropic.com",       "Best for writing & long docs"),
        ("DeepSeek",      "deepseek",   "deepseek_key",   "PAID",  "platform.deepseek.com",       "Cheapest paid (~Rs 0.10/1k calls)"),
    ]
    result = []
    for disp, name, key_field, tier, url, note in providers:
        has_key = bool(cfg.get(key_field)) if key_field else (name in ("gemini-free", "ollama"))
        result.append({
            "display": disp, "name": name, "key_field": key_field,
            "tier": tier, "url": url, "note": note,
            "has_key": has_key,
            "available": _is_available(name),
        })
    return result


# ── Shared helper ─────────────────────────────────────────────────────
def _openai_compat(name, url, api_key, model, prompt, system_prompt,
                   max_tokens, timeout=30, extra_headers=None):
    """Call any OpenAI-compatible chat endpoint using the shared session."""
    if not _is_available(name):
        return None
    try:
        headers = {"Authorization": f"Bearer {api_key}",
                   "Content-Type": "application/json"}
        if extra_headers:
            headers.update(extra_headers)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = _session.post(url, headers=headers, timeout=timeout,
                             json={"model": model, "messages": messages,
                                   "max_tokens": max_tokens, "temperature": 0.7})
        if resp.status_code == 429:
            _mark_failed(name, base_cd=300)
            return None
        if resp.status_code in (401, 403):
            _mark_failed(name, base_cd=3600)
            return None
        data = resp.json()
        if "choices" in data:
            _mark_ok(name)
            return data["choices"][0]["message"]["content"]
        return None
    except Exception:
        _mark_failed(name)
        return None


# ══════════════════════════════════════════════════════════════════════
# OPENAI API
# ══════════════════════════════════════════════════════════════════════
def _call_openai(prompt, system_prompt="", max_tokens=2000):
    """Call OpenAI API (GPT-4o-mini)."""
    cfg = load_ai_config()
    api_key = cfg.get("openai_key", "")
    if not api_key:
        return None
    return _openai_compat("openai", "https://api.openai.com/v1/chat/completions",
                          api_key, cfg.get("openai_model", "gpt-4o-mini"),
                          prompt, system_prompt, max_tokens, timeout=60)


# ══════════════════════════════════════════════════════════════════════
# CLAUDE API
# ══════════════════════════════════════════════════════════════════════
def _call_claude(prompt, system_prompt="", max_tokens=2000):
    """Call Anthropic Claude API."""
    cfg = load_ai_config()
    api_key = cfg.get("claude_key", "")
    model = cfg.get("claude_model", "claude-sonnet-4-20250514")
    if not api_key or not _is_available("claude"):
        return None
    try:
        headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01",
                   "Content-Type": "application/json"}
        body = {"model": model, "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]}
        if system_prompt:
            body["system"] = system_prompt
        resp = _session.post("https://api.anthropic.com/v1/messages",
                             headers=headers, timeout=60, json=body)
        if resp.status_code == 429:
            _mark_failed("claude", 300); return None
        data = resp.json()
        if "content" in data:
            _mark_ok("claude")
            return data["content"][0]["text"]
        return None
    except Exception:
        _mark_failed("claude"); return None


# ══════════════════════════════════════════════════════════════════════
# GEMINI API (Google AI — free key at aistudio.google.com/apikey)
# ══════════════════════════════════════════════════════════════════════
def _call_gemini(prompt, system_prompt="", max_tokens=2000, use_free=False):
    """Call Google Gemini via OpenAI-compat endpoint (key) or native REST (free)."""
    cfg = load_ai_config()
    api_key = cfg.get("gemini_key", "")
    model = cfg.get("gemini_model", "gemini-2.5-flash")
    tag = "gemini" if api_key and not use_free else "gemini-free"

    if not _is_available(tag):
        return None
    if not api_key and not use_free:
        return None

    try:
        if api_key and not use_free:
            # OpenAI-compat path — faster parsing
            result = _openai_compat(
                tag,
                "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                api_key, model, prompt, system_prompt, max_tokens, timeout=30)
            return result
        else:
            # Key-free native path
            url = ("https://generativelanguage.googleapis.com/v1beta/models/"
                   "gemini-2.0-flash-exp:generateContent")
            full = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            body = {"contents": [{"role": "user", "parts": [{"text": full}]}],
                    "generationConfig": {"maxOutputTokens": max_tokens}}
            resp = _session.post(url, headers={"Content-Type": "application/json"},
                                 timeout=30, json=body)
            if resp.status_code == 429:
                _mark_failed(tag, 300); return None
            data = resp.json()
            if "candidates" in data:
                _mark_ok(tag)
                return data["candidates"][0]["content"]["parts"][0]["text"]
            return None
    except Exception:
        _mark_failed(tag); return None


# ══════════════════════════════════════════════════════════════════════
# DEEPSEEK (paid but ultra cheap — platform.deepseek.com)
# ══════════════════════════════════════════════════════════════════════
def _call_deepseek(prompt, system_prompt="", max_tokens=2000):
    cfg = load_ai_config()
    api_key = cfg.get("deepseek_key", "")
    if not api_key:
        return None
    return _openai_compat("deepseek", "https://api.deepseek.com/v1/chat/completions",
                          api_key, "deepseek-chat", prompt, system_prompt, max_tokens, timeout=60)


# ══════════════════════════════════════════════════════════════════════
# GROQ — FREE  (console.groq.com — Llama 3.3 70B, fastest)
# ══════════════════════════════════════════════════════════════════════
def _call_groq(prompt, system_prompt="", max_tokens=2000):
    cfg = load_ai_config()
    api_key = cfg.get("groq_key", "")
    if not api_key:
        return None
    return _openai_compat("groq", "https://api.groq.com/openai/v1/chat/completions",
                          api_key, "llama-3.3-70b-versatile",
                          prompt, system_prompt, max_tokens, timeout=30)


# ══════════════════════════════════════════════════════════════════════
# CEREBRAS — FREE  (cloud.cerebras.ai — even faster than Groq)
# ══════════════════════════════════════════════════════════════════════
def _call_cerebras(prompt, system_prompt="", max_tokens=2000):
    cfg = load_ai_config()
    api_key = cfg.get("cerebras_key", "")
    if not api_key:
        return None
    return _openai_compat("cerebras", "https://api.cerebras.ai/v1/chat/completions",
                          api_key, "llama-3.3-70b",
                          prompt, system_prompt, max_tokens, timeout=30)


# ══════════════════════════════════════════════════════════════════════
# MISTRAL — FREE tier  (console.mistral.ai — EU privacy)
# ══════════════════════════════════════════════════════════════════════
def _call_mistral(prompt, system_prompt="", max_tokens=2000):
    cfg = load_ai_config()
    api_key = cfg.get("mistral_key", "")
    if not api_key:
        return None
    return _openai_compat("mistral", "https://api.mistral.ai/v1/chat/completions",
                          api_key, "mistral-small-latest",
                          prompt, system_prompt, max_tokens, timeout=30)


# ══════════════════════════════════════════════════════════════════════
# OPENROUTER — FREE $0 models  (openrouter.ai/keys)
# ══════════════════════════════════════════════════════════════════════
def _call_openrouter(prompt, system_prompt="", max_tokens=2000):
    cfg = load_ai_config()
    api_key = cfg.get("openrouter_key", "")
    if not api_key:
        return None
    return _openai_compat(
        "openrouter", "https://openrouter.ai/api/v1/chat/completions",
        api_key, "meta-llama/llama-3.3-70b-instruct:free",
        prompt, system_prompt, max_tokens, timeout=45,
        extra_headers={"HTTP-Referer": "https://biobitumen.yuga.in",
                       "X-Title": "Bio-Bitumen Consultant Portal"})


# ══════════════════════════════════════════════════════════════════════
# GITHUB MODELS — FREE for GitHub users  (github.com/marketplace/models)
# ══════════════════════════════════════════════════════════════════════
def _call_github_models(prompt, system_prompt="", max_tokens=2000):
    cfg = load_ai_config()
    api_key = cfg.get("github_token", "")
    if not api_key:
        return None
    return _openai_compat(
        "github", "https://models.inference.ai.azure.com/chat/completions",
        api_key, "gpt-4o-mini",
        prompt, system_prompt, max_tokens, timeout=45)


# ══════════════════════════════════════════════════════════════════════
# OLLAMA — LOCAL  (ollama.com — truly unlimited, offline)
# Install: https://ollama.com  |  then: ollama pull llama3.2
# ══════════════════════════════════════════════════════════════════════
def _call_ollama(prompt, system_prompt="", max_tokens=2000):
    cfg = load_ai_config()
    host = cfg.get("ollama_host", "http://localhost:11434").rstrip("/")
    model = cfg.get("ollama_model", "llama3.2")
    if not _is_available("ollama"):
        return None
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = _session.post(
            f"{host}/api/chat",
            json={"model": model, "messages": messages, "stream": False,
                  "options": {"num_predict": max_tokens}},
            timeout=120)
        if resp.status_code == 200:
            _mark_ok("ollama")
            return resp.json().get("message", {}).get("content")
        _mark_failed("ollama", 30)
        return None
    except Exception:
        _mark_failed("ollama", 30)
        return None


# ══════════════════════════════════════════════════════════════════════
# BUILT-IN OFFLINE ENGINE (always works, zero internet)
# ══════════════════════════════════════════════════════════════════════
def _call_offline(prompt, system_prompt="", max_tokens=2000):  # system_prompt/max_tokens kept for interface parity
    """Built-in offline knowledge engine for bio-bitumen DPR questions."""
    _ = system_prompt, max_tokens  # interface parity with other providers
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
def _dispatch(provider, prompt, system_prompt, max_tokens):
    """Call a single provider by name. Returns text or None."""
    if provider == "groq":          return _call_groq(prompt, system_prompt, max_tokens)
    if provider == "cerebras":      return _call_cerebras(prompt, system_prompt, max_tokens)
    if provider == "gemini":        return _call_gemini(prompt, system_prompt, max_tokens, use_free=False)
    if provider == "gemini-free":   return _call_gemini(prompt, system_prompt, max_tokens, use_free=True)
    if provider == "mistral":       return _call_mistral(prompt, system_prompt, max_tokens)
    if provider == "openrouter":    return _call_openrouter(prompt, system_prompt, max_tokens)
    if provider == "github":        return _call_github_models(prompt, system_prompt, max_tokens)
    if provider == "ollama":        return _call_ollama(prompt, system_prompt, max_tokens)
    if provider == "openai":        return _call_openai(prompt, system_prompt, max_tokens)
    if provider == "claude":        return _call_claude(prompt, system_prompt, max_tokens)
    if provider == "deepseek":      return _call_deepseek(prompt, system_prompt, max_tokens)
    if provider == "offline":       return _call_offline(prompt, system_prompt, max_tokens)
    return None


# Default chain — free providers first, paid as premium fallback, offline always last
_DEFAULT_CHAIN = [
    "groq", "cerebras", "gemini", "mistral", "openrouter",
    "github", "ollama", "gemini-free",
    "openai", "claude", "deepseek",
    "offline",
]


def ask_ai(prompt, system_prompt="", max_tokens=2000):
    """
    Ask AI using best available provider. Auto-fails over through all 11 providers.
    Free providers tried first; offline engine is the ultimate fallback.
    Returns: (response_text, provider_name)
    """
    cfg = load_ai_config()
    pref = cfg.get("preferred_provider", "groq")

    # Put preferred provider at front of chain
    chain = [pref] + [p for p in _DEFAULT_CHAIN if p != pref]

    for provider in chain:
        try:
            result = _dispatch(provider, prompt, system_prompt, max_tokens)
            if result and len(result) > 10:
                return result, provider
        except Exception:
            continue

    return _call_offline(prompt, system_prompt, max_tokens), "offline"


# ══════════════════════════════════════════════════════════════════════
# SPECIALIZED AI FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_BASE = """You are BIO-BITUMEN PROJECT ASSISTANT for PPS Anantams Corporation,
specializing in Bio-Modified Bitumen plant setup in India. You represent Prince Pratap Shah — 25 years hands-on in the bitumen industry (since 2001), MCA-registered Director since 2009 (DIN 06680837), founder of Omnipotent Industries Limited (BSE-listed via IPO 2020, CIN L74999MH2016PLC285902 — 3 plants, 11 JVs), founder of PPS Anantams Corporation Pvt Ltd (CIN U46632GJ2019PTC110676, 2019), proprietor of Global Enterprises (AMT Techno Worldwide Marketing Rep, 2015-17) and PS Enterprises (1.2 Lakh MT UK bitumen contract, 2023). 9 plants commissioned with 9+ documented plant innovations.

RULES YOU MUST FOLLOW:
1. Numbers must be real — from formulas, market rates, or IS standards. Never invent.
2. If a value is missing, ASK for it. Never assume.
3. Always tell the user what comes next: "Next I can do: [Option A] / [Option B]"
4. Never suggest removing legally mandatory items (IS 2825, IS 14489, NBC 2016, CPCB).
5. Never say project is "guaranteed profitable" — say "projections show..."

YOUR EXPERTISE:
- Pyrolysis technology (450-550°C, bio-oil 32%, bio-char 28%, syngas 22%)
- Indian Standards (IS 73, IS 2825, IS 14489, NBC 2016, Factories Act)
- Financial modelling, DPR writing, BOQ preparation
- 15 plant zones (A-O): Gate to Maintenance, 82 equipment items
- India bitumen market: ₹45,750/T VG30, NHAI green mandate
- Government schemes: MNRE, CGTMSE, State MSME subsidies

Format: Use headings, bullet points, tables. Be specific with numbers."""


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

    trade = company.get("trade_name", "") if company else ""
    system = SYSTEM_PROMPT_BASE + f"\nYou are writing a bank-ready DPR section for {trade}."
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


# ══════════════════════════════════════════════════════════════════════
# AI ORCHESTRATOR — Routes questions to the best specialist AI
# ══════════════════════════════════════════════════════════════════════
def ai_orchestrator(question, cfg=None):
    """Smart orchestrator that routes questions to the best AI specialist.

    Routing logic:
    - Financial/DPR/cost questions → DeepSeek (maths) or OpenAI (analysis)
    - Live price/market questions → Gemini (web search) or offline engine
    - Policy/govt/scheme questions → Gemini (web search) or offline engine
    - Document/writing questions → Claude (best writing) or OpenAI
    - General questions → best available via fallback chain

    Returns: (answer, provider, specialist_role)
    """
    q = question.lower()

    # Determine specialist role
    if any(w in q for w in ['cost', 'price', 'roi', 'irr', 'dscr', 'break-even', 'profit',
                             'investment', 'emi', 'loan', 'financial', 'margin', 'revenue']):
        role = "financial_analyst"
        system = ("You are a chartered accountant and financial analyst for bio-bitumen DPR. "
                  "Give specific numbers, formulas, and calculations. Use Indian accounting standards.")
        preferred_chain = ["deepseek", "groq", "cerebras", "openai", "gemini",
                           "mistral", "openrouter", "claude", "gemini-free", "offline"]

    elif any(w in q for w in ['write', 'draft', 'document', 'dpr', 'report', 'proposal',
                                'letter', 'email', 'application']):
        role = "document_writer"
        system = ("You are a professional DPR document writer. Write bank-ready, formal English. "
                  "Use proper formatting, headings, and specific project data.")
        preferred_chain = ["claude", "openai", "groq", "cerebras", "gemini",
                           "mistral", "deepseek", "gemini-free", "offline"]

    elif any(w in q for w in ['policy', 'scheme', 'mnre', 'government', 'subsidy', 'tender',
                                'nhai', 'regulation', 'compliance', 'license']):
        role = "policy_advisor"
        system = ("You are an expert on Indian government policies for bio-energy and infrastructure. "
                  "Reference specific schemes, portal URLs, and application procedures.")
        preferred_chain = ["gemini", "groq", "cerebras", "openrouter", "mistral",
                           "github", "openai", "gemini-free", "offline"]

    elif any(w in q for w in ['bitumen price', 'crude oil', 'market', 'live', 'current',
                                'today', 'latest', 'iocl']):
        role = "market_analyst"
        system = ("You are a commodities market analyst for Indian bitumen industry. "
                  "Give current price estimates with sources and methodology.")
        preferred_chain = ["gemini", "groq", "cerebras", "openrouter", "gemini-free",
                           "openai", "offline"]

    elif any(w in q for w in ['process', 'pyrolysis', 'technology', 'reactor', 'yield',
                                'temperature', 'equipment', 'drawing']):
        role = "technical_expert"
        system = ("You are a chemical engineer specializing in biomass pyrolysis and bio-bitumen. "
                  "Reference IS standards, CSIR-CRRI specs, and specific equipment parameters.")
        preferred_chain = ["groq", "cerebras", "openai", "claude", "deepseek",
                           "gemini", "mistral", "gemini-free", "offline"]
    else:
        role = "general_consultant"
        system = SYSTEM_PROMPT_BASE
        preferred_chain = None  # Use default chain

    # Add project context
    context = ""
    if cfg:
        context = (f"\nProject: {cfg.get('capacity_tpd', 20):.0f} TPD, Rs {cfg.get('investment_cr', 8):.2f} Cr, "
                   f"{cfg.get('state', 'Maharashtra')}, ROI: {cfg.get('roi_pct', 20):.1f}%")
        system += context

    # Route to specialist chain
    if preferred_chain:
        for provider in preferred_chain:
            try:
                result = _dispatch(provider, question, system, 2000)
                if result and len(result) > 10:
                    return result, provider, role
            except Exception:
                continue
        return _call_offline(question, system), "offline", role
    else:
        result, provider = ask_ai(question, system)
        return result, provider, role


def test_api_connection():
    """Test all providers — returns status dict. Only tests those with keys configured."""
    cfg = load_ai_config()
    ping = "Say OK"

    PROVIDERS = [
        # (name, key_field, model_label, call_fn)
        ("groq",       "groq_key",       "llama-3.3-70b-versatile",      lambda: _call_groq(ping, max_tokens=5)),
        ("cerebras",   "cerebras_key",   "llama-3.3-70b",                lambda: _call_cerebras(ping, max_tokens=5)),
        ("gemini",     "gemini_key",     "gemini-2.5-flash",             lambda: _call_gemini(ping, max_tokens=5)),
        ("mistral",    "mistral_key",    "mistral-small-latest",         lambda: _call_mistral(ping, max_tokens=5)),
        ("openrouter", "openrouter_key", "llama-3.3-70b:free",           lambda: _call_openrouter(ping, max_tokens=5)),
        ("github",     "github_token",   "gpt-4o-mini",                  lambda: _call_github_models(ping, max_tokens=5)),
        ("openai",     "openai_key",     cfg.get("openai_model","gpt-4o-mini"), lambda: _call_openai(ping, max_tokens=5)),
        ("claude",     "claude_key",     cfg.get("claude_model",""),     lambda: _call_claude(ping, max_tokens=5)),
        ("deepseek",   "deepseek_key",   "deepseek-chat",                lambda: _call_deepseek(ping, max_tokens=5)),
    ]
    results = {}
    for name, key_field, model_label, fn in PROVIDERS:
        if cfg.get(key_field):
            r = fn()
            results[name] = {"status": "OK" if r else "FAILED", "model": model_label}
        else:
            results[name] = {"status": "No key", "model": model_label}

    # Always-on providers
    r = _call_gemini(ping, max_tokens=5, use_free=True)
    results["gemini-free"] = {"status": "OK" if r else "FAILED", "model": "gemini-2.0-flash-exp"}

    r = _call_ollama(ping, max_tokens=5)
    results["ollama"] = {
        "status": "OK" if r else "Not running (install from ollama.com)",
        "model": cfg.get("ollama_model", "llama3.2")
    }
    results["offline"] = {"status": "ALWAYS ON", "model": "Built-in DPR Engine"}
    return results
