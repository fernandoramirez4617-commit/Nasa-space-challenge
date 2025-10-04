def clamp(x: float, a: float, b: float) -> float:
    return max(a, min(b, x))

def update_water(agua: float, riego: float, lluvia: float, consumo: float) -> float:
    nueva = agua + riego + lluvia - consumo
    return clamp(nueva, 0, 100)

def classify_water(agua: float) -> str:
    if agua < 30:
        return "seco"
    if 40 <= agua <= 70:
        return "bien"
    if agua > 85:
        return "encharcado"
    return "medio"

def tip_by_status(status: str) -> str:
    return {
        "seco": "Suelo **seco**. Riega si es posible 🌵",
        "bien": "Humedad **óptima**. Buen crecimiento 🌱",
        "encharcado": "Exceso de agua. Evita riego hoy 🌊",
        "medio": "Humedad **media**. Observa el cultivo 👀",
    }[status]
