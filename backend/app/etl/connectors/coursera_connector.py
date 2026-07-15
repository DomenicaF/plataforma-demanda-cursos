"""Conector de datos REALES: dataset público de cursos de Coursera.

Origen: dataset abierto de Coursera (~890 cursos reales), publicado en Kaggle
(siddharthm1698/coursera-course-dataset) y replicado públicamente en GitHub.
Trae nº de estudiantes inscritos, dificultad y organización, pero NO fecha de
publicación ni materia. Por eso:
  - published_at se deja vacío (los cursos se registran en el periodo de carga).
  - La categoría se infiere del título mediante coincidencia de palabras clave
    (clasificación básica por texto), etiquetando como "Otros" lo no reconocido.

La URL es configurable mediante config['url'].
"""
import pandas as pd

from app.etl.connectors.base import BaseConnector

DEFAULT_URL = (
    "https://raw.githubusercontent.com/Siddharth1698/Coursera-Course-Dataset/"
    "master/UCoursera_Courses.csv"
)

# Áreas de conocimiento y palabras clave para clasificar el título
CATEGORY_KEYWORDS = {
    "Data Science": ["data", "statistic", "analytics", "sql", "excel"],
    "Machine Learning": ["machine learning", "deep learning", "neural", "tensorflow", "ai"],
    "Programming": ["python", "java", "programming", "software", "developer", "c++"],
    "Web Development": ["web", "javascript", "html", "css", "react", "frontend"],
    "Business & Marketing": ["business", "marketing", "management", "finance", "leadership"],
    "Cloud & IT": ["cloud", "aws", "azure", "google cloud", "network", "devops"],
    "Cybersecurity": ["security", "cyber", "hacking", "cryptograph"],
    "Health & Medicine": ["health", "medicine", "medical", "clinical", "nursing"],
    "Language & Arts": ["language", "english", "writing", "music", "art", "design"],
}


def _infer_category(title: str) -> str:
    t = (title or "").lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(k in t for k in keywords):
            return category
    return "Otros"


def _parse_enrolled(value) -> int | None:
    """Convierte '5.3k', '124k', '1.2m' a un entero."""
    if pd.isna(value):
        return None
    s = str(value).strip().lower().replace(",", "")
    mult = 1
    if s.endswith("k"):
        mult, s = 1_000, s[:-1]
    elif s.endswith("m"):
        mult, s = 1_000_000, s[:-1]
    try:
        return int(float(s) * mult)
    except ValueError:
        return None


class CourseraConnector(BaseConnector):
    def fetch(self) -> pd.DataFrame:
        url = self.config.get("url", DEFAULT_URL)
        raw = pd.read_csv(url)

        out = pd.DataFrame({
            "external_id": raw.iloc[:, 0].astype(str),  # primera col = índice
            "title": raw["course_title"],
            "description": raw["course_title"],
            "instructor": raw["course_organization"],
            "price": None,
            "duration_hours": None,
            "language": "en",
            "difficulty_level": raw["course_difficulty"],
            "num_students": raw["course_students_enrolled"].apply(_parse_enrolled),
            "published_at": None,  # el dataset no incluye fecha de publicación
            "platform": "Coursera",
            "category": raw["course_title"].apply(_infer_category),
        })
        return out
