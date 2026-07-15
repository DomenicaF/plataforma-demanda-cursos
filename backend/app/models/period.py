"""Entidad Period (periodo). Modela la dimensión temporal (año, mes o semana)
sobre la que se calculan métricas y tendencias.
"""
from sqlalchemy import Column, Date, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Period(Base):
    __tablename__ = "period"

    id = Column(Integer, primary_key=True, index=True)
    # Granularidad: "year", "month" o "week"
    granularity = Column(String(10), nullable=False, default="month")
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=True)   # 1-12 si granularity = month
    week = Column(Integer, nullable=True)    # 1-53 si granularity = week
    start_date = Column(Date, nullable=False, index=True)
    label = Column(String(20), nullable=False)  # p. ej. "2025-03"

    metrics = relationship("Metric", back_populates="period")
    tendencies = relationship("Tendency", back_populates="period")

    __table_args__ = (
        UniqueConstraint("granularity", "label", name="uq_period_gran_label"),
    )
