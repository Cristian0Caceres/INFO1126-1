# proyecto2/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# CORRECTO: rutas absolutas desde el módulo raíz
from api.controllers import clients, orders, reports, summary

app = FastAPI(
    title="Sistema Logístico de Drones - API",
    description="API para simulación de rutas, pedidos y generación de reportes",
    version="2.0"
)

# Habilitar CORS para permitir conexión desde otras apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar endpoints
app.include_router(clients.router, prefix="/clients", tags=["Clients"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
app.include_router(summary.router, prefix="/info/reports", tags=["Summary"])

@app.get("/")
def root():
    return {"message": "API del Sistema Logístico funcionando correctamente"}
