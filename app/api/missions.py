from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import crud
from app.models.db_models import Game

router = APIRouter(prefix="/misiones", tags=["misiones"])

# Lista de logros (puede crecer)
LOGROS = {
    "racha_3": "Mantener 3 días seguidos en buen estado ",
    "50_puntos": "Alcanzar 50 puntos ",
    "ahorrador": "Juntar 20 monedas ",
}

def check_logros(game: Game) -> list[str]:
    res = []
    if game.racha_buena >= 3:
        res.append("racha_3")
    if game.puntos >= 50:
        res.append("50_puntos")
    if game.monedas >= 20:
        res.append("ahorrador")
    return res

@router.get("/")
def ver_misiones(db: Session = Depends(get_db)):
    game = crud.ensure_game(db)
    desbloqueados = check_logros(game)
    return {
        "misiones_diarias": [
            "Mantén la humedad entre 40 y 70 para ganar +5 puntos y +2 monedas.",
            "Evita 2 días seguidos de sequía."
        ],
        "logros_desbloqueados": {k: LOGROS[k] for k in desbloqueados},
        "logros_posibles": LOGROS
    }
