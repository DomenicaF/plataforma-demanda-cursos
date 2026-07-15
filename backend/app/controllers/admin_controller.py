"""Controlador de administración de fuentes de datos (RF-01 / CU-01).

Todas las operaciones de escritura requieren rol Administrador (RNF-06).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.schemas.schemas import DataSourceCreate, DataSourceOut, DataSourceUpdate
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin/sources", tags=["Administración de fuentes"])


@router.get("", response_model=list[DataSourceOut])
def list_sources(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return AdminService(db).list_sources()


@router.post("", response_model=DataSourceOut, status_code=201)
def create_source(payload: DataSourceCreate, db: Session = Depends(get_db),
                  _=Depends(require_admin)):
    return AdminService(db).create_source(payload.model_dump())


@router.put("/{source_id}", response_model=DataSourceOut)
def update_source(source_id: int, payload: DataSourceUpdate,
                  db: Session = Depends(get_db), _=Depends(require_admin)):
    updated = AdminService(db).update_source(
        source_id, payload.model_dump(exclude_unset=True)
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Fuente de datos no encontrada")
    return updated


@router.delete("/{source_id}", status_code=204)
def delete_source(source_id: int, db: Session = Depends(get_db),
                  _=Depends(require_admin)):
    if not AdminService(db).delete_source(source_id):
        raise HTTPException(status_code=404, detail="Fuente de datos no encontrada")
