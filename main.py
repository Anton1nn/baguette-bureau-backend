# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import auth, clients, orders, messages, whatsapp, processed_orders

# Création de l’application FastAPI
app = FastAPI(
    title="Baguette & Bureau",
    description="SaaS pour la gestion des commandes B2B de boulangeries artisanales.",
    version="1.0.0",
)

# Création des tables avec moteur async au démarrage de l'app
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Configuration CORS pour autoriser le frontend Render + local
origins = [
    "https://baguette-bureau-frontend.onrender.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(clients.router, prefix="/clients", tags=["Clients"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(messages.router, tags=["Messages"])
app.include_router(whatsapp.router, tags=["WhatsApp"])
app.include_router(processed_orders.router, prefix="/orders", tags=["Processed Orders"])

# Route de test
@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Baguette & Bureau !"}
