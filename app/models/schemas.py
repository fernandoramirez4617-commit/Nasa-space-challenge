class Ubicacion(BaseModel):
    lat: float
    lon: float

class Fecha(BaseModel):
    yyyy_mm_dd: str  # e.g., "2025-10-04"
