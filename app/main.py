# app/main.py
from fastapi import FastAPI
from app.api import game

app = FastAPI(title="Farm Data Quest API")
app.include_router(game.router)

@app.get("/")
def root():
    return {"message": "Bienvenido a Farm Data Quest API 🚜"}
