"""Servicio de análisis de tendencias.

Recalcula las métricas por categoría y periodo a partir de los cursos cargados
y deriva las tendencias (dirección, tasa de crecimiento y nivel de confianza).
También expone el análisis de tópicos sobre las descripciones de los cursos.
"""
from collections import defaultdict

from sqlalchemy.orm import Session

from app.analysis import topics, trends
from app.models.course import Course
from app.models.platform import Platform
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.metric_repository import MetricRepository

# Caché en memoria del análisis de tópicos (LDA es costoso; se calcula una vez
# y se refresca tras cada ETL). Clave = nº de tópicos.
_TOPIC_CACHE: dict[int, list[dict]] = {}


class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.catalog = CatalogRepository(db)
        self.metrics = MetricRepository(db)

    def recompute_all(self) -> dict:
        """Recalcula métricas y tendencias para todas las categorías/periodos."""
        courses = self.db.query(Course).all()

        # Agrupación: (categoría, periodo) -> acumuladores
        grouped: dict[tuple[int, int], dict] = defaultdict(
            lambda: {"num_courses": 0, "num_students": 0, "price_sum": 0.0, "price_n": 0}
        )
        for course in courses:
            ref_date = course.published_at or course.created_at
            if ref_date is None:
                continue
            period = self.catalog.get_or_create_period(ref_date.date(), "month")
            for category in course.categories:
                key = (category.id, period.id)
                g = grouped[key]
                g["num_courses"] += 1
                g["num_students"] += course.num_students or 0
                if course.price is not None:
                    g["price_sum"] += course.price
                    g["price_n"] += 1
        self.db.flush()

        # Persistir métricas
        for (cat_id, period_id), g in grouped.items():
            avg_price = g["price_sum"] / g["price_n"] if g["price_n"] else None
            self.metrics.upsert_metric(
                cat_id, period_id,
                num_courses=g["num_courses"],
                num_students=g["num_students"],
                avg_price=avg_price,
            )
        self.db.flush()

        self._compute_changes_and_tendencies()
        self.db.commit()
        _TOPIC_CACHE.clear()  # los datos cambiaron: invalidar tópicos cacheados
        return {"categorias_periodos": len(grouped)}

    def _compute_changes_and_tendencies(self):
        """Calcula la variación entre periodos y la tendencia por categoría."""
        rows = self.metrics.series_by_category()
        # Ordenar por categoría y fecha
        by_cat: dict[str, list] = defaultdict(list)
        for r in rows:
            by_cat[r.category].append(r)

        # Necesitamos ids; recargamos métricas ordenadas por categoría/periodo
        from app.models.category import Category
        from app.models.metric import Metric
        from app.models.period import Period

        for category in self.db.query(Category).all():
            metrics = (
                self.db.query(Metric)
                .join(Period, Period.id == Metric.period_id)
                .filter(Metric.category_id == category.id)
                .order_by(Period.start_date)
                .all()
            )
            if not metrics:
                continue

            # Variación respecto al periodo anterior
            prev = None
            series = []
            for m in metrics:
                m.change_pct = trends.growth_rate(prev, m.num_courses) if prev is not None else None
                prev = m.num_courses
                series.append(m.num_courses)

            # Tendencia global de la categoría (se asocia al último periodo)
            t = trends.linear_trend(series)
            last_period_id = metrics[-1].period_id
            self.metrics.upsert_tendency(
                category.id, last_period_id,
                direction=t["direction"],
                growth_rate=t["growth_rate"],
                confidence_level=t["confidence_level"],
            )

    def topic_analysis(self, num_topics: int = 5, refresh: bool = False) -> list[dict]:
        """Descubre los temas latentes en las descripciones de los cursos.

        Analiza solo descripciones reales de cursos (excluye Google Trends, que
        no son texto de curso). Cachea el resultado por rendimiento (RNF-01).
        """
        if not refresh and num_topics in _TOPIC_CACHE:
            return _TOPIC_CACHE[num_topics]

        query = (
            self.db.query(Course)
            .outerjoin(Platform, Platform.id == Course.platform_id)
            .filter((Platform.name.is_(None)) | (Platform.name != "Google Trends"))
        )
        docs = [f"{c.title} {c.description or ''}" for c in query.all()]
        result = topics.discover_topics(docs, num_topics=num_topics)
        _TOPIC_CACHE[num_topics] = result
        return result
