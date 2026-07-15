"""Servicio ETL: expone la ejecución del proceso y su historial (CU-02)."""
from sqlalchemy.orm import Session

from app.etl.pipeline import run_etl
from app.repositories.etl_repository import ETLRepository


class ETLService:
    def __init__(self, db: Session):
        self.db = db

    def run(self, data_source_id: int | None = None) -> dict:
        return run_etl(self.db, data_source_id)

    def history(self, limit: int = 50) -> list[dict]:
        runs = ETLRepository(self.db).list(limit)
        return [
            {
                "id": r.id,
                "data_source_id": r.data_source_id,
                "started_at": r.started_at,
                "finished_at": r.finished_at,
                "status": r.status,
                "records_extracted": r.records_extracted,
                "records_transformed": r.records_transformed,
                "records_loaded": r.records_loaded,
                "duration_seconds": r.duration_seconds,
                "error_message": r.error_message,
            }
            for r in runs
        ]
