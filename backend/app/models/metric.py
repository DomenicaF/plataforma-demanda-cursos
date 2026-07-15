"""Entidad Metric (métrica). Almacena los valores calculados para cada
categoría y periodo: número de cursos, número de estudiantes, precio medio,
y la variación respecto al periodo anterior.
"""
from sqlalchemy import Column, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Metric(Base):
    __tablename__ = "metric"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    period_id = Column(Integer, ForeignKey("period.id"), nullable=False)

    num_courses = Column(Integer, nullable=False, default=0)
    num_students = Column(Integer, nullable=True, default=0)
    avg_price = Column(Float, nullable=True)
    # Variación porcentual del nº de cursos frente al periodo anterior
    change_pct = Column(Float, nullable=True)

    category = relationship("Category", back_populates="metrics")
    period = relationship("Period", back_populates="metrics")

    __table_args__ = (
        UniqueConstraint("category_id", "period_id", name="uq_metric_cat_period"),
    )
