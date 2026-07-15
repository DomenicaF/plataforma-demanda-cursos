"""Controlador del proceso ETL (CU-02).

La ejecución manual requiere rol Administrador; el historial es consultable por
cualquier usuario autenticado.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.schemas.schemas import ETLRunOut
from app.services.etl_service import ETLService

router = APIRouter(prefix="/etl", tags=["Proceso ETL"])


@router.post("/run")
def run_etl(source_id: int | None = None, db: Session = Depends(get_db),
            _=Depends(require_admin)):
    """Ejecuta el ETL para una fuente concreta o para todas las activas."""
    return ETLService(db).run(source_id)


@router.get("/history", response_model=list[ETLRunOut])
def history(limit: int = 50, db: Session = Depends(get_db),
            _=Depends(get_current_user)):
    return ETLService(db).history(limit)
