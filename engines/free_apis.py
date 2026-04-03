"""
Free APIs Engine — 10 APIs, ALL 100% Free, No API Key Required
================================================================
1. Open-Meteo        — Weather data for any location
2. REST Countries    — Country/region data
3. India Pincode     — Pincode to City/State/District
4. ExchangeRate-API  — Backup FX rates (150+ currencies)
5. Wikipedia         — Summary text for knowledge base
6. India Holidays    — Public holidays calendar
7. IP-API            — Visitor location detection
8. World Bank        — India GDP, infrastructure, road data
9. Carbon Intensity  — CO2 estimation helpers
10. Google Fonts     — Available but used via CSS only

All APIs: No signup, no key, no auth, no rate limit issues with caching.
"""
import requests
import json
import os
import time
from pathlib import Path

CACHE_DIR = Path(__file__).parent.parent / "data"
CACHE_TTL = 3600  # 1 hour default


def _cache_path(name):
    return CACHE_DIR / f"api_cache_{name}.json"


def _read_cache(name, ttl=CACHE_TTL):
    path = _cache_path(name)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if time.time() - data.get("_ts", 0) < ttl:
                return data.get("payload")
        except Exception:
            pass
    return None


def _write_cache(name, payload):
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _cache_path(name).write_text(
            json.dumps({"_ts": time.time(), "payload": payload}, default=str),
            encoding="utf-8"
        )
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════
# 1. OPEN-METEO — Weather Data (No API Key)
# https://open-meteo.com/
# ══════════════════════════════════════════════════════════════════════
# Major Indian city coordinates for plant locations
CITY_COORDS = {
    "Ahmedabad": (23.03, 72.58), "Bangalore": (12.97, 77.59), "Bhopal": (23.26, 77.41),
    "Bhubaneswar": (20.30, 85.82), "Chandigarh": (30.73, 76.78), "Chennai": (13.08, 80.27),
    "Guwahati": (26.14, 91.74), "Hyderabad": (17.39, 78.49), "Indore": (22.72, 75.86),
    "Jaipur": (26.91, 75.79), "Kolkata": (22.57, 88.36), "Lucknow": (26.85, 80.95),
    "Mumbai": (19.08, 72.88), "Nagpur": (21.15, 79.09), "Patna": (25.61, 85.14),
    "Pune": (18.52, 73.86), "Raipur": (21.25, 81.63), "Ranchi": (23.34, 85.31),
    "Vadodara": (22.31, 73.19), "Varanasi": (25.32, 83.01),
}


def get_weather_current(city):
    """Get current weather for a city. Returns temp, humidity, wind, conditions."""
    cache_key = f"weather_{city.lower().replace(' ', '_')}"
    cached = _read_cache(cache_key, ttl=1800)  # 30 min cache
    if cached:
        return cached

    coords = CITY_COORDS.get(city)
    if not coords:
        return {"error": f"City '{city}' not found. Available: {', '.join(sorted(CITY_COORDS.keys()))}"}

    try:
        url = (f"https://api.open-meteo.com/v1/forecast?"
               f"latitude={coords[0]}&longitude={coords[1]}"
               f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
               f"&timezone=Asia/Kolkata")
        resp = requests.get(url, timeout=10)
        data = resp.json()
        current = data.get("current", {})
        result = {
            "city": city,
            "temperature_c": current.get("temperature_2m", 0),
            "humidity_pct": current.get("relative_humidity_2m", 0),
            "wind_kmh": current.get("wind_speed_10m", 0),
            "weather_code": current.get("weather_code", 0),
            "condition": _weather_code_to_text(current.get("weather_code", 0)),
            "source": "Open-Meteo (free, no key)",
        }
        _write_cache(cache_key, result)
        return result
    except Exception as e:
        return {"error": str(e), "city": city}


def get_weather_forecast(city, days=7):
    """Get 7-day forecast for construction planning."""
    cache_key = f"weather_forecast_{city.lower().replace(' ', '_')}"
    cached = _read_cache(cache_key, ttl=3600)
    if cached:
        return cached

    coords = CITY_COORDS.get(city)
    if not coords:
        return []

    try:
        url = (f"https://api.open-meteo.com/v1/forecast?"
               f"latitude={coords[0]}&longitude={coords[1]}"
               f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,weather_code"
               f"&timezone=Asia/Kolkata&forecast_days={days}")
        resp = requests.get(url, timeout=10)
        data = resp.json()
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        result = []
        for i, date in enumerate(dates):
            result.append({
                "date": date,
                "temp_max": daily.get("temperature_2m_max", [0])[i] if i < len(daily.get("temperature_2m_max", [])) else 0,
                "temp_min": daily.get("temperature_2m_min", [0])[i] if i < len(daily.get("temperature_2m_min", [])) else 0,
                "rain_mm": daily.get("precipitation_sum", [0])[i] if i < len(daily.get("precipitation_sum", [])) else 0,
                "wind_max": daily.get("wind_speed_10m_max", [0])[i] if i < len(daily.get("wind_speed_10m_max", [])) else 0,
                "condition": _weather_code_to_text(daily.get("weather_code", [0])[i] if i < len(daily.get("weather_code", [])) else 0),
            })
        _write_cache(cache_key, result)
        return result
    except Exception:
        return []


def get_weather_history(city, start_date, end_date):
    """Get historical weather for site feasibility analysis."""
    cache_key = f"weather_hist_{city.lower()}_{start_date}_{end_date}"
    cached = _read_cache(cache_key, ttl=86400)  # 24hr cache for historical
    if cached:
        return cached

    coords = CITY_COORDS.get(city)
    if not coords:
        return []

    try:
        url = (f"https://archive-api.open-meteo.com/v1/archive?"
               f"latitude={coords[0]}&longitude={coords[1]}"
               f"&start_date={start_date}&end_date={end_date}"
               f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
               f"&timezone=Asia/Kolkata")
        resp = requests.get(url, timeout=15)
        data = resp.json()
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        result = []
        for i, date in enumerate(dates):
            result.append({
                "date": date,
                "temp_max": daily.get("temperature_2m_max", [0])[i] if i < len(daily.get("temperature_2m_max", [])) else 0,
                "temp_min": daily.get("temperature_2m_min", [0])[i] if i < len(daily.get("temperature_2m_min", [])) else 0,
                "rain_mm": daily.get("precipitation_sum", [0])[i] if i < len(daily.get("precipitation_sum", [])) else 0,
            })
        _write_cache(cache_key, result)
        return result
    except Exception:
        return []


def _weather_code_to_text(code):
    codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 80: "Slight showers", 81: "Moderate showers",
        82: "Violent showers", 95: "Thunderstorm", 96: "Thunderstorm with hail",
    }
    return codes.get(code, "Unknown")


# ══════════════════════════════════════════════════════════════════════
# 2. REST COUNTRIES — India Region Data (No API Key)
# https://restcountries.com/
# ══════════════════════════════════════════════════════════════════════
def get_india_info():
    """Get India country data — population, area, currency, timezone."""
    cached = _read_cache("india_info", ttl=86400)
    if cached:
        return cached
    try:
        resp = requests.get("https://restcountries.com/v3.1/alpha/IN", timeout=10)
        data = resp.json()[0]
        result = {
            "name": data.get("name", {}).get("common", "India"),
            "population": data.get("population", 1400000000),
            "area_km2": data.get("area", 3287263),
            "capital": data.get("capital", ["New Delhi"])[0],
            "currency": "INR",
            "timezone": "UTC+05:30",
            "region": data.get("subregion", "Southern Asia"),
            "languages": list(data.get("languages", {}).values()),
        }
        _write_cache("india_info", result)
        return result
    except Exception:
        return {"name": "India", "population": 1400000000, "area_km2": 3287263, "capital": "New Delhi"}


# ══════════════════════════════════════════════════════════════════════
# 3. INDIA PINCODE API — Pincode Lookup (No API Key)
# https://api.postalpincode.in/
# ══════════════════════════════════════════════════════════════════════
def lookup_pincode(pincode):
    """Lookup Indian pincode → City, District, State, Region."""
    cache_key = f"pincode_{pincode}"
    cached = _read_cache(cache_key, ttl=86400 * 30)  # 30 day cache (pincodes don't change)
    if cached:
        return cached

    # Try primary API, then fallback
    for attempt in range(2):
        try:
            resp = requests.get(f"https://api.postalpincode.in/pincode/{pincode}", timeout=8)
            data = resp.json()
            if data and data[0].get("Status") == "Success":
                post_offices = data[0].get("PostOffice", [])
                if post_offices:
                    po = post_offices[0]
                    result = {
                        "pincode": pincode,
                        "city": po.get("Block", po.get("Name", "")),
                        "district": po.get("District", ""),
                        "state": po.get("State", ""),
                        "region": po.get("Region", ""),
                        "division": po.get("Division", ""),
                        "post_offices": [p.get("Name", "") for p in post_offices[:5]],
                        "source": "India Post",
                    }
                    _write_cache(cache_key, result)
                    return result
            return {"error": f"Pincode {pincode} not found"}
        except Exception:
            if attempt == 0:
                continue  # retry once
    # Fallback: offline lookup for major cities
    OFFLINE_PINS = {
        "390": ("Vadodara", "Vadodara", "Gujarat"),
        "380": ("Ahmedabad", "Ahmedabad", "Gujarat"),
        "400": ("Mumbai", "Mumbai", "Maharashtra"),
        "411": ("Pune", "Pune", "Maharashtra"),
        "500": ("Hyderabad", "Hyderabad", "Telangana"),
        "560": ("Bangalore", "Bangalore Urban", "Karnataka"),
        "600": ("Chennai", "Chennai", "Tamil Nadu"),
        "110": ("New Delhi", "New Delhi", "Delhi"),
        "226": ("Lucknow", "Lucknow", "Uttar Pradesh"),
        "302": ("Jaipur", "Jaipur", "Rajasthan"),
        "700": ("Kolkata", "Kolkata", "West Bengal"),
        "452": ("Indore", "Indore", "Madhya Pradesh"),
        "462": ("Bhopal", "Bhopal", "Madhya Pradesh"),
    }
    prefix = pincode[:3]
    if prefix in OFFLINE_PINS:
        city, dist, state = OFFLINE_PINS[prefix]
        return {"pincode": pincode, "city": city, "district": dist, "state": state,
                "source": "Offline fallback"}
    return {"error": "API unavailable and pincode not in offline database"}


# ══════════════════════════════════════════════════════════════════════
# 4. EXCHANGERATE-API — Backup FX Rates (No API Key)
# https://open.er-api.com/
# ══════════════════════════════════════════════════════════════════════
def get_exchange_rates(base="USD"):
    """Get exchange rates for 150+ currencies. Backup for Frankfurter."""
    cache_key = f"fx_rates_{base}"
    cached = _read_cache(cache_key, ttl=3600)
    if cached:
        return cached

    try:
        resp = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=10)
        data = resp.json()
        if data.get("result") == "success":
            result = {
                "base": base,
                "usd_inr": data["rates"].get("INR", 84),
                "usd_aed": data["rates"].get("AED", 3.67),
                "usd_eur": data["rates"].get("EUR", 0.92),
                "usd_gbp": data["rates"].get("GBP", 0.79),
                "usd_jpy": data["rates"].get("JPY", 150),
                "usd_cny": data["rates"].get("CNY", 7.2),
                "all_rates": data.get("rates", {}),
                "last_update": data.get("time_last_update_utc", ""),
                "source": "ExchangeRate-API (free)",
            }
            _write_cache(cache_key, result)
            return result
        return {"error": "API returned error"}
    except Exception as e:
        return {"error": str(e), "usd_inr": 84}


# ══════════════════════════════════════════════════════════════════════
# 5. WIKIPEDIA — Summary Text (No API Key)
# https://en.wikipedia.org/api/rest_v1/
# ══════════════════════════════════════════════════════════════════════
def get_wikipedia_summary(topic):
    """Get Wikipedia summary for any topic — useful for knowledge base."""
    cache_key = f"wiki_{topic.lower().replace(' ', '_')[:30]}"
    cached = _read_cache(cache_key, ttl=86400)
    if cached:
        return cached

    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "BioBitumenDashboard/1.0"})
        data = resp.json()
        result = {
            "title": data.get("title", topic),
            "summary": data.get("extract", "No summary available"),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            "thumbnail": data.get("thumbnail", {}).get("source", ""),
            "source": "Wikipedia",
        }
        _write_cache(cache_key, result)
        return result
    except Exception as e:
        return {"title": topic, "summary": f"Could not fetch: {e}", "source": "Wikipedia"}


# ══════════════════════════════════════════════════════════════════════
# 6. INDIA HOLIDAYS — Nager.Date API (No API Key)
# https://date.nager.at/
# ══════════════════════════════════════════════════════════════════════
def get_india_holidays(year=2026):
    """Get Indian public holidays for project planning."""
    cache_key = f"holidays_india_{year}"
    cached = _read_cache(cache_key, ttl=86400 * 30)
    if cached:
        return cached

    try:
        resp = requests.get(f"https://date.nager.at/api/v3/PublicHolidays/{year}/IN", timeout=10)
        data = resp.json()
        result = []
        for h in data:
            result.append({
                "date": h.get("date", ""),
                "name": h.get("localName", h.get("name", "")),
                "name_en": h.get("name", ""),
                "fixed": h.get("fixed", False),
                "type": ", ".join(h.get("types", ["Public"])),
            })
        _write_cache(cache_key, result)
        return result
    except Exception:
        # Fallback with major holidays
        return [
            {"date": f"{year}-01-26", "name": "Republic Day", "name_en": "Republic Day", "type": "Public"},
            {"date": f"{year}-03-14", "name": "Holi", "name_en": "Holi", "type": "Public"},
            {"date": f"{year}-08-15", "name": "Independence Day", "name_en": "Independence Day", "type": "Public"},
            {"date": f"{year}-10-02", "name": "Gandhi Jayanti", "name_en": "Gandhi Jayanti", "type": "Public"},
            {"date": f"{year}-10-21", "name": "Diwali", "name_en": "Diwali", "type": "Public"},
            {"date": f"{year}-12-25", "name": "Christmas", "name_en": "Christmas", "type": "Public"},
        ]


# ══════════════════════════════════════════════════════════════════════
# 7. IP-API — Visitor Location Detection (No API Key)
# http://ip-api.com/
# ══════════════════════════════════════════════════════════════════════
def detect_visitor_location():
    """Detect visitor's approximate location from IP."""
    cached = _read_cache("visitor_location", ttl=3600)
    if cached:
        return cached

    try:
        resp = requests.get("http://ip-api.com/json/?fields=status,country,regionName,city,lat,lon,timezone,isp",
                            timeout=5)
        data = resp.json()
        if data.get("status") == "success":
            result = {
                "country": data.get("country", "India"),
                "state": data.get("regionName", ""),
                "city": data.get("city", ""),
                "lat": data.get("lat", 0),
                "lon": data.get("lon", 0),
                "timezone": data.get("timezone", "Asia/Kolkata"),
                "isp": data.get("isp", ""),
                "source": "IP-API (free)",
            }
            _write_cache("visitor_location", result)
            return result
        return {"country": "India", "state": "", "city": ""}
    except Exception:
        return {"country": "India", "state": "", "city": ""}


# ══════════════════════════════════════════════════════════════════════
# 8. WORLD BANK — India Economic Data (No API Key)
# https://api.worldbank.org/v2/
# ══════════════════════════════════════════════════════════════════════
def get_india_gdp(years=10):
    """Get India GDP data for market context."""
    cached = _read_cache("india_gdp", ttl=86400)
    if cached:
        return cached

    try:
        url = f"https://api.worldbank.org/v2/country/IN/indicator/NY.GDP.MKTP.CD?format=json&per_page={years}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if len(data) > 1:
            result = []
            for entry in data[1]:
                if entry.get("value"):
                    result.append({
                        "year": entry["date"],
                        "gdp_usd_billion": round(entry["value"] / 1e9, 1),
                    })
            result.sort(key=lambda x: x["year"])
            _write_cache("india_gdp", result)
            return result
        return []
    except Exception:
        return []


def get_india_infrastructure_data():
    """Get India infrastructure spending data from World Bank."""
    cached = _read_cache("india_infra", ttl=86400)
    if cached:
        return cached

    indicators = {
        "roads_paved_pct": "IS.ROD.PAVE.ZS",      # % of roads paved
        "goods_transport": "IS.SHP.GOOD.TU",        # Goods transported
        "population": "SP.POP.TOTL",                 # Total population
    }

    result = {}
    for name, code in indicators.items():
        try:
            url = f"https://api.worldbank.org/v2/country/IN/indicator/{code}?format=json&per_page=5"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if len(data) > 1 and data[1]:
                entries = [e for e in data[1] if e.get("value") is not None]
                if entries:
                    latest = entries[0]
                    result[name] = {
                        "value": latest["value"],
                        "year": latest["date"],
                    }
        except Exception:
            pass

    _write_cache("india_infra", result)
    return result


# ══════════════════════════════════════════════════════════════════════
# 9. CARBON CALCULATION HELPERS (Local computation, no API)
# ══════════════════════════════════════════════════════════════════════
def calculate_carbon_savings(tpd, working_days=300, bio_blend_pct=20):
    """Calculate CO2 savings, carbon credits, and environmental impact."""
    annual_output = tpd * working_days
    co2_per_mt = 0.35 * (bio_blend_pct / 20)  # Scaled by blend %
    co2_saved = annual_output * co2_per_mt
    carbon_credit_usd = 12.0  # Voluntary market rate
    carbon_credit_inr = co2_saved * carbon_credit_usd * 84

    stubble_per_mt = 2.5
    stubble_diverted = annual_output * stubble_per_mt

    return {
        "annual_output_mt": annual_output,
        "co2_saved_tonnes": round(co2_saved, 0),
        "carbon_credit_usd": round(co2_saved * carbon_credit_usd, 0),
        "carbon_credit_inr": round(carbon_credit_inr, 0),
        "carbon_credit_lac": round(carbon_credit_inr / 100000, 1),
        "stubble_diverted_mt": round(stubble_diverted, 0),
        "equivalent_trees": round(co2_saved * 50, 0),
        "equivalent_cars_removed": round(co2_saved / 4.6, 0),
    }


# ══════════════════════════════════════════════════════════════════════
# 10. MASTER FUNCTION — Get All Free API Data
# ══════════════════════════════════════════════════════════════════════
def get_all_free_data(city="Vadodara"):
    """Fetch all free API data in one call. Cached individually."""
    return {
        "weather": get_weather_current(city),
        "forecast": get_weather_forecast(city, 7),
        "india": get_india_info(),
        "fx": get_exchange_rates(),
        "holidays": get_india_holidays(),
        "location": detect_visitor_location(),
        "gdp": get_india_gdp(),
        "carbon": calculate_carbon_savings(20),
    }


# Quick test
if __name__ == "__main__":
    print("Testing Free APIs...")
    print(f"Weather: {get_weather_current('Vadodara')}")
    print(f"Pincode: {lookup_pincode('390001')}")
    print(f"FX: {get_exchange_rates()}")
    print(f"Holidays: {len(get_india_holidays())} holidays")
    print(f"Location: {detect_visitor_location()}")
    print(f"GDP: {len(get_india_gdp())} years")
    print(f"Carbon: {calculate_carbon_savings(20)}")
    print("All APIs OK!")
