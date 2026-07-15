"""Orquestador del proceso ETL.

Encadena las etapas extraer → validar → limpiar → cargar y registra la
trazabilidad de la ejecución en Registration_ETL (RF-02, HU-02, CU-02).
Tras la carga, dispara el recálculo de métricas y tendencias.
"""
import json
import logging

from sqlalchemy.orm import Session

from app.etl import stages
from app.repositories.data_source_repository import DataSourceRepository
from app.repositories.etl_repository import ETLRepository

logger = logging.getLogger("etl")


def run_etl(db: Session, data_source_id: int | None = None) -> dict:
    """Ejecuta el ETL para una fuente concreta o para todas las activas."""
    ds_repo = DataSourceRepository(db)
    if data_source_id is not None:
        sources = [ds_repo.get(data_source_id)]
        sources = [s for s in sources if s is not None]
    else:
        sources = [s for s in ds_repo.list() if s.is_active]

    resultados = []
    for source in sources:
        resultados.append(_run_single(db, source))

    # Recalcular métricas y tendencias con los datos ya cargados
    from app.services.analysis_service import AnalysisService
    AnalysisService(db).recompute_all()

    return {"ejecuciones": resultados}


def _run_single(db: Session, source) -> dict:
    etl_repo = ETLRepository(db)
    ds_repo = DataSourceRepository(db)
    run = etl_repo.start(source.id)
    extracted = transformed = loaded = 0
    try:
        config = json.loads(source.config) if source.config else {}
        # EXTRAER
        raw = stages.extract(source.source_type, config)
        extracted = len(raw)
        # VALIDAR + LIMPIAR
        validated = stages.validate(raw)
        cleaned = stages.clean(validated)
        transformed = len(cleaned)
        # CARGAR
        loaded = stages.load(db, cleaned, source.id)

        ds_repo.mark_run(source)
        etl_repo.finish(run, "exito", extracted, transformed, loaded)
        logger.info(
            "ETL fuente '%s': extraídos=%d transformados=%d cargados=%d",
            source.name, extracted, transformed, loaded,
        )
        return {
            "fuente": source.name, "estado": "exito",
            "extraidos": extracted, "transformados": transformed, "cargados": loaded,
        }
    except Exception as exc:  # noqa: BLE001 — se registra cualquier fallo
        db.rollback()
        etl_repo.finish(run, "error", extracted, transformed, loaded, str(exc))
        logger.exception("Error en ETL de la fuente '%s'", source.name)
        return {"fuente": source.name, "estado": "error", "error": str(exc)}
