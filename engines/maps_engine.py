"""
Maps Engine — Plant location visualization using free APIs.
Uses OpenStreetMap (free, no API key) for map display in Streamlit.
"""

# City coordinates for plant locations
CITY_COORDS = {
    "Ahmedabad": (23.03, 72.58), "Bangalore": (12.97, 77.59), "Bhopal": (23.26, 77.41),
    "Bhubaneswar": (20.30, 85.82), "Chandigarh": (30.73, 76.78), "Chennai": (13.08, 80.27),
    "Guwahati": (26.14, 91.74), "Hyderabad": (17.39, 78.49), "Indore": (22.72, 75.86),
    "Jaipur": (26.91, 75.79), "Kolkata": (22.57, 88.36), "Lucknow": (26.85, 80.95),
    "Mumbai": (19.08, 72.88), "Nagpur": (21.15, 79.09), "Patna": (25.61, 85.14),
    "Pune": (18.52, 73.86), "Raipur": (21.25, 81.63), "Ranchi": (23.34, 85.31),
    "Vadodara": (22.31, 73.19), "Varanasi": (25.32, 83.01),
}

# Biomass source locations (FPO/mandis within 100km of major cities)
BIOMASS_SOURCES = {
    "Vadodara": [
        {"name": "Anand FPO", "type": "Rice Straw", "lat": 22.55, "lon": 72.95, "distance_km": 40},
        {"name": "Nadiad Mandi", "type": "Cotton Stalk", "lat": 22.69, "lon": 72.87, "distance_km": 55},
        {"name": "Bharuch Sugar Mill", "type": "Bagasse", "lat": 21.71, "lon": 72.99, "distance_km": 70},
    ],
    "Lucknow": [
        {"name": "Barabanki FPO", "type": "Rice Straw", "lat": 26.93, "lon": 81.18, "distance_km": 30},
        {"name": "Sitapur Mandi", "type": "Wheat Straw", "lat": 27.57, "lon": 80.68, "distance_km": 85},
        {"name": "Lakhimpur Sugar Mill", "type": "Bagasse", "lat": 27.95, "lon": 80.78, "distance_km": 95},
    ],
    "Pune": [
        {"name": "Baramati FPO", "type": "Sugarcane Bagasse", "lat": 18.15, "lon": 74.58, "distance_km": 100},
        {"name": "Solapur Cotton Gin", "type": "Cotton Stalk", "lat": 17.67, "lon": 75.91, "distance_km": 120},
    ],
}

# NHAI/PWD offices for buyer proximity
NHAI_OFFICES = {
    "Gujarat": [{"name": "NHAI RO Ahmedabad", "lat": 23.03, "lon": 72.58}],
    "Uttar Pradesh": [{"name": "NHAI RO Lucknow", "lat": 26.85, "lon": 80.95}],
    "Maharashtra": [{"name": "NHAI RO Mumbai", "lat": 19.08, "lon": 72.88}],
}


def get_plant_map_data(cfg):
    """Get map data for plant location + nearby sources."""
    city = cfg.get("location", "Vadodara")
    state = cfg.get("state", "Gujarat")

    # Plant location
    plant_coords = CITY_COORDS.get(city, (22.31, 73.19))

    # Nearby biomass
    biomass = BIOMASS_SOURCES.get(city, [])

    # NHAI offices
    nhai = NHAI_OFFICES.get(state, [])

    # Build map points
    points = [{"name": f"PLANT: {city}", "lat": plant_coords[0], "lon": plant_coords[1],
               "type": "Plant", "color": "#CC3333"}]

    for b in biomass:
        points.append({"name": f"{b['name']} ({b['type']})", "lat": b["lat"], "lon": b["lon"],
                        "type": "Biomass", "color": "#00AA44"})

    for n in nhai:
        points.append({"name": n["name"], "lat": n["lat"], "lon": n["lon"],
                        "type": "NHAI", "color": "#003366"})

    return {
        "center": plant_coords,
        "points": points,
        "biomass_sources": biomass,
        "city": city,
        "state": state,
    }


def get_streamlit_map_df(cfg):
    """Return DataFrame for st.map() display."""
    import pandas as pd
    data = get_plant_map_data(cfg)
    rows = []
    for p in data["points"]:
        rows.append({"lat": p["lat"], "lon": p["lon"]})
    return pd.DataFrame(rows)
