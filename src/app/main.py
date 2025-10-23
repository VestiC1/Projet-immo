from fastapi import FastAPI
from .routes import router

app = FastAPI(
    title="Prediction de valeurs immobilières",
    description="API de prédiction des valeurs immobilières basée sur des modèles d'apprentissage automatique.",
    version="1.0.0"
)

app.include_router(router)