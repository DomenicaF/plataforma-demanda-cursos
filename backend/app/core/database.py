"""Capa de persistencia: motor y sesiones de SQLAlchemy.

Centraliza la creación del engine y la fábrica de sesiones. El resto de la
aplicación obtiene una sesión mediante la dependencia `get_db`, lo que
mantiene el acceso a datos aislado del resto de capas (RNF-02, RNF-05).
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from app.core.config import settings

# pool_pre_ping evita errores por conexiones caducadas (RNF-04 disponibilidad)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para todos los modelos ORM
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI que entrega una sesión y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
