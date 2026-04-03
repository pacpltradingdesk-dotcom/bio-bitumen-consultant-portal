"""
AI Settings — API Key Management for OpenAI + Claude
======================================================
Enter API keys, select models, test connections, manage AI features.
Keys stored locally in data/ai_config.json (never committed to git).
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

st.sidebar.markdown("---")
if st.sidebar.button("Print This Page", key="print_page"):
    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

st.title("AI Settings — API Key Management")
st.markdown("**Configure OpenAI (GPT-4o) and/or Claude (Sonnet) for AI-powered features**")
st.markdown("---")

# Load current config
ai_cfg = load_ai_config()

# ══════════════════════════════════════════════════════════════════════
# STATUS PANEL
# ══════════════════════════════════════════════════════════════════════
active = get_active_provider()
available = is_ai_available()

status_color = "#00AA44" if available else "#FF8800"
st.markdown(f"""
<div style="background: {status_color}15; border: 2px solid {status_color}; border-radius: 12px;
            padding: 15px 20px; margin-bottom: 15px;">
    <h3 style="color: {status_color}; margin: 0;">
        AI Status: {'ACTIVE — Using ' + active.upper() if active else 'NOT CONFIGURED — Enter API keys below'}
    </h3>
    <p style="margin: 5px 0 0 0; color: #666;">
        {'AI-powered DPR writing, financial analysis, smart chat, and auto-reports are enabled.' if available
         else 'System uses built-in knowledge base (100+ patterns). Add API keys for AI-powered features.'}
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# API KEY INPUT
# ══════════════════════════════════════════════════════════════════════
st.subheader("1. Enter API Keys")
st.caption("Keys are stored locally in `data/ai_config.json` — never uploaded to GitHub")

key_col1, key_col2 = st.columns(2)

with key_col1:
    st.markdown("### OpenAI (GPT-4o)")
    st.markdown("[Get API key](https://platform.openai.com/api-keys)")
    openai_key = st.text_input("OpenAI API Key", value=ai_cfg.get("openai_key", ""),
                                type="password", placeholder="sk-...", key="openai_key")
    openai_model = st.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1-nano"],
                                 index=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1-nano"].index(
                                     ai_cfg.get("openai_model", "gpt-4o-mini")),
                                 key="openai_model")

    st.markdown("""
    **Pricing (approximate):**
    - gpt-4o-mini: ~$0.15/1M tokens (cheapest, good quality)
    - gpt-4o: ~$2.50/1M tokens (best quality)
    - gpt-4.1-mini: ~$0.40/1M tokens (latest, fast)
    """)

with key_col2:
    st.markdown("### Anthropic Claude")
    st.markdown("[Get API key](https://console.anthropic.com/settings/keys)")
    claude_key = st.text_input("Claude API Key", value=ai_cfg.get("claude_key", ""),
                                type="password", placeholder="sk-ant-...", key="claude_key")
    claude_model = st.selectbox("Claude Model", ["claude-sonnet-4-20250514", "claude-haiku-4-5-20251001"],
                                 index=0, key="claude_model")

    st.markdown("""
    **Pricing (approximate):**
    - Claude Sonnet: ~$3/1M tokens (best quality)
    - Claude Haiku: ~$0.25/1M tokens (fast, cheap)
    """)

st.markdown("---")

# Preferred provider
st.subheader("2. Preferred AI Provider")
preferred = st.radio("Use which provider first?",
                      ["openai", "claude"],
                      format_func=lambda x: "OpenAI (GPT)" if x == "openai" else "Anthropic (Claude)",
                      index=0 if ai_cfg.get("preferred_provider", "openai") == "openai" else 1,
                      horizontal=True, key="preferred")
st.caption("If preferred provider fails, system auto-falls back to the other one.")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════════════
if st.button("SAVE API SETTINGS", type="primary", key="save_ai"):
    new_config = {
        "openai_key": openai_key,
        "claude_key": claude_key,
        "openai_model": openai_model,
        "claude_model": claude_model,
        "preferred_provider": preferred,
    }
    save_ai_config(new_config)
    st.success("API settings saved! AI features are now available across the system.")
    st.rerun()

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# TEST CONNECTION
# ══════════════════════════════════════════════════════════════════════
st.subheader("3. Test API Connection")

if st.button("Test Both APIs", key="test_apis"):
    with st.spinner("Testing API connections..."):
        results = test_api_connection()

    for provider, info in results.items():
        status = info["status"]
        icon = "✅" if status == "OK" else ("⚠️" if status == "No key" else "❌")
        color = "#00AA44" if status == "OK" else ("#FF8800" if status == "No key" else "#CC3333")

        st.markdown(f"""
        <div style="background: {color}10; border-left: 4px solid {color}; padding: 10px 15px;
                    border-radius: 0 8px 8px 0; margin-bottom: 10px;">
            <strong>{icon} {provider.upper()}</strong> — {status}
            {f' | Model: {info["model"]}' if info["model"] else ''}
            {f' | Response: {info["response"][:60]}' if info.get("response") else ''}
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# AI FEATURES OVERVIEW
# ══════════════════════════════════════════════════════════════════════
st.subheader("4. AI-Powered Features")

features = [
    ("AI DPR Writer", "Writes professional DPR sections with perfect English, bank-ready formatting",
     "Document Hub → Generate DPR", available),
    ("AI Financial Analysis", "Analyzes your P&L, gives bankability score, identifies risks and recommendations",
     "Financial Model page → AI Analysis button", available),
    ("Smart AI Chat", "Answers ANY question about bio-bitumen with real AI intelligence (not just patterns)",
     "AI Advisor page → Chat input", available),
    ("Auto Report Writer", "Generates complete sections: Executive Summary, Market Analysis, Risk Assessment",
     "Document Hub → AI Write Section", available),
]

for name, desc, location, active_feat in features:
    icon = "🟢" if active_feat else "🔴"
    st.markdown(f"{icon} **{name}** — {desc}")
    st.caption(f"   Location: {location}")

if not available:
    st.info("Add API keys above to enable all AI features. Without keys, the system uses built-in knowledge base (100+ patterns).")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# QUICK AI TEST
# ══════════════════════════════════════════════════════════════════════
if available:
    st.subheader("5. Quick AI Test")
    test_prompt = st.text_input("Ask AI anything:", placeholder="What is the best state for bio-bitumen plant?",
                                 key="test_prompt")
    if test_prompt and st.button("Ask AI", key="test_ask"):
        with st.spinner("Thinking..."):
            from engines.ai_engine import ask_ai
            response, provider = ask_ai(test_prompt,
                "You are a bio-bitumen industry expert. Answer concisely in 3-4 sentences.")
        st.markdown(f"**{provider.upper()}:** {response}")

st.markdown("---")
st.caption(f"{COMPANY['name']} | AI Settings | Keys stored locally, never uploaded to GitHub")
