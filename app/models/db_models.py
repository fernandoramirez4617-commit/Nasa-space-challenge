from sqlalchemy import Column, Integer, Float, String, DateTime, func
from app.db.session import Base

class Game(Base):
    __tablename__ = "game"

    id = Column(Integer, primary_key=True, index=True)
    dia = Column(Integer, default=0)
    agua = Column(Float, default=50.0)
    consumo = Column(Float, default=5.0)
    rendimiento = Column(Float, default=100.0)
    puntos = Column(Integer, default=0)
    monedas = Column(Integer, default=0)
    racha_buena = Column(Integer, default=0)
    nivel = Column(Integer, default=1)

class DayLog(Base):
    __tablename__ = "day_log"

    id = Column(Integer, primary_key=True, index=True)
    dia = Column(Integer)
    riego = Column(Float, default=0.0)
    lluvia = Column(Float, default=0.0)
    agua = Column(Float)
    situacion = Column(String(32))
    puntos = Column(Integer)
    monedas = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
