from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import crud
from app.models.db_models import Game

router = APIRouter(prefix="/tienda", tags=["tienda"])

OFERTAS = {
    "riego_eficiente": {"costo": 10, "efecto": "reduce consumo de agua a 4 mm/día"},
    "fertilizante_organico": {"costo": 15, "efecto": "sube +5 rendimiento inmediato"},
}

@router.get("/")
def ver_ofertas():
    return {"ofertas": OFERTAS}

@router.post("/{item}")
def comprar(item: str, db: Session = Depends(get_db)):
    game = crud.ensure_game(db)

    if item not in OFERTAS:
        return {"ok": False, "mensaje": "Ese producto no existe ❌"}

    oferta = OFERTAS[item]
    if game.monedas < oferta["costo"]:
        return {"ok": False, "mensaje": "No tienes monedas suficientes 💸"}

    # descontar
    game.monedas -= oferta["costo"]

    # aplicar efectos simples
    if item == "riego_eficiente":
        game.consumo = 4.0
    elif item == "fertilizante_organico":
        game.rendimiento += 5

    crud.update_game(db, game)

    return {"ok": True, "mensaje": f"Compraste {item} ✅", "estado": {
        "dia": game.dia, "monedas": game.monedas, "consumo": game.consumo, "rendimiento": game.rendimiento
    }}
