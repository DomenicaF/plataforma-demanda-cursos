"""Interfaz común de los conectores de adquisición.

El esquema de salida esperado (columnas del DataFrame) es:
    external_id, title, description, instructor, price, duration_hours,
    language, difficulty_level, num_students, published_at,
    platform, category
Cada conector traduce su fuente concreta a este esquema.
"""
from abc import ABC, abstractmethod

import pandas as pd

COMMON_COLUMNS = [
    "external_id", "title", "description", "instructor", "price",
    "duration_hours", "language", "difficulty_level", "num_students",
    "published_at", "platform", "category",
]


class BaseConnector(ABC):
    def __init__(self, config: dict | None = None):
        self.config = config or {}

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """Extrae los datos de la fuente y los devuelve en el esquema común."""
        raise NotImplementedError

    @staticmethod
    def empty_frame() -> pd.DataFrame:
        return pd.DataFrame(columns=COMMON_COLUMNS)
