"""Servicio del tablero: prepara las series de datos que consume el frontend.

Devuelve estructuras listas para graficar con Plotly (resumen, evolución
temporal y comparación de categorías), aplicando los filtros dinámicos.
"""
from collections import defaultdict

from sqlalchemy.orm import Session

from app.analysis import trends
from app.models.category import Category, course_category
from app.models.course import Course
from app.models.platform import Platform
from app.repositories.metric_repository import MetricRepository


def _next_months(last_label: str, n: int) -> list[str]:
    """Genera las etiquetas 'YYYY-MM' de los n meses siguientes a last_label."""
    y, m = map(int, last_label.split("-"))
    labels = []
    for _ in range(n):
        m += 1
        if m > 12:
            m = 1; y += 1
        labels.append(f"{y:04d}-{m:02d}")
    return labels


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.metrics = MetricRepository(db)

    # ------------------------------------------------------------------
    # Series separadas por naturaleza del dato:
    #   - OFERTA  (Udemy): nº de cursos publicados por mes (medida = conteo)
    #   - DEMANDA (Google Trends): índice de interés 0-100 por mes (media)
    # Así cada gráfico representa una magnitud coherente y real.
    # ------------------------------------------------------------------
    def _platform_series(self, platform_name: str, measure: str) -> dict:
        rows = (
            self.db.query(
                Category.name.label("category"),
                Course.published_at.label("published_at"),
                Course.num_students.label("num_students"),
            )
            .join(course_category, course_category.c.course_id == Course.id)
            .join(Category, Category.id == course_category.c.category_id)
            .join(Platform, Platform.id == Course.platform_id)
            .filter(Platform.name == platform_name)
            .filter(Course.published_at.isnot(None))
            .all()
        )

        # Acumular por (categoría, YYYY-MM)
        agg: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
        for r in rows:
            label = f"{r.published_at.year:04d}-{r.published_at.month:02d}"
            agg[r.category][label].append(r.num_students or 0)

        series = []
        for category, periods in agg.items():
            ordered = sorted(periods.items())
            if measure == "count":
                values = [len(v) for _, v in ordered]
            else:  # avg_interest
                values = [round(sum(v) / len(v), 1) if v else 0 for _, v in ordered]
            series.append({
                "category": category,
                "periods": [p for p, _ in ordered],
                "values": values,
            })
        series.sort(key=lambda s: sum(s["values"]), reverse=True)
        return {"series": series}

    def supply_series(self) -> dict:
        """Oferta: nº de cursos publicados por mes (Udemy, con fechas reales)."""
        return self._platform_series("Udemy", "count")

    def demand_series(self) -> dict:
        """Demanda: índice de interés de búsqueda por mes (Google Trends)."""
        return self._platform_series("Google Trends", "avg_interest")

    def demand_forecast(self, months: int = 6) -> dict:
        """Predicción básica: proyecta la demanda de cada área 'months' meses
        hacia el futuro mediante regresión lineal (modelo predictivo básico)."""
        base = self._platform_series("Google Trends", "avg_interest")["series"]
        out = []
        for s in base:
            if len(s["values"]) < 3:
                continue
            fc_vals = trends.forecast(s["values"], months)
            fc_periods = _next_months(s["periods"][-1], months)
            out.append({
                "category": s["category"],
                "periods": s["periods"],
                "values": s["values"],
                "forecast_periods": fc_periods,
                "forecast_values": fc_vals,
            })
        out.sort(key=lambda s: sum(s["values"]), reverse=True)
        return {"series": out, "horizon": months}

    def summary(self) -> dict:
        data = self.metrics.summary()
        data["top_growing"] = [
            {
                "category": r.category,
                "direction": r.direction,
                "growth_rate": r.growth_rate,
                "confidence_level": r.confidence_level,
            }
            for r in self.metrics.top_growing(limit=5)
        ]
        return data

    def categories(self) -> list[dict]:
        return [
            {"id": c.id, "name": c.name}
            for c in self.db.query(Category).order_by(Category.name).all()
        ]

    def time_series(self, category_ids: list[int] | None = None) -> dict:
        """Serie temporal de nº de cursos por categoría (para gráfico de líneas)."""
        rows = self.metrics.series_by_category(category_ids)
        series: dict[str, dict] = {}
        for r in rows:
            s = series.setdefault(r.category, {"category": r.category, "periods": [], "values": []})
            s["periods"].append(r.period)
            s["values"].append(r.num_courses)
        return {"series": list(series.values())}

    def category_comparison(self) -> dict:
        """Total de cursos por categoría (para gráfico de barras)."""
        rows = self.metrics.series_by_category()
        totals: dict[str, int] = {}
        for r in rows:
            totals[r.category] = totals.get(r.category, 0) + (r.num_courses or 0)
        ordered = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
        return {
            "categories": [k for k, _ in ordered],
            "values": [v for _, v in ordered],
        }
