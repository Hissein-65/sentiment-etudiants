# =============================================================================
# Fichier : main.py
# Rôle    : Point d'entrée principal de l'API FastAPI.
#           Démarre le serveur, crée les tables, charge le modèle IA,
#           et enregistre toutes les routes.
#           Lancement : uvicorn backend.main:app --reload --port 8000
# =============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database import creer_tables
from backend.routers.commentaires import router as router_commentaires
from backend.services.prediction_service import service_prediction


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Actions au démarrage et à l'arrêt du serveur."""
    print("\n[DÉMARRAGE] Initialisation de l'API...")
    creer_tables()
    service_prediction.charger()
    print("[DÉMARRAGE] API prête ✅\n")
    yield
    print("[ARRÊT] Fermeture de l'API.")


# ── Application FastAPI ────────────────────────────────────────────────────────
app = FastAPI(
    title       = "API Analyse de Sentiments Étudiants",
    description = (
        "API REST pour analyser automatiquement les sentiments des commentaires "
        "d'étudiants en utilisant le modèle CamemBERT fine-tuné.\n\n"
        "**Classes :** 0=Négatif | 1=Neutre | 2=Positif"
    ),
    version     = "1.0.0",
    lifespan    = lifespan
)

# ── CORS (permet à Flutter et Streamlit de contacter l'API) ───────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Enregistrement des routes ─────────────────────────────────────────────────
app.include_router(router_commentaires)


# ── Route de santé ────────────────────────────────────────────────────────────
@app.get("/", tags=["Santé"])
def racine():
    return {
        "message" : "API Analyse de Sentiments Étudiants — opérationnelle",
        "version" : "1.0.0",
        "docs"    : "/docs"
    }


@app.get("/health", tags=["Santé"])
def health_check():
    return {
        "status"       : "ok",
        "modele_charge": service_prediction._initialise
    }
