"""Entidad Tendency (tendencia). Recoge la tendencia derivada de las métricas a
lo largo del tiempo, con su tasa de crecimiento y un nivel de confianza.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Tendency(Base):
    __tablename__ = "tendency"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    period_id = Column(Integer, ForeignKey("period.id"), nullable=False)

    # Dirección: "creciente", "decreciente" o "estable"
    direction = Column(String(20), nullable=False)
    growth_rate = Column(Float, nullable=True)      # tasa de crecimiento (%)
    confidence_level = Column(Float, nullable=True)  # 0..1 (bondad del ajuste)
    computed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    category = relationship("Category", back_populates="tendencies")
    period = relationship("Period", back_populates="tendencies")
