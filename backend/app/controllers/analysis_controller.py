"""Controlador de análisis: recálculo de tendencias y modelado de tópicos."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["Análisis"])


@router.post("/recompute")
def recompute(db: Session = Depends(get_db), _=Depends(require_admin)):
    """Recalcula métricas y tendencias a partir de los cursos cargados."""
    return AnalysisService(db).recompute_all()


@router.get("/topics")
def topics(num_topics: int = 5, db: Session = Depends(get_db),
           _=Depends(get_current_user)):
    """Descubre los temas latentes en las descripciones de los cursos (LDA)."""
    return {"topics": AnalysisService(db).topic_analysis(num_topics)}
