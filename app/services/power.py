# Stub para futuro: aquí conectarás la API de NASA POWER
# https://power.larc.nasa.gov/
# Por ahora devolvemos 0 mm de lluvia y ET0 ~ 5 mm para mantener simple.

def get_daily_climate(lat: float, lon: float, date_iso: str) -> dict:
    return {
        "precip_mm": 0.0,
        "et0_mm": 5.0
    }
