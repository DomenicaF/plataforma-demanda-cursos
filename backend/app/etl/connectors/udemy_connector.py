"""Conector de datos REALES: dataset público de cursos de Udemy.

Origen: dataset abierto de Udemy (3.678 cursos reales, 2011-2017), publicado en
Kaggle (andrewmvd/udemy-courses) y replicado públicamente en GitHub. Incluye
fecha real de publicación y materia, lo que permite construir series temporales
reales de la oferta por área de conocimiento.

La URL es configurable mediante config['url'].
"""
import re

import pandas as pd

from app.etl.connectors.base import BaseConnector

DEFAULT_URL = (
    "https://raw.githubusercontent.com/srivi15/Udemy-courses-data-analysis/"
    "master/dataset/udemy_courses.csv"
)


def _duration_to_hours(value: str) -> float | None:
    """Convierte '1.5 hours' o '43 mins' a horas (float)."""
    if not isinstance(value, str):
        return None
    m = re.search(r"([\d.]+)", value)
    if not m:
        return None
    num = float(m.group(1))
    if "min" in value.lower():
        return round(num / 60.0, 2)
    return num


class UdemyConnector(BaseConnector):
    def fetch(self) -> pd.DataFrame:
        url = self.config.get("url", DEFAULT_URL)
        raw = pd.read_csv(url)

        out = pd.DataFrame({
            "external_id": raw["course_id"].astype(str),
            "title": raw["course_title"],
            "description": raw.get("subject"),  # el dataset no trae descripción
            "instructor": None,
            "price": pd.to_numeric(raw["price"], errors="coerce"),
            "duration_hours": raw["content_duration"].apply(_duration_to_hours),
            "language": "en",
            "difficulty_level": raw["level"],
            "num_students": pd.to_numeric(raw["num_subscribers"], errors="coerce"),
            "published_at": raw["published_timestamp"],
            "platform": "Udemy",
            "category": raw["subject"],
        })
        return out
