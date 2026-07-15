"""Etapas (filtros) del proceso ETL, organizadas como una tubería
'pipes and filters': extraer → validar → limpiar → cargar.

Cada función recibe y devuelve un DataFrame de Pandas (salvo la carga, que
persiste en la base de datos), de modo que las etapas son independientes y
reutilizables (RNF-02, RNF-05).
"""
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.etl.connectors import get_connector
from app.etl.connectors.base import COMMON_COLUMNS
from app.models.course import Course
from app.repositories.catalog_repository import CatalogRepository


# ----------------------------- EXTRAER -----------------------------
def extract(source_type: str, config: dict | None) -> pd.DataFrame:
    """Obtiene los datos crudos desde la fuente configurada."""
    connector_cls = get_connector(source_type)
    connector = connector_cls(config)
    df = connector.fetch()
    # Garantiza que existan todas las columnas del esquema común
    for col in COMMON_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan
    return df[COMMON_COLUMNS]


# ----------------------------- VALIDAR -----------------------------
def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Descarta filas sin datos mínimos válidos (título y categoría)."""
    if df.empty:
        return df
    df = df.copy()
    df["title"] = df["title"].astype("string").str.strip()
    df["category"] = df["category"].astype("string").str.strip()
    valid = df["title"].notna() & (df["title"] != "") \
        & df["category"].notna() & (df["category"] != "")
    return df[valid]


# ----------------------------- LIMPIAR -----------------------------
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Estandariza formatos, corrige tipos y elimina duplicados."""
    if df.empty:
        return df
    df = df.copy()

    # Normalización de texto
    for col in ["title", "description", "instructor", "language",
                "difficulty_level", "platform", "category"]:
        df[col] = df[col].astype("string").str.strip()
    df["category"] = df["category"].str.title()
    df["language"] = df["language"].str.lower()

    # Tipos numéricos (valores no convertibles -> NaN)
    for col in ["price", "duration_hours", "num_students"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["num_students"] = df["num_students"].fillna(0).astype(int)

    # Fechas
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")

    # Eliminación de duplicados por (external_id) o por (title, platform)
    if df["external_id"].notna().any():
        df = df.drop_duplicates(subset=["external_id"], keep="first")
    df = df.drop_duplicates(subset=["title", "platform"], keep="first")

    return df


# ----------------------------- CARGAR ------------------------------
def load(db: Session, df: pd.DataFrame, data_source_id: int | None) -> int:
    """Persiste los cursos en la base de datos, evitando duplicados."""
    if df.empty:
        return 0
    catalog = CatalogRepository(db)
    loaded = 0

    for _, row in df.iterrows():
        external_id = None if pd.isna(row["external_id"]) else str(row["external_id"])
        if data_source_id and catalog.course_exists(external_id, data_source_id):
            continue

        platform = catalog.get_or_create_platform(
            row["platform"] if not pd.isna(row["platform"]) else "Desconocida"
        )
        category = catalog.get_or_create_category(row["category"])

        published = None if pd.isna(row["published_at"]) else row["published_at"].to_pydatetime()
        course = Course(
            external_id=external_id,
            title=str(row["title"]),
            description=None if pd.isna(row["description"]) else str(row["description"]),
            instructor=None if pd.isna(row["instructor"]) else str(row["instructor"]),
            price=None if pd.isna(row["price"]) else float(row["price"]),
            duration_hours=None if pd.isna(row["duration_hours"]) else float(row["duration_hours"]),
            language=None if pd.isna(row["language"]) else str(row["language"]),
            difficulty_level=None if pd.isna(row["difficulty_level"]) else str(row["difficulty_level"]),
            num_students=int(row["num_students"]),
            published_at=published,
            platform_id=platform.id,
            data_source_id=data_source_id,
        )
        course.categories.append(category)
        catalog.add_course(course)
        loaded += 1

    db.commit()
    return loaded
