"""Conectores de adquisición de datos.

Cada conector implementa la interfaz `BaseConnector.fetch()` y devuelve un
DataFrame con un esquema común. Añadir una nueva fuente consiste en crear un
nuevo conector, sin tocar el resto del sistema (RNF-02 escalabilidad).
"""
from app.etl.connectors.base import BaseConnector
from app.etl.connectors.csv_connector import CSVConnector
from app.etl.connectors.coursera_connector import CourseraConnector
from app.etl.connectors.google_trends_connector import GoogleTrendsConnector
from app.etl.connectors.udemy_connector import UdemyConnector


def get_connector(source_type: str) -> type[BaseConnector]:
    """Fábrica de conectores según el tipo de fuente."""
    registry = {
        "csv": CSVConnector,                 # dataset local de ejemplo (offline)
        "udemy": UdemyConnector,             # datos reales de cursos (Udemy)
        "coursera": CourseraConnector,       # datos reales de cursos (Coursera)
        "google_trends": GoogleTrendsConnector,  # demanda real de búsqueda
    }
    if source_type not in registry:
        raise ValueError(f"Tipo de fuente no soportado: {source_type}")
    return registry[source_type]


__all__ = [
    "BaseConnector", "CSVConnector", "UdemyConnector", "CourseraConnector",
    "GoogleTrendsConnector", "get_connector",
]
