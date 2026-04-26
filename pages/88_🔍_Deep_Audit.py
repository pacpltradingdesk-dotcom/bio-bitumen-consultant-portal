"""
88 · Deep Audit — 167-Check Enterprise Health Dashboard
=========================================================
10 categories × 167 checks — score ring, category cards,
drill-down, filter tabs, activity stream.
Dark gold theme: #15130F / #E8B547
"""

import json
import sys
import threading
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import init_state, get_config

# ── paths ───────────────────────────────────────────────────────────────
_HERE         = Path(__file__).parent.parent
RESULTS_PATH  = _HERE / "data" / "audit_results.json"

st.set_page_config(
    page_title="Deep Audit · Bio Bitumen",
    page_icon="🔍",
    layout="wide",
)
init_state()
cfg = get_config()

# ── CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#15130F;}
[data-testid="stSidebar"]{background:#1A1710;}
h1,h2,h3,h4,label,.stMarkdown p,.stMarkdown li{color:#F0E6D3;}
.stButton>button{background:#E8B547;color:#15130F;font-weight:700;
  border:none;border-radius:6px;padding:6px 18px;}
.stButton>button:hover{background:#F5C842;}
[data-testid="stMetricValue"]{color:#E8B547 !important;}
[data-testid="stMetricLabel"]{color:#B09060 !important;}

.stat-card{background:#1E1B14;border:1px solid #3A3520;border-radius:10px;
  padding:18px 22px;text-align:center;}
.stat-num {font-size:2.4rem;font-weight:800;line-height:1.1;}
.stat-lbl {font-size:0.82rem;color:#9A8A6A;margin-top:2px;}

.cat-card {background:#1E1B14;border:1px solid #2E2B1F;border-radius:10px;
  padding:14px 16px;margin:4px 0;}
.cat-title{font-weight:700;font-size:1.05rem;color:#E8B547;margin-bottom:6px;}
.score-bar-bg{background:#2E2B1F;border-radius:4px;height:6px;width:100%;margin:4px 0 8px;}
.score-bar-fill{height:6px;border-radius:4px;transition:width .4s;}
.pill{display:inline-block;border-radius:10px;padding:1px 9px;
  font-size:11px;font-weight:600;margin:1px;}
.pill-pass{background:#1B3A25;color:#51CF66;}
.pill-warn{background:#3A2E00;color:#FFD43B;}
.pill-fail{background:#3A1010;color:#FF6B6B;}
.pill-fix {background:#1A1A3A;color:#74C0FC;}

.chk-row{padding:5px 8px;border-radius:4px;margin:2px 0;display:flex;align-items:flex-start;gap:8px;}
.chk-row.pass{background:#1B2A1E;}
.chk-row.warn{background:#2A2410;}
.chk-row.fail{background:#2A1414;}
.chk-id  {font-family:monospace;font-size:11px;color:#9A8A6A;min-width:40px;padding-top:1px;}
.chk-name{font-size:13px;color:#E0D4B8;flex:1;}
.chk-msg {font-size:12px;color:#9A8A6A;flex:2;}
.chk-icon{font-size:15px;min-width:20px;}

.stream-item{padding:6px 10px;border-left:3px solid #3A3520;margin:2px 0;
  border-radius:0 6px 6px 0;background:#1A1710;}
.stream-item.pass{border-left-color:#51CF66;}
.stream-item.warn{border-left-color:#FFD43B;}
.stream-item.fail{border-left-color:#FF6B6B;}
.stream-time{font-size:10px;color:#7A6A4A;}
.stream-txt {font-size:12px;color:#C8B88A;}

.ring-wrap{display:flex;flex-direction:column;align-items:center;
  justify-content:center;padding:10px 0;}
.trend-spark{display:flex;align-items:flex-end;gap:3px;height:50px;margin-top:8px;}
.spark-bar  {width:10px;border-radius:2px 2px 0 0;background:#E8B547;opacity:.7;}
</style>
""", unsafe_allow_html=True)

# ── helpers ─────────────────────────────────────────────────────────────

def load_results():
    try:
        return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def score_color(s):
    if s >= 80:
        return "#51CF66"
    if s >= 60:
        return "#FFD43B"
    return "#FF6B6B"


def status_icon(s):
    return {"pass": "✅", "warn": "⚠️", "fail": "❌"}.get(s, "❔")


def svg_ring(score, size=220):
    r = 80
    cx = cy = size // 2
    circ = 2 * 3.14159 * r
    dash = circ * score / 100
    gap  = circ - dash
    col  = score_color(score)
    return f"""
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <circle cx="{cx}" cy="{cy}" r="{r}"
    fill="none" stroke="#2E2B1F" stroke-width="14"/>
  <circle cx="{cx}" cy="{cy}" r="{r}"
    fill="none" stroke="{col}" stroke-width="14"
    stroke-dasharray="{dash:.1f} {gap:.1f}"
    stroke-linecap="round"
    transform="rotate(-90 {cx} {cy})"/>
  <text x="{cx}" y="{cy - 10}" text-anchor="middle"
    font-size="38" font-weight="800" fill="{col}">{score}</text>
  <text x="{cx}" y="{cy + 16}" text-anchor="middle"
    font-size="13" fill="#9A8A6A">/ 100</text>
  <text x="{cx}" y="{cy + 34}" text-anchor="middle"
    font-size="11" fill="#7A6A4A">Health Score</text>
</svg>"""


def spark_bars(history):
    if not history:
        return ""
    scores = [h["score"] for h in history[-15:]]
    mx = max(scores) if scores else 100
    bars = ""
    for s in scores:
        h = max(4, int(s / max(mx, 1) * 44))
        c = score_color(s)
        bars += f'<div class="spark-bar" style="height:{h}px;background:{c};opacity:.8;" title="{s}"></div>'
    return f'<div class="trend-spark">{bars}</div>'


CATEGORY_META = {
    "S": {"name": "Skill",    "color": "#7EC8E3"},
    "E": {"name": "Engine",   "color": "#51CF66"},
    "B": {"name": "Behavior", "color": "#FFD43B"},
    "R": {"name": "AI Reply", "color": "#E8B547"},
    "W": {"name": "Worker",   "color": "#A9E34B"},
    "K": {"name": "Backend",  "color": "#74C0FC"},
    "F": {"name": "Frontend", "color": "#B197FC"},
    "O": {"name": "Output",   "color": "#FF9999"},
    "A": {"name": "API",      "color": "#FF6B9D"},
    "P": {"name": "Pipeline", "color": "#63E6BE"},
}

# ── header ───────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="color:#E8B547;margin-bottom:2px;">🔍 Deep Audit</h1>
<p style="color:#9A8A6A;margin-top:0;">167 checks · 10 categories · Enterprise health monitoring</p>
""", unsafe_allow_html=True)

# ── controls ─────────────────────────────────────────────────────────────
btn_col, info_col = st.columns([3, 5])

with btn_col:
    run_col, ref_col = st.columns(2)
    with run_col:
        run_now = st.button("▶ Run Full Audit", type="primary", key="run_audit_btn")
    with ref_col:
        refresh = st.button("↻ Refresh", key="refresh_btn")

with info_col:
    data = load_results()
    if data.get("run_at"):
        try:
            ts = datetime.fromisoformat(data["run_at"])
            elapsed = data.get("elapsed_sec", 0)
            st.markdown(
                f'<p style="color:#9A8A6A;font-size:13px;padding-top:8px;">'
                f'Last run: <b style="color:#C8A84A;">{ts.strftime("%d %b %Y %H:%M")}</b> · '
                f'{elapsed:.1f}s · {data.get("total", 0)} checks</p>',
                unsafe_allow_html=True,
            )
        except Exception:
            pass
    else:
        st.markdown(
            '<p style="color:#7A6A4A;font-size:13px;padding-top:8px;">'
            'No audit data yet — click ▶ Run Full Audit</p>',
            unsafe_allow_html=True,
        )

# ── run audit ────────────────────────────────────────────────────────────
if run_now:
    with st.spinner("Running 167 checks across 10 categories… (30–60 s)"):
        try:
            from engines.audit_engine import run_full_audit
            data = run_full_audit(verbose=False)
            st.success(f"Audit complete — Score: {data['score']}/100")
        except Exception as ex:
            st.error(f"Audit engine error: {ex}")
    st.rerun()

if refresh:
    data = load_results()

st.markdown("---")

# ── guard: no data ────────────────────────────────────────────────────────
if not data:
    st.info("No audit results found. Click **▶ Run Full Audit** to start.")
    st.stop()

# ── HERO SECTION ──────────────────────────────────────────────────────────
score      = data.get("score", 0)
total      = data.get("total", 0)
passes     = data.get("pass", 0)
warns      = data.get("warn", 0)
fails      = data.get("fail", 0)
auto_fixed = data.get("auto_fixed", 0)
history    = data.get("history", [])
cat_scores = data.get("category_scores", {})
results    = data.get("results", [])

ring_col, stats_col = st.columns([1, 2])

with ring_col:
    st.markdown(
        f'<div class="ring-wrap">{svg_ring(score)}{spark_bars(history)}'
        f'<p style="font-size:11px;color:#7A6A4A;margin-top:6px;">'
        f'{len(history)} run{"s" if len(history) != 1 else ""} history</p></div>',
        unsafe_allow_html=True,
    )

with stats_col:
    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, num, lbl, clr in [
        (sc1, passes,     "Passing",    "#51CF66"),
        (sc2, warns,      "Warnings",   "#FFD43B"),
        (sc3, fails,      "Failing",    "#FF6B6B"),
        (sc4, auto_fixed, "Auto-Fixed", "#74C0FC"),
    ]:
        with col:
            st.markdown(
                f'<div class="stat-card">'
                f'<div class="stat-num" style="color:{clr};">{num}</div>'
                f'<div class="stat-lbl">{lbl}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # mini trend line
    if len(history) >= 2:
        trend_scores = [h["score"] for h in history[-10:]]
        trend_df = pd.DataFrame({"Run": list(range(1, len(trend_scores) + 1)),
                                  "Score": trend_scores})
        import plotly.graph_objects as go
        fig_trend = go.Figure(go.Scatter(
            x=trend_df["Run"], y=trend_df["Score"],
            mode="lines+markers",
            line=dict(color="#E8B547", width=2),
            marker=dict(color="#E8B547", size=5),
            fill="tozeroy",
            fillcolor="rgba(232,181,71,0.1)",
        ))
        fig_trend.update_layout(
            height=110, margin=dict(t=8, b=8, l=30, r=8),
            paper_bgcolor="#1E1B14", plot_bgcolor="#1E1B14",
            xaxis=dict(visible=False),
            yaxis=dict(range=[0, 100], tickfont=dict(color="#9A8A6A", size=9),
                       gridcolor="#2E2B1F"),
            showlegend=False,
        )
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")

# ── CATEGORY CARDS (2 × 5 grid) ──────────────────────────────────────────
st.markdown('<h3 style="color:#E8B547;">Category Breakdown</h3>', unsafe_allow_html=True)

cat_keys = list(CATEGORY_META.keys())
col_sets = [st.columns(5), st.columns(5)]

for i, ck in enumerate(cat_keys):
    row = i // 5
    col = i % 5
    meta = CATEGORY_META[ck]
    cs   = cat_scores.get(ck, {})
    cscore = cs.get("score", 0)
    cp     = cs.get("pass", 0)
    cw     = cs.get("warn", 0)
    cf     = cs.get("fail", 0)
    ct     = cs.get("total", cp + cw + cf) or 1
    col_color = score_color(cscore)
    bar_w  = cscore

    with col_sets[row][col]:
        st.markdown(
            f'<div class="cat-card">'
            f'<div class="cat-title" style="color:{meta["color"]};">'
            f'{ck} · {meta["name"]}</div>'
            f'<div style="font-size:1.6rem;font-weight:800;color:{col_color};">{cscore}</div>'
            f'<div class="score-bar-bg"><div class="score-bar-fill" '
            f'style="width:{bar_w}%;background:{col_color};"></div></div>'
            f'<span class="pill pill-pass">✓ {cp}</span>'
            f'<span class="pill pill-warn">⚠ {cw}</span>'
            f'<span class="pill pill-fail">✗ {cf}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── DRILL-DOWN per category ───────────────────────────────────────────────
st.markdown('<h3 style="color:#E8B547;">Drill-Down by Category</h3>', unsafe_allow_html=True)

# group results
grouped = {}
for r in results:
    grouped.setdefault(r["category"], []).append(r)

for ck in cat_keys:
    meta = CATEGORY_META[ck]
    cat_res = grouped.get(ck, [])
    if not cat_res:
        continue
    cs    = cat_scores.get(ck, {})
    cscore = cs.get("score", 0)
    cf    = cs.get("fail", 0)
    cw    = cs.get("warn", 0)
    label = f"{ck} · {meta['name']} — {cscore}/100  ({len(cat_res)} checks"
    label += f", {cf} fail" if cf else ""
    label += f", {cw} warn" if cw else ""
    label += ")"

    with st.expander(label, expanded=(cf > 0)):
        rows_html = ""
        for r in cat_res:
            s    = r["status"]
            icon = status_icon(s)
            fix_badge = (
                '<span class="pill pill-fix">auto-fixed</span>'
                if r.get("auto_fixed") else ""
            )
            rows_html += (
                f'<div class="chk-row {s}">'
                f'<span class="chk-icon">{icon}</span>'
                f'<span class="chk-id">{r["id"]}</span>'
                f'<span class="chk-name">{r["name"]}{fix_badge}</span>'
                f'<span class="chk-msg">{r.get("message","")}</span>'
                f'</div>'
            )
        st.markdown(rows_html, unsafe_allow_html=True)

st.markdown("---")

# ── FILTER TABS ───────────────────────────────────────────────────────────
st.markdown('<h3 style="color:#E8B547;">All Checks — Filter View</h3>', unsafe_allow_html=True)

tab_all, tab_fail, tab_warn, tab_pass, tab_crit = st.tabs(
    ["All", f"❌ Failed ({fails})", f"⚠️ Warned ({warns})",
     f"✅ Passed ({passes})", "🔥 Critical Only"]
)

def render_check_table(items):
    if not items:
        st.info("No checks in this filter.")
        return
    rows = []
    for r in items:
        rows.append({
            "ID":       r["id"],
            "Cat":      r["category"],
            "Check":    r["name"],
            "Status":   r["status"].upper(),
            "Message":  r.get("message", ""),
            "Fixed":    "✔" if r.get("auto_fixed") else "",
        })
    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=min(400, 36 + len(rows) * 35),
    )
    st.download_button(
        "⬇ Download CSV",
        df.to_csv(index=False),
        file_name=f"audit_filter_{datetime.now():%Y%m%d_%H%M}.csv",
        mime="text/csv",
        key=f"dl_csv_{id(items)}",
    )

with tab_all:
    render_check_table(results)

with tab_fail:
    render_check_table([r for r in results if r["status"] == "fail"])

with tab_warn:
    render_check_table([r for r in results if r["status"] == "warn"])

with tab_pass:
    render_check_table([r for r in results if r["status"] == "pass"])

with tab_crit:
    # Critical = fail in K (backend), A (api), P (pipeline) categories
    crit = [r for r in results if r["status"] == "fail" and r["category"] in ("K", "A", "P", "E")]
    render_check_table(crit)

st.markdown("---")

# ── ACTIVITY STREAM ───────────────────────────────────────────────────────
st.markdown('<h3 style="color:#E8B547;">Recent Activity Stream</h3>', unsafe_allow_html=True)

# Show last 30 results sorted by ts (most recent first)
recent = sorted(results, key=lambda r: r.get("ts", ""), reverse=True)[:30]

stream_html = ""
for r in recent:
    s   = r["status"]
    ts  = r.get("ts", "")[:16].replace("T", " ") if r.get("ts") else ""
    txt = f'[{r["id"]}] {r["name"]} — {r.get("message","")}'
    stream_html += (
        f'<div class="stream-item {s}">'
        f'<span class="stream-time">{ts}</span> '
        f'<span class="stream-txt">{status_icon(s)} {txt}</span>'
        f'</div>'
    )

st.markdown(stream_html, unsafe_allow_html=True)

# ── sidebar summary ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
<div style="background:#1E1B14;border:1px solid #3A3520;border-radius:8px;
  padding:14px 12px;margin-bottom:12px;">
  <div style="color:#E8B547;font-weight:700;font-size:1.1rem;">Audit Score</div>
  <div style="font-size:2.6rem;font-weight:900;color:{score_color(score)};">{score}</div>
  <div style="color:#9A8A6A;font-size:0.8rem;">/ 100 health points</div>
  <hr style="border-color:#3A3520;margin:8px 0;">
  <div style="font-size:12px;color:#B09060;">
    ✅ {passes} passing<br>
    ⚠️ {warns} warnings<br>
    ❌ {fails} failing<br>
    🔧 {auto_fixed} auto-fixed
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("**Category scores:**")
    for ck, meta in CATEGORY_META.items():
        cs = cat_scores.get(ck, {})
        s  = cs.get("score", 0)
        bar = int(s / 10)
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin:2px 0;">'
            f'<span style="color:{meta["color"]};font-weight:700;min-width:24px;">{ck}</span>'
            f'<span style="color:#9A8A6A;font-size:12px;min-width:66px;">{meta["name"]}</span>'
            f'<span style="color:{score_color(s)};font-weight:600;font-size:13px;">{s}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if st.button("Print Report", key="print_audit"):
        import streamlit.components.v1 as _stc
        _stc.html("<script>window.print();</script>", height=0)

# ── export ────────────────────────────────────────────────────────────────
st.markdown("---")
ex1, ex2 = st.columns(2)
with ex1:
    if results:
        df_all = pd.DataFrame([{
            "ID": r["id"], "Category": r["category"],
            "Check": r["name"], "Status": r["status"],
            "Message": r.get("message", ""),
            "Auto-Fixed": r.get("auto_fixed", False),
            "Timestamp": r.get("ts", ""),
        } for r in results])
        try:
            import io
            from openpyxl import Workbook
            wb = Workbook(); ws = wb.active; ws.title = "Deep Audit"
            ws.append(list(df_all.columns))
            for row in df_all.itertuples(index=False):
                ws.append(list(row))
            buf = io.BytesIO(); wb.save(buf)
            st.download_button(
                "Download Excel",
                buf.getvalue(),
                file_name=f"deep_audit_{datetime.now():%Y%m%d}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_xl_88",
                type="primary",
            )
        except Exception:
            st.download_button(
                "Download CSV",
                df_all.to_csv(index=False),
                file_name=f"deep_audit_{datetime.now():%Y%m%d}.csv",
                mime="text/csv",
                key="dl_csv_88",
            )

with ex2:
    if st.button("Print", key="exp_prt_88"):
        import streamlit.components.v1 as _stc
        _stc.html("<script>window.print();</script>", height=0)

# ── AI assist ─────────────────────────────────────────────────────────────
try:
    from engines.ai_engine import is_ai_available, ask_ai
    if is_ai_available():
        with st.expander("AI Assist — Audit Interpretation"):
            if st.button("Generate AI Summary", type="primary", key="ai_88"):
                top_fails = [r["name"] for r in results if r["status"] == "fail"][:5]
                prompt = (
                    f"Bio-bitumen portal deep audit: score {score}/100, "
                    f"{passes} passing, {warns} warnings, {fails} failing. "
                    f"Top failures: {', '.join(top_fails) if top_fails else 'none'}. "
                    "Summarise what needs fixing most urgently in 3 bullet points. "
                    "Professional consultant format."
                )
                with st.spinner("AI working…"):
                    resp, prov = ask_ai(prompt, "Senior system auditor.")
                if resp:
                    st.markdown(f"**via {prov.upper()}:**")
                    st.markdown(resp)
except Exception:
    pass

# ── next steps ────────────────────────────────────────────────────────────
try:
    from engines.page_navigation import add_next_steps
    add_next_steps(st, "88")
except Exception:
    pass
