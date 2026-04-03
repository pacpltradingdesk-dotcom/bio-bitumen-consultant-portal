"""
Multi-Language Support — English + Hindi
=========================================
Key pages translated. Toggle in sidebar.
"""
import streamlit as st

TRANSLATIONS = {
    "en": {
        "welcome": "Welcome to Bio Bitumen Consulting System",
        "tagline": "ONE-POINT SOLUTION: Land Selection → Plant Setup → Financial Closure",
        "select_client": "Select Your Client Type",
        "new_investor": "New Investor / Farmer Group",
        "bitumen_owner": "Existing Bitumen Plant Owner",
        "biomass_company": "Biomass / Agro Waste Company",
        "pyrolysis_owner": "Existing Pyrolysis Plant Owner",
        "step1": "Market Opportunity",
        "step2": "Feasibility Analysis",
        "step3": "Technical Solution",
        "step4": "Financial Benefit",
        "step5": "Implementation Plan",
        "step6": "Compliance & Licenses",
        "step7": "Execution — What We Provide",
        "step8": "Final Output — Ready to Start",
        "investment": "Investment",
        "revenue": "Revenue",
        "profit": "Profit",
        "roi": "Return on Investment",
        "break_even": "Break-Even",
        "capacity": "Plant Capacity",
        "location": "Location",
        "staff": "Staff Required",
        "power": "Power Required",
        "contact": "Contact Us",
        "generate_dpr": "Generate DPR",
        "download": "Download",
        "why_now": "Why Bio-Bitumen NOW?",
        "everything_ready": "Everything is READY. Let's Start.",
        "documents_ready": "All Documents Ready",
        "drawings_ready": "All Drawings Ready",
    },
    "hi": {
        "welcome": "बायो बिटुमेन कंसल्टिंग सिस्टम में आपका स्वागत है",
        "tagline": "एक ही जगह सब कुछ: जमीन चयन → प्लांट सेटअप → वित्तीय समापन",
        "select_client": "अपना क्लाइंट प्रकार चुनें",
        "new_investor": "नया निवेशक / किसान समूह",
        "bitumen_owner": "मौजूदा बिटुमेन प्लांट मालिक",
        "biomass_company": "बायोमास / कृषि अपशिष्ट कंपनी",
        "pyrolysis_owner": "मौजूदा पायरोलिसिस प्लांट मालिक",
        "step1": "बाजार अवसर",
        "step2": "व्यवहार्यता विश्लेषण",
        "step3": "तकनीकी समाधान",
        "step4": "वित्तीय लाभ",
        "step5": "कार्यान्वयन योजना",
        "step6": "अनुपालन और लाइसेंस",
        "step7": "निष्पादन — हम क्या प्रदान करते हैं",
        "step8": "अंतिम आउटपुट — शुरू करने के लिए तैयार",
        "investment": "निवेश",
        "revenue": "राजस्व",
        "profit": "लाभ",
        "roi": "निवेश पर प्रतिफल",
        "break_even": "ब्रेक-ईवन",
        "capacity": "प्लांट क्षमता",
        "location": "स्थान",
        "staff": "कर्मचारी आवश्यक",
        "power": "बिजली आवश्यक",
        "contact": "संपर्क करें",
        "generate_dpr": "DPR बनाएं",
        "download": "डाउनलोड",
        "why_now": "बायो-बिटुमेन अभी क्यों?",
        "everything_ready": "सब कुछ तैयार है। शुरू करें।",
        "documents_ready": "सभी दस्तावेज तैयार",
        "drawings_ready": "सभी ड्रॉइंग तैयार",
    },
}


def get_lang():
    """Get current language from session state."""
    return st.session_state.get("language", "en")


def set_lang(lang):
    """Set language."""
    st.session_state["language"] = lang


def t(key):
    """Translate a key to current language."""
    lang = get_lang()
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


def language_selector():
    """Show language toggle in sidebar."""
    lang = get_lang()
    col1, col2 = st.sidebar.columns(2)
    if col1.button("English", type="primary" if lang == "en" else "secondary", width="stretch"):
        set_lang("en")
        st.rerun()
    if col2.button("हिंदी", type="primary" if lang == "hi" else "secondary", width="stretch"):
        set_lang("hi")
        st.rerun()
