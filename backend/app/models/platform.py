"""Entidad Platform (plataforma). Una plataforma puede tener varias fuentes de
datos asociadas y agrupa los cursos que provienen de ella.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Platform(Base):
    __tablename__ = "platform"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True, index=True)
    url = Column(String(500), nullable=True)

    data_sources = relationship("DataSource", back_populates="platform")
    courses = relationship("Course", back_populates="platform")
