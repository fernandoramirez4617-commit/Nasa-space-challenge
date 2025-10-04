# app/api/game.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/game", tags=["game"])

class TickIn(BaseModel):
    irrigation_mm: float = 0
    nitrogen_kg_ha: float = 0

game_state = {"day": 0, "water_used": 0.0, "nitrogen_applied": 0.0}

@router.post("/tick")
def simulate_tick(payload: TickIn):
    game_state["day"] += 1
    game_state["water_used"] += payload.irrigation_mm
    game_state["nitrogen_applied"] += payload.nitrogen_kg_ha
    return {"message": f"Día {game_state['day']} ok", "state": game_state}

@router.get("/state")
def get_state():
    return game_state
