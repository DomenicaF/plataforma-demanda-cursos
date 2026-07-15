"""Funciones de análisis de tendencias.

Implementan el cálculo de tasas de crecimiento, las variaciones temporales y la
detección de la dirección de la tendencia mediante una regresión lineal simple,
cuyo coeficiente de determinación (R²) se usa como nivel de confianza.
Corresponde a la sección 'Implementación del análisis de tendencias'.
"""
import numpy as np


def growth_rate(previous: float, current: float) -> float | None:
    """Variación porcentual entre dos periodos consecutivos."""
    if previous is None or previous == 0:
        return None
    return round((current - previous) / previous * 100.0, 2)


def linear_trend(values: list[float]) -> dict:
    """Ajusta una recta a la serie y devuelve pendiente, dirección y R².

    - direction: 'creciente', 'decreciente' o 'estable'
    - growth_rate: crecimiento total de la serie (%), de inicio a fin
    - confidence_level: R² del ajuste (0..1)
    """
    n = len(values)
    if n < 2:
        return {"direction": "estable", "slope": 0.0,
                "growth_rate": None, "confidence_level": None}

    x = np.arange(n, dtype=float)
    y = np.array(values, dtype=float)

    slope, intercept = np.polyfit(x, y, 1)
    y_pred = slope * x + intercept
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    first, last = y[0], y[-1]
    total_growth = round((last - first) / first * 100.0, 2) if first != 0 else None

    # Umbral para considerar la serie estable frente al valor medio
    mean_abs = abs(y.mean()) if y.mean() != 0 else 1.0
    if abs(slope) < 0.05 * mean_abs:
        direction = "estable"
    elif slope > 0:
        direction = "creciente"
    else:
        direction = "decreciente"

    return {
        "direction": direction,
        "slope": round(float(slope), 4),
        "growth_rate": total_growth,
        "confidence_level": round(max(0.0, min(1.0, r2)), 3),
    }


def forecast(values: list[float], horizon: int = 6,
             lo: float = 0.0, hi: float = 100.0) -> list[float]:
    """Modelo predictivo básico: proyecta la serie 'horizon' periodos hacia el
    futuro mediante una regresión lineal, acotando los valores al rango [lo, hi]
    (el índice de interés de búsqueda se mueve entre 0 y 100).
    """
    n = len(values)
    if n < 2:
        return [round(values[-1], 1)] * horizon if values else []
    x = np.arange(n, dtype=float)
    y = np.array(values, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    out = []
    for i in range(1, horizon + 1):
        v = slope * (n - 1 + i) + intercept
        out.append(round(float(min(hi, max(lo, v))), 1))
    return out
