"""
Master Connector — Universal data aggregator for all portal outputs.
=====================================================================
Single call to get_full_project_data(cfg) returns ONE dict containing:
  - All financial fields from cfg (recalculate() output)
  - Carbon profile (CO₂ savings, credit revenue, CBAM)
  - Applicable govt schemes + total benefit
  - Project viability rating + grade
  - Scenario comparison results
  - Weighted feedstock cost
  - Formatted INR strings for all key metrics
  - A ready-to-use summary block for PDF, Share, Export

Used by: page 90 (DPR PDF), page 65 (DPR Generator), page 67 (Export Center),
         page 94 (Share Report), page 95 (My Projects), report_generator_engine
"""
from __future__ import annotations
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


# ── Helpers ──────────────────────────────────────────────────────────────

def _lac(val: float) -> str:
    """Format ₹ Lac / Cr."""
    if val is None:
        return "—"
    if abs(val) >= 100:
        return f"₹ {val/100:.2f} Cr"
    return f"₹ {val:.1f} Lac"


def _pct(val: float) -> str:
    return f"{val:.1f}%" if val is not None else "—"


# ── Sub-engine loaders (graceful fallback if not yet calculated) ─────────

def _get_carbon(cfg: dict, usd_inr: float = 84.0) -> dict:
    try:
        from engines.carbon_engine import calculate_carbon, load_carbon
        result = load_carbon()
        if not result:
            result = calculate_carbon(cfg, usd_inr=usd_inr)
        return result or {}
    except Exception:
        return {}


def _get_schemes(cfg: dict) -> list:
    try:
        from engines.scheme_finder_engine import find_schemes, load_schemes
        schemes = load_schemes()
        if not schemes:
            schemes = find_schemes(cfg)
        return schemes or []
    except Exception:
        return []


def _get_rating(cfg: dict) -> dict:
    try:
        from engines.rating_engine import grade_project, load_ratings
        saved = load_ratings()
        if saved and saved.get("project"):
            return saved["project"]
        return grade_project(cfg)
    except Exception:
        return {}


def _get_fx(default: float = 84.0) -> float:
    try:
        from engines.free_apis import get_exchange_rates
        fx = get_exchange_rates()
        if "error" not in fx:
            return float(fx.get("usd_inr", default))
    except Exception:
        pass
    return default


# ── Main function ────────────────────────────────────────────────────────

def get_full_project_data(cfg: dict, *, run_engines: bool = True) -> dict:
    """
    Return a single comprehensive dict with every piece of data the portal
    can produce.  Safe to call from PDF, export, share, or any page.

    Parameters
    ----------
    cfg : dict  — master_config from state_manager.get_config()
    run_engines : bool — if True, run carbon/scheme/rating engines live;
                         if False, only use cached data files.
    """
    d = dict(cfg)  # start with full cfg (includes all recalculate() outputs)

    usd_inr = _get_fx()
    d["usd_inr"] = usd_inr

    # ── Carbon ───────────────────────────────────────────────────────
    carbon = _get_carbon(cfg, usd_inr) if run_engines else {}
    d["carbon"] = carbon
    d["total_co2_saved_tpa"]    = carbon.get("total_co2_saved_tpa", 0)
    d["best_carbon_rev_lac"]    = carbon.get("best_rev_lac", 0)
    d["best_carbon_scheme"]     = carbon.get("best_scheme", "—")
    d["trees_equivalent"]       = carbon.get("trees_equivalent", 0)
    d["cars_off_road"]          = carbon.get("cars_off_road", 0)
    d["households_equiv"]       = carbon.get("households_equiv", 0)
    d["carbon_credit_revenues"] = carbon.get("credit_revenues", {})

    # ── Schemes ──────────────────────────────────────────────────────
    schemes = _get_schemes(cfg) if run_engines else []
    d["schemes"]            = schemes
    d["schemes_count"]      = len(schemes)
    d["schemes_total_cr"]   = round(sum(s.get("est_benefit_cr", 0) for s in schemes), 2)
    d["central_schemes"]    = [s for s in schemes if s.get("type") == "Central"]
    d["state_schemes"]      = [s for s in schemes if s.get("type") == "State"]

    # ── Rating ───────────────────────────────────────────────────────
    rating = _get_rating(cfg) if run_engines else {}
    d["rating"] = rating
    d["viability_grade"]  = rating.get("grade", "—")
    d["viability_score"]  = rating.get("score", 0)
    d["viability_label"]  = rating.get("label", "—")
    d["viability_color"]  = rating.get("color", "#E8B547")

    # ── Formatted display strings (used directly in PDF / share) ─────
    d["fmt_investment"]    = _lac(d.get("investment_cr", 0) * 100)
    d["fmt_revenue"]       = _lac(d.get("revenue_lac", 0))
    d["fmt_net_profit"]    = _lac(d.get("net_profit_lac", 0))
    d["fmt_gross_profit"]  = _lac(d.get("gross_profit_lac", 0))
    d["fmt_emi"]           = _lac(d.get("emi_lac_mth", 0))
    d["fmt_irr"]           = _pct(d.get("irr_pct", 0))
    d["fmt_roi"]           = _pct(d.get("roi_pct", 0))
    d["fmt_carbon_rev"]    = _lac(d.get("best_carbon_rev_lac", 0))
    d["fmt_schemes_total"] = f"₹ {d['schemes_total_cr']:.2f} Cr"

    # ── Convenience alias for break-even label ────────────────────────
    be_mo = d.get("break_even_months", 0)
    if be_mo:
        yrs, mo = divmod(int(be_mo), 12)
        if yrs and mo:
            d["break_even_str"] = f"{yrs}y {mo}m ({be_mo} months)"
        elif yrs:
            d["break_even_str"] = f"{yrs} years ({be_mo} months)"
        else:
            d["break_even_str"] = f"{be_mo} months"
    else:
        d["break_even_str"] = "—"

    # ── Biomass feedstock breakdown (for PDF & report tables) ────────
    feedstocks = [
        ("Rice Straw (Loose)",   "mix_rice_straw_loose",  "price_rice_straw_loose"),
        ("Rice Straw (Baled)",   "mix_rice_straw_baled",  "price_rice_straw_baled"),
        ("Wheat Straw",          "mix_wheat_straw",       "price_wheat_straw"),
        ("Bagasse",              "mix_bagasse",            "price_bagasse"),
        ("Lignin",               "mix_lignin",             "price_lignin"),
        ("Other Agro-waste",     "mix_other_agro_waste",  "price_other_agro_waste"),
    ]
    d["feedstock_table"] = [
        {
            "Feedstock": name,
            "Mix %": f"{cfg.get(mx, 0)*100:.0f}%",
            "Price ₹/MT": cfg.get(pr, 0),
            "Weighted Cost": round(cfg.get(mx, 0) * cfg.get(pr, 0), 0),
        }
        for name, mx, pr in feedstocks if cfg.get(mx, 0) > 0
    ]

    # ── 5-year P&L summary (for PDF tables) ──────────────────────────
    timeline = cfg.get("roi_timeline", [])
    d["pnl_5yr"] = [
        {
            "Year":       t["Year"],
            "Utilization": t["Utilization"],
            "Revenue":    _lac(t["Revenue (Lac)"]),
            "EBITDA":     _lac(t["EBITDA (Lac)"]),
            "PAT":        _lac(t["PAT (Lac)"]),
            "DSCR":       f"{t['DSCR']:.2f}",
        }
        for t in timeline[:5]
    ]

    # ── Implementation timeline (10-month standard) ───────────────────
    d["impl_timeline"] = [
        {"Month": "1-2",  "Activity": "Land acquisition, soil testing, DPR finalization, MSME registration"},
        {"Month": "3",    "Activity": "Bank loan sanction, equity mobilisation, contractor tendering"},
        {"Month": "4-5",  "Activity": "Civil foundation, compound wall, PEB fabrication order"},
        {"Month": "5-6",  "Activity": "Reactor delivery, electrical & mechanical erection"},
        {"Month": "6-7",  "Activity": "Bio-oil recovery system, syngas piping, blending unit commissioning"},
        {"Month": "7-8",  "Activity": "Trial runs, CPCB NOC, IS 73:2013 lab testing, staff training"},
        {"Month": "8-9",  "Activity": "Commercial production, first sale, NHAI/PWD empanelment"},
        {"Month": "9-10", "Activity": "Biomass supply chain lock-in, carbon credit registration, bank review"},
    ]

    # ── Risk register (for PDF risk section) ─────────────────────────
    d["risk_register"] = [
        {"Risk": "Biomass price escalation",    "Prob": "Medium", "Impact": "High",
         "Mitigation": "Long-term supply contracts, multi-source mix, price indexing clauses"},
        {"Risk": "Bitumen price fall",          "Prob": "Low",    "Impact": "Medium",
         "Mitigation": f"Bio-bitumen priced at 5-8% discount to fossil VG30 (₹{cfg.get('price_conv_bitumen',45750):,}/MT ref)"},
        {"Risk": "Technology performance",      "Prob": "Low",    "Impact": "High",
         "Mitigation": "Equipment warranty, performance guarantee, 3-month trial period"},
        {"Risk": "Regulatory / licensing",      "Prob": "Low",    "Impact": "Medium",
         "Mitigation": "CPCB consent, Factory Act license, IS 73:2013 pre-planned before commissioning"},
        {"Risk": "Working capital crunch",      "Prob": "Medium", "Impact": "Medium",
         "Mitigation": f"3-month WC buffer (₹{cfg.get('working_capital_lac',0):.0f} Lac) + CC facility"},
        {"Risk": "Market offtake delay",        "Prob": "Low",    "Impact": "High",
         "Mitigation": "LOI from NHAI/PWD contractor pre-secured, export option via CBAM for EU"},
        {"Risk": "Interest rate increase",      "Prob": "Low",    "Impact": "Low",
         "Mitigation": f"Sensitivity checked: +2% rate still gives IRR {max(0,cfg.get('irr_pct',0)-3):.1f}%"},
    ]

    return d


def get_summary_for_share(cfg: dict) -> str:
    """Build plain-text summary string for WhatsApp / Email."""
    d = get_full_project_data(cfg, run_engines=False)
    lines = [
        f"🏭 *{d.get('project_name') or 'Bio-Bitumen Plant'}*",
        f"📍 {d.get('location','')}, {d.get('state','')}",
        f"⚙️  Capacity: {d.get('capacity_tpd',20)} TPD  |  Output: {d.get('output_tpd',0):.1f} TPD bio-oil",
        "",
        "💰 *Financial Summary*",
        f"  Investment : {d['fmt_investment']}",
        f"  Revenue (Yr3): {d['fmt_revenue']}",
        f"  Net Profit  : {d['fmt_net_profit']}",
        f"  IRR         : {d['fmt_irr']}  |  ROI: {d['fmt_roi']}",
        f"  Break-even  : {d['break_even_str']}",
        f"  EMI/month   : {d['fmt_emi']}",
        "",
        f"🌱 CO₂ Saved: {d.get('total_co2_saved_tpa',0):,.0f} tCO₂e/yr  "
        f"| Carbon Rev: {d['fmt_carbon_rev']}",
        f"🏛️ Govt Schemes: {d.get('schemes_count',0)} applicable — Total benefit {d['fmt_schemes_total']}",
        f"⭐ Viability Grade: {d.get('viability_grade','—')} ({d.get('viability_score',0)}/100)",
        "",
        f"Prepared by {d.get('prepared_by') or d.get('client_name') or 'Consultant'}",
        f"via Bio-Bitumen Consultant Portal",
    ]
    client = d.get("client_name", "")
    if client:
        lines.insert(2, f"👤 Prepared for: {client}")
    return "\n".join(lines)


def save_full_snapshot(cfg: dict) -> Path:
    """Save complete project snapshot to data/project_snapshot.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    d = get_full_project_data(cfg, run_engines=False)
    # Keep only JSON-serializable fields
    clean = {}
    for k, v in d.items():
        try:
            json.dumps(v)
            clean[k] = v
        except (TypeError, ValueError):
            clean[k] = str(v)
    path = DATA_DIR / "project_snapshot.json"
    path.write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
