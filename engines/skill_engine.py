"""
Skill Engine — Background AI workers for Bio Bitumen Consultant Portal
======================================================================
4 workers analyse every portal module and write one-line suggestions
to data/notes.json, which the Skill Engine page (87) reads live.

Workers:
  DrawingImprover      → layout / drawing modules
  CostingOptimizer     → financial / costing modules
  WriteupEnhancer      → document / writeup modules
  CrossModuleCoord     → audits ALL modules for inconsistencies

AI Failover: uses ask_ai() from ai_engine.py (Groq → Gemini → ... → offline)

Usage:
  python -m engines.skill_engine          # one-shot
  SKILL_MODE=loop python -m engines.skill_engine   # every 5 min

notes.json schema:
  {
    "scanned_at": "ISO",
    "project": "...",
    "notes": {
      "Module Name": {
        "sev": "info|warn|action",
        "text": "one-line suggestion",
        "actionable": bool,
        "worker": "...",
        "generated_at": "ISO"
      }
    }
  }
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent.parent
NOTES_PATH = _HERE / "data" / "notes.json"
CFG_PATH   = _HERE / "data" / "ai_config.json"

# ── Bio Bitumen module registry ────────────────────────────────────────
# (name, group, skill_types[], data_hints{})
# skill_types: "drawing" | "costing" | "writeup"  (empty = skip)
MODULES = [
    # ── ENGINEERING ───────────────────────────────────────────────────
    ("Plant Design",        "engineering", ["drawing"],
        {"area_note": "check L-shape vs rectangular for husk flow"}),
    ("AI Plant Layouts",    "engineering", ["drawing", "ai"],
        {"iterations": 3, "provider": "gemini"}),
    ("AI Drawings",         "engineering", ["drawing", "ai"],
        {"last_fail_check": "verify provider key status"}),
    ("Drawings",            "engineering", ["drawing"],
        {"check": "missing dimensions, north arrow, scale bar"}),
    ("Process Flow",        "engineering", ["drawing"],
        {"check": "step efficiency >= 0.80 at each stage"}),
    ("Three Process",       "engineering", ["drawing"],
        {"check": "all three bio-bitumen routes shown"}),
    ("Technology",          "engineering", ["writeup"],
        {"choice": "slow-pyrolysis + bio-binder upgrade"}),
    ("Raw Material",        "engineering", ["costing"],
        {"husk_rate": "Rs 2-4/kg, verify seasonal variation"}),
    ("Lab Testing",         "engineering", [],  {}),
    ("Product Grades",      "engineering", [],  {}),

    # ── FINANCIAL ─────────────────────────────────────────────────────
    ("Investment Optimizer","financial",   ["costing"],
        {"schemes": ["MSME-CGTMSE", "PMEGP", "State-IPS"]}),
    ("Detailed Costing",    "financial",   ["costing"],
        {"check": "GST on all line items, depreciation rate"}),
    ("Working Capital",     "financial",   ["costing"],
        {"check": "30-day husk buffer + 15-day AR cycle"}),
    ("Loan EMI",            "financial",   ["costing"],
        {"bench_rate": 8.5, "check": "floating vs fixed spread"}),
    ("Cash Flow 5-Year",    "financial",   ["costing"],
        {"check": "WC change synced in Year 3, terminal value"}),
    ("Break Even",          "financial",   ["costing"],
        {"bench": "break-even <= 60% utilisation for bankability"}),
    ("ROI Quick Calc",      "financial",   ["costing"],
        {"bench": "ROI 20-35%, IRR 26-36%"}),
    ("Capacity Compare",    "financial",   ["costing"],
        {"options": [25, 50, 100], "unit": "MT/day bio-bitumen"}),
    ("Sensitivity",         "financial",   ["costing"],
        {"check": "husk price +/-30%, bitumen price +/-20%"}),
    ("Financial",           "financial",   [],  {}),
    ("State Profitability", "financial",   ["costing"],
        {"check": "freight differential per state, VG-10 local price"}),

    # ── DOCUMENTS ─────────────────────────────────────────────────────
    ("DPR Generator",       "documents",   ["writeup"],
        {"check": "executive summary, promoter background, B/S"}),
    ("Vendor Emails",       "documents",   ["writeup"],
        {"check": "gmail OAuth, CC bank/consultant in thread"}),
    ("Project Standards",   "documents",   ["writeup"],
        {"check": "IS 73 compliance clause, BIS certif needed?"}),
    ("Send",                "documents",   ["writeup"],
        {"check": "email dispatch log, read receipt tracking"}),
    ("Document Hub",        "documents",   [],  {}),
    ("Export Center",       "documents",   [],  {}),

    # ── MARKET ────────────────────────────────────────────────────────
    ("Market",              "market",      ["writeup"],
        {"check": "state-wise road CAGR, NHAI pipeline demand"}),
    ("Competitor Intel",    "market",      [],
        {"check": "SerpAPI quota, last refresh date"}),
    ("News Feed",           "market",      [],  {}),
    ("Location",            "market",      [],
        {"check": "husk radius 50 km, road connectivity to NHAI"}),
    ("Buyers",              "market",      ["writeup"],
        {"check": "NHAI empanelled contractors list current?"}),

    # ── COMPLIANCE & RISK ─────────────────────────────────────────────
    ("Compliance",          "compliance",  ["writeup"],
        {"check": "state PCB consent, MSME Udyam, fire NOC"}),
    ("Environmental",       "compliance",  ["writeup"],
        {"check": "stack emission limits, ETP capacity vs effluent"}),
    ("Risk Matrix",         "compliance",  ["writeup"],
        {"check": "husk price risk, bitumen import parity risk"}),
    ("NHAI Tenders",        "compliance",  ["writeup"],
        {"check": "tender validity dates, technical bid clauses"}),

    # ── EXECUTION ─────────────────────────────────────────────────────
    ("Meeting Planner",     "execution",   ["writeup"],
        {"check": "banker MOM format, follow-up action list"}),
    ("Project Gantt",       "execution",   [],
        {"check": "civil milestone = 6 months, commissioning M14"}),
    ("Procurement",         "execution",   [],
        {"check": "4 quotes pending, preferred vendor shortlist"}),
    ("Timeline",            "execution",   [],  {}),

    # ── AI & TOOLS ────────────────────────────────────────────────────
    ("AI Full Consultant",  "ai_tools",    [],  {}),
    ("AI Advisor",          "ai_tools",    [],  {}),
    ("Guarantor AI",        "ai_tools",    [],  {}),
    ("PMC Files",           "ai_tools",    [],  {}),
    ("Nav Health",          "ai_tools",    [],  {}),

    # ── OTHER ─────────────────────────────────────────────────────────
    ("Presenter",           "other",       [],  {}),
    ("Dashboard",           "other",       [],  {}),
    ("Client Manager",      "other",       [],  {}),
    ("Project Setup",       "other",       [],  {}),
    ("Customers",           "other",       [],  {}),
    ("Analytics",           "other",       [],  {}),
    ("System Calculations", "other",       [],  {}),
    ("Advanced Tools",      "other",       [],  {}),
    ("AI Settings",         "other",       [],  {}),
    ("System Health",       "other",       [],  {}),
]


# ── load project context from ai_config.json ──────────────────────────

def _load_context():
    try:
        cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    except Exception:
        cfg = {}
    return {
        "name":      cfg.get("client_name", "Bio Bitumen Plant"),
        "capacity":  f"{cfg.get('capacity_tpd', 50)} TPD bio-bitumen",
        "location":  f"{cfg.get('location', 'India')}, {cfg.get('state', '')}".strip(", "),
        "stage":     "DPR Preparation",
        "budget":    f"INR {cfg.get('investment_cr', 6.5):.1f} Cr",
        "product":   "VG-10 (Rs 48k/MT) + PMB (Rs 72k/MT)",
        "biomass":   cfg.get("biomass_source", "Rice Husk"),
        "irr":       f"{cfg.get('irr_pct', 26)}%",
        "dscr":      f"{cfg.get('dscr_yr3', 1.35)}x",
        "audience":  ["Investors", "Banks (CMA)", "NHAI", "Govt schemes"],
    }


def _ctx_string():
    ctx = _load_context()
    lines = ["BIO BITUMEN PROJECT CONTEXT:"]
    for k, v in ctx.items():
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)


# ── AI call — delegates to ai_engine.ask_ai() ─────────────────────────

def _ask(prompt):
    """Try ai_engine ask_ai first, fall back to direct Groq/Gemini."""
    try:
        from engines.ai_engine import ask_ai
        return ask_ai(prompt, max_tokens=160)
    except Exception:
        pass
    # direct fallback (when run as script)
    import requests
    providers = [
        ("Groq",       "https://api.groq.com/openai/v1/chat/completions",
         "llama-3.3-70b-versatile", "GROQ_API_KEY"),
        ("Gemini",     "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
         "gemini-2.0-flash", "GEMINI_API_KEY"),
        ("OpenRouter", "https://openrouter.ai/api/v1/chat/completions",
         "meta-llama/llama-3.3-70b-instruct:free", "OPENROUTER_API_KEY"),
    ]
    for name, url, model, env in providers:
        key = os.getenv(env)
        if not key:
            continue
        try:
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model,
                      "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 160, "temperature": 0.3},
                timeout=25,
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except Exception:
            continue
    return None


def _parse(text):
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        return {"sev": "info", "text": text[:130]}


# ── skills ────────────────────────────────────────────────────────────

_JSON_INSTRUCTION = (
    'Reply ONLY in JSON: {"sev": "info|warn|action", "text": "one sentence max 90 chars"}'
)

_BASE = _ctx_string()


def _drawing_prompt(name, data):
    return f"""Senior plant-design engineer reviewing module '{name}'.
{_BASE}
Hints: {json.dumps(data)}
Suggest ONE concrete drawing/layout improvement. Mark warn/action if broken.
{_JSON_INSTRUCTION}"""


def _costing_prompt(name, data):
    return f"""CA + CMA expert reviewing financial module '{name}'.
{_BASE}
Hints: {json.dumps(data)}
Suggest ONE specific financial improvement (missing GST, outdated rate, govt scheme, etc.).
{_JSON_INSTRUCTION}"""


def _writeup_prompt(name, data):
    return f"""DPR writer for Indian banks/investors reviewing module '{name}'.
{_BASE}
Hints: {json.dumps(data)}
Suggest ONE concrete improvement to the write-up (missing clause, wrong tone, outdated info).
{_JSON_INSTRUCTION}"""


def _cross_prompt(all_mods):
    summary = "\n".join(
        f"- {n} ({g}): {json.dumps(d)}" for n, g, _, d in all_mods if d
    )
    return f"""Audit a Bio Bitumen DPR project for cross-module inconsistencies.
{_BASE}

MODULE SUMMARIES:
{summary}

Find up to 3 SPECIFIC inconsistencies (e.g. capacity in Plant Design vs Cash Flow).
Reply ONLY in JSON list:
[{{"module":"Name","sev":"warn","text":"one sentence max 90 chars"}}]
If nothing inconsistent, return []."""


SKILL_MAP = {
    "drawing": _drawing_prompt,
    "costing": _costing_prompt,
    "writeup": _writeup_prompt,
}


# ── engine ────────────────────────────────────────────────────────────

def run_scan(verbose=True):
    notes = {}
    ctx = _ctx_string()

    if verbose:
        print(f"\n[{datetime.now():%H:%M:%S}] Scanning {len(MODULES)} modules...")

    for i, (name, group, types, data) in enumerate(MODULES, 1):
        if not types:
            continue
        skill_type = next((t for t in ("drawing", "costing", "writeup") if t in types), None)
        if not skill_type:
            continue

        if verbose:
            print(f"  ({i:02d}) {name:<26} ", end="", flush=True)

        prompt = SKILL_MAP[skill_type](name, data)
        raw = _ask(prompt)
        parsed = _parse(raw)

        if parsed and isinstance(parsed, dict) and "text" in parsed:
            notes[name] = {
                "sev":          parsed.get("sev", "info"),
                "text":         parsed["text"][:130],
                "actionable":   parsed.get("sev") in ("warn", "action"),
                "worker":       f"{skill_type}-worker",
                "generated_at": datetime.now().isoformat(),
            }
            if verbose:
                icon = {"warn": "⚠", "action": "→", "info": "i"}.get(notes[name]["sev"], "•")
                print(f"{icon} {notes[name]['text'][:60]}")
        else:
            if verbose:
                print("✗ no response")

    # cross-module audit
    if verbose:
        print("\n  Cross-module audit...", end=" ", flush=True)
    raw = _ask(_cross_prompt(MODULES))
    conflicts = []
    if raw:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1].lstrip("json").strip()
        try:
            conflicts = json.loads(raw)
        except Exception:
            pass
    for c in conflicts:
        mod = c.get("module", "")
        if mod and mod not in notes:
            notes[mod] = {
                "sev":          c.get("sev", "warn"),
                "text":         c.get("text", "")[:130],
                "actionable":   True,
                "worker":       "cross-module-coordinator",
                "generated_at": datetime.now().isoformat(),
            }
    if verbose:
        print(f"found {len(conflicts)} inconsistencies")

    out = {
        "scanned_at": datetime.now().isoformat(),
        "project":    _load_context()["name"],
        "notes":      notes,
    }
    NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    NOTES_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    if verbose:
        print(f"\n  Saved {len(notes)} notes → data/notes.json\n")
    return out


def load_notes():
    """Read notes.json; returns {} if missing."""
    try:
        return json.loads(NOTES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ── CLI entry ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    mode = os.getenv("SKILL_MODE", "once")
    if mode == "loop":
        interval = int(os.getenv("SKILL_INTERVAL_SEC", "300"))
        print(f"Continuous mode — every {interval}s. Ctrl-C to stop.")
        while True:
            run_scan()
            time.sleep(interval)
    else:
        run_scan()
        print("Done. Set SKILL_MODE=loop to run continuously.")
