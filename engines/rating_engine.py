"""
Rating & Grading Engine — 4 Systems
=====================================
1. grade_project(cfg)          → Project Viability Rating  (A+ … D)
2. grade_dpr(cfg, pages_dir)   → DPR Completeness Grade    (0–100%)
3. grade_product(cfg)          → IS 73:2013 Product Grade  (VG-10/30/40/80)
4. grade_vendor(vendor)        → Vendor / Supplier Rating   (A … D)

Each function returns a dict with: score, grade, color, summary, breakdown
"""

from __future__ import annotations
from pathlib import Path
import json, re
from datetime import datetime

_HERE = Path(__file__).parent.parent
DATA_DIR = _HERE / "data"

# ── shared helpers ──────────────────────────────────────────────────────

GRADE_SCALE = [
    (90, "A+", "#51CF66", "Excellent"),
    (80, "A",  "#74C0FC", "Very Good"),
    (70, "B+", "#A9E34B", "Good"),
    (60, "B",  "#FFD43B", "Satisfactory"),
    (50, "C",  "#FF8C42", "Below Average"),
    ( 0, "D",  "#FF6B6B", "Poor"),
]

def _grade(score: float):
    for threshold, letter, color, label in GRADE_SCALE:
        if score >= threshold:
            return letter, color, label
    return "D", "#FF6B6B", "Poor"


def _save(key: str, result: dict):
    path = DATA_DIR / "ratings.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        data = {}
    data[key] = {**result, "graded_at": datetime.now().isoformat()}
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_ratings() -> dict:
    path = DATA_DIR / "ratings.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        return {}


# ══════════════════════════════════════════════════════════════════════
# 1. PROJECT VIABILITY RATING
# ══════════════════════════════════════════════════════════════════════

# States with active biomass/bio-energy subsidy schemes
SUBSIDY_STATES = {
    "Punjab", "Haryana", "Uttar Pradesh", "Maharashtra", "Gujarat",
    "Rajasthan", "Madhya Pradesh", "Karnataka", "Tamil Nadu", "Telangana",
}

# States with strong biomass availability
HIGH_BIOMASS_STATES = {
    "Punjab", "Haryana", "Uttar Pradesh", "Bihar", "Madhya Pradesh",
    "Maharashtra", "Gujarat", "Andhra Pradesh", "West Bengal",
}

def grade_project(cfg: dict) -> dict:
    """
    Score the bio-bitumen project on 7 dimensions (100 pts total).
    Returns: {score, grade, color, label, summary, breakdown}
    """
    breakdown = []
    total = 0

    # ── 1. IRR (20 pts) ───────────────────────────────────────────────
    irr = float(cfg.get("irr_pct", 0) or 0)
    if irr >= 28:
        pts, note = 20, f"IRR {irr:.1f}% — Outstanding"
    elif irr >= 22:
        pts, note = 16, f"IRR {irr:.1f}% — Strong"
    elif irr >= 16:
        pts, note = 11, f"IRR {irr:.1f}% — Acceptable"
    elif irr >= 10:
        pts, note = 6,  f"IRR {irr:.1f}% — Marginal"
    else:
        pts, note = 2,  f"IRR {irr:.1f}% — Weak"
    breakdown.append({"dim": "IRR", "max": 20, "score": pts, "note": note})
    total += pts

    # ── 2. ROI (15 pts) ───────────────────────────────────────────────
    roi = float(cfg.get("roi_pct", 0) or 0)
    if roi >= 28:
        pts, note = 15, f"ROI {roi:.1f}% — Excellent"
    elif roi >= 22:
        pts, note = 12, f"ROI {roi:.1f}% — Very good"
    elif roi >= 16:
        pts, note = 8,  f"ROI {roi:.1f}% — Adequate"
    elif roi >= 10:
        pts, note = 4,  f"ROI {roi:.1f}% — Low"
    else:
        pts, note = 1,  f"ROI {roi:.1f}% — Very low"
    breakdown.append({"dim": "ROI", "max": 15, "score": pts, "note": note})
    total += pts

    # ── 3. Break-even (15 pts) ────────────────────────────────────────
    bev = int(cfg.get("break_even_months", 999) or 999)
    if bev <= 24:
        pts, note = 15, f"Break-even {bev} months — Excellent"
    elif bev <= 36:
        pts, note = 12, f"Break-even {bev} months — Good"
    elif bev <= 48:
        pts, note = 8,  f"Break-even {bev} months — Acceptable"
    elif bev <= 60:
        pts, note = 4,  f"Break-even {bev} months — Long"
    else:
        pts, note = 1,  f"Break-even {bev} months — Very long"
    breakdown.append({"dim": "Break-even", "max": 15, "score": pts, "note": note})
    total += pts

    # ── 4. Plant capacity (15 pts) ────────────────────────────────────
    cap = float(cfg.get("capacity_tpd", 0) or 0)
    if cap >= 100:
        pts, note = 15, f"{cap:.0f} TPD — Commercial scale"
    elif cap >= 50:
        pts, note = 12, f"{cap:.0f} TPD — Large"
    elif cap >= 20:
        pts, note = 9,  f"{cap:.0f} TPD — Medium"
    elif cap >= 10:
        pts, note = 5,  f"{cap:.0f} TPD — Small"
    else:
        pts, note = 2,  f"{cap:.0f} TPD — Pilot scale"
    breakdown.append({"dim": "Capacity", "max": 15, "score": pts, "note": note})
    total += pts

    # ── 5. Bio-oil yield (15 pts) ────────────────────────────────────
    yld = float(cfg.get("bio_oil_yield_pct", 0) or 0)
    if yld >= 38:
        pts, note = 15, f"Yield {yld:.0f}% — Excellent feedstock"
    elif yld >= 30:
        pts, note = 12, f"Yield {yld:.0f}% — Good"
    elif yld >= 22:
        pts, note = 8,  f"Yield {yld:.0f}% — Average"
    else:
        pts, note = 3,  f"Yield {yld:.0f}% — Low — review feedstock"
    breakdown.append({"dim": "Bio-oil Yield", "max": 15, "score": pts, "note": note})
    total += pts

    # ── 6. State subsidy availability (10 pts) ───────────────────────
    state = cfg.get("state", "")
    if state in SUBSIDY_STATES:
        pts, note = 10, f"{state} — Active biomass subsidy schemes"
    else:
        pts, note = 5,  f"{state} — Verify state subsidy schemes"
    breakdown.append({"dim": "State Subsidies", "max": 10, "score": pts, "note": note})
    total += pts

    # ── 7. Raw material proximity (10 pts) ───────────────────────────
    if state in HIGH_BIOMASS_STATES:
        pts, note = 10, f"{state} — Strong biomass belt"
    else:
        pts, note = 5,  f"{state} — Moderate biomass availability"
    breakdown.append({"dim": "Biomass Proximity", "max": 10, "score": pts, "note": note})
    total += pts

    grade, color, label = _grade(total)

    # narrative summary
    if total >= 85:
        summary = "Highly bankable project. Strong IRR, fast payback and favourable location make this a prime investment opportunity."
    elif total >= 70:
        summary = "Viable project with good fundamentals. Fine-tune pricing or capacity to move to A+ tier."
    elif total >= 55:
        summary = "Marginal viability. Address the lowest-scoring dimensions before presenting to lenders."
    else:
        summary = "Project needs significant restructuring. Review feedstock, capacity, or financial structure."

    result = {
        "score": total, "grade": grade, "color": color, "label": label,
        "summary": summary, "breakdown": breakdown,
        "max_score": 100,
    }
    _save("project", result)
    return result


# ══════════════════════════════════════════════════════════════════════
# 2. DPR COMPLETENESS GRADE
# ══════════════════════════════════════════════════════════════════════

DPR_SECTIONS = [
    # (section_name, page_prefix_pattern, weight)
    ("Project Overview",        r"^0[12]_",   8),
    ("Location & Site",         r"^12_",       6),
    ("Market Analysis",         r"^(20|21|22|23)_", 7),
    ("Raw Material",            r"^24_",       8),
    ("Plant & Machinery",       r"^(29|30|31|32|33|34|35)_", 9),
    ("Manpower & HR",           r"^(36|37)_",  6),
    ("Financials",              r"^(10|11|13|14)_", 10),
    ("Revenue Projections",     r"^(38|39|40)_", 7),
    ("Regulatory / Licenses",   r"^(50|51|52|53|54)_", 8),
    ("Engineering Drawings",    r"^(63|64)_",  6),
    ("DPR Document",            r"^(65|60)_",  8),
    ("Export / Final Report",   r"^(67|62)_",  7),
    ("AI Analysis Done",        r"^(62|81|83)_", 5),
    ("Guarantor Cleared",       r"^84_",       5),
    ("PMC Files Uploaded",      r"^85_",       5),
]

def grade_dpr(cfg: dict, pages_dir: Path | None = None) -> dict:
    """
    Check which DPR sections have corresponding pages and data.
    Returns: {score, grade, color, label, summary, sections}
    """
    if pages_dir is None:
        pages_dir = _HERE / "pages"

    page_names = [p.name for p in pages_dir.glob("*.py")]
    sections = []
    total_weight = sum(s[2] for s in DPR_SECTIONS)
    earned = 0

    for sec_name, pattern, weight in DPR_SECTIONS:
        present = any(re.match(pattern, pn) for pn in page_names)

        # bonus: check if data files suggest section was used
        data_bonus = False
        if "Financials" in sec_name:
            data_bonus = cfg.get("investment_cr") is not None
        elif "Guarantor" in sec_name:
            data_bonus = (DATA_DIR / "guarantor_state.json").exists()
        elif "PMC" in sec_name:
            data_bonus = (DATA_DIR / "projects").exists()
        elif "AI Analysis" in sec_name:
            data_bonus = (DATA_DIR / "notes.json").exists()
        elif "Raw Material" in sec_name:
            data_bonus = bool(cfg.get("biomass_price_per_mt") or cfg.get("state"))

        if present and data_bonus:
            status, pts = "complete", weight
        elif present:
            status, pts = "page_only", round(weight * 0.65)
        else:
            status, pts = "missing", 0

        earned += pts
        sections.append({
            "section": sec_name,
            "status": status,
            "weight": weight,
            "earned": pts,
            "pct": round(pts / weight * 100),
        })

    score = round(earned / total_weight * 100)
    grade, color, label = _grade(score)

    missing = [s["section"] for s in sections if s["status"] == "missing"]
    partial = [s["section"] for s in sections if s["status"] == "page_only"]

    if score >= 85:
        summary = "DPR is comprehensive and investor-ready."
    elif score >= 70:
        summary = f"Good coverage. Complete data entry in: {', '.join(partial[:3]) or 'remaining sections'}."
    elif score >= 50:
        summary = f"Partial DPR. Missing: {', '.join(missing[:4])}."
    else:
        summary = "DPR is incomplete. Fill in all major sections before submission."

    result = {
        "score": score, "grade": grade, "color": color, "label": label,
        "summary": summary, "sections": sections,
        "missing": missing, "partial": partial,
        "max_score": 100,
    }
    _save("dpr", result)
    return result


# ══════════════════════════════════════════════════════════════════════
# 3. IS 73:2013 PRODUCT GRADE
# ══════════════════════════════════════════════════════════════════════

# IS 73:2013 Viscosity Graded Bitumen specifications
IS73_GRADES = {
    "VG-10": {
        "abs_viscosity_range": (800, 1200),    # Poise at 60°C
        "kin_viscosity_min":  250,             # cSt at 135°C
        "softening_pt_min":   40,              # °C
        "flash_pt_min":       220,             # °C
        "ductility_min":      75,              # cm at 25°C
        "penetration_range":  (80, 100),       # 0.1mm at 25°C
        "use": "Cold climates, light traffic",
    },
    "VG-30": {
        "abs_viscosity_range": (2400, 3600),
        "kin_viscosity_min":  300,
        "softening_pt_min":   47,
        "flash_pt_min":       220,
        "ductility_min":      40,
        "penetration_range":  (45, 79),
        "use": "Moderate traffic, general paving",
    },
    "VG-40": {
        "abs_viscosity_range": (3200, 4800),
        "kin_viscosity_min":  350,
        "softening_pt_min":   50,
        "flash_pt_min":       220,
        "ductility_min":      25,
        "penetration_range":  (35, 45),
        "use": "High traffic, hot climates",
    },
    "VG-80": {
        "abs_viscosity_range": (6400, 9600),
        "kin_viscosity_min":  400,
        "softening_pt_min":   55,
        "flash_pt_min":       220,
        "ductility_min":      15,
        "penetration_range":  (25, 35),
        "use": "Industrial, modified bitumen base",
    },
}

def grade_product(test_params: dict | None = None) -> dict:
    """
    Determine IS 73:2013 VG grade eligibility from lab test parameters.
    test_params keys: abs_viscosity, kin_viscosity, softening_pt,
                      flash_pt, ductility, penetration
    If test_params is None/empty, returns grade guide with typical ranges.
    """
    if not test_params:
        # Return reference guide — no actual test data
        grades_info = []
        for grade, spec in IS73_GRADES.items():
            grades_info.append({
                "grade": grade,
                "abs_viscosity": f"{spec['abs_viscosity_range'][0]}–{spec['abs_viscosity_range'][1]} P",
                "softening_pt": f"≥ {spec['softening_pt_min']} °C",
                "penetration": f"{spec['penetration_range'][0]}–{spec['penetration_range'][1]} (0.1mm)",
                "ductility": f"≥ {spec['ductility_min']} cm",
                "use": spec["use"],
            })
        return {
            "mode": "guide",
            "grades": grades_info,
            "summary": "Enter lab test results to determine which grade your product qualifies for.",
        }

    # Evaluate each grade
    eligible = []
    results = {}

    for grade, spec in IS73_GRADES.items():
        checks = {}
        passed = 0
        total_checks = 0

        av = test_params.get("abs_viscosity")
        if av is not None:
            total_checks += 1
            lo, hi = spec["abs_viscosity_range"]
            ok = lo <= av <= hi
            checks["Absolute Viscosity (P)"] = {
                "value": av, "required": f"{lo}–{hi}", "pass": ok
            }
            if ok: passed += 1

        kv = test_params.get("kin_viscosity")
        if kv is not None:
            total_checks += 1
            ok = kv >= spec["kin_viscosity_min"]
            checks["Kinematic Viscosity (cSt)"] = {
                "value": kv, "required": f"≥ {spec['kin_viscosity_min']}", "pass": ok
            }
            if ok: passed += 1

        sp = test_params.get("softening_pt")
        if sp is not None:
            total_checks += 1
            ok = sp >= spec["softening_pt_min"]
            checks["Softening Point (°C)"] = {
                "value": sp, "required": f"≥ {spec['softening_pt_min']}", "pass": ok
            }
            if ok: passed += 1

        fp = test_params.get("flash_pt")
        if fp is not None:
            total_checks += 1
            ok = fp >= spec["flash_pt_min"]
            checks["Flash Point (°C)"] = {
                "value": fp, "required": f"≥ {spec['flash_pt_min']}", "pass": ok
            }
            if ok: passed += 1

        duc = test_params.get("ductility")
        if duc is not None:
            total_checks += 1
            ok = duc >= spec["ductility_min"]
            checks["Ductility (cm)"] = {
                "value": duc, "required": f"≥ {spec['ductility_min']}", "pass": ok
            }
            if ok: passed += 1

        pen = test_params.get("penetration")
        if pen is not None:
            total_checks += 1
            lo, hi = spec["penetration_range"]
            ok = lo <= pen <= hi
            checks["Penetration (0.1mm)"] = {
                "value": pen, "required": f"{lo}–{hi}", "pass": ok
            }
            if ok: passed += 1

        score = round(passed / max(total_checks, 1) * 100)
        qualifies = (total_checks > 0 and passed == total_checks)
        if qualifies:
            eligible.append(grade)

        results[grade] = {
            "score": score, "passed": passed,
            "total_checks": total_checks, "qualifies": qualifies,
            "checks": checks, "use": spec["use"],
        }

    if eligible:
        best = eligible[-1]  # highest qualifying grade
        summary = f"Product qualifies for: {', '.join(eligible)}. Recommended grade: {best}."
    else:
        # find closest
        best_g = max(results, key=lambda g: results[g]["score"])
        summary = (f"No grade fully met. Closest: {best_g} ({results[best_g]['score']}% criteria met). "
                   "Review failing parameters.")

    result = {
        "mode": "tested",
        "eligible": eligible,
        "results": results,
        "summary": summary,
        "test_params": test_params,
    }
    _save("product", result)
    return result


# ══════════════════════════════════════════════════════════════════════
# 4. VENDOR / SUPPLIER RATING
# ══════════════════════════════════════════════════════════════════════

VENDOR_CRITERIA = [
    ("price",       "Price Competitiveness",  25, "Is quoted price ≤ market average?"),
    ("delivery",    "Delivery Reliability",   25, "On-time delivery record (%)"),
    ("quality",     "Product / Service Quality", 25, "Quality consistency rating"),
    ("support",     "After-sales Support",    15, "Responsiveness and service"),
    ("compliance",  "Compliance & Docs",      10, "GST, PAN, certifications present"),
]

def grade_vendor(vendor: dict) -> dict:
    """
    Score a vendor dict with keys matching VENDOR_CRITERIA[0] (price/delivery/quality/support/compliance).
    Values should be 0–100 raw scores.
    Returns: {score, grade, color, label, summary, breakdown}
    """
    breakdown = []
    total = 0

    for key, label, weight, hint in VENDOR_CRITERIA:
        raw = float(vendor.get(key, 0) or 0)
        raw = max(0, min(100, raw))
        pts = round(raw * weight / 100)
        breakdown.append({
            "criterion": label, "raw": raw, "weight": weight,
            "score": pts, "hint": hint,
        })
        total += pts

    grade, color, label_ = _grade(total)

    name = vendor.get("name", "Vendor")
    if total >= 85:
        summary = f"{name} is a preferred vendor. Recommend long-term agreement."
    elif total >= 70:
        summary = f"{name} is reliable. Minor improvements needed in low-scoring areas."
    elif total >= 55:
        summary = f"{name} is acceptable. Monitor closely and consider alternatives."
    else:
        summary = f"{name} is below standard. Seek alternative suppliers."

    result = {
        "score": total, "grade": grade, "color": color, "label": label_,
        "summary": summary, "breakdown": breakdown,
        "name": name, "max_score": 100,
    }
    return result


def save_vendor_ratings(vendors: list[dict]) -> list[dict]:
    """Grade and persist a list of vendor dicts."""
    rated = [grade_vendor(v) for v in vendors]
    path = DATA_DIR / "vendor_ratings.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"rated_at": datetime.now().isoformat(), "vendors": rated},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return rated


def load_vendor_ratings() -> list[dict]:
    path = DATA_DIR / "vendor_ratings.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("vendors", [])
    except Exception:
        return []
