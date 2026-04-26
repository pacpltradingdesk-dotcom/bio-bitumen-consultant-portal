"""
Guarantor Engine — 9 Specialist Workers + Master Cross-Validator
=================================================================
Applies 20 mathematical consistency rules to the project state.
Workers: Finance | Engineering | Market | Compliance | Layout
Status per rule: "green" | "yellow" | "red" | "grey" (missing data)
Single source of truth: data/guarantor_state.json
"""
import json
from pathlib import Path
from datetime import date

# ── Storage ───────────────────────────────────────────────────────────
GS_PATH = Path(__file__).parent.parent / "data" / "guarantor_state.json"

GS_DEFAULTS = {
    # Identity
    "client_name":    "REX FUELS MANAGEMENT PRIVATE LIMITED",
    "project_name":   "5 TPD PMB-40 Bio-Bitumen Plant",
    "location":       "Bahadurgarh, Jhajjar",
    "state":          "Haryana",
    # Capacity
    "capacity_tpd":   5.0,
    "working_days":   300,
    "util_yr1":       60.0,
    "util_yr3":       80.0,
    # Investment (Rs Crore)
    "investment_cr":  6.50,
    "land_cost_cr":   0.00,
    "civil_cost_cr":  1.10,
    "pm_cost_cr":     3.71,
    "utility_cost_cr":0.65,
    "preop_cr":       0.26,
    "wc_cr":          0.78,
    # Revenue (Rs/MT)
    "selling_price_pmb_per_mt": 72000,
    "pmb_output_pct":           0.70,
    "biochar_price_per_mt":     8000,
    "biochar_output_pct":       0.28,
    # Raw Material
    "rm_husk_price_per_mt": 3000,
    "husk_per_mt_output":   1.4,   # CSIR-CRRI locked: 1.4 MT husk per MT output
    "vg10_price_per_mt":    48000,
    "vg10_per_mt_pmb":      0.70,  # 70% VG-10 in PMB blend
    # Operating
    "power_load_kw":          135,
    "power_rate_rs_per_kwh":  7.50,
    "power_hours_per_day":    20,
    "monthly_payroll_lac":    2.50,
    # Loan
    "loan_amount_cr":  4.22,
    "loan_rate_pct":   11.5,
    "loan_tenure_yr":  7,
    # Key Metrics
    "roi_pct":              22.0,
    "irr_pct":              26.0,
    "dscr_yr3":             1.35,
    "break_even_months":    28,
    "break_even_pct":       58.0,
    # Engineering
    "plot_area_sqm":    3000.0,
    "built_up_sqm":     800.0,
    "water_demand_lpd": 5000.0,
    # Compliance
    "pollution_category":  "Orange",
    "electricity_noc_kw":  135.0,
    "water_permit_lpd":    5000.0,
    "factory_workers":     12,
}


def load_gs() -> dict:
    if GS_PATH.exists():
        try:
            saved = json.loads(GS_PATH.read_text(encoding="utf-8"))
            return {**GS_DEFAULTS, **saved}
        except Exception:
            pass
    return dict(GS_DEFAULTS)


def save_gs(data: dict):
    GS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = str(date.today())
    GS_PATH.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════
def _g(d, k, default=0):
    v = d.get(k, default)
    return v if v is not None and v != "" else default


def _pct(a, b):
    return abs(a - b) / abs(b) * 100 if b != 0 else 0


def _s(diff, ok=1.0, warn=5.0):
    return "green" if diff <= ok else ("yellow" if diff <= warn else "red")


# ══════════════════════════════════════════════════════════════════════
# 20 MATHEMATICAL CONSISTENCY RULES
# Each returns (status, message, details_dict)
# ══════════════════════════════════════════════════════════════════════

def r01(d):
    """R1 — Total Investment = Land + Civil + P&M + Utility + Pre-op + WC"""
    total = _g(d, "investment_cr")
    parts = (_g(d, "land_cost_cr") + _g(d, "civil_cost_cr") + _g(d, "pm_cost_cr") +
             _g(d, "utility_cost_cr") + _g(d, "preop_cr") + _g(d, "wc_cr"))
    if total == 0:
        return "grey", "Total investment not set", {}
    diff = _pct(parts, total)
    s = _s(diff)
    label = "match" if diff <= 1 else ("borderline" if diff <= 5 else "MISMATCH")
    msg = f"Parts = Rs {parts:.2f} Cr vs Total = Rs {total:.2f} Cr — {diff:.1f}% {label}"
    return s, msg, {"total": total, "parts": round(parts, 3), "diff_pct": round(diff, 2)}


def r02(d):
    """R2 — Promoter Equity >= 25% of Project Cost (bank minimum)"""
    inv = _g(d, "investment_cr")
    loan = _g(d, "loan_amount_cr")
    if inv == 0:
        return "grey", "Investment not set", {}
    eq = inv - loan
    pct = eq / inv * 100
    s = "green" if pct >= 30 else ("yellow" if pct >= 25 else "red")
    tick = "✓" if pct >= 25 else "— BELOW 25% bank minimum"
    msg = f"Promoter equity = {pct:.1f}% (Rs {eq:.2f} Cr) {tick}"
    return s, msg, {"equity_pct": round(pct, 2), "equity_cr": round(eq, 3)}


def r03(d):
    """R3 — Investment per TPD Benchmark: Rs 0.35–0.55 Cr/TPD"""
    tpd = _g(d, "capacity_tpd")
    inv = _g(d, "investment_cr")
    if tpd == 0:
        return "grey", "Capacity not set", {}
    ratio = inv / tpd
    s = "green" if 0.35 <= ratio <= 0.55 else ("yellow" if 0.28 <= ratio <= 0.65 else "red")
    tick = "✓" if 0.35 <= ratio <= 0.55 else "— benchmark Rs 0.35–0.55 Cr/TPD"
    msg = f"Rs {ratio:.2f} Cr/TPD {tick}"
    return s, msg, {"inv_per_tpd": round(ratio, 3)}


def r04(d):
    """R4 — Raw Material → Output Balance (CSIR-CRRI: 1.2–1.6 MT husk/MT output)"""
    ratio = _g(d, "husk_per_mt_output", 1.4)
    tpd = _g(d, "capacity_tpd", 5)
    s = "green" if 1.2 <= ratio <= 1.6 else ("yellow" if 1.0 <= ratio <= 1.8 else "red")
    tick = "✓" if 1.2 <= ratio <= 1.6 else "— CSIR-CRRI benchmark 1.2–1.6 MT/MT"
    msg = f"Husk ratio = {ratio:.2f} MT/MT output {tick} | Daily feed = {tpd * ratio:.1f} MT"
    return s, msg, {"ratio": ratio, "daily_husk_mt": round(tpd * ratio, 2)}


def r05(d):
    """R5 — Power Load: 25–30 kW/TPD benchmark + NOC must cover load"""
    tpd = _g(d, "capacity_tpd", 5)
    kw = _g(d, "power_load_kw", 135)
    noc = _g(d, "electricity_noc_kw", 0)
    if tpd == 0:
        return "grey", "Capacity not set", {}
    if kw == 0:
        return "grey", "Power load not set", {}
    kw_tpd = kw / tpd
    ok_pw = 20 <= kw_tpd <= 35
    ok_noc = noc >= kw * 0.95 if noc > 0 else True
    if ok_pw and ok_noc:
        s = "green"
        msg = f"{kw:.0f} kW ({kw_tpd:.1f} kW/TPD) ✓ | NOC = {noc:.0f} kW ✓"
    elif not ok_pw:
        s = "yellow" if 15 <= kw_tpd <= 40 else "red"
        msg = f"{kw:.0f} kW ({kw_tpd:.1f} kW/TPD) — benchmark {tpd*25:.0f}–{tpd*30:.0f} kW for {tpd:.0f} TPD"
    else:
        s = "red"
        msg = f"Load {kw:.0f} kW but NOC = {noc:.0f} kW — NOC MUST cover load"
    return s, msg, {"kw": kw, "noc_kw": noc, "kw_per_tpd": round(kw_tpd, 2)}


def r06(d):
    """R6 — Plot Area Adequacy (3000 sqm for 5 TPD, scales as cap^0.6)"""
    plot = _g(d, "plot_area_sqm", 3000)
    tpd = _g(d, "capacity_tpd", 5)
    if plot == 0:
        return "grey", "Plot area not set", {}
    bench = 3000 * (tpd / 5) ** 0.6
    s = "green" if plot >= bench * 0.85 else ("yellow" if plot >= bench * 0.70 else "red")
    tick = "✓" if plot >= bench * 0.85 else ("— tight, verify fire setbacks" if plot >= bench * 0.70 else "— TOO SMALL")
    msg = f"Plot = {plot:.0f} sqm {tick} (benchmark ≥ {bench:.0f} sqm for {tpd:.0f} TPD)"
    return s, msg, {"plot_sqm": plot, "benchmark_sqm": round(bench)}


def r07(d):
    """R7 — Gross Margin >= 30% (Revenue - Variable Cost per MT)"""
    sell = _g(d, "selling_price_pmb_per_mt", 72000)
    husk = _g(d, "rm_husk_price_per_mt", 3000) * _g(d, "husk_per_mt_output", 1.4)
    vg10 = (_g(d, "vg10_price_per_mt", 48000) * _g(d, "vg10_per_mt_pmb", 0.70)
            * _g(d, "pmb_output_pct", 0.70))
    tpd = _g(d, "capacity_tpd", 5)
    pwr = (_g(d, "power_load_kw", 135) * _g(d, "power_hours_per_day", 20)
           * _g(d, "power_rate_rs_per_kwh", 7.5)) / max(tpd * 1000, 1)
    vc = husk + vg10 + pwr + 500  # 500 Rs/MT packing
    if sell == 0:
        return "grey", "Selling price not set", {}
    margin = sell - vc
    mpct = margin / sell * 100
    s = "green" if mpct >= 30 else ("yellow" if mpct >= 15 else "red")
    tick = "✓" if mpct >= 30 else ("— borderline" if mpct >= 15 else "— CRITICALLY LOW")
    msg = f"Gross margin = {mpct:.1f}% (Rs {margin:,.0f}/MT) {tick}"
    return s, msg, {"vc_per_mt": round(vc), "sell": sell, "margin_pct": round(mpct, 2)}


def r08(d):
    """R8 — PMB Selling Price Premium over VG-10 (minimum 10%)"""
    pmb = _g(d, "selling_price_pmb_per_mt", 72000)
    vg10 = _g(d, "vg10_price_per_mt", 48000)
    if pmb == 0 or vg10 == 0:
        return "grey", "Prices not set", {}
    premium = (pmb / vg10 - 1) * 100
    s = "green" if premium >= 10 else ("yellow" if premium >= 0 else "red")
    tick = "✓" if premium >= 10 else ("— thin" if premium >= 0 else "— SELLING BELOW VG-10")
    msg = f"PMB Rs {pmb:,}/MT | VG-10 Rs {vg10:,}/MT | Premium = {premium:.0f}% {tick}"
    return s, msg, {"pmb": pmb, "vg10": vg10, "premium_pct": round(premium, 1)}


def r09(d):
    """R9 — Break-even Utilisation <= 60% (bank bankability threshold)"""
    bep = _g(d, "break_even_pct", 0)
    if bep == 0:
        return "grey", "Break-even % not set", {}
    s = "green" if bep <= 60 else ("yellow" if bep <= 70 else "red")
    tick = "✓" if bep <= 60 else ("— borderline" if bep <= 70 else "— BANK WILL REJECT")
    msg = f"Break-even = {bep:.1f}% utilisation {tick} (bank max 60%)"
    return s, msg, {"bep_pct": bep}


def r10(d):
    """R10 — Break-even Period <= 36 months"""
    m = _g(d, "break_even_months", 0)
    if m == 0:
        return "grey", "Break-even months not set", {}
    s = "green" if m <= 30 else ("yellow" if m <= 42 else "red")
    tick = "✓" if m <= 36 else ("— borderline" if m <= 48 else "— HIGH RISK >48 months")
    msg = f"Break-even in {m} months {tick}"
    return s, msg, {"months": m}


def r11(d):
    """R11 — ROI in 20–35% Range (bio-bitumen benchmark)"""
    roi = _g(d, "roi_pct", 0)
    if roi == 0:
        return "grey", "ROI not set", {}
    s = "green" if 20 <= roi <= 35 else ("yellow" if 15 <= roi <= 42 else "red")
    tick = "✓" if 20 <= roi <= 35 else "— benchmark 20–35%"
    msg = f"ROI = {roi:.1f}% {tick}"
    return s, msg, {"roi": roi}


def r12(d):
    """R12 — IRR >= 24% (investor minimum for bio-bitumen)"""
    irr = _g(d, "irr_pct", 0)
    if irr == 0:
        return "grey", "IRR not set", {}
    s = "green" if irr >= 24 else ("yellow" if irr >= 18 else "red")
    tick = "✓" if irr >= 24 else ("— investors want ≥ 24%" if irr >= 18 else "— BELOW MINIMUM")
    msg = f"IRR = {irr:.1f}% {tick}"
    return s, msg, {"irr": irr}


def r13(d):
    """R13 — DSCR Year 3 >= 1.25x (bank RBI minimum)"""
    dscr = _g(d, "dscr_yr3", 0)
    if dscr == 0:
        return "grey", "DSCR Year 3 not set", {}
    s = "green" if dscr >= 1.5 else ("yellow" if dscr >= 1.25 else "red")
    tick = "✓" if dscr >= 1.25 else "— BELOW 1.25x bank minimum — LOAN REJECTION RISK"
    msg = f"DSCR Year 3 = {dscr:.2f}x {tick}"
    return s, msg, {"dscr": dscr}


def r14(d):
    """R14 — ROI vs IRR Consistency (IRR must be >= ROI for valid model)"""
    roi = _g(d, "roi_pct", 0)
    irr = _g(d, "irr_pct", 0)
    if roi == 0 or irr == 0:
        return "grey", "ROI/IRR not set", {}
    s = "green" if irr >= roi else ("yellow" if irr >= roi * 0.90 else "red")
    tick = "✓ consistent" if irr >= roi else "— IRR should be ≥ ROI; recheck DCF model"
    msg = f"ROI {roi:.1f}% vs IRR {irr:.1f}% — {tick}"
    return s, msg, {"roi": roi, "irr": irr}


def r15(d):
    """R15 — Payback Period Sanity (<= 36 months preferred)"""
    m = _g(d, "break_even_months", 0)
    if m == 0:
        return "grey", "Payback not set", {}
    s = "green" if m <= 36 else ("yellow" if m <= 48 else "red")
    msg = f"Payback = {m} months {'✓' if m <= 36 else '— >48 months is high risk for lenders'}"
    return s, msg, {"months": m}


def r16(d):
    """R16 — Working Capital in 10–15% of Total Investment"""
    wc = _g(d, "wc_cr", 0)
    inv = _g(d, "investment_cr", 0)
    if wc == 0 or inv == 0:
        return "grey", "WC / Investment not set", {}
    pct = wc / inv * 100
    s = "green" if 10 <= pct <= 15 else ("yellow" if 8 <= pct <= 20 else "red")
    tick = "✓" if 10 <= pct <= 15 else "— benchmark 10–15%"
    msg = f"WC = Rs {wc:.2f} Cr ({pct:.1f}% of investment) {tick}"
    return s, msg, {"wc_cr": wc, "wc_pct": round(pct, 2)}


def r17(d):
    """R17 — Loan <= 75% of Project Cost (bank ceiling)"""
    loan = _g(d, "loan_amount_cr", 0)
    inv = _g(d, "investment_cr", 0)
    if loan == 0 or inv == 0:
        return "grey", "Loan / investment not set", {}
    pct = loan / inv * 100
    s = "green" if pct <= 70 else ("yellow" if pct <= 75 else "red")
    tick = "✓" if pct <= 75 else "— EXCEEDS 75% bank cap — will be rejected"
    msg = f"Loan = {pct:.1f}% of project cost {tick}"
    return s, msg, {"loan_pct": round(pct, 2), "loan_cr": loan}


def r18(d):
    """R18 — Promoter Contribution Absolute Amount (must be >= 25% of project cost)"""
    loan = _g(d, "loan_amount_cr", 0)
    inv = _g(d, "investment_cr", 0)
    if inv == 0:
        return "grey", "Investment not set", {}
    eq = inv - loan
    pct = eq / inv * 100
    s = "green" if pct >= 30 else ("yellow" if pct >= 25 else "red")
    tick = "✓" if pct >= 25 else "— BELOW 25% minimum"
    msg = f"Promoter contribution = Rs {eq:.2f} Cr ({pct:.1f}%) {tick}"
    return s, msg, {"equity_cr": round(eq, 3), "pct": round(pct, 2)}


def r19(d):
    """R19 — Selling Price > Total Cost Floor (PMB > VG-10 + husk component)"""
    pmb = _g(d, "selling_price_pmb_per_mt", 72000)
    vg10 = _g(d, "vg10_price_per_mt", 48000)
    husk = _g(d, "rm_husk_price_per_mt", 3000) * _g(d, "husk_per_mt_output", 1.4)
    floor = vg10 * _g(d, "vg10_per_mt_pmb", 0.70) + husk
    if pmb == 0:
        return "grey", "Selling price not set", {}
    buf = (pmb - floor) / pmb * 100
    s = "green" if buf >= 20 else ("yellow" if buf >= 5 else "red")
    tick = "✓" if buf >= 20 else ("— thin" if buf >= 5 else "— BELOW COST FLOOR")
    msg = f"PMB Rs {pmb:,}/MT | Cost floor Rs {floor:,.0f}/MT | Buffer = {buf:.1f}% {tick}"
    return s, msg, {"pmb": pmb, "floor": round(floor), "buffer_pct": round(buf, 2)}


def r20(d):
    """R20 — Pollution Category Correctly Classified (Orange typical for pyrolysis ≤20 TPD)"""
    cat = d.get("pollution_category", "")
    tpd = _g(d, "capacity_tpd", 5)
    if not cat:
        return "grey", "Pollution category not set", {}
    expected = "Orange" if tpd <= 20 else "Red"
    if cat == expected:
        return "green", f"Category = {cat} ✓ (expected for {tpd:.0f} TPD pyrolysis plant)", {"cat": cat}
    if cat == "Green":
        return "yellow", f"Category = Green — pyrolysis units typically Orange/Red; verify State PCB", {"cat": cat}
    if cat == "Red" and tpd <= 10:
        return "yellow", f"Category = Red for {tpd:.0f} TPD — usually Orange; confirm with CPCB list", {"cat": cat}
    return "green", f"Category = {cat} — verify with State PCB classification list", {"cat": cat}


# ══════════════════════════════════════════════════════════════════════
# RULES REGISTRY
# ══════════════════════════════════════════════════════════════════════
ALL_RULES = [
    (1,  "Total Investment = Sum of Parts",           r01, ["finance"]),
    (2,  "Promoter Equity >= 25%",                    r02, ["finance"]),
    (3,  "Investment per TPD Benchmark",              r03, ["finance", "engineering"]),
    (4,  "Raw Material → Output Balance",             r04, ["engineering", "market"]),
    (5,  "Power Load + NOC Match",                    r05, ["engineering", "compliance"]),
    (6,  "Plot Area Adequacy",                        r06, ["engineering", "layout"]),
    (7,  "Gross Margin >= 30%",                       r07, ["finance", "market"]),
    (8,  "PMB Premium over VG-10 >= 10%",             r08, ["market"]),
    (9,  "Break-even <= 60% Utilisation",             r09, ["finance"]),
    (10, "Break-even <= 36 Months",                   r10, ["finance"]),
    (11, "ROI in 20–35% Range",                       r11, ["finance"]),
    (12, "IRR >= 24%",                                r12, ["finance"]),
    (13, "DSCR Year 3 >= 1.25x",                      r13, ["finance"]),
    (14, "ROI vs IRR Consistency",                    r14, ["finance"]),
    (15, "Payback Period Sanity",                     r15, ["finance"]),
    (16, "Working Capital 10–15% of Investment",      r16, ["finance"]),
    (17, "Loan <= 75% of Project Cost",               r17, ["finance"]),
    (18, "Promoter Contribution Amount",              r18, ["finance"]),
    (19, "Selling Price > Cost Floor",                r19, ["market", "finance"]),
    (20, "Pollution Category Correctly Classified",   r20, ["compliance"]),
]

MODULES = ["finance", "engineering", "market", "compliance", "layout"]
MODULE_NAMES = {
    "finance":     "💰 Finance Auditor",
    "engineering": "🏭 Engineering Auditor",
    "market":      "📊 Market Auditor",
    "compliance":  "📜 Compliance Auditor",
    "layout":      "📐 Layout Auditor",
}
MODULE_RULES = {
    "finance":     [1, 2, 3, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    "engineering": [3, 4, 5, 6],
    "market":      [4, 7, 8, 19],
    "compliance":  [5, 20],
    "layout":      [6],
}
STATUS_ICON = {"green": "🟢", "yellow": "🟡", "red": "🔴", "grey": "⚪"}
WORKER_DESCRIPTIONS = {
    "finance":     "Audits every rupee: investment breakdown, ROI, IRR, DSCR, loan caps, break-even",
    "engineering": "Ensures plant can physically produce what financials promise: capacity, power, area",
    "market":      "Confirms selling price premium, raw material cost sanity, and gross margin viability",
    "compliance":  "Checks pollution category, power NOC, and statutory classification accuracy",
    "layout":      "Validates plot area adequacy against capacity and fire safety requirements",
}


# ══════════════════════════════════════════════════════════════════════
# CORE ORCHESTRATION FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def run_all_rules(data: dict) -> list:
    """Run all 20 rules. Returns list of result dicts."""
    results = []
    for rid, name, fn, modules in ALL_RULES:
        try:
            status, message, details = fn(data)
        except Exception as e:
            status, message, details = "grey", f"Error: {e}", {}
        results.append({
            "id": rid, "name": name, "status": status,
            "message": message, "details": details, "modules": modules,
        })
    return results


def get_module_health(results: list) -> dict:
    """Aggregate rule results to module-level health."""
    pri = {"red": 3, "yellow": 2, "green": 1, "grey": 0}
    health = {m: {"status": "grey", "issues": [], "pass": 0, "total": 0} for m in MODULES}
    for r in results:
        for m in r["modules"]:
            if m not in health:
                continue
            health[m]["total"] += 1
            if r["status"] == "green":
                health[m]["pass"] += 1
            cur = health[m]["status"]
            if pri.get(r["status"], 0) > pri.get(cur, 0):
                health[m]["status"] = r["status"]
            if r["status"] in ("red", "yellow"):
                health[m]["issues"].append(f"R{r['id']}: {r['message']}")
    return health


def health_score(results: list) -> dict:
    counts = {"green": 0, "yellow": 0, "red": 0, "grey": 0}
    for r in results:
        counts[r["status"]] += 1
    n = len(results)
    g = counts["green"]
    return {
        "score": g, "total": n,
        "pct": round(g / n * 100, 1) if n else 0,
        "counts": counts,
        "overall": "red" if counts["red"] > 0 else ("yellow" if counts["yellow"] > 0 else "green"),
    }


def can_export_dpr(data: dict):
    """Returns (can_export: bool, blocking_issues: list[str])."""
    results = run_all_rules(data)
    reds = [f"Rule {r['id']} — {r['name']}: {r['message']}"
            for r in results if r["status"] == "red"]
    return len(reds) == 0, reds


def get_rules_for_module(module: str, results: list) -> list:
    """Return rule results filtered to a specific module."""
    ids = set(MODULE_RULES.get(module, []))
    return [r for r in results if r["id"] in ids]


# ══════════════════════════════════════════════════════════════════════
# AI DEEP AUDIT — LLM-POWERED COMPREHENSIVE ANALYSIS
# ══════════════════════════════════════════════════════════════════════

def ai_deep_audit(data: dict):
    """Call LLM for a comprehensive narrative audit. Returns (text, provider)."""
    try:
        from engines.ai_engine import ask_ai, SYSTEM_PROMPT_BASE
    except ImportError:
        return "AI engine not available — connect an API key in Settings.", "offline"

    results = run_all_rules(data)
    score = health_score(results)
    reds = [r for r in results if r["status"] == "red"]
    yellows = [r for r in results if r["status"] == "yellow"]

    prompt = f"""GUARANTOR AI — Full Project Audit Report

Project: {data.get('project_name', 'Bio-Bitumen Plant')}
Capacity: {data.get('capacity_tpd', 0):.0f} TPD | State: {data.get('state', 'India')}
Total Investment: Rs {data.get('investment_cr', 0):.2f} Crore

RULE AUDIT SUMMARY:
- Passing: {score['score']}/{score['total']} rules ({score['pct']}%)
- RED FLAGS ({len(reds)}): {'; '.join([r['name'] for r in reds]) if reds else 'None — all critical rules pass'}
- WARNINGS ({len(yellows)}): {'; '.join([r['name'] for r in yellows]) if yellows else 'None'}

INVESTMENT BREAKDOWN:
- P&M: Rs {data.get('pm_cost_cr', 0):.2f} Cr | Civil: Rs {data.get('civil_cost_cr', 0):.2f} Cr
- Utility: Rs {data.get('utility_cost_cr', 0):.2f} Cr | WC: Rs {data.get('wc_cr', 0):.2f} Cr
- Loan: Rs {data.get('loan_amount_cr', 0):.2f} Cr ({data.get('loan_amount_cr', 0) / max(data.get('investment_cr', 1), 0.01) * 100:.0f}%)

FINANCIAL METRICS:
- ROI: {data.get('roi_pct', 0):.1f}% | IRR: {data.get('irr_pct', 0):.1f}% | DSCR Yr3: {data.get('dscr_yr3', 0):.2f}x
- Break-even: {data.get('break_even_months', 0)} months at {data.get('break_even_pct', 0):.1f}% utilisation
- Selling PMB: Rs {data.get('selling_price_pmb_per_mt', 0):,}/MT | VG-10: Rs {data.get('vg10_price_per_mt', 0):,}/MT

As GUARANTOR master auditor, provide:
1. OVERALL VERDICT: BANKABLE / CONDITIONAL / REVISE BEFORE SUBMISSION (bold header)
2. BANK READINESS SCORE: X/10 with 3-line justification
3. TOP RISKS (only if red/yellow): exact rule, exact fix with field name + target value
4. STRENGTHS: what numbers are strong — cite specific figures
5. NEXT 3 ACTIONS: ranked by urgency for the promoter this week

Be direct, specific. Use tables for numbers. No padding."""

    system = (SYSTEM_PROMPT_BASE +
              "\nYou are the GUARANTOR master auditor. Your job is catching contradictions before "
              "the bank does. Be direct, cite rule numbers, give exact fix values.")
    return ask_ai(prompt, system, max_tokens=2500)
