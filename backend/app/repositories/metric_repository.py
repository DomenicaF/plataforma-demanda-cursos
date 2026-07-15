"""Repositorio de métricas y tendencias, y consultas para el tablero.

Concentra las consultas analíticas para que el tablero responda con rapidez
(RNF-01) y para mantener el SQL fuera de las capas superiores.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.course import Course
from app.models.metric import Metric
from app.models.period import Period
from app.models.tendency import Tendency


class MetricRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_metric(self, category_id: int, period_id: int, **values) -> Metric:
        metric = self.db.query(Metric).filter(
            Metric.category_id == category_id, Metric.period_id == period_id
        ).first()
        if metric is None:
            metric = Metric(category_id=category_id, period_id=period_id, **values)
            self.db.add(metric)
        else:
            for k, v in values.items():
                setattr(metric, k, v)
        return metric

    def upsert_tendency(self, category_id: int, period_id: int, **values) -> Tendency:
        tendency = self.db.query(Tendency).filter(
            Tendency.category_id == category_id, Tendency.period_id == period_id
        ).first()
        if tendency is None:
            tendency = Tendency(category_id=category_id, period_id=period_id, **values)
            self.db.add(tendency)
        else:
            for k, v in values.items():
                setattr(tendency, k, v)
        return tendency

    # --- Consultas para el tablero ---
    def series_by_category(self, category_ids: list[int] | None = None):
        """Serie temporal de nº de cursos por categoría y periodo."""
        q = (
            self.db.query(
                Category.name.label("category"),
                Period.label.label("period"),
                Period.start_date.label("start_date"),
                Metric.num_courses.label("num_courses"),
                Metric.num_students.label("num_students"),
                Metric.change_pct.label("change_pct"),
            )
            .join(Metric, Metric.category_id == Category.id)
            .join(Period, Period.id == Metric.period_id)
        )
        if category_ids:
            q = q.filter(Category.id.in_(category_ids))
        return q.order_by(Period.start_date, Category.name).all()

    def summary(self) -> dict:
        total_courses = self.db.query(func.count(Course.id)).scalar() or 0
        total_categories = self.db.query(func.count(Category.id)).scalar() or 0
        total_students = self.db.query(func.sum(Course.num_students)).scalar() or 0
        num_periods = self.db.query(func.count(Period.id)).scalar() or 0
        return {
            "total_courses": int(total_courses),
            "total_categories": int(total_categories),
            "total_students": int(total_students),
            "num_periods": int(num_periods),
        }

    def top_growing(self, limit: int = 5):
        """Categorías con mayor tasa de crecimiento (última tendencia)."""
        sub = (
            self.db.query(
                Tendency.category_id,
                func.max(Period.start_date).label("max_date"),
            )
            .join(Period, Period.id == Tendency.period_id)
            .group_by(Tendency.category_id)
            .subquery()
        )
        rows = (
            self.db.query(
                Category.name.label("category"),
                Tendency.direction,
                Tendency.growth_rate,
                Tendency.confidence_level,
            )
            .join(Tendency, Tendency.category_id == Category.id)
            .join(Period, Period.id == Tendency.period_id)
            .join(
                sub,
                (sub.c.category_id == Tendency.category_id)
                & (sub.c.max_date == Period.start_date),
            )
            .order_by(Tendency.growth_rate.desc())
            .limit(limit)
            .all()
        )
        return rows
