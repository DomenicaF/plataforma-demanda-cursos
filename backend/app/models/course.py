"""Entidad Course (curso). Almacena los datos de cada curso recolectado:
título, descripción, instructor, precio, duración, idioma, nivel de dificultad
y número de estudiantes.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.category import course_category


class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), nullable=True, index=True)  # id en la fuente
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    instructor = Column(String(200), nullable=True)
    price = Column(Float, nullable=True)
    duration_hours = Column(Float, nullable=True)
    language = Column(String(50), nullable=True)
    difficulty_level = Column(String(50), nullable=True)
    num_students = Column(Integer, nullable=True)
    published_at = Column(DateTime, nullable=True, index=True)

    platform_id = Column(Integer, ForeignKey("platform.id"), nullable=True)
    data_source_id = Column(Integer, ForeignKey("data_source.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    platform = relationship("Platform", back_populates="courses")
    data_source = relationship("DataSource", back_populates="courses")
    categories = relationship(
        "Category", secondary=course_category, back_populates="courses"
    )
