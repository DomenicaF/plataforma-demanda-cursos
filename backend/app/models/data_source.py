"""Entidad Data_source (fuente de datos). Documenta el origen de la información:
tipo, URL y formato. Es el elemento central del RF-01 (gestión de fuentes).
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class DataSource(Base):
    __tablename__ = "data_source"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    # Tipo de conector: "csv" (dataset de ejemplo) o "google_trends" (real)
    source_type = Column(String(50), nullable=False, default="csv")
    url = Column(String(500), nullable=True)
    data_format = Column(String(50), nullable=True)  # csv, json, api...
    # Frecuencia de actualización sugerida (en horas)
    update_frequency_hours = Column(Integer, nullable=True, default=24)
    # Parámetros específicos del conector, serializados en JSON (texto)
    config = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    platform_id = Column(Integer, ForeignKey("platform.id"), nullable=True)

    platform = relationship("Platform", back_populates="data_sources")
    courses = relationship("Course", back_populates="data_source")
    etl_runs = relationship("RegistrationETL", back_populates="data_source")
