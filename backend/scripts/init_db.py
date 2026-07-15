"""Inicializa la base de datos: crea las tablas, los usuarios iniciales
(administrador y analista) y registra las fuentes de datos por defecto
(el dataset CSV de ejemplo y el conector de Google Trends).

Uso:  python -m scripts.init_db     (desde la carpeta backend)
"""
import json
import sys
from pathlib import Path

# Permite ejecutar el script directamente
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings          # noqa: E402
from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.core.security import hash_password    # noqa: E402
import app.models  # noqa: E402,F401
from app.models.data_source import DataSource  # noqa: E402
from app.models.platform import Platform       # noqa: E402
from app.models.user import User               # noqa: E402


def main():
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # --- Usuarios iniciales ---
        if db.query(User).count() == 0:
            db.add_all([
                User(
                    full_name="Administrador",
                    email=settings.ADMIN_EMAIL,
                    hashed_password=hash_password(settings.ADMIN_PASSWORD),
                    role="administrador",
                ),
                User(
                    full_name="Analista",
                    email=settings.ANALISTA_EMAIL,
                    hashed_password=hash_password(settings.ANALISTA_PASSWORD),
                    role="analista",
                ),
            ])
            print(f"  Usuario admin: {settings.ADMIN_EMAIL} / {settings.ADMIN_PASSWORD}")
            print(f"  Usuario analista: {settings.ANALISTA_EMAIL} / {settings.ANALISTA_PASSWORD}")

        # --- Fuentes de datos REALES por defecto ---
        if db.query(DataSource).count() == 0:
            db.add(DataSource(
                name="Cursos Udemy (dataset real, con fechas 2011-2017)",
                source_type="udemy",
                data_format="csv",
                url="https://raw.githubusercontent.com/srivi15/"
                    "Udemy-courses-data-analysis/master/dataset/udemy_courses.csv",
                update_frequency_hours=24,
                is_active=True,
            ))
            db.add(DataSource(
                name="Cursos Coursera (dataset real, ~890 cursos)",
                source_type="coursera",
                data_format="csv",
                url="https://raw.githubusercontent.com/Siddharth1698/"
                    "Coursera-Course-Dataset/master/UCoursera_Courses.csv",
                update_frequency_hours=24,
                is_active=True,
            ))
            db.add(DataSource(
                name="Tendencias de búsqueda (Google Trends, demanda real)",
                source_type="google_trends",
                data_format="api",
                update_frequency_hours=24,
                is_active=True,
                config=json.dumps({
                    # 5 años de demanda real y actual (2021-2026), por área
                    "terms": ["data science", "machine learning", "web development",
                              "cybersecurity", "cloud computing",
                              "artificial intelligence", "digital marketing",
                              "python programming", "graphic design"],
                    "timeframe": "today 5-y",
                }),
            ))
            # Dataset local de ejemplo, como respaldo offline (inactivo)
            plat = Platform(name="Dataset de ejemplo (offline)", url=None)
            db.add(plat)
            db.flush()
            db.add(DataSource(
                name="Cursos en línea (CSV de ejemplo, offline)",
                source_type="csv",
                data_format="csv",
                update_frequency_hours=24,
                is_active=False,
                platform_id=plat.id,
            ))
            print("  Fuentes de datos reales registradas (Udemy, Coursera, Google Trends).")

        db.commit()
        print("Base de datos inicializada correctamente.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
