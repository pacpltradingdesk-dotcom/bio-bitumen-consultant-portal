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
# API KEY INPUT — All 4 paid/free providers
# ══════════════════════════════════════════════════════════════════════
st.subheader("1. API Keys")
st.caption("Keys stored locally in `data/ai_config.json` — never uploaded anywhere except the AI provider")

c1, c2 = st.columns(2)
with c1:
    st.markdown("### OpenAI (GPT-4o)")
    st.markdown("[Get key](https://platform.openai.com/api-keys) — Free tier, then pay-per-use")
    openai_key = st.text_input("OpenAI API Key", value=ai_cfg.get("openai_key", ""),
                                type="password", placeholder="sk-...", key="openai_key_in")
    openai_model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
                                 index=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"].index(
                                     ai_cfg.get("openai_model", "gpt-4o-mini")))

    st.markdown("### Gemini (Google AI)")
    st.markdown("[Get FREE key](https://aistudio.google.com/apikey) — Free tier, no payment needed")
    gemini_key = st.text_input("Gemini API Key", value=ai_cfg.get("gemini_key", ""),
                                type="password", placeholder="AIza...", key="gemini_key_in")
    st.caption("Without key: Gemini Flash free tier works for basic questions. With key: higher limits.")

with c2:
    st.markdown("### Anthropic Claude")
    st.markdown("[Get key](https://console.anthropic.com/settings/keys)")
    claude_key = st.text_input("Claude API Key", value=ai_cfg.get("claude_key", ""),
                                type="password", placeholder="sk-ant-...", key="claude_key_in")
    claude_model = st.selectbox("Model", ["claude-sonnet-4-20250514", "claude-haiku-4-5-20251001"],
                                 index=0, key="claude_model_sel")

    st.markdown("### DeepSeek (Ultra Cheap)")
    st.markdown("[Get key](https://platform.deepseek.com) — ₹0.05-0.15 per 1000 questions")
    deepseek_key = st.text_input("DeepSeek API Key", value=ai_cfg.get("deepseek_key", ""),
                                  type="password", placeholder="sk-...", key="deepseek_key_in")
    st.caption("Best quality per rupee. Excellent for bulk AI usage.")

st.markdown("---")

# Preferred provider
st.subheader("2. Preferred AI Provider")
providers = ["openai", "claude", "gemini", "deepseek"]
provider_labels = {"openai": "OpenAI (GPT)", "claude": "Claude (Anthropic)",
                   "gemini": "Gemini (Google)", "deepseek": "DeepSeek"}
current_pref = ai_cfg.get("preferred_provider", "openai")
if current_pref not in providers:
    current_pref = "openai"
preferred = st.radio("Primary provider (others are automatic fallback):",
                      providers, format_func=lambda x: provider_labels[x],
                      index=providers.index(current_pref), horizontal=True)
st.caption("If preferred fails, system auto-tries: next paid → Gemini free → Offline engine. User never sees failure.")

st.markdown("---")

# SAVE
if st.button("SAVE ALL API SETTINGS", type="primary", key="save_ai"):
    new_config = {
        "openai_key": openai_key, "claude_key": claude_key,
        "gemini_key": gemini_key, "deepseek_key": deepseek_key,
        "openai_model": openai_model, "claude_model": claude_model,
        "gemini_model": "gemini-2.0-flash", "deepseek_model": "deepseek-chat",
        "preferred_provider": preferred,
    }
    save_ai_config(new_config)
    st.success("All API settings saved! 6-provider fallback chain active.")
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
st.caption(f"{COMPANY['name']} | AI Auto-Connection Manager | 6 providers, never fails")
