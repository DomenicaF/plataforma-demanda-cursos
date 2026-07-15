"""Repositorio del registro de ejecuciones ETL (trazabilidad, RF-02/HU-02)."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.registration_etl import RegistrationETL


class ETLRepository:
    def __init__(self, db: Session):
        self.db = db

    def start(self, data_source_id: int | None) -> RegistrationETL:
        run = RegistrationETL(data_source_id=data_source_id, status="en_progreso")
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def finish(self, run: RegistrationETL, status: str, extracted: int,
               transformed: int, loaded: int, error: str | None = None) -> RegistrationETL:
        run.finished_at = datetime.now(timezone.utc)
        run.status = status
        run.records_extracted = extracted
        run.records_transformed = transformed
        run.records_loaded = loaded
        run.error_message = error
        started = run.started_at
        if started is not None:
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            run.duration_seconds = (run.finished_at - started).total_seconds()
        self.db.commit()
        self.db.refresh(run)
        return run

    def list(self, limit: int = 50) -> list[RegistrationETL]:
        return (
            self.db.query(RegistrationETL)
            .order_by(RegistrationETL.started_at.desc())
            .limit(limit)
            .all()
        )
