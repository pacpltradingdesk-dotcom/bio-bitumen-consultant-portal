"""
Scenario Comparison Engine
============================
Run multiple project scenarios and compare side-by-side.
Each scenario is a dict of parameter overrides applied on top of DEFAULTS.
"""
from __future__ import annotations
from pathlib import Path
import json, copy
from datetime import datetime

_HERE = Path(__file__).parent.parent
DATA_DIR = _HERE / "data"

DEFAULT_SCENARIOS = [
    {"label": "Pilot (5 TPD)",    "capacity_tpd": 5,   "color": "#74C0FC"},
    {"label": "Small (10 TPD)",   "capacity_tpd": 10,  "color": "#A9E34B"},
    {"label": "Medium (20 TPD)",  "capacity_tpd": 20,  "color": "#E8B547"},
    {"label": "Large (50 TPD)",   "capacity_tpd": 50,  "color": "#FF9999"},
]

OUTPUT_KEYS = [
    ("capacity_tpd",       "Capacity (TPD)"),
    ("investment_cr",      "Investment (₹ Cr)"),
    ("revenue_lac",        "Revenue / Year (₹ Lac)"),
    ("operating_cost_lac", "Operating Cost (₹ Lac)"),
    ("gross_profit_lac",   "Gross Profit (₹ Lac)"),
    ("net_profit_lac",     "Net Profit (₹ Lac)"),
    ("roi_pct",            "ROI (%)"),
    ("irr_pct",            "IRR (%)"),
    ("break_even_months",  "Break-even (Months)"),
    ("emi_lac_mth",        "Monthly EMI (₹ Lac)"),
    ("output_tpd",         "Bio-Oil Output (TPD)"),
]


def _compute_scenario(base_cfg: dict, overrides: dict) -> dict:
    """Apply overrides and compute financials without Streamlit session state."""
    cfg = copy.deepcopy(base_cfg)
    cfg.update(overrides)

    cap   = float(cfg.get("capacity_tpd", 20))
    days  = int(cfg.get("working_days", 300))
    oil_y = float(cfg.get("bio_oil_yield_pct", 32)) / 100
    char_y= float(cfg.get("bio_char_yield_pct", 28)) / 100
    price = float(cfg.get("selling_price_per_mt", 35000))
    char_p= float(cfg.get("biochar_price_per_mt", 8000))
    rm_cost= float(cfg.get("raw_material_cost_per_mt", 2500))
    op_cost_pm = float(cfg.get("power_cost_per_mt", 800) or 0) + \
                 float(cfg.get("labour_cost_per_mt", 600) or 0) + \
                 float(cfg.get("chemical_cost_per_mt", 400) or 0) + \
                 float(cfg.get("maintenance_pct", 2) or 2) / 100 * 1000

    # Production
    annual_biomass = cap * days
    annual_oil     = annual_biomass * oil_y
    annual_char    = annual_biomass * char_y

    # Revenue
    rev_oil  = annual_oil  * price / 100000    # → Lac
    rev_char = annual_char * char_p / 100000
    revenue  = rev_oil + rev_char

    # Costs
    rm_total  = annual_biomass * rm_cost / 100000
    op_total  = annual_biomass * op_cost_pm / 100000
    total_cost= rm_total + op_total

    gross_profit = revenue - total_cost

    # Investment (scales with capacity)
    inv_base = float(cfg.get("investment_cr", 6.4) or 6.4)
    # Scale investment proportionally from base 20 TPD
    base_cap = float(cfg.get("_base_cap", 20) or 20)
    inv_scaled = inv_base * (cap / base_cap) ** 0.65   # sub-linear scaling
    invest_lac = inv_scaled * 100

    # Loan
    eq = float(cfg.get("equity_ratio", 0.4))
    loan_lac = invest_lac * (1 - eq)
    ir = float(cfg.get("interest_rate", 0.115))
    tenure = int(cfg.get("emi_tenure_months", 84))
    r = ir / 12
    if r > 0 and tenure > 0:
        emi = loan_lac * r * (1 + r) ** tenure / ((1 + r) ** tenure - 1)
    else:
        emi = 0
    annual_interest = loan_lac * ir * 0.5   # average
    dep = invest_lac * float(cfg.get("depreciation_rate", 0.1))
    tax_r= float(cfg.get("tax_rate", 0.25))
    pbt  = gross_profit - annual_interest - dep
    tax  = max(pbt * tax_r, 0)
    net_profit = pbt - tax
    roi   = net_profit / max(invest_lac, 1) * 100
    # IRR approximation
    cf = [-invest_lac] + [net_profit + dep] * 7
    irr = _xirr(cf)
    # Break-even
    cash_acc = net_profit + dep
    bev = invest_lac / max(cash_acc / 12, 1)

    return {
        "capacity_tpd":       round(cap, 1),
        "investment_cr":      round(inv_scaled, 2),
        "revenue_lac":        round(revenue, 1),
        "operating_cost_lac": round(total_cost, 1),
        "gross_profit_lac":   round(gross_profit, 1),
        "net_profit_lac":     round(net_profit, 1),
        "roi_pct":            round(roi, 1),
        "irr_pct":            round(irr, 1),
        "break_even_months":  round(bev),
        "emi_lac_mth":        round(emi, 2),
        "output_tpd":         round(cap * oil_y, 2),
    }


def _xirr(cashflows: list[float], guess: float = 0.15) -> float:
    """Simple Newton-Raphson IRR approximation."""
    rate = guess
    for _ in range(100):
        npv  = sum(cf / (1 + rate) ** i for i, cf in enumerate(cashflows))
        dnpv = sum(-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cashflows))
        if abs(dnpv) < 1e-10:
            break
        rate -= npv / dnpv
        if rate < -0.99:
            rate = -0.99
    return round(rate * 100, 1)


def run_scenarios(base_cfg: dict,
                  scenarios: list[dict] | None = None) -> list[dict]:
    """
    Run all scenarios. Each scenario dict needs at least 'label' and one override key.
    Returns list of scenario result dicts.
    """
    if scenarios is None:
        scenarios = DEFAULT_SCENARIOS

    base_cfg["_base_cap"] = float(base_cfg.get("capacity_tpd", 20))
    results = []
    for sc in scenarios:
        label = sc.get("label", "Scenario")
        color = sc.get("color", "#E8B547")
        overrides = {k: v for k, v in sc.items() if k not in ("label", "color")}
        computed = _compute_scenario(base_cfg, overrides)
        results.append({"label": label, "color": color, **computed})

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "scenario_results.json").write_text(
        json.dumps({"run_at": datetime.now().isoformat(), "scenarios": results},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return results


def load_scenarios() -> list[dict]:
    path = DATA_DIR / "scenario_results.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("scenarios", [])
    except Exception:
        return []
