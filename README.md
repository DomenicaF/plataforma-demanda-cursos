# Plataforma de Análisis de Demanda de Cursos en Línea

Implementación del sistema descrito en el TFM *"Predicción de tendencias
educativas en plataformas online a través de análisis de texto y modelos
predictivos"* (UNIR — Máster en Análisis y Visualización de Datos Masivos).

Aplicación web que **recolecta, almacena, analiza y visualiza** la demanda de
cursos en línea en un único tablero interactivo, siguiendo la arquitectura por
capas y el modelo de datos definidos en el documento.

---

## Arquitectura

```
Tablero (React + Plotly)                      ← capa de presentación
        │  HTTP/REST
API REST (FastAPI)                            ← controladores → servicios → repositorios
        │
ETL (Python + Pandas, "pipes & filters")      ← extraer → validar → limpiar → cargar
        │                                         (conectores enchufables)
Base de datos (MySQL + SQLAlchemy)            ← capa de persistencia
```

Correspondencia con el **modelo C4** del documento:
- **Contexto**: Administrador y Analista usan la plataforma; ésta consume fuentes abiertas externas.
- **Contenedores**: React+Plotly ↔ API FastAPI ↔ servicio ETL ↔ MySQL.
- **Componentes**: `controllers/` → `services/` → `repositories/` → `models/` (persistencia) + `etl/`.

### Entidades del modelo de datos (`backend/app/models/`)
`Course`, `Category`, `course_category` (intermedia), `Platform`, `DataSource`,
`Period`, `Metric`, `Tendency`, `RegistrationETL`, `User`.

---

## Puesta en marcha

### Opción A — Docker (todo en uno, recomendado)
Requisitos: Docker Desktop.
```bash
docker compose up --build
```
- Tablero: http://localhost:3000
- API + documentación OpenAPI: http://localhost:8000/docs
- El backend crea las tablas y los usuarios/fuentes por defecto al arrancar.

### Opción B — Local (Laragon/Windows)
Requisitos: Python 3.11+, Node 18+, MySQL (Laragon).

**Backend**
```bash
cd backend
python -m venv .venv && .venv\Scripts\activate     # Windows
pip install -r requirements.txt
copy .env.example .env                              # ajuste DATABASE_URL si hace falta
# Cree la base de datos vacía "plataforma_cursos" en MySQL, luego:
python -m scripts.init_db          # tablas + usuarios + fuentes por defecto
python -m scripts.run_etl          # carga el dataset de ejemplo y calcula tendencias
uvicorn app.main:app --reload      # API en http://localhost:8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev                        # tablero en http://localhost:5173
```

### Usuarios de demostración
| Rol | Correo | Contraseña |
|-----|--------|-----------|
| Administrador | admin@demo.com | admin123 |
| Analista | analista@demo.com | analista123 |

---

## Fuentes de datos (reales, activas por defecto)
1. **Cursos de Udemy** (`source_type: udemy`) — dataset público real (~3.678
   cursos, 2011–2017) con **fecha de publicación real** y materia. Es la fuente
   principal para las series temporales. Origen: Kaggle *andrewmvd/udemy-courses*,
   replicado en GitHub.
2. **Cursos de Coursera** (`source_type: coursera`) — dataset público real (~890
   cursos) con nº de estudiantes y dificultad. No incluye fecha de publicación
   (se registran en el periodo de carga) ni materia (la categoría se **infiere
   del título** por palabras clave). Origen: Kaggle *siddharthm1698*, en GitHub.
3. **Google Trends** (`source_type: google_trends`) — **demanda de búsqueda real**
   (índice de interés semanal, últimos 12 meses) vía `pytrends`. Sin credenciales.

> **Nota de honestidad / validez**: las tres fuentes son reales, pero cubren
> rangos temporales distintos (Udemy 2011–2017; Coursera sin fecha → periodo de
> carga; Google Trends 2025–2026). Téngalo en cuenta al interpretar la serie
> temporal combinada. Existe además un **dataset sintético de respaldo**
> (`backend/seed/courses_sample.csv`, fuente `csv`, desactivada) solo para
> demostración offline; **no debe usarse para conclusiones**.

Añadir una nueva fuente = crear un conector en `backend/app/etl/connectors/`
que implemente `BaseConnector.fetch()` y registrarlo en la fábrica (RNF-02).

---

## Análisis implementado
- **Tendencias** (`app/analysis/trends.py`): tasa de crecimiento, variación
  entre periodos, dirección (creciente/estable/decreciente) por regresión
  lineal y nivel de confianza (R²).
- **Minería de texto** (`app/analysis/topics.py`): modelado de tópicos con LDA
  sobre las descripciones de los cursos.

---

## Trazabilidad con el documento (requisitos → código)

| Elemento | Dónde está implementado |
|---|---|
| **RF-01 / CU-01 / HU-01** Gestión de fuentes | `controllers/admin_controller.py`, `services/admin_service.py` |
| **RF-02 / CU-02 / HU-02** ETL automático + registro | `etl/pipeline.py`, `etl/stages.py`, `models/registration_etl.py` |
| RF Procesar / transformar / almacenar | `etl/stages.py` (validate, clean, load) |
| RF Análisis de tendencias | `services/analysis_service.py`, `analysis/trends.py` |
| RF Visualización / tablero | `frontend/` + `controllers/dashboard_controller.py` |
| **RNF-01** Rendimiento (<3 s) | consultas agregadas en `repositories/metric_repository.py` |
| **RNF-02** Escalabilidad (conectores) | `etl/connectors/` con fábrica `get_connector` |
| **RNF-03** Usabilidad | tablero React con filtros dinámicos |
| **RNF-05** Mantenibilidad | separación en capas + documentación + OpenAPI en `/docs` |
| **RNF-06** Seguridad (roles) | `core/security.py` (JWT + `require_admin`) |

---

## Estructura del proyecto
```
plataforma-demanda-cursos/
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── controllers/   # capa de presentación de la API
│   │   ├── services/      # lógica de negocio
│   │   ├── repositories/  # acceso a datos
│   │   ├── models/        # entidades ORM (persistencia)
│   │   ├── etl/           # pipeline pipes & filters + conectores
│   │   ├── analysis/      # tendencias y modelado de tópicos
│   │   ├── schemas/       # validación Pydantic
│   │   └── core/          # config, BD, seguridad
│   ├── scripts/           # init_db, run_etl, generate_sample, smoke_test
│   └── seed/              # dataset de ejemplo
└── frontend/              # React + Plotly (tablero)
```

## Pruebas
Prueba de humo end-to-end del backend (ETL + análisis + API):
```bash
cd backend
# usa una BD SQLite temporal para no tocar MySQL
DATABASE_URL="sqlite:///./smoke.db" SECRET_KEY="test" python -m scripts.smoke_test
```
