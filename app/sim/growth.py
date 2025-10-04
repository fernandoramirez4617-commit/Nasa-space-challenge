from app.sim.water_balance import clamp

def daily_scoring(situacion: str, estado: dict) -> str:
    """
    Modifica puntos, monedas, racha y rendimiento según la situación del agua.
    Devuelve un mensaje corto.
    """
    if situacion == "bien":
        estado["puntos"] += 5
        estado["monedas"] += 2
        estado["racha_buena"] += 1
        estado["rendimiento"] = clamp(estado["rendimiento"] + 1, 0, 120)
        return "¡Buen manejo de agua! +5 pts, +2 monedas"
    elif situacion == "seco":
        estado["puntos"] -= 2
        estado["racha_buena"] = 0
        estado["rendimiento"] = clamp(estado["rendimiento"] - 3, 0, 120)
        return "Suelo seco: -2 pts"
    elif situacion == "encharcado":
        estado["puntos"] -= 1
        estado["racha_buena"] = 0
        estado["rendimiento"] = clamp(estado["rendimiento"] - 1, 0, 120)
        return "Exceso de agua: -1 pt"
    else:
        estado["racha_buena"] = 0
        return "Día neutro."

def maybe_level_up(estado: dict) -> str | None:
    nuevo = max(1, estado["puntos"] // 25 + 1)
    if nuevo > estado["nivel"]:
        estado["nivel"] = nuevo
        return f"🎖️ ¡Subiste al nivel {nuevo}!"
    return None
