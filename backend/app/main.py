"""Punto de entrada de la API REST (FastAPI).

Configura CORS, registra los controladores (capa de presentación de la API) y
crea las tablas en el arranque. La documentación interactiva OpenAPI queda
disponible en /docs (RNF-05 mantenibilidad).
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.controllers import (
    admin_controller,
    analysis_controller,
    auth_controller,
    dashboard_controller,
    etl_controller,
)
import app.models  # noqa: F401 — registra los modelos en Base.metadata

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "Plataforma para recolectar, almacenar, analizar y visualizar la "
        "demanda de cursos en línea. Trabajo Fin de Máster (UNIR)."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _warm_topic_cache():
    """Precalcula el análisis de tópicos (LDA) en segundo plano para que el
    primer acceso al tablero sea inmediato."""
    from app.core.database import SessionLocal
    from app.services.analysis_service import AnalysisService
    try:
        db = SessionLocal()
        AnalysisService(db).topic_analysis(5)
        db.close()
        logging.info("Caché de tópicos precalentada.")
    except Exception:  # noqa: BLE001
        logging.exception("No se pudo precalentar la caché de tópicos")


@app.on_event("startup")
def on_startup():
    # Crea las tablas si no existen (en producción usar migraciones)
    Base.metadata.create_all(bind=engine)
    # Precalienta la caché de tópicos sin bloquear el arranque
    import threading
    threading.Thread(target=_warm_topic_cache, daemon=True).start()


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok", "app": settings.APP_NAME}


api = settings.API_V1_PREFIX
app.include_router(auth_controller.router, prefix=api)
app.include_router(admin_controller.router, prefix=api)
app.include_router(etl_controller.router, prefix=api)
app.include_router(dashboard_controller.router, prefix=api)
app.include_router(analysis_controller.router, prefix=api)
