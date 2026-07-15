"""Evaluación objetiva del sistema: pruebas funcionales, rendimiento y calidad
de datos del ETL. Genera resultados reales y reproducibles para el TFM.

Requiere el backend en ejecución en http://127.0.0.1:8000.
Uso:  python -m scripts.evaluate_system
"""
import statistics
import time

import requests

BASE = "http://127.0.0.1:8000"
API = f"{BASE}/api"


def login(email, password):
    r = requests.post(f"{API}/auth/login",
                      data={"username": email, "password": password}, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]


def timeit(method, url, headers=None, runs=10, **kw):
    times = []
    last = None
    for _ in range(runs):
        t0 = time.perf_counter()
        last = requests.request(method, url, headers=headers, timeout=60, **kw)
        times.append((time.perf_counter() - t0) * 1000)
    return {
        "media_ms": round(statistics.mean(times), 1),
        "max_ms": round(max(times), 1),
        "status": last.status_code,
    }


def main():
    print("=" * 60)
    print("EVALUACIÓN DEL SISTEMA — pruebas funcionales, rendimiento y datos")
    print("=" * 60)

    admin = login("admin@demo.com", "admin123")
    analista = login("analista@demo.com", "analista123")
    ha = {"Authorization": f"Bearer {admin}"}
    hn = {"Authorization": f"Bearer {analista}"}

    # -------- 1. PRUEBAS FUNCIONALES (validación de requisitos) --------
    print("\n[1] PRUEBAS FUNCIONALES")
    checks = []

    def check(req, desc, ok):
        checks.append((req, desc, ok))
        print(f"   {'OK ' if ok else 'FALLA'} | {req} | {desc}")

    # RNF-06: se exige autenticación
    r = requests.get(f"{API}/dashboard/summary", timeout=30)
    check("RNF-06", "El acceso sin token se rechaza (401)", r.status_code == 401)

    # RNF-06: control por roles (analista no administra)
    r = requests.post(f"{API}/admin/sources", headers=hn,
                      json={"name": "x", "source_type": "csv"}, timeout=30)
    check("RNF-06", "El analista no puede administrar fuentes (403)", r.status_code == 403)

    # RF-01: el admin gestiona fuentes (crear + eliminar)
    r = requests.post(f"{API}/admin/sources", headers=ha,
                      json={"name": "Prueba eval", "source_type": "csv", "is_active": False}, timeout=30)
    created = r.status_code == 201
    sid = r.json()["id"] if created else None
    if sid:
        requests.delete(f"{API}/admin/sources/{sid}", headers=ha, timeout=30)
    check("RF-01", "El administrador crea y elimina fuentes de datos", created)

    # RF-02: existe traza de ejecuciones del ETL
    r = requests.get(f"{API}/etl/history", headers=ha, timeout=30)
    history = r.json() if r.status_code == 200 else []
    check("RF-02", "El ETL registra su ejecución (trazabilidad)", len(history) > 0)

    # RF análisis + viz: el tablero entrega datos
    r = requests.get(f"{API}/dashboard/summary", headers=ha, timeout=30)
    summ = r.json() if r.status_code == 200 else {}
    check("RF-viz", "El tablero entrega el resumen con datos", summ.get("total_courses", 0) > 0)

    r = requests.get(f"{API}/dashboard/demand-series", headers=ha, timeout=30)
    check("RF-análisis", "Serie de demanda disponible", len(r.json().get("series", [])) > 0)
    r = requests.get(f"{API}/dashboard/supply-series", headers=ha, timeout=30)
    check("RF-análisis", "Serie de oferta disponible", len(r.json().get("series", [])) > 0)

    passed = sum(1 for *_, ok in checks if ok)
    print(f"   --> {passed}/{len(checks)} pruebas superadas")

    # -------- 2. RENDIMIENTO (RNF-01: < 3 s) --------
    print("\n[2] RENDIMIENTO (media de 10 ejecuciones)")
    endpoints = {
        "/dashboard/summary": ("GET", f"{API}/dashboard/summary"),
        "/dashboard/demand-series": ("GET", f"{API}/dashboard/demand-series"),
        "/dashboard/supply-series": ("GET", f"{API}/dashboard/supply-series"),
        "/analysis/topics": ("GET", f"{API}/analysis/topics?num_topics=5"),
    }
    for name, (m, url) in endpoints.items():
        res = timeit(m, url, headers=ha, runs=10)
        cumple = "OK" if res["max_ms"] < 3000 else "REVISAR"
        print(f"   {name:32s} media={res['media_ms']:7.1f} ms  max={res['max_ms']:7.1f} ms  [{cumple}]")

    # -------- 3. CALIDAD DEL PROCESO ETL --------
    print("\n[3] CALIDAD DEL PROCESO ETL")
    exitos = sum(1 for h in history if h["status"] == "exito")
    print(f"   Ejecuciones registradas: {len(history)}  (éxito: {exitos})")
    for h in history:
        ext = h["records_extracted"]; tr = h["records_transformed"]; ld = h["records_loaded"]
        dur = h.get("duration_seconds")
        dedup = round((1 - tr / ext) * 100, 1) if ext else 0
        print(f"   fuente#{h['data_source_id']} estado={h['status']:6s} "
              f"extraídos={ext:5d} transformados={tr:5d} cargados={ld:5d} "
              f"depurado={dedup:4.1f}%  dur={dur}s")

    print("\nEVALUACIÓN COMPLETADA.")


if __name__ == "__main__":
    main()
