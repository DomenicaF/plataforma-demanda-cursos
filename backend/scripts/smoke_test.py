"""Prueba de humo end-to-end del backend (usa la BD indicada por DATABASE_URL).

Verifica: inicialización, ETL sobre el CSV de ejemplo, recálculo de análisis,
consultas del tablero, modelado de tópicos y la API con autenticación.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.services.analysis_service import AnalysisService  # noqa: E402
from app.services.dashboard_service import DashboardService  # noqa: E402
from app.services.etl_service import ETLService  # noqa: E402
import scripts.init_db as init_db  # noqa: E402


def main():
    print("== 1. Inicializar BD y datos ==")
    init_db.main()

    db = SessionLocal()
    try:
        print("\n== 2. Ejecutar ETL (CSV de ejemplo) ==")
        result = ETLService(db).run()
        for r in result["ejecuciones"]:
            print("  ", r)

        print("\n== 3. Resumen del tablero ==")
        summary = DashboardService(db).summary()
        print("  ", summary)
        assert summary["total_courses"] > 0, "No se cargaron cursos"

        print("\n== 4. Serie temporal (primeras 2 categorías) ==")
        ts = DashboardService(db).time_series()
        for s in ts["series"][:2]:
            print(f"   {s['category']}: {len(s['periods'])} periodos, "
                  f"últimos valores {s['values'][-3:]}")

        print("\n== 5. Comparación de categorías ==")
        comp = DashboardService(db).category_comparison()
        for c, v in list(zip(comp["categories"], comp["values"]))[:5]:
            print(f"   {c}: {v}")

        print("\n== 6. Modelado de tópicos (LDA) ==")
        topics = AnalysisService(db).topic_analysis(num_topics=5)
        for t in topics:
            print(f"   Tópico {t['topic']}: {', '.join(t['keywords'][:6])}")
    finally:
        db.close()

    print("\n== 7. API con autenticación ==")
    from app.main import app
    client = TestClient(app)

    r = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        data={"username": settings.ADMIN_EMAIL, "password": settings.ADMIN_PASSWORD},
    )
    assert r.status_code == 200, f"login falló: {r.status_code} {r.text}"
    token = r.json()["access_token"]
    print("   login OK, rol:", r.json()["role"])

    headers = {"Authorization": f"Bearer {token}"}
    r = client.get(f"{settings.API_V1_PREFIX}/dashboard/summary", headers=headers)
    assert r.status_code == 200, f"summary falló: {r.text}"
    print("   /dashboard/summary OK:", r.json()["total_courses"], "cursos")

    r = client.get(f"{settings.API_V1_PREFIX}/dashboard/comparison", headers=headers)
    assert r.status_code == 200
    print("   /dashboard/comparison OK:", len(r.json()["categories"]), "categorías")

    # Un analista NO debe poder crear fuentes (RNF-06)
    ra = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        data={"username": settings.ANALISTA_EMAIL, "password": settings.ANALISTA_PASSWORD},
    )
    at = ra.json()["access_token"]
    r = client.post(
        f"{settings.API_V1_PREFIX}/admin/sources",
        headers={"Authorization": f"Bearer {at}"},
        json={"name": "X", "source_type": "csv"},
    )
    assert r.status_code == 403, f"el analista no debería poder crear fuentes: {r.status_code}"
    print("   control de acceso por rol OK (analista bloqueado con 403)")

    print("\n TODAS LAS PRUEBAS PASARON ")


if __name__ == "__main__":
    main()
