# app/models/schemas.py
from pydantic import BaseModel

class Dia(BaseModel):
    riego: float = 0
    lluvia: float = 0

class Config(BaseModel):
    consumo: float = 5.0
    azar_eventos: float = 0.2  # 0..1

class EstadoOut(BaseModel):
    dia: int
    agua: float
    rendimiento: float
    consumo: float
    puntos: int
    monedas: int
    racha_buena: int
    nivel: int
    estado: str
    tip: str

# 👇 Tus clases (válidas en Pydantic v1 y v2)
class Ubicacion(BaseModel):
    lat: float
    lon: float

class Fecha(BaseModel):
    yyyy_mm_dd: str  # e.g., "2025-10-04"
