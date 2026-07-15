"""Controlador del tablero: resumen, series temporales, comparación y filtros."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.schemas import CategoryOut
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Tablero"])


@router.get("/summary")
def summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return DashboardService(db).summary()


@router.get("/categories", response_model=list[CategoryOut])
def categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return DashboardService(db).categories()


@router.get("/time-series")
def time_series(
    category_ids: list[int] | None = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Evolución temporal del nº de cursos, con filtro opcional por categoría."""
    return DashboardService(db).time_series(category_ids)


@router.get("/comparison")
def comparison(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return DashboardService(db).category_comparison()


@router.get("/supply-series")
def supply_series(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Oferta: cursos publicados por mes (Udemy, 2011-2017)."""
    return DashboardService(db).supply_series()


@router.get("/demand-series")
def demand_series(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Demanda: índice de interés de búsqueda por mes (Google Trends, 2021-2026)."""
    return DashboardService(db).demand_series()


@router.get("/demand-forecast")
def demand_forecast(months: int = 6, db: Session = Depends(get_db),
                    _=Depends(get_current_user)):
    """Predicción básica de la demanda (proyección por regresión lineal)."""
    return DashboardService(db).demand_forecast(months)
