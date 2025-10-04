"""
Cliente sencillo para NASA POWER:
- Daily Single Point
Doc: https://power.larc.nasa.gov/docs/services/api/parameters/
"""
from datetime import date
import requests

BASE = "https://power.larc.nasa.gov/api/temporal/daily/point"
# Usaremos precipitación (PRECTOTCORR) y ET0 de FAO (ET0) si está disponible.

def fetch_daily(lat: float, lon: float, day: date) -> dict:
    ymd = day.strftime("%Y%m%d")
    params = {
        "parameters": "PRECTOTCORR,ET0",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": ymd,
        "end": ymd,
        "format": "JSON"
    }
    r = requests.get(BASE, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    # Extraer valores
    d = data.get("properties", {}).get("parameter", {})
    precip = list(d.get("PRECTOTCORR", {}).values())[0] if "PRECTOTCORR" in d else 0.0
    et0 = list(d.get("ET0", {}).values())[0] if "ET0" in d else 5.0  # fallback
    return {"precip_mm": float(precip), "et0_mm": float(et0)}
