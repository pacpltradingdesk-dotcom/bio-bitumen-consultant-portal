"""
87 · Skill Engine — AI Background Workers
==========================================
Runs 4 AI workers that analyse every portal module and write
one-line suggestions. Reads notes.json live; user can
Apply / Dismiss / Ask AI to refine each suggestion.
"""

import json
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

import streamlit as st
sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import init_state, get_config

# ── paths ──────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent.parent
NOTES_PATH    = _HERE / "data" / "notes.json"
ACTIONS_PATH  = _HERE / "data" / "notes_actions.json"

st.set_page_config(
    page_title="Skill Engine · Bio Bitumen",
    page_icon="🧠",
    layout="wide",
)
init_state()
cfg = get_config()

# ── custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#15130F;}
[data-testid="stSidebar"]{background:#1A1710;}
h1,h2,h3,h4,label,p,.stMarkdown{color:#F0E6D3;}
.stButton>button{background:#E8B547;color:#15130F;font-weight:700;border:none;border-radius:6px;}
.stButton>button:hover{background:#F5C842;}
.badge-info   {background:#1E3A5F;color:#7EC8E3;padding:2px 8px;border-radius:10px;font-size:12px;}
.badge-warn   {background:#4A3000;color:#FFB300;padding:2px 8px;border-radius:10px;font-size:12px;}
.badge-action {background:#3D0000;color:#FF6B6B;padding:2px 8px;border-radius:10px;font-size:12px;}
.note-card    {background:#1E1B14;border-left:4px solid #E8B547;padding:10px 14px;
               border-radius:0 8px 8px 0;margin:4px 0;}
.note-card.warn   {border-left-color:#FFB300;}
.note-card.action {border-left-color:#FF6B6B;}
.note-card.info   {border-left-color:#7EC8E3;}
.module-row   {background:#1E1B14;padding:6px 10px;border-radius:6px;margin:2px 0;}
.worker-card  {background:#1E1B14;border:1px solid #3A3520;border-radius:8px;
               padding:14px;margin:4px;}
.pipeline-box {background:#1E1B14;border:1px solid #E8B547;border-radius:8px;
               padding:16px;text-align:center;color:#E8B547;}
.pipeline-arrow{color:#E8B547;font-size:22px;text-align:center;}
table.notes-table{width:100%;border-collapse:collapse;}
table.notes-table th{background:#2A2618;color:#E8B547;padding:8px 10px;
                     text-align:left;font-size:13px;border-bottom:1px solid #3A3520;}
table.notes-table td{padding:7px 10px;font-size:13px;color:#F0E6D3;
                     border-bottom:1px solid #2A2618;vertical-align:top;}
table.notes-table tr:hover td{background:#1E1B14;}
</style>
""", unsafe_allow_html=True)


# ── helpers ────────────────────────────────────────────────────────────

def _load_notes():
    try:
        return json.loads(NOTES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_actions():
    try:
        return json.loads(ACTIONS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_actions(actions):
    ACTIONS_PATH.write_text(json.dumps(actions, indent=2, ensure_ascii=False), encoding="utf-8")


def _badge(sev):
    icons = {"warn": "⚠", "action": "→", "info": "ℹ"}
    labels = {"warn": "WARNING", "action": "ACTION", "info": "INFO"}
    cls = {"warn": "badge-warn", "action": "badge-action", "info": "badge-info"}
    i = icons.get(sev, "•")
    l = labels.get(sev, "INFO")
    c = cls.get(sev, "badge-info")
    return f'<span class="{c}">{i} {l}</span>'


def _sev_color(sev):
    return {"warn": "#FFB300", "action": "#FF6B6B", "info": "#7EC8E3"}.get(sev, "#AAA")


def _run_scan_background():
    """Launch skill_engine.py as a subprocess."""
    try:
        subprocess.Popen(
            [sys.executable, "-m", "engines.skill_engine"],
            cwd=str(_HERE),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        st.session_state["scan_started"] = datetime.now().isoformat()
    except Exception as e:
        st.error(f"Could not start scan: {e}")


def _ask_ai_refine(module, current_text):
    """Quick AI refinement call."""
    try:
        from engines.ai_engine import ask_ai
        prompt = (
            f"Module: {module}\n"
            f"Current suggestion: {current_text}\n\n"
            "Expand this into 2-3 actionable bullet points with specific numbers "
            "or steps. Keep it concise (under 200 words)."
        )
        return ask_ai(prompt, max_tokens=300)
    except Exception as e:
        return f"AI unavailable: {e}"


# ── session state init ─────────────────────────────────────────────────
if "dismissed"   not in st.session_state: st.session_state["dismissed"]   = set()
if "applied"     not in st.session_state: st.session_state["applied"]     = set()
if "refinements" not in st.session_state: st.session_state["refinements"] = {}
if "scan_started"not in st.session_state: st.session_state["scan_started"]= ""

# load persistent actions
_acts = _load_actions()
st.session_state["dismissed"].update(_acts.get("dismissed", []))
st.session_state["applied"].update(_acts.get("applied", []))


# ── page header ────────────────────────────────────────────────────────
st.markdown("# 🧠 Skill Engine")
st.markdown("Background AI workers analyse every module and surface one-line improvement suggestions.")

data   = _load_notes()
notes  = data.get("notes", {})
ts     = data.get("scanned_at", "")
proj   = data.get("project", "—")

# status bar
c1, c2, c3, c4, c5 = st.columns(5)
total_notes  = len(notes)
active_notes = sum(1 for m, n in notes.items() if m not in st.session_state["dismissed"])
warn_count   = sum(1 for n in notes.values() if n.get("sev") == "warn")
action_count = sum(1 for n in notes.values() if n.get("sev") == "action")
applied_count= len(st.session_state["applied"])

for col, label, val, color in [
    (c1, "Total Suggestions", total_notes,   "#E8B547"),
    (c2, "Active",            active_notes,  "#7EC8E3"),
    (c3, "Warnings",          warn_count,    "#FFB300"),
    (c4, "Actions",           action_count,  "#FF6B6B"),
    (c5, "Applied",           applied_count, "#51CF66"),
]:
    col.markdown(
        f'<div style="background:#1E1B14;border-radius:8px;padding:12px;text-align:center;">'
        f'<div style="color:{color};font-size:28px;font-weight:700;">{val}</div>'
        f'<div style="color:#999;font-size:12px;">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("")

# last scan info + run button
col_ts, col_btn, col_mode = st.columns([3, 1, 1])
with col_ts:
    if ts:
        try:
            dt = datetime.fromisoformat(ts)
            age_min = int((datetime.now() - dt).total_seconds() / 60)
            st.caption(f"Last scan: {dt:%d %b %Y %H:%M} ({age_min} min ago) · Project: {proj}")
        except Exception:
            st.caption(f"Last scan: {ts}")
    else:
        st.caption("No scan yet. Click **Run Scan** to generate suggestions.")

with col_btn:
    if st.button("▶ Run Scan", use_container_width=True):
        _run_scan_background()
        st.info("Scan started in background. Refresh page in ~30 seconds to see results.")

with col_mode:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if st.session_state["scan_started"]:
    st.caption(f"Scan launched at {st.session_state['scan_started']}")

st.divider()

# ── tabs ───────────────────────────────────────────────────────────────
tab_table, tab_cards, tab_pipeline, tab_workers, tab_dismissed = st.tabs([
    "📋 Module Table", "🃏 Note Cards", "⚙ Pipeline", "👷 Workers", "🗑 Dismissed"
])


# ══════════════════════════════════════════════════════════════════════
# TAB 1 — MODULE TABLE (with AI Note column)
# ══════════════════════════════════════════════════════════════════════
with tab_table:
    from engines.skill_engine import MODULES as MODULE_REGISTRY

    st.markdown("### Module Table — AI Note Column")
    st.caption("Every module that has an AI suggestion is shown below. Use Apply / Dismiss / Ask AI per row.")

    # filter controls
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1:
        search_q = st.text_input("Search modules", placeholder="type module name...", label_visibility="collapsed")
    with fc2:
        sev_filter = st.selectbox("Severity", ["All", "action", "warn", "info"], label_visibility="collapsed")
    with fc3:
        show_empty = st.checkbox("Show modules with no note", value=False)

    # build rows
    rows = []
    for name, group, types, _ in MODULE_REGISTRY:
        note = notes.get(name)
        if not note and not show_empty:
            continue
        if name in st.session_state["dismissed"]:
            continue
        sev = note["sev"] if note else "—"
        if sev_filter != "All" and sev != sev_filter:
            continue
        if search_q and search_q.lower() not in name.lower():
            continue
        rows.append((name, group, types, note))

    if not rows:
        st.info("No notes match the current filter. Run a scan or adjust filters.")
    else:
        for name, group, types, note in rows:
            col_mod, col_sev, col_note, col_btns = st.columns([2, 1, 5, 2])

            with col_mod:
                applied_mark = " ✅" if name in st.session_state["applied"] else ""
                st.markdown(f"**{name}**{applied_mark}")
                st.caption(group)

            with col_sev:
                if note:
                    st.markdown(_badge(note["sev"]), unsafe_allow_html=True)
                    st.caption(note.get("worker", "")[:25])
                else:
                    st.markdown('<span style="color:#555;">—</span>', unsafe_allow_html=True)

            with col_note:
                if note:
                    color = _sev_color(note["sev"])
                    st.markdown(
                        f'<div class="note-card {note["sev"]}">'
                        f'<span style="color:{color};font-weight:600;">{note["text"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    # show refinement if available
                    if name in st.session_state["refinements"]:
                        with st.expander("AI Refinement", expanded=True):
                            st.markdown(st.session_state["refinements"][name])
                else:
                    st.caption("No suggestion yet")

            with col_btns:
                if note:
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if st.button("✅", key=f"apply_{name}", help="Mark Applied"):
                            st.session_state["applied"].add(name)
                            _acts = _load_actions()
                            _acts["applied"] = list(st.session_state["applied"])
                            _save_actions(_acts)
                            st.rerun()
                    with b2:
                        if st.button("✖", key=f"dismiss_{name}", help="Dismiss"):
                            st.session_state["dismissed"].add(name)
                            _acts = _load_actions()
                            _acts["dismissed"] = list(st.session_state["dismissed"])
                            _save_actions(_acts)
                            st.rerun()
                    with b3:
                        if st.button("🤖", key=f"ai_{name}", help="Ask AI to expand"):
                            with st.spinner("Asking AI..."):
                                ref = _ask_ai_refine(name, note["text"])
                                st.session_state["refinements"][name] = ref
                            st.rerun()

            st.markdown('<hr style="border:none;border-top:1px solid #2A2618;margin:2px 0;">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# TAB 2 — NOTE CARDS (visual card layout)
# ══════════════════════════════════════════════════════════════════════
with tab_cards:
    st.markdown("### Suggestion Cards")

    active_notes_list = [
        (m, n) for m, n in notes.items()
        if m not in st.session_state["dismissed"]
    ]
    if not active_notes_list:
        st.info("No active suggestions. Run a scan first.")
    else:
        # group by severity
        for sev_label, sev_key, icon in [
            ("Actions Required", "action", "→"),
            ("Warnings",         "warn",   "⚠"),
            ("Info",             "info",   "ℹ"),
        ]:
            group_notes = [(m, n) for m, n in active_notes_list if n.get("sev") == sev_key]
            if not group_notes:
                continue
            st.markdown(f"#### {icon} {sev_label} ({len(group_notes)})")
            cols = st.columns(3)
            for idx, (mod, note) in enumerate(group_notes):
                col = cols[idx % 3]
                with col:
                    color = _sev_color(sev_key)
                    applied = "✅ " if mod in st.session_state["applied"] else ""
                    st.markdown(
                        f'<div class="note-card {sev_key}" style="min-height:90px;">'
                        f'<div style="color:#E8B547;font-weight:700;font-size:13px;">{applied}{mod}</div>'
                        f'<div style="color:{color};font-size:13px;margin:4px 0;">{note["text"]}</div>'
                        f'<div style="color:#666;font-size:11px;">{note.get("worker","")}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    ba, bd = st.columns(2)
                    with ba:
                        if st.button("Apply", key=f"card_apply_{mod}"):
                            st.session_state["applied"].add(mod)
                            _acts = _load_actions()
                            _acts["applied"] = list(st.session_state["applied"])
                            _save_actions(_acts)
                            st.rerun()
                    with bd:
                        if st.button("Dismiss", key=f"card_dismiss_{mod}"):
                            st.session_state["dismissed"].add(mod)
                            _acts = _load_actions()
                            _acts["dismissed"] = list(st.session_state["dismissed"])
                            _save_actions(_acts)
                            st.rerun()


# ══════════════════════════════════════════════════════════════════════
# TAB 3 — PIPELINE PANEL
# ══════════════════════════════════════════════════════════════════════
with tab_pipeline:
    st.markdown("### Skill Engine Pipeline")
    st.caption("How suggestions are generated — 3-stage flow.")

    # Stage 1 — Inputs
    st.markdown("#### Stage 1 — Inputs")
    in1, in2, in3 = st.columns(3)
    for col, icon, label, desc in [
        (in1, "📂", "Project Context",  "Capacity, location, investment, product prices"),
        (in2, "📋", "Module Registry",  "55 portal modules with skill tags"),
        (in3, "🔑", "AI Config",        "Provider keys from data/ai_config.json"),
    ]:
        col.markdown(
            f'<div class="pipeline-box">'
            f'<div style="font-size:28px;">{icon}</div>'
            f'<div style="font-weight:700;">{label}</div>'
            f'<div style="color:#AAA;font-size:12px;margin-top:4px;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)

    # Stage 2 — Workers
    st.markdown("#### Stage 2 — Workers")
    w1, w2, w3, w4 = st.columns(4)
    worker_data = [
        (w1, "🖌", "Drawing Improver",  "drawing",
         ["Plant Design", "AI Plant Layouts", "AI Drawings", "Drawings", "Process Flow", "Three Process"],
         "#E8B547"),
        (w2, "💰", "Costing Optimizer", "costing",
         ["Raw Material", "Detailed Costing", "Working Capital", "Loan EMI", "Cash Flow 5-Year",
          "Break Even", "ROI Quick Calc", "Sensitivity", "State Profitability"],
         "#51CF66"),
        (w3, "📝", "Writeup Enhancer",  "writeup",
         ["Technology", "DPR Generator", "Market", "Compliance", "Environmental",
          "Meeting Planner", "Buyers", "NHAI Tenders"],
         "#7EC8E3"),
        (w4, "🔗", "Cross-Module Coord","all",
         ["All 55 modules", "Finds capacity mismatches", "Finds rate mismatches",
          "Flags stale data links"],
         "#FF6B6B"),
    ]
    for col, icon, name, tag, watches, color in worker_data:
        watch_html = "".join(f'<div style="color:#AAA;font-size:11px;">• {w}</div>' for w in watches[:4])
        col.markdown(
            f'<div class="worker-card">'
            f'<div style="font-size:24px;">{icon}</div>'
            f'<div style="color:{color};font-weight:700;font-size:14px;">{name}</div>'
            f'<div style="color:#777;font-size:11px;margin:2px 0 6px;">watches: {tag}</div>'
            f'{watch_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)

    # Stage 3 — Free AI Pool
    st.markdown("#### Stage 3 — Free AI Pool (failover chain)")
    ai_cols = st.columns(6)
    providers = [
        ("Groq",       "Llama 3.3 70B",       "#51CF66", "fastest"),
        ("Gemini",     "gemini-2.0-flash",     "#4285F4", "1M ctx"),
        ("OpenRouter", "Llama 3.3 free",       "#E8B547", "100+ models"),
        ("Cerebras",   "Llama 3.3 70B",        "#FF6B6B", "ultra fast"),
        ("Mistral",    "mistral-free",          "#AAA",   "EU privacy"),
        ("Offline",    "Built-in rules",        "#777",   "always on"),
    ]
    for col, (pname, model, color, note) in zip(ai_cols, providers):
        col.markdown(
            f'<div style="background:#1E1B14;border:1px solid {color};border-radius:6px;'
            f'padding:8px;text-align:center;">'
            f'<div style="color:{color};font-weight:700;font-size:13px;">{pname}</div>'
            f'<div style="color:#999;font-size:10px;">{model}</div>'
            f'<div style="color:#666;font-size:10px;">{note}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)

    # Stage 4 — Output
    st.markdown("#### Stage 4 — Output")
    o1, o2, o3 = st.columns(3)
    for col, icon, label, desc in [
        (o1, "💾", "data/notes.json",     "One suggestion per module, severity + worker tag"),
        (o2, "📊", "Module Table",         "AI Note column with Apply / Dismiss / Ask AI"),
        (o3, "🔄", "Auto-refresh",         "Re-run every 5 min with SKILL_MODE=loop"),
    ]:
        col.markdown(
            f'<div class="pipeline-box">'
            f'<div style="font-size:24px;">{icon}</div>'
            f'<div style="font-weight:700;">{label}</div>'
            f'<div style="color:#AAA;font-size:12px;margin-top:4px;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # notes.json preview
    with st.expander("📄 notes.json preview"):
        if notes:
            st.json({k: v for k, v in list(notes.items())[:5]})
        else:
            st.caption("No notes yet. Click Run Scan on the main header.")


# ══════════════════════════════════════════════════════════════════════
# TAB 4 — WORKER CARDS (detailed per-worker view)
# ══════════════════════════════════════════════════════════════════════
with tab_workers:
    st.markdown("### Worker Details")
    st.caption("See exactly which modules each worker covers and their current suggestion status.")

    worker_groups = {
        "🖌 Drawing Improver":   ("drawing-worker",          "#E8B547"),
        "💰 Costing Optimizer":  ("costing-worker",          "#51CF66"),
        "📝 Writeup Enhancer":   ("writeup-worker",          "#7EC8E3"),
        "🔗 Cross-Module Coord": ("cross-module-coordinator","#FF6B6B"),
    }

    for wlabel, (wkey, wcolor) in worker_groups.items():
        worker_notes = {m: n for m, n in notes.items() if n.get("worker") == wkey}
        with st.expander(f"{wlabel} — {len(worker_notes)} suggestions", expanded=False):
            if not worker_notes:
                st.caption("No suggestions from this worker yet.")
            else:
                rows_html = ""
                for mod, note in worker_notes.items():
                    icon = {"warn": "⚠", "action": "→", "info": "ℹ"}.get(note["sev"], "•")
                    color = _sev_color(note["sev"])
                    ts_short = note.get("generated_at", "")[:16].replace("T", " ")
                    rows_html += (
                        f"<tr>"
                        f"<td style='color:{wcolor};font-weight:600;'>{mod}</td>"
                        f"<td><span style='color:{color};'>{icon} {note['sev'].upper()}</span></td>"
                        f"<td>{note['text']}</td>"
                        f"<td style='color:#666;font-size:11px;'>{ts_short}</td>"
                        f"</tr>"
                    )
                st.markdown(
                    f"<table class='notes-table'>"
                    f"<tr><th>Module</th><th>Severity</th><th>Suggestion</th><th>Generated</th></tr>"
                    f"{rows_html}</table>",
                    unsafe_allow_html=True,
                )


# ══════════════════════════════════════════════════════════════════════
# TAB 5 — DISMISSED NOTES
# ══════════════════════════════════════════════════════════════════════
with tab_dismissed:
    st.markdown("### Dismissed Suggestions")
    dismissed_list = [
        (m, notes[m]) for m in st.session_state["dismissed"]
        if m in notes
    ]
    if not dismissed_list:
        st.info("No dismissed suggestions.")
    else:
        st.caption(f"{len(dismissed_list)} dismissed — click Restore to bring back.")
        for mod, note in dismissed_list:
            col_m, col_n, col_b = st.columns([2, 5, 1])
            with col_m:
                st.markdown(f"**{mod}**")
            with col_n:
                st.caption(note["text"])
            with col_b:
                if st.button("Restore", key=f"restore_{mod}"):
                    st.session_state["dismissed"].discard(mod)
                    _acts = _load_actions()
                    _acts["dismissed"] = list(st.session_state["dismissed"])
                    _save_actions(_acts)
                    st.rerun()

        if st.button("🗑 Clear All Dismissed"):
            st.session_state["dismissed"].clear()
            _acts = _load_actions()
            _acts["dismissed"] = []
            _save_actions(_acts)
            st.rerun()

# ── sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 Skill Engine")
    st.divider()

    if notes:
        st.markdown("**Last Scan Summary**")
        # severity distribution bar
        counts = {"action": 0, "warn": 0, "info": 0}
        for n in notes.values():
            counts[n.get("sev", "info")] = counts.get(n.get("sev", "info"), 0) + 1
        for sev, cnt in counts.items():
            color = _sev_color(sev)
            pct = int(cnt / max(total_notes, 1) * 100)
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;margin:2px 0;">'
                f'<span style="color:{color};">{sev.upper()}</span>'
                f'<span style="color:#E8B547;">{cnt}</span></div>'
                f'<div style="background:#2A2618;border-radius:4px;height:4px;">'
                f'<div style="background:{color};width:{pct}%;height:4px;border-radius:4px;"></div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("No notes yet.")

    st.divider()
    st.markdown("**Quick Actions**")
    if st.button("▶ Run Scan", key="sb_scan", use_container_width=True):
        _run_scan_background()
        st.info("Scan started.")

    st.divider()
    st.markdown("**Loop Mode**")
    st.code("SKILL_MODE=loop\npython -m engines.skill_engine", language="bash")
    st.caption("Runs every 5 min in background.")

    st.divider()
    st.markdown("**Applied Progress**")
    if total_notes > 0:
        pct = int(applied_count / total_notes * 100)
        st.progress(pct / 100, text=f"{applied_count}/{total_notes} applied ({pct}%)")
    else:
        st.caption("Run a scan to see progress.")
