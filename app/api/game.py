from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import random

from app.db.session import get_db
from app.db import crud
from app.models.db_models import Game
from app.models.schemas import Dia, Config, EstadoOut
from app.sim.water_balance import update_water, classify_water, tip_by_status
from app.sim.growth import daily_scoring, maybe_level_up

router = APIRouter(prefix="/campo", tags=["campo"])

# ---- Config global simple (memoria) ----
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

@router.post("/nuevo")
def nuevo_juego(db: Session = Depends(get_db)):
    game = crud.reset_game(db, consumo=5.0)
    return {"ok": True, "mensaje": "Nueva partida lista 🌾", "estado": {
        "dia": game.dia, "agua": game.agua, "consumo": game.consumo,
        "rendimiento": game.rendimiento, "puntos": game.puntos,
        "monedas": game.monedas, "racha_buena": game.racha_buena, "nivel": game.nivel
    }}

@router.post("/config")
def configurar(nueva: Config, db: Session = Depends(get_db)):
    global AZAR_EVENTOS
    AZAR_EVENTOS = float(nueva.azar_eventos)
    game = crud.ensure_game(db)
    game.consumo = float(nueva.consumo)
    crud.update_game(db, game)
    return {"ok": True, "mensaje": "Configuración guardada ⚙️",
            "config": {"consumo": game.consumo, "azar_eventos": AZAR_EVENTOS}}

@router.get("/objetivos")
def objetivos():
    return {
        "mision_diaria": "Mantén la humedad en 40–70 para ganar +5 puntos y +2 monedas.",
        "tips": ["Riega poco y seguido", "Evita riego si el suelo está >85"]
    }

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

@router.post("/avanzar")
def avanzar(dia: Dia, db: Session = Depends(get_db)):
    game: Game = crud.ensure_game(db)

    # 1) día + agua base
    game.dia += 1
    game.agua = update_water(game.agua, dia.riego, dia.lluvia, game.consumo)

    mensajes = []
    # 2) evento aleatorio
    ev = evento_aleatorio()
    if ev:
        game.agua = max(0, min(100, game.agua + ev["delta_agua"]))
        game.puntos += ev["delta_puntos"]
        game.monedas = max(0, game.monedas + ev["delta_monedas"])
        mensajes.append(ev["mensaje"])

    # 3) scoring por situación
    situacion = classify_water(game.agua)
    mensajes.append(daily_scoring(situacion, game.__dict__))
    subida = maybe_level_up(game.__dict__)
    if subida: mensajes.append(subida)

    # 4) persistir y log
    crud.update_game(db, game)
    crud.add_daylog(
        db,
        dia=game.dia, riego=dia.riego, lluvia=dia.lluvia,
        agua=game.agua, situacion=situacion, puntos=game.puntos, monedas=game.monedas
    )

    return {
        "ok": True,
        "mensajes": mensajes,
        "resumen": {
            "dia": game.dia, "riego": dia.riego, "lluvia": dia.lluvia,
            "agua": round(game.agua, 1), "situacion": situacion,
            "puntos": game.puntos, "monedas": game.monedas
        },
        "tip": tip_by_status(situacion)
    }
