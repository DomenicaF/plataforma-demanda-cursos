"""Entidad User (usuario). Almacena las cuentas y sus roles (administrador o
analista), base del control de acceso diferenciado (RNF-06).
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.core.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=True)
    email = Column(String(200), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    # Rol: "administrador" o "analista"
    role = Column(String(20), nullable=False, default="analista")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
