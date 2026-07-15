"""Entidad Category (categoría / área de conocimiento) y la tabla intermedia
Course_category que resuelve la relación muchos-a-muchos con Course.
"""
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from app.core.database import Base

# Tabla intermedia Course_category (un curso puede tener varias categorías)
course_category = Table(
    "course_category",
    Base.metadata,
    Column("course_id", ForeignKey("course.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("category.id", ondelete="CASCADE"), primary_key=True),
)


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    courses = relationship(
        "Course", secondary=course_category, back_populates="categories"
    )
    metrics = relationship("Metric", back_populates="category")
    tendencies = relationship("Tendency", back_populates="category")
