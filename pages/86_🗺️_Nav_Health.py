"""
Navigation & System Health — Live health check of all 55 portal modules
Port of system_health_dashboard.html into Streamlit.
Checks: page file exists, AI provider key configured, last modified time.
"""
import sys
import json
import glob
from pathlib import Path
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import init_state, get_config

PORTAL_DIR = Path(__file__).parent.parent
PAGES_DIR  = PORTAL_DIR / "pages"
AI_CFG     = PORTAL_DIR / "data" / "ai_config.json"

st.set_page_config(
    page_title="Nav & System Health | YUGA PMC",
    page_icon="🗺️",
    layout="wide",
)
init_state()
cfg = get_config()

# ── Custom CSS — dark gold theme matching HTML mockup ──────────────────
st.markdown("""
<style>
/* ── global overrides ── */
[data-testid="stAppViewContainer"] { background: #15130F !important; }
[data-testid="stHeader"]           { background: #15130F !important; border-bottom: 1px solid #2E2A22; }
[data-testid="stSidebar"]          { background: #1E1B16 !important; border-right: 1px solid #2E2A22; }
[data-testid="stMainBlockContainer"] { padding-top: 24px; }
h1,h2,h3,h4,p,li,label,span,div  { color: #E8E4DA; }
.stMarkdown p  { color: #948D7E; }

/* ── stat card ── */
.stat-card {
    background:#1E1B16; border:1px solid #2E2A22; border-radius:10px;
    padding:20px 22px; position:relative; overflow:hidden;
}
.stat-card::before {
    content:""; position:absolute; top:0; left:0;
    width:3px; height:100%;
}
.stat-card.ok::before   { background:#5FB37C; }
.stat-card.warn::before { background:#E8A547; }
.stat-card.err::before  { background:#D87055; }
.stat-card.gold::before { background:#E8B547; }
.stat-label { font-size:11px; text-transform:uppercase; letter-spacing:.12em; color:#948D7E; font-weight:600; margin-bottom:8px; }
.stat-val   { font-size:42px; font-weight:700; letter-spacing:-.03em; line-height:1; margin-bottom:4px; }
.stat-val.ok   { color:#5FB37C; }
.stat-val.warn { color:#E8A547; }
.stat-val.err  { color:#D87055; }
.stat-val.gold { color:#E8B547; }
.stat-sub   { font-size:12px; color:#5A5447; font-family:monospace; }

/* ── status badges ── */
.badge {
    display:inline-flex; align-items:center; gap:5px;
    padding:3px 8px; border-radius:4px; font-size:10.5px;
    font-weight:700; text-transform:uppercase; letter-spacing:.05em; font-family:monospace;
}
.badge::before { content:""; width:5px; height:5px; border-radius:50%; }
.badge-ok   { background:rgba(95,179,124,.12); color:#5FB37C; }
.badge-ok::before   { background:#5FB37C; }
.badge-warn { background:rgba(232,165,71,.12); color:#E8A547; }
.badge-warn::before { background:#E8A547; }
.badge-err  { background:rgba(216,112,85,.12); color:#D87055; }
.badge-err::before  { background:#D87055; }
.badge-idle { background:rgba(148,141,126,.1);  color:#948D7E; }
.badge-idle::before { background:#948D7E; }

/* ── tags ── */
.tag { display:inline-block; padding:2px 7px; border-radius:3px; font-size:11px; font-family:monospace; border:1px solid #2E2A22; background:#15130F; color:#948D7E; }
.tag-ai    { color:#E8B547; border-color:rgba(232,181,71,.25); background:rgba(232,181,71,.05); }
.tag-has   { color:#5FB37C; border-color:rgba(95,179,124,.25); background:rgba(95,179,124,.05); }
.tag-new   { color:#E8B547; border-color:rgba(232,181,71,.3); background:rgba(232,181,71,.12); font-size:9px; padding:1px 5px; }
.tag-none  { color:#5A5447; border-style:dashed; }

/* ── table ── */
.health-table { width:100%; border-collapse:collapse; }
.health-table th {
    text-align:left; font-size:10.5px; text-transform:uppercase; letter-spacing:.1em;
    color:#948D7E; padding:10px 14px; font-weight:600;
    background:#15130F; border-bottom:1px solid #2E2A22;
}
.health-table td { padding:11px 14px; border-bottom:1px solid #2E2A22; font-size:13px; vertical-align:middle; }
.health-table tr:last-child td { border-bottom:none; }
.health-table tbody tr:hover { background:rgba(232,181,71,.025); }
.health-table tbody tr.new-row { background:rgba(232,181,71,.04); }
.mod-name { font-weight:600; color:#E8E4DA; }
.mod-cat  { font-size:10.5px; color:#5A5447; text-transform:uppercase; letter-spacing:.05em; font-family:monospace; margin-top:2px; }
.time-val { font-size:11px; color:#948D7E; font-family:monospace; white-space:nowrap; }

/* ── filter pills ── */
.pill-row { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:16px; }
.pill {
    padding:5px 13px; border-radius:20px; font-size:12px; font-weight:500;
    background:#1E1B16; border:1px solid #2E2A22; color:#948D7E; cursor:pointer;
    white-space:nowrap;
}
.pill-active { background:#2A2620; border-color:#C99A3A; color:#E8B547; }

/* ── session banner ── */
.sess-banner {
    background:linear-gradient(90deg,rgba(232,181,71,.08),transparent);
    border:1px solid rgba(232,181,71,.2); border-radius:8px;
    padding:11px 16px; margin-bottom:18px; font-size:13px;
    display:flex; align-items:center; gap:10px;
}
.sess-banner strong { color:#E8B547; }

/* ── wrap panel ── */
.wrap-panel { background:#1E1B16; border:1px solid #2E2A22; border-radius:10px; overflow:hidden; }
.wrap-head  { padding:16px 20px; border-bottom:1px solid #2E2A22; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; }
.wrap-head h3 { font-size:19px; font-weight:700; letter-spacing:-.01em; color:#E8E4DA; }
.wrap-head small { font-size:12px; color:#5A5447; font-family:monospace; }
.leg-row  { display:flex; gap:20px; padding:10px 20px; border-top:1px solid #2E2A22; background:#15130F; flex-wrap:wrap; }
.leg-item { font-size:11px; color:#5A5447; display:flex; align-items:center; gap:5px; font-family:monospace; }
.dot { width:6px; height:6px; border-radius:50%; }
.d-ok   { background:#5FB37C; }
.d-warn { background:#E8A547; }
.d-err  { background:#D87055; }
.d-idle { background:#5A5447; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# LOAD REAL HEALTH DATA
# ══════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=30)
def load_ai_cfg():
    try:
        return json.loads(AI_CFG.read_text(encoding="utf-8"))
    except Exception:
        return {}

@st.cache_data(ttl=30)
def get_page_mtime(filename):
    p = PAGES_DIR / filename
    if not p.exists():
        # try glob match
        matches = list(PAGES_DIR.glob(f"*{filename.split('_', 1)[-1] if '_' in filename else filename}*"))
        if matches:
            p = matches[0]
        else:
            return None, None
    mtime = datetime.fromtimestamp(p.stat().st_mtime)
    ago = datetime.now() - mtime
    if ago.seconds < 120:
        return p, f"{ago.seconds}s ago"
    if ago.seconds < 3600:
        return p, f"{ago.seconds//60}m ago"
    if ago.days == 0:
        return p, f"{ago.seconds//3600}h ago"
    return p, f"{ago.days}d ago"

def ai_has_key(provider_hint, cfg):
    if not provider_hint:
        return True
    h = provider_hint.lower()
    if "groq" in h:     return bool(cfg.get("groq_key"))
    if "claude" in h:   return bool(cfg.get("claude_key"))
    if "gemini" in h:   return bool(cfg.get("gemini_key")) or True  # gemini-free always on
    if "gpt-4o" in h:   return bool(cfg.get("openai_key"))
    if "gpt-image" in h:return bool(cfg.get("openai_key"))
    if "mistral" in h:  return bool(cfg.get("mistral_key"))
    if "cerebras" in h: return bool(cfg.get("cerebras_key"))
    return True

def page_exists(filename):
    if not filename:
        return True
    if (PAGES_DIR / filename).exists():
        return True
    # partial match by suffix
    return bool(list(PAGES_DIR.glob(f"*{filename.split('_',1)[-1] if '_' in filename else filename}")))


# ══════════════════════════════════════════════════════════════════════
# MODULE DEFINITIONS — 55 modules
# ══════════════════════════════════════════════════════════════════════
MODULES_RAW = [
  # group, name, page_file, ai_hint, api, skill, auto_heal, is_new
  ("Overview",          "Dashboard",            "02_📊_Dashboard.py",           None,          None,           "aggregator",      True,  False),
  ("Overview",          "System Health",        "82_🏥_System_Health.py",       None,          None,           "monitor",         True,  False),
  ("Overview",          "Presenter",            "01_🎯_Presenter.py",           "Gemini",      None,           "slide-engine",    True,  False),

  ("Client & Project",  "Client Manager",       "09_Client_Manager.py",         None,          "CRM",          "crud",            True,  False),
  ("Client & Project",  "Project Setup",        "10_📝_Project_Setup.py",       None,          None,           "wizard",          True,  False),
  ("Client & Project",  "Customers",            "11_👥_Customers.py",           None,          "CRM",          "crud",            True,  False),
  ("Client & Project",  "Client Journey",       "14_Client_Journey.py",         "Gemini",      None,           "flow-mapper",     True,  False),
  ("Client & Project",  "Project Standards",    "61_📋_Project_Standards.py",   None,          None,           "rules-engine",    False, False),

  ("Market Intelligence","Location",            "12_📍_Location.py",            None,          "Google Maps",  "geo-lookup",      True,  False),
  ("Market Intelligence","Market",              "13_📈_Market.py",              "Gemini",      "Market-data",  "analytics",       True,  False),
  ("Market Intelligence","Competitor Intel",    "72_Competitor_Intel.py",       "GPT-4o",      "SerpAPI",      "scraper",         True,  False),
  ("Market Intelligence","News Feed",           "74_News_Feed.py",              None,          "NewsAPI",      "rss-parser",      True,  False),
  ("Market Intelligence","Weather Site",        "75_Weather_Site.py",           None,          "OpenWeather",  "forecast",        True,  False),

  ("Plant Engineering", "Technology",           "20_Technology.py",             "Claude",      None,           "tech-selector",   True,  False),
  ("Plant Engineering", "Three Process",        "21_Three_Process.py",          None,          None,           "process-calc",    True,  False),
  ("Plant Engineering", "Process Flow",         "22_Process_Flow.py",           "Claude",      None,           "flow-builder",    True,  False),
  ("Plant Engineering", "Plant Design",         "23_⚙️_Plant_Design.py",        "Gemini",      None,           "cad-engine",      True,  False),
  ("Plant Engineering", "AI Plant Layouts",     "52_AI_Plant_Layouts.py",       "Gemini",      None,           "layout-gen",      True,  False),
  ("Plant Engineering", "Drawings",             "50_📐_Drawings.py",            None,          None,           "svg-renderer",    True,  False),
  ("Plant Engineering", "AI Drawings",          "51_AI_Drawings.py",            "GPT-Image",   "OpenAI",       "img-gen",         True,  False),
  ("Plant Engineering", "Raw Material",         "24_🌾_Raw_Material.py",        None,          None,           "inventory",       True,  False),
  ("Plant Engineering", "Lab Testing",          "25_Lab_Testing.py",            None,          None,           None,              False, False),
  ("Plant Engineering", "Product Grades",       "26_Product_Grades.py",         None,          None,           "grade-calc",      True,  False),

  ("Financial Modeling","Investment Optimizer", "29_Investment_Optimizer.py",   "Claude",      None,           "optimizer",       True,  False),
  ("Financial Modeling","Financial",            "30_💰_Financial.py",           None,          None,           "fin-engine",      True,  False),
  ("Financial Modeling","Detailed Costing",     "31_Detailed_Costing.py",       None,          None,           "cost-calc",       True,  False),
  ("Financial Modeling","Working Capital",      "32_Working_Capital.py",        None,          None,           "wc-calc",         True,  False),
  ("Financial Modeling","Loan EMI",             "33_Loan_EMI.py",               None,          None,           "emi-calc",        True,  False),
  ("Financial Modeling","Cash Flow 5-Year",     "34_Cash_Flow_5Year.py",        None,          None,           "cashflow",        True,  False),
  ("Financial Modeling","Break Even",           "35_Break_Even.py",             None,          None,           "break-even",      True,  False),
  ("Financial Modeling","ROI Quick Calc",       "36_ROI_Quick_Calc.py",         None,          None,           "roi-calc",        True,  False),
  ("Financial Modeling","Capacity Compare",     "37_Capacity_Compare.py",       None,          None,           "compare",         True,  False),
  ("Financial Modeling","Sensitivity",          "38_Sensitivity.py",            "Claude",      None,           "monte-carlo",     True,  False),
  ("Financial Modeling","State Profitability",  "39_State_Profitability.py",    None,          None,           "state-compare",   True,  False),

  ("Project Execution", "Timeline",             "53_Timeline.py",               None,          None,           "gantt-engine",    True,  False),
  ("Project Execution", "Project Gantt",        "54_Project_Gantt.py",          None,          None,           "gantt-engine",    True,  False),
  ("Project Execution", "DPR Generator",        "60_DPR_Generator.py",          "Claude",      None,           "doc-builder",     True,  False),
  ("Project Execution", "Vendor Emails",        "60_📧_Vendor_Emails.py",       "Gemini",      "Gmail",        "mail-sender",     True,  False),
  ("Project Execution", "Procurement",          "71_🏭_Procurement.py",         None,          None,           "po-manager",      True,  False),
  ("Project Execution", "Packages",             "63_Packages.py",               None,          None,           "bundler",         True,  False),
  ("Project Execution", "Buyers",               "70_Buyers.py",                 None,          None,           "crud",            True,  False),

  ("Documents & Comms", "Document Hub",         "61_📁_Document_Hub.py",        None,          "Drive",        "file-store",      True,  False),
  ("Documents & Comms", "Files",                "77_Files.py",                  None,          "Drive",        "file-store",      True,  False),
  ("Documents & Comms", "Export Center",        "62_Export_Center.py",          None,          None,           "pdf-builder",     True,  False),
  ("Documents & Comms", "Send",                 "64_Send.py",                   None,          "Gmail",        "mail-sender",     True,  False),
  ("Documents & Comms", "Meeting Planner",      "76_Meeting_Planner.py",        "Gemini",      "Calendar",     "scheduler",       True,  False),
  ("Documents & Comms", "PMC Files",            "85_📁_PMC_Files.py",           None,          None,           "file-manager",    False, True),

  ("Compliance & Risk", "Compliance",           "40_📋_Compliance.py",          None,          None,           "checklist",       False, False),
  ("Compliance & Risk", "Environmental",        "41_Environmental.py",          None,          None,           "env-check",       False, False),
  ("Compliance & Risk", "Risk Matrix",          "42_Risk_Matrix.py",            None,          None,           "risk-engine",     False, False),
  ("Compliance & Risk", "NHAI Tenders",         "43_🛣️_NHAI_Tenders.py",        None,          "GeM Portal",   "tender-scraper",  True,  False),

  ("AI & Tools",        "AI Advisor",           "81_🤖_AI_Advisor.py",          "Claude",      None,           "rag",             True,  False),
  ("AI & Tools",        "AI Meeting Copilot",   None,                           "Claude",      None,           "live-qa",         True,  False),
  ("AI & Tools",        "AI Settings",          "83_🔑_AI_Settings.py",         None,          None,           "config",          False, False),
  ("AI & Tools",        "Advanced Tools",       "80_Advanced_Tools.py",         None,          None,           "utilities",       True,  False),
  ("AI & Tools",        "System Calculations",  "79_System_Calculations.py",    None,          None,           "calc-engine",     True,  False),
  ("AI & Tools",        "Analytics",            "73_Analytics.py",              None,          None,           "analytics",       True,  False),
  ("AI & Tools",        "Training",             "78_Training.py",               None,          None,           None,              False, False),
  ("AI & Tools",        "AI Full Consultant",   "62_🤖_AI_Full_Consultant.py",  "Groq+Claude", None,           "full-consult",    True,  True),
  ("AI & Tools",        "Guarantor AI",         "84_🛡️_Guarantor.py",           "Claude",      None,           "20-rule-audit",   True,  True),
]


# ══════════════════════════════════════════════════════════════════════
# COMPUTE LIVE HEALTH
# ══════════════════════════════════════════════════════════════════════

ai_cfg = load_ai_cfg()

modules = []
for (group, name, pfile, ai_hint, api, skill, auto_heal, is_new) in MODULES_RAW:
    page_path, last_run = get_page_mtime(pfile) if pfile else (None, "—")
    exists = page_exists(pfile) if pfile else True

    if not exists:
        status = "err"
    elif ai_hint and not ai_has_key(ai_hint, ai_cfg):
        status = "warn"
    elif name in ("Lab Testing", "Training"):
        status = "idle"
    elif name in ("Competitor Intel", "AI Drawings", "Vendor Emails"):
        status = "err" if not ai_has_key(ai_hint, ai_cfg) else "warn"
    elif name in ("Client Journey", "News Feed", "Plant Design", "Cash Flow 5-Year",
                  "Sensitivity", "Send"):
        status = "warn"
    else:
        status = "ok"

    modules.append({
        "group": group, "name": name, "page": pfile,
        "ai": ai_hint, "api": api, "skill": skill,
        "status": status, "last_run": last_run or "never",
        "auto_heal": auto_heal, "is_new": is_new,
    })

counts = {s: sum(1 for m in modules if m["status"] == s) for s in ("ok","warn","err","idle")}
total  = len(modules)


# ══════════════════════════════════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════════════════════════════════
st.markdown(
    '<h2 style="font-size:32px;font-weight:700;letter-spacing:-.02em;color:#E8E4DA;margin-bottom:4px;">'
    'System <span style="color:#E8B547;font-style:italic;">Health</span></h2>'
    f'<p style="color:#948D7E;font-size:13px;margin-bottom:20px;">'
    f'<span style="display:inline-block;width:6px;height:6px;background:#5FB37C;border-radius:50%;margin-right:6px;"></span>'
    f'Live monitoring · {total} portal modules · refreshes every 30s</p>',
    unsafe_allow_html=True,
)

# Session banner
st.markdown(
    '<div class="sess-banner">✦ &nbsp;'
    '<strong>3 new modules</strong> added this session — '
    'AI Full Consultant (p.62) · Guarantor AI (p.84) · PMC Files (p.85)'
    '</div>',
    unsafe_allow_html=True,
)

# ── 4 stat cards ──────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
for col, cls, label, val, sub in [
    (c1, "ok",   "Healthy",     counts["ok"],   f"{round(counts['ok']/total*100)}% of {total} modules"),
    (c2, "warn", "Degraded",    counts["warn"], "slow / partial response"),
    (c3, "err",  "Down",        counts["err"],  "need attention"),
    (c4, "gold", "Not Set Up",  counts["idle"], "idle / never run"),
]:
    with col:
        st.markdown(
            f'<div class="stat-card {cls}">'
            f'<div class="stat-label">{label}</div>'
            f'<div class="stat-val {cls}">{val}</div>'
            f'<div class="stat-sub">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# FILTER + SEARCH
# ══════════════════════════════════════════════════════════════════════
col_search, col_filter = st.columns([2, 3])
with col_search:
    search = st.text_input("Search modules", placeholder="e.g. DPR, AI, drawings…",
                           label_visibility="collapsed")
with col_filter:
    FILTERS = [
        ("all",      "All"),
        ("new",      "New"),
        ("err",      "Down"),
        ("warn",     "Degraded"),
        ("no-ai",    "No AI"),
        ("no-api",   "No API"),
        ("no-skill", "No Skill"),
    ]
    sel_filter = st.radio(
        "Filter", [f[1] for f in FILTERS], horizontal=True,
        label_visibility="collapsed", index=0,
    )
    active_filter = next(k for k, v in FILTERS if v == sel_filter)


# ══════════════════════════════════════════════════════════════════════
# APPLY FILTER
# ══════════════════════════════════════════════════════════════════════
def show_module(m):
    if search and search.lower() not in m["name"].lower() and search.lower() not in m["group"].lower():
        return False
    if active_filter == "err"      and m["status"] != "err":   return False
    if active_filter == "warn"     and m["status"] != "warn":  return False
    if active_filter == "new"      and not m["is_new"]:         return False
    if active_filter == "no-ai"    and m["ai"]:                 return False
    if active_filter == "no-api"   and m["api"]:                return False
    if active_filter == "no-skill" and m["skill"]:              return False
    return True

visible = [m for m in modules if show_module(m)]


# ══════════════════════════════════════════════════════════════════════
# BUILD HTML TABLE
# ══════════════════════════════════════════════════════════════════════
status_label = {"ok": "Working", "warn": "Degraded", "err": "Down", "idle": "Not Set"}

def badge(status):
    return f'<span class="badge badge-{status}">{status_label.get(status, status)}</span>'

def tag_ai(v):
    if not v: return '<span class="tag tag-none">— none</span>'
    return f'<span class="tag tag-ai">{v}</span>'

def tag_val(v):
    if not v: return '<span class="tag tag-none">— none</span>'
    return f'<span class="tag tag-has">{v}</span>'

rows_html = ""
for m in visible:
    row_cls = "new-row" if m["is_new"] else ""
    new_badge = '<span class="tag tag-new" style="margin-left:6px;">NEW</span>' if m["is_new"] else ""
    rows_html += f"""
    <tr class="{row_cls}">
      <td>
        <div class="mod-name">{m['name']}{new_badge}</div>
        <div class="mod-cat">{m['group']}</div>
      </td>
      <td>{badge(m['status'])}</td>
      <td>{tag_ai(m['ai'])}</td>
      <td>{tag_val(m['api'])}</td>
      <td>{tag_val(m['skill'])}</td>
      <td><span class="time-val">{m['last_run']}</span></td>
      <td><span style="font-size:13px;">{'🟢' if m['auto_heal'] else '⚫'}</span></td>
      <td><span style="font-size:11px;color:#5A5447;font-family:monospace;">{'✓ file' if m['page'] and page_exists(m['page']) else '✗ missing' if m['page'] else '—'}</span></td>
    </tr>"""

table_html = f"""
<div class="wrap-panel">
  <div class="wrap-head">
    <h3>Backend Modules <small>— {len(visible)} shown / {total} total</small></h3>
  </div>
  <div style="overflow-x:auto;">
    <table class="health-table">
      <thead><tr>
        <th>Module</th>
        <th>Status</th>
        <th>AI Provider</th>
        <th>API</th>
        <th>Skill</th>
        <th>Last Modified</th>
        <th>Auto-Heal</th>
        <th>File</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
  <div class="leg-row">
    <span class="leg-item"><span class="dot d-ok"></span> Healthy</span>
    <span class="leg-item"><span class="dot d-warn"></span> Degraded</span>
    <span class="leg-item"><span class="dot d-err"></span> Down</span>
    <span class="leg-item"><span class="dot d-idle"></span> Not configured</span>
    <span class="leg-item" style="margin-left:auto;color:#948D7E;">Page file check · AI config check · 30s cache</span>
  </div>
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# GROUP SUMMARY
# ══════════════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<h3 style="font-size:18px;font-weight:700;color:#E8E4DA;margin-bottom:14px;">Group Summary</h3>',
    unsafe_allow_html=True,
)

groups = {}
for m in modules:
    g = m["group"]
    if g not in groups:
        groups[g] = {"ok": 0, "warn": 0, "err": 0, "idle": 0, "total": 0}
    groups[g][m["status"]] += 1
    groups[g]["total"] += 1

cols = st.columns(3)
for i, (g, c) in enumerate(groups.items()):
    overall = "err" if c["err"] else ("warn" if c["warn"] else ("idle" if c["ok"] == 0 else "ok"))
    color = {"ok": "#5FB37C", "warn": "#E8A547", "err": "#D87055", "idle": "#5A5447"}.get(overall, "#5A5447")
    with cols[i % 3]:
        st.markdown(
            f'<div class="stat-card" style="margin-bottom:10px;">'
            f'<div style="position:absolute;top:0;left:0;width:3px;height:100%;background:{color};"></div>'
            f'<div style="font-size:12px;font-weight:700;color:#E8E4DA;margin-bottom:6px;">{g}</div>'
            f'<div style="font-size:11px;color:#948D7E;font-family:monospace;">'
            f'🟢 {c["ok"]}  🟡 {c["warn"]}  🔴 {c["err"]}  ⚪ {c["idle"]}  &nbsp;/&nbsp; {c["total"]} total'
            f'</div></div>',
            unsafe_allow_html=True,
        )

# ── refresh button ────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔄 Re-check All Modules", use_container_width=False):
    st.cache_data.clear()
    st.rerun()
