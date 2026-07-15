"""Servicio de administración de fuentes de datos (RF-01 / CU-01).

Encapsula la lógica de negocio para gestionar el catálogo de fuentes: alta,
consulta, actualización y baja, delegando el acceso a datos al repositorio.
"""
import json

from sqlalchemy.orm import Session

from app.repositories.data_source_repository import DataSourceRepository


class AdminService:
    def __init__(self, db: Session):
        self.repo = DataSourceRepository(db)

    def list_sources(self):
        return self.repo.list()

    def get_source(self, source_id: int):
        return self.repo.get(source_id)

    def create_source(self, data: dict):
        if isinstance(data.get("config"), dict):
            data["config"] = json.dumps(data["config"], ensure_ascii=False)
        return self.repo.create(**data)

    def update_source(self, source_id: int, data: dict):
        source = self.repo.get(source_id)
        if source is None:
            return None
        if isinstance(data.get("config"), dict):
            data["config"] = json.dumps(data["config"], ensure_ascii=False)
        return self.repo.update(source, **data)

    def delete_source(self, source_id: int) -> bool:
        source = self.repo.get(source_id)
        if source is None:
            return False
        self.repo.delete(source)
        return True
