"""Repositorio del catálogo (cursos, categorías, plataformas y periodos).

Agrupa el acceso a las entidades de referencia y ofrece utilidades de
'get or create' usadas por el proceso ETL para evitar duplicados.
"""
from datetime import date

from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.course import Course
from app.models.period import Period
from app.models.platform import Platform


class CatalogRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Categorías ---
    def get_or_create_category(self, name: str) -> Category:
        name = name.strip()
        cat = self.db.query(Category).filter(Category.name == name).first()
        if cat is None:
            cat = Category(name=name)
            self.db.add(cat)
            self.db.flush()
        return cat

    def list_categories(self) -> list[Category]:
        return self.db.query(Category).order_by(Category.name).all()

    # --- Plataformas ---
    def get_or_create_platform(self, name: str, url: str | None = None) -> Platform:
        name = (name or "Desconocida").strip()
        plat = self.db.query(Platform).filter(Platform.name == name).first()
        if plat is None:
            plat = Platform(name=name, url=url)
            self.db.add(plat)
            self.db.flush()
        return plat

    # --- Periodos ---
    def get_or_create_period(self, d: date, granularity: str = "month") -> Period:
        if granularity == "month":
            label = f"{d.year:04d}-{d.month:02d}"
            start = date(d.year, d.month, 1)
            period = self.db.query(Period).filter(
                Period.granularity == "month", Period.label == label
            ).first()
            if period is None:
                period = Period(
                    granularity="month", year=d.year, month=d.month,
                    start_date=start, label=label,
                )
                self.db.add(period)
                self.db.flush()
            return period
        # Granularidad anual como alternativa
        label = f"{d.year:04d}"
        period = self.db.query(Period).filter(
            Period.granularity == "year", Period.label == label
        ).first()
        if period is None:
            period = Period(
                granularity="year", year=d.year, start_date=date(d.year, 1, 1),
                label=label,
            )
            self.db.add(period)
            self.db.flush()
        return period

    # --- Cursos ---
    def add_course(self, course: Course) -> Course:
        self.db.add(course)
        return course

    def course_exists(self, external_id: str, data_source_id: int) -> bool:
        if not external_id:
            return False
        return self.db.query(Course.id).filter(
            Course.external_id == external_id,
            Course.data_source_id == data_source_id,
        ).first() is not None
