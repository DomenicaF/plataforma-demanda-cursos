"""Entidad Registration_ETL (registro de ETL). Conserva la trazabilidad de cada
ejecución del proceso: fecha, estado, nº de registros extraídos/transformados/
cargados, tiempo de ejecución y posibles errores (soporta RF-02 y HU-02).
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class RegistrationETL(Base):
    __tablename__ = "registration_etl"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_source.id"), nullable=True)

    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    finished_at = Column(DateTime, nullable=True)
    # Estado: "en_progreso", "exito", "error"
    status = Column(String(20), nullable=False, default="en_progreso")

    records_extracted = Column(Integer, default=0)
    records_transformed = Column(Integer, default=0)
    records_loaded = Column(Integer, default=0)
    duration_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)

    data_source = relationship("DataSource", back_populates="etl_runs")
