"""Shared market data — single source of truth for VG30, crude, FX."""


def get_vg30_price():
    """Get consistent VG30 price from live calculation engine.
    ALL pages must call this instead of having independent calculations.
    Fallback: Rs 45,000/MT if APIs unavailable.
    """
    try:
        from engines.live_calculation_engine import get_live_market_inputs, calculate_live_vg30_price
        live = get_live_market_inputs()
        result = calculate_live_vg30_price(live["crude_oil_usd"], live["usd_inr"])
        return result.get("vg30_estimated", 45000)
    except Exception:
        return 45000  # Safe fallback


def get_crude_price():
    """Get consistent crude oil price."""
    try:
        from engines.market_data_api import get_market_summary
        market = get_market_summary()
        crude = market.get("crude_oil")
        if isinstance(crude, dict):
            return crude.get("latest_price", 75)
        if isinstance(crude, list) and crude:
            return crude[-1].get("price_usd", 75)
    except Exception:
        pass
    return 75.0


def get_fx_rate():
    """Get consistent USD/INR rate."""
    try:
        from engines.free_apis import get_exchange_rates
        fx = get_exchange_rates()
        if "error" not in fx:
            return fx.get("usd_inr", 84)
    except Exception:
        pass
    return 84.0
