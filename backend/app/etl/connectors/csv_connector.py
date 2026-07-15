"""Conector CSV: lee el dataset de ejemplo (estilo Kaggle) de cursos en línea.

Permite que el sistema funcione de inmediato, sin internet ni credenciales,
lo que resulta idóneo para la demostración y las pruebas de usabilidad.
La ruta del archivo se toma de config['path'] o del dataset incluido.
"""
from pathlib import Path

import pandas as pd

from app.etl.connectors.base import BaseConnector

DEFAULT_DATASET = (
    Path(__file__).resolve().parents[3] / "seed" / "courses_sample.csv"
)


class CSVConnector(BaseConnector):
    def fetch(self) -> pd.DataFrame:
        path = Path(self.config.get("path", DEFAULT_DATASET))
        if not path.exists():
            raise FileNotFoundError(f"No se encontró el dataset CSV: {path}")
        df = pd.read_csv(path)
        # El CSV de ejemplo ya viene en el esquema común; se devuelven las
        # columnas conocidas y se ignoran las adicionales.
        keep = [c for c in df.columns if c in self.empty_frame().columns]
        return df[keep]
