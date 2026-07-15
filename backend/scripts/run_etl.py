"""Ejecuta el proceso ETL desde la línea de comandos (útil para programarlo
con el planificador del sistema operativo, cumpliendo HU-02: ejecución
automática sin intervención del usuario).

Uso:
    python -m scripts.run_etl            # todas las fuentes activas
    python -m scripts.run_etl 1          # solo la fuente con id=1
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal  # noqa: E402
from app.services.etl_service import ETLService  # noqa: E402


def main():
    source_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    db = SessionLocal()
    try:
        result = ETLService(db).run(source_id)
        print("Resultado ETL:")
        for run in result["ejecuciones"]:
            print(" -", run)
    finally:
        db.close()


if __name__ == "__main__":
    main()
