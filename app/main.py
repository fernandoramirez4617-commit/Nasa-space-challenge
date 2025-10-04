from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.api import game
from app.db.session import Base, engine

# Crear tablas al arrancar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Simulador del Campo",
    description="Decide riego y observa el estado del suelo de forma simple.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

app.include_router(game.router)

@app.get("/", response_class=HTMLResponse)
def portada():
    return """
    <main style="font-family:system-ui;max-width:760px;margin:48px auto;padding:0 16px;line-height:1.6">
      <h1>🌾 Simulador del Campo</h1>
      <p>API de juego sencilla para agricultores.</p>
      <ul>
        <li><b>Nuevo juego:</b> <code>POST /campo/nuevo</code></li>
        <li><b>Configurar:</b> <code>POST /campo/config</code> {"consumo":5,"azar_eventos":0.2}</li>
        <li><b>Ver estado:</b> <code>GET /campo/estado</code></li>
        <li><b>Avanzar día:</b> <code>POST /campo/avanzar</code> {"riego":20,"lluvia":0}</li>
        <li><b>Historial:</b> <code>GET /campo/historial</code></li>
      </ul>
      <p>👉 Prueba interactiva en <a href="/docs">/docs</a></p>
    </main>
    """
