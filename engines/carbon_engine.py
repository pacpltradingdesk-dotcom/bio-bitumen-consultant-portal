"""
Carbon Credit & Sustainability Engine
=======================================
Calculates CO₂ savings from bio-bitumen vs fossil bitumen,
carbon credit revenue, and sustainability metrics.
"""
from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime

_HERE = Path(__file__).parent.parent
DATA_DIR = _HERE / "data"

# ── Carbon constants ─────────────────────────────────────────────────────
# Fossil bitumen lifecycle CO₂: ~0.45 tCO₂/MT (refinery + transport)
FOSSIL_BITUMEN_CO2_PER_MT  = 0.45   # tCO₂ per MT bitumen
# Bio-bitumen net CO₂: biomass is carbon-neutral; process emissions ~0.08 tCO₂/MT
BIO_BITUMEN_CO2_PER_MT     = 0.08
# Net savings per MT bio-bitumen produced
NET_CO2_SAVING_PER_MT      = FOSSIL_BITUMEN_CO2_PER_MT - BIO_BITUMEN_CO2_PER_MT  # 0.37

# Carbon credit market prices (tCO₂e)
CARBON_PRICES = {
    "India PAT Scheme":        3.0,   # USD/tCO₂e (PAT — Perform Achieve Trade)
    "Voluntary (Gold Std)":   15.0,   # USD/tCO₂e
    "Voluntary (Verra VCS)":  12.0,
    "EU ETS (CBAM import)":   65.0,   # EUR/tCO₂e (affects imports to EU)
    "India Carbon Market":     8.0,   # Estimated India carbon market price 2026
}

# Biomass co-products carbon benefit
BIOCHAR_SEQUESTRATION_PER_MT = 1.5   # tCO₂e sequestered per MT biochar (stable carbon)
SYNGAS_SUBSTITUTION_PER_MT   = 0.12  # tCO₂e avoided per MT syngas (replaces LPG/NG)


def calculate_carbon(cfg: dict, usd_inr: float = 84.0) -> dict:
    """
    Full carbon & sustainability calculation.
    Returns: {annual_co2_saved, annual_credits, revenue by scheme, total_inr, details}
    """
    capacity_tpd  = float(cfg.get("capacity_tpd", 20) or 20)
    working_days  = int(cfg.get("working_days", 300) or 300)
    oil_yield_pct = float(cfg.get("bio_oil_yield_pct", 32) or 32) / 100
    char_yield_pct= float(cfg.get("bio_char_yield_pct", 28) or 28) / 100
    syngas_pct    = float(cfg.get("syngas_yield_pct", 15) or 15) / 100

    annual_biomass   = capacity_tpd * working_days            # MT/year
    annual_bio_oil   = annual_biomass * oil_yield_pct         # MT/year
    annual_biochar   = annual_biomass * char_yield_pct        # MT/year
    annual_syngas    = annual_biomass * syngas_pct            # MT/year

    # ── CO₂ savings ───────────────────────────────────────────────────
    co2_from_bitumen_sub = annual_bio_oil * NET_CO2_SAVING_PER_MT
    co2_from_biochar     = annual_biochar * BIOCHAR_SEQUESTRATION_PER_MT
    co2_from_syngas      = annual_syngas  * SYNGAS_SUBSTITUTION_PER_MT
    total_co2_saved      = co2_from_bitumen_sub + co2_from_biochar + co2_from_syngas

    # ── Carbon revenue by scheme ───────────────────────────────────────
    credit_revenues = {}
    for scheme, price_usd in CARBON_PRICES.items():
        rev_usd = total_co2_saved * price_usd
        rev_inr = rev_usd * usd_inr
        credit_revenues[scheme] = {
            "price_usd": price_usd,
            "revenue_usd": round(rev_usd, 0),
            "revenue_inr_lac": round(rev_inr / 100000, 2),
        }

    # Best achievable (Gold Standard voluntary)
    best_scheme  = max(credit_revenues, key=lambda k: credit_revenues[k]["revenue_usd"])
    best_rev_lac = credit_revenues[best_scheme]["revenue_inr_lac"]

    # ── Sustainability metrics ─────────────────────────────────────────
    trees_equivalent = total_co2_saved * 45   # 1 tree absorbs ~22 kg CO₂/year → 45 trees/tCO₂
    cars_off_road    = total_co2_saved / 4.6  # avg car ~4.6 tCO₂/year
    households_equiv = total_co2_saved / 2.5  # avg household ~2.5 tCO₂/year

    result = {
        "annual_biomass_mt":     round(annual_biomass),
        "annual_bio_oil_mt":     round(annual_bio_oil),
        "annual_biochar_mt":     round(annual_biochar),
        "annual_syngas_mt":      round(annual_syngas),
        "co2_from_bitumen_sub":  round(co2_from_bitumen_sub, 1),
        "co2_from_biochar":      round(co2_from_biochar, 1),
        "co2_from_syngas":       round(co2_from_syngas, 1),
        "total_co2_saved_tpa":   round(total_co2_saved, 1),
        "credit_revenues":       credit_revenues,
        "best_scheme":           best_scheme,
        "best_rev_lac":          best_rev_lac,
        "trees_equivalent":      round(trees_equivalent),
        "cars_off_road":         round(cars_off_road, 1),
        "households_equiv":      round(households_equiv, 1),
        "usd_inr_used":          usd_inr,
        "calculated_at":         datetime.now().isoformat(),
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "carbon_results.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return result


def load_carbon() -> dict:
    path = DATA_DIR / "carbon_results.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def cbam_assessment(annual_bio_oil_mt: float, usd_inr: float = 84.0) -> dict:
    """EU Carbon Border Adjustment Mechanism — export opportunity assessment."""
    eu_ets_price_eur = 65.0
    cbam_saving_per_mt = FOSSIL_BITUMEN_CO2_PER_MT * eu_ets_price_eur
    annual_cbam_eur = annual_bio_oil_mt * cbam_saving_per_mt
    annual_cbam_inr = annual_cbam_eur * usd_inr * 0.92  # EUR/USD ~0.92
    return {
        "cbam_saving_per_mt_eur": round(cbam_saving_per_mt, 2),
        "annual_cbam_saving_eur": round(annual_cbam_eur, 0),
        "annual_cbam_saving_lac_inr": round(annual_cbam_inr / 100000, 2),
        "note": "Applies if exporting to EU — bio-bitumen avoids CBAM levy vs fossil bitumen",
    }
