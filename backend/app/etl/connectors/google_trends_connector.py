"""Conector real (configurable): tendencias de búsqueda vía Google Trends.

Usa la librería pytrends. Traduce el interés de búsqueda por término
(cada término se trata como una "categoría") a filas del esquema común,
donde num_students representa el índice de interés (0-100) del periodo.

Se activa desde la administración de fuentes. Si pytrends no está instalado
o falla la red, lanza una excepción controlada que el ETL registra como error
sin afectar al resto de fuentes (RNF-02, RNF-04).
"""
from datetime import datetime

import pandas as pd

from app.core.config import settings
from app.etl.connectors.base import BaseConnector


class GoogleTrendsConnector(BaseConnector):
    def fetch(self) -> pd.DataFrame:
        if not settings.GOOGLE_TRENDS_ENABLED:
            raise RuntimeError("El conector de Google Trends está deshabilitado.")

        try:
            from pytrends.request import TrendReq
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "pytrends no está instalado. Ejecute: pip install pytrends"
            ) from exc

        # Términos a consultar (áreas de conocimiento). Configurables por fuente.
        terms: list[str] = self.config.get(
            "terms",
            ["data science", "machine learning", "web development",
             "cybersecurity", "cloud computing"],
        )
        timeframe = self.config.get("timeframe", "today 12-m")

        pytrends = TrendReq(hl=settings.GOOGLE_TRENDS_LANG, tz=0)
        rows: list[dict] = []

        # Google Trends admite hasta 5 términos por consulta
        for i in range(0, len(terms), 5):
            batch = terms[i : i + 5]
            pytrends.build_payload(
                batch, timeframe=timeframe, geo=settings.GOOGLE_TRENDS_GEO
            )
            interest = pytrends.interest_over_time()
            if interest.empty:
                continue
            for ts, record in interest.iterrows():
                published = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
                for term in batch:
                    if term not in record:
                        continue
                    rows.append({
                        # id y título únicos por semana para conservar la serie
                        "external_id": f"gt-{term}-{published:%Y%m%d}",
                        "title": f"Interés '{term}' ({published:%Y-%m-%d})",
                        "description": f"Índice de interés de Google Trends para '{term}'.",
                        "instructor": None,
                        "price": None,
                        "duration_hours": None,
                        "language": settings.GOOGLE_TRENDS_LANG,
                        "difficulty_level": None,
                        "num_students": int(record[term]),  # índice 0-100
                        "published_at": published if isinstance(published, datetime) else None,
                        "platform": "Google Trends",
                        "category": term,
                    })

        if not rows:
            return self.empty_frame()
        return pd.DataFrame(rows)
