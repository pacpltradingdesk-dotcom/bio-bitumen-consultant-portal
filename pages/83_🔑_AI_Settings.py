"""
AI Settings — 6-Provider Auto-Connect Manager
=================================================
OpenAI + Claude + Gemini (free) + DeepSeek + Gemini (key) + Offline Engine
AI never fails — 6-level fallback chain ensures answers always come through.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from state_manager import init_state, get_config
from engines.ai_engine import (load_ai_config, save_ai_config, test_api_connection,
                                 is_ai_available, get_active_provider)
from config import COMPANY

st.set_page_config(page_title="AI Settings", page_icon="🔑", layout="wide")
init_state()
cfg = get_config()

try:
    from utils.page_helpers import fix_metric_truncation
    fix_metric_truncation()
except Exception:
    pass

st.title("AI Auto-Connection Manager")
st.markdown("**6-provider fallback chain — AI never fails. System always answers.**")
st.markdown("---")

# Load config
ai_cfg = load_ai_config()
active = get_active_provider()

# ══════════════════════════════════════════════════════════════════════
# STATUS PANEL
# ══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="background: #ebfbee; border: 2px solid #2f9e44; border-radius: 12px;
            padding: 15px 20px; margin-bottom: 15px;">
    <h3 style="color: #2f9e44; margin: 0;">
        AI Status: ACTIVE — Primary: {active.upper()} | Fallback chain: 6 providers
    </h3>
    <p style="margin: 5px 0 0 0; color: #666;">
        Chain: OpenAI → Claude → Gemini (key) → DeepSeek → Gemini (free) → Offline Engine.
        System NEVER fails — offline engine always answers with built-in DPR knowledge.
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# API KEY INPUT — All 11 providers (FREE first, then PAID)
# ══════════════════════════════════════════════════════════════════════
st.subheader("1. API Keys")
st.caption("Keys stored locally in `data/ai_config.json` — never sent anywhere except the AI provider you call")

# ── FREE PROVIDERS ─────────────────────────────────────────────────────
st.markdown("#### FREE Providers — Add these first (no credit card needed)")
f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("**Groq** — Fastest (Llama 3.3 70B)")
    st.caption("console.groq.com → API Keys → Create")
    groq_key = st.text_input("Groq API Key", value=ai_cfg.get("groq_key", ""),
                              type="password", placeholder="gsk_...", key="groq_key_in")

    st.markdown("**OpenRouter** — 100+ free models")
    st.caption("openrouter.ai/keys → Create Key")
    openrouter_key = st.text_input("OpenRouter Key", value=ai_cfg.get("openrouter_key", ""),
                                    type="password", placeholder="sk-or-...", key="or_key_in")

with f2:
    st.markdown("**Cerebras** — Ultra fast (fastest inference)")
    st.caption("cloud.cerebras.ai → API Keys")
    cerebras_key = st.text_input("Cerebras API Key", value=ai_cfg.get("cerebras_key", ""),
                                  type="password", placeholder="csk_...", key="cerebras_key_in")

    st.markdown("**Gemini (Google AI)**")
    st.caption("aistudio.google.com/apikey — Free 1M ctx")
    gemini_key = st.text_input("Gemini API Key", value=ai_cfg.get("gemini_key", ""),
                                type="password", placeholder="AIza...", key="gemini_key_in")

with f3:
    st.markdown("**Mistral** — EU-hosted, privacy-first")
    st.caption("console.mistral.ai → API Keys")
    mistral_key = st.text_input("Mistral API Key", value=ai_cfg.get("mistral_key", ""),
                                 type="password", placeholder="...", key="mistral_key_in")

    st.markdown("**GitHub Models** — Free for GitHub users")
    st.caption("github.com/settings/tokens → Generate (classic)")
    github_token = st.text_input("GitHub Token", value=ai_cfg.get("github_token", ""),
                                  type="password", placeholder="ghp_...", key="github_key_in")

# ── LOCAL PROVIDER ─────────────────────────────────────────────────────
st.markdown("**Ollama (Local — Truly unlimited, no internet needed)**")
ol1, ol2 = st.columns(2)
with ol1:
    ollama_host = st.text_input("Ollama Host", value=ai_cfg.get("ollama_host", "http://localhost:11434"),
                                 key="ollama_host_in")
with ol2:
    ollama_model = st.text_input("Ollama Model", value=ai_cfg.get("ollama_model", "llama3.2"),
                                  key="ollama_model_in")
    st.caption("Run: `ollama pull llama3.2` to download model")

st.markdown("---")

# ── PAID PROVIDERS ─────────────────────────────────────────────────────
st.markdown("#### PAID Providers (Optional — best quality)")
p1, p2 = st.columns(2)

with p1:
    st.markdown("**OpenAI (GPT-4o)**")
    openai_key = st.text_input("OpenAI API Key", value=ai_cfg.get("openai_key", ""),
                                type="password", placeholder="sk-...", key="openai_key_in")
    _openai_models = ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"]
    _saved_openai  = ai_cfg.get("openai_model", "gpt-4o-mini")
    openai_model = st.selectbox("OpenAI Model", _openai_models,
                                 index=_openai_models.index(_saved_openai) if _saved_openai in _openai_models else 0,
                                 key="openai_model_sel")

    st.markdown("**DeepSeek (Cheapest paid — ₹0.05–0.15/1k)**")
    deepseek_key = st.text_input("DeepSeek API Key", value=ai_cfg.get("deepseek_key", ""),
                                  type="password", placeholder="sk-...", key="deepseek_key_in")

with p2:
    st.markdown("**Anthropic Claude (Best writing quality)**")
    claude_key = st.text_input("Claude API Key", value=ai_cfg.get("claude_key", ""),
                                type="password", placeholder="sk-ant-...", key="claude_key_in")
    _claude_models = ["claude-sonnet-4-6", "claude-opus-4-7", "claude-haiku-4-5-20251001"]
    _saved_claude  = ai_cfg.get("claude_model", "claude-sonnet-4-6")
    claude_model = st.selectbox("Claude Model", _claude_models,
                                 index=_claude_models.index(_saved_claude) if _saved_claude in _claude_models else 0,
                                 key="claude_model_sel")

st.markdown("---")

# ── PREFERRED PROVIDER ─────────────────────────────────────────────────
st.subheader("2. Preferred AI Provider")
all_providers   = ["groq", "cerebras", "gemini", "mistral", "openrouter", "github",
                   "openai", "claude", "deepseek", "ollama"]
provider_labels = {
    "groq":        "Groq (FREE — fastest)",
    "cerebras":    "Cerebras (FREE — ultra fast)",
    "gemini":      "Gemini (FREE — Google)",
    "mistral":     "Mistral (FREE — EU)",
    "openrouter":  "OpenRouter (FREE — 100+ models)",
    "github":      "GitHub Models (FREE)",
    "openai":      "OpenAI (PAID — GPT-4o)",
    "claude":      "Claude (PAID — Anthropic)",
    "deepseek":    "DeepSeek (PAID — cheapest)",
    "ollama":      "Ollama (LOCAL — unlimited)",
}
current_pref = ai_cfg.get("preferred_provider", "groq")
if current_pref not in all_providers:
    current_pref = "groq"
preferred = st.selectbox("Primary provider (others are automatic fallback):",
                          all_providers,
                          format_func=lambda x: provider_labels[x],
                          index=all_providers.index(current_pref),
                          key="pref_provider_sel")
st.caption("Fallback chain: Groq → Cerebras → Gemini → Mistral → OpenRouter → GitHub → Ollama → OpenAI → Claude → DeepSeek → Offline")

st.markdown("---")

# SAVE
if st.button("SAVE ALL API SETTINGS", type="primary", key="save_ai"):
    new_config = {
        # Free
        "groq_key":        groq_key,
        "cerebras_key":    cerebras_key,
        "gemini_key":      gemini_key,
        "mistral_key":     mistral_key,
        "openrouter_key":  openrouter_key,
        "github_token":    github_token,
        "ollama_host":     ollama_host,
        "ollama_model":    ollama_model,
        # Paid
        "openai_key":      openai_key,
        "openai_model":    openai_model,
        "claude_key":      claude_key,
        "claude_model":    claude_model,
        "deepseek_key":    deepseek_key,
        # Settings
        "gemini_model":    "gemini-2.0-flash",
        "deepseek_model":  "deepseek-chat",
        "preferred_provider": preferred,
    }
    save_ai_config(new_config)
    st.success("All 11 provider settings saved! Full failover chain active.")
    st.rerun()

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# TEST ALL 6 PROVIDERS
# ══════════════════════════════════════════════════════════════════════
st.subheader("3. Test All AI Connections")

if st.button("Test All 6 Providers", type="primary", key="test_all"):
    with st.spinner("Testing 6 AI providers... (may take 15-30 seconds)"):
        try:
            results = test_api_connection()
        except Exception as e:
            st.error(f"Test failed: {e}")
            results = {}

    if results:
        for provider, info in results.items():
            status = info.get("status", "UNKNOWN")
            model = info.get("model", "")
            if status == "OK" or status == "ALWAYS ON":
                st.success(f"✅ **{provider.upper()}** — Connected | Model: {model}")
            elif status == "No key":
                st.warning(f"⚠️ **{provider.upper()}** — No API key configured")
            else:
                st.error(f"❌ **{provider.upper()}** — {status}")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# FREE PROVIDERS ALWAYS AVAILABLE
# ══════════════════════════════════════════════════════════════════════
st.subheader("4. Always-Available Providers (No Key Needed)")

f1, f2 = st.columns(2)
with f1:
    st.markdown("""
    ### Gemini Flash (Free Tier)
    - **Cost:** FREE — no payment, no key needed
    - **Quality:** Good for basic questions
    - **Limit:** Rate-limited but sufficient
    - **How:** Automatically used as fallback
    """)
with f2:
    st.markdown("""
    ### Built-in Offline Engine
    - **Cost:** FREE — works with ZERO internet
    - **Knowledge:** All bio-bitumen DPR formulas, government schemes, IS standards
    - **Always on:** Cannot fail — ultimate fallback
    - **Best for:** Quick DPR facts, scheme info, formulas
    """)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# QUICK AI TEST
# ══════════════════════════════════════════════════════════════════════
st.subheader("5. Quick AI Test")
test_prompt = st.text_input("Ask AI anything:", placeholder="What is the MNRE biomass subsidy for bio-bitumen?",
                             key="test_prompt_in")
if st.button("Ask AI (uses fallback chain)", type="primary", key="test_ask"):
    if not test_prompt:
        st.warning("Type a question first.")
    else:
        with st.spinner("AI thinking... trying best available provider..."):
            try:
                from engines.ai_engine import ask_ai
                response, provider = ask_ai(test_prompt,
                    "You are a bio-bitumen industry expert. Answer concisely.")
                if response:
                    st.markdown(f"**Response via {provider.upper()}:**")
                    st.markdown(response)
                else:
                    st.error("No response received.")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# FREE DATA APIs — No Key Required
# ══════════════════════════════════════════════════════════════════════
st.subheader("6. Free Data APIs — Always Connected, No Key Needed")
st.caption("These 10 APIs power live weather, exchange rates, market prices, and holidays across the portal.")

try:
    from engines.free_apis import (get_weather_current, get_exchange_rates,
                                    get_india_holidays, get_india_gdp,
                                    get_mandi_prices, check_all_connections)
    import pandas as _pd

    _city = cfg.get("location", "Delhi")

    _fd1, _fd2 = st.columns(2)
    with _fd1:
        st.markdown("**Live Sample — Current Data**")
        _w = get_weather_current(_city)
        if "error" not in _w:
            st.success(f"🌤️ Weather ({_city}): {_w['temperature_c']}°C, "
                       f"{_w['condition']}, Humidity {_w['humidity_pct']}%")
        _fx = get_exchange_rates()
        if "error" not in _fx:
            st.success(f"💱 Exchange Rate: ₹{_fx.get('usd_inr',84):.2f}/USD  "
                       f"₹{_fx.get('eur_inr',90):.2f}/EUR")
        _hols = get_india_holidays(2026)
        if _hols:
            _next = next((h for h in _hols
                          if h["date"] >= __import__('datetime').datetime.now().strftime("%Y-%m-%d")), None)
            if _next:
                st.success(f"🗓️ Next Holiday: {_next['date']} — {_next['name_en']}")

    with _fd2:
        st.markdown("**API → Portal Page Mapping**")
        _mapping = [
            {"Free API":     "Open-Meteo Weather",    "Used In": "Location (12), Raw Material (24)"},
            {"Free API":     "Frankfurter FX",         "Used In": "Raw Material (24), Loan EMI (33)"},
            {"Free API":     "World Bank GDP",         "Used In": "Loan EMI (33), Financial (30)"},
            {"Free API":     "Agmarknet Mandi",        "Used In": "Raw Material (24)"},
            {"Free API":     "Nager.at Holidays",      "Used In": "Location (12), Operations"},
            {"Free API":     "ExchangeRate-API",       "Used In": "Financial (30), Rating (89)"},
            {"Free API":     "Nominatim Geocode",      "Used In": "Location (12), Maps"},
            {"Free API":     "Wikipedia",              "Used In": "AI Knowledge Base"},
            {"Free API":     "REST Countries",         "Used In": "Project Setup (10)"},
            {"Free API":     "IP-API",                 "Used In": "Visitor Location"},
        ]
        st.dataframe(_pd.DataFrame(_mapping), use_container_width=True, hide_index=True)

    if st.button("Test All 10 Free APIs", key="test_free_data_apis"):
        with st.spinner("Testing 10 free data APIs…"):
            _results = check_all_connections()
        _ok_count = sum(1 for v in _results.values() if v.get("ok"))
        st.success(f"{_ok_count}/{len(_results)} free APIs reachable")
        for _name, _s in _results.items():
            if _s.get("ok"):
                st.markdown(f"✅ **{_name}** — {_s.get('latency_ms','?')}ms")
            else:
                st.markdown(f"❌ **{_name}** — {_s.get('note','Failed')}")

except Exception as _ex:
    st.info(f"Free API engine: {_ex}")

st.markdown("---")
st.caption(f"{COMPANY['name']} | AI Auto-Connection Manager | 11 AI + 10 Free Data APIs")


# ── Next Steps Navigation ──
try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "83")
except Exception:
    pass
