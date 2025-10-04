from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, datetime

import random
from app.db.session import get_db
from app.db import crud
from app.models.db_models import Game
from app.models.schemas import Dia, Config, EstadoOut, Ubicacion, Fecha
from app.sim.water_balance import update_water, classify_water, tip_by_status
from app.sim.growth import daily_scoring, maybe_level_up
from app.services.power import fetch_daily

router = APIRouter(prefix="/campo", tags=["campo"])

# Probabilidad de evento aleatorio
AZAR_EVENTOS = 0.2

def evento_aleatorio() -> dict | None:
    if random.random() > AZAR_EVENTOS:
        return None
    return random.choice([
        {"mensaje":"Día ventoso: evapora +2 mm 💨", "delta_agua": -2, "delta_puntos": 1, "delta_monedas": 0},
        {"mensaje":"Día nublado: evapora -2 mm ☁️", "delta_agua": +2, "delta_puntos": 0, "delta_monedas": 0},
        {"mensaje":"Vecino comparte consejo: +3 pts 🤝", "delta_agua": 0, "delta_puntos": 3, "delta_monedas": 0},
        {"mensaje":"Fuga en manguera: pierdes 1 moneda 💧", "delta_agua": -1, "delta_puntos": 0, "delta_monedas": -1},
    ])

# -------- setup/estado --------
@router.post("/nuevo")
def nuevo_juego(db: Session = Depends(get_db)):
    game = crud.reset_game(db, consumo=5.0)
    return {"ok": True, "mensaje": "Nueva partida lista 🌾", "estado": estado_dict(game)}

@router.post("/config")
def configurar(nueva: Config, db: Session = Depends(get_db)):
    global AZAR_EVENTOS
    AZAR_EVENTOS = float(nueva.azar_eventos)
    game = crud.ensure_game(db)
    game.consumo = float(nueva.consumo)
    crud.update_game(db, game)
    return {"ok": True, "mensaje": "Configuración guardada ⚙️",
            "config": {"consumo": game.consumo, "azar_eventos": AZAR_EVENTOS}}

@router.post("/ubicacion")
def set_ubicacion(ubi: Ubicacion, db: Session = Depends(get_db)):
    game = crud.set_location(db, lat=ubi.lat, lon=ubi.lon)
    return {"ok": True, "mensaje": "Ubicación guardada 📍", "lat": game.lat, "lon": game.lon}

@router.post("/fecha")
def set_fecha(payload: Fecha, db: Session = Depends(get_db)):
    try:
        d = datetime.strptime(payload.yyyy_mm_dd, "%Y-%m-%d").date()
    except ValueError:
        return {"ok": False, "mensaje": "Formato de fecha inválido. Usa YYYY-MM-DD."}
    game = crud.set_date(db, d)
    return {"ok": True, "mensaje": "Fecha actualizada 📅", "fecha": str(game.fecha)}

@router.get("/estado", response_model=EstadoOut)
def ver_estado(db: Session = Depends(get_db)):
    game = crud.ensure_game(db)
    estado = classify_water(game.agua)
    return {
        "dia": game.dia,
        "agua": round(game.agua, 1),
        "rendimiento": round(game.rendimiento, 1),
        "consumo": game.consumo,
        "puntos": game.puntos,
        "monedas": game.monedas,
        "racha_buena": game.racha_buena,
        "nivel": game.nivel,
        "estado": estado,
        "tip": tip_by_status(estado)
    }

@router.get("/historial")
def ver_historial(db: Session = Depends(get_db)):
    logs = crud.get_history(db, limit=30)
    return {"historial": [
        {"dia": l.dia, "riego": l.riego, "lluvia": l.lluvia,
         "agua": round(l.agua, 1), "situacion": l.situacion,
         "puntos": l.puntos, "monedas": l.monedas,
         "cuando": l.created_at.isoformat() if l.created_at else None}
        for l in reversed(logs)
    ]}

# -------- jugar manual --------
@router.post("/avanzar")
def avanzar(dia: Dia, db: Session = Depends(get_db)):
    game = crud.ensure_game(db)
    return _tick(game, db, lluvia=dia.lluvia, riego=dia.riego)

# -------- jugar automático con NASA POWER --------
@router.post("/avanzar_auto")
def avanzar_auto(db: Session = Depends(get_db)):
    game = crud.ensure_game(db)
    if game.lat is None or game.lon is None:
        return {"ok": False, "mensaje": "Primero configura ubicación con /campo/ubicacion 📍"}
    if game.fecha is None:
        game.fecha = date.today()

    # Traer clima real del día actual
    clima = fetch_daily(game.lat, game.lon, game.fecha)
    lluvia = float(clima.get("precip_mm", 0.0))
    et0 = float(clima.get("et0_mm", game.consumo))
    # Ajustamos consumo a ET0 del día (limitado a 2..8)
    game.consumo = max(2.0, min(8.0, et0))

    # Registrar tick (sin riego, o puedes poner estrategia simple)
    res = _tick(game, db, lluvia=lluvia, riego=0.0, info_extra={"et0": et0})

    # Pasar a la siguiente fecha
    crud.next_date(db)
    res["info_clima"] = {"lluvia_mm": lluvia, "et0_mm": et0, "fecha": str(game.fecha)}
    return res

# -------- helpers internos --------
def _tick(game: Game, db: Session, lluvia: float, riego: float, info_extra: dict | None = None):
    # avanzar día y actualizar agua
    game.dia += 1
    game.agua = update_water(game.agua, riego, lluvia, game.consumo)

    mensajes = []
    ev = evento_aleatorio()
    if ev:
        game.agua = max(0, min(100, game.agua + ev["delta_agua"]))
        game.puntos += ev["delta_puntos"]
        game.monedas = max(0, game.monedas + ev["delta_monedas"])
        mensajes.append(ev["mensaje"])

    situacion = classify_water(game.agua)
    mensajes.append(daily_scoring(situacion, game.__dict__))
    subida = maybe_level_up(game.__dict__)
    if subida:
        mensajes.append(subida)

    # persistir y log
    crud.update_game(db, game)
    crud.add_daylog(
        db,
        dia=game.dia, riego=riego, lluvia=lluvia,
        agua=game.agua, situacion=situacion, puntos=game.puntos, monedas=game.monedas
    )

    out = {
        "ok": True,
        "mensajes": mensajes,
        "resumen": {
            "dia": game.dia, "riego": riego, "lluvia": lluvia,
            "agua": round(game.agua, 1), "situacion": situacion,
            "puntos": game.puntos, "monedas": game.monedas,
        },
        "tip": tip_by_status(situacion)
    }
    if info_extra:
        out["extra"] = info_extra
    return out

def estado_dict(g: Game):
    return {
        "dia": g.dia, "agua": g.agua, "consumo": g.consumo,
        "rendimiento": g.rendimiento, "puntos": g.puntos,
        "monedas": g.monedas, "racha_buena": g.racha_buena, "nivel": g.nivel,
        "lat": g.lat, "lon": g.lon, "fecha": str(g.fecha) if g.fecha else None
    }
