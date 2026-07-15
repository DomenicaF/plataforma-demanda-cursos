"""Modelos ORM (capa de persistencia).

Reexporta todas las entidades para que `Base.metadata.create_all` las registre.
Corresponde al diagrama entidad-relación descrito en el TFM.
"""
from app.models.category import Category, course_category
from app.models.course import Course
from app.models.platform import Platform
from app.models.data_source import DataSource
from app.models.period import Period
from app.models.metric import Metric
from app.models.tendency import Tendency
from app.models.registration_etl import RegistrationETL
from app.models.user import User

__all__ = [
    "Category",
    "course_category",
    "Course",
    "Platform",
    "DataSource",
    "Period",
    "Metric",
    "Tendency",
    "RegistrationETL",
    "User",
]
