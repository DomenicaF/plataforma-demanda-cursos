"""Repositorio de fuentes de datos (RF-01: gestión de fuentes)."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.data_source import DataSource


class DataSourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[DataSource]:
        return self.db.query(DataSource).order_by(DataSource.id).all()

    def get(self, source_id: int) -> DataSource | None:
        return self.db.query(DataSource).filter(DataSource.id == source_id).first()

    def create(self, **data) -> DataSource:
        source = DataSource(**data)
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def update(self, source: DataSource, **data) -> DataSource:
        for key, value in data.items():
            if value is not None:
                setattr(source, key, value)
        self.db.commit()
        self.db.refresh(source)
        return source

    def delete(self, source: DataSource) -> None:
        self.db.delete(source)
        self.db.commit()

    def mark_run(self, source: DataSource) -> None:
        source.last_run_at = datetime.now(timezone.utc)
        self.db.commit()
