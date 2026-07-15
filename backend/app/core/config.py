"""Configuración central de la aplicación.

Carga los parámetros desde variables de entorno / archivo .env usando
pydantic-settings, de modo que el mismo código funcione en desarrollo,
en Docker y en la nube sin cambios (RNF-02, RNF-05).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Aplicación ---
    APP_NAME: str = "Plataforma de Análisis de Demanda de Cursos"
    API_V1_PREFIX: str = "/api"

    # --- Base de datos ---
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/plataforma_cursos"

    # --- Seguridad (JWT) ---
    SECRET_KEY: str = "cambie-esta-clave-por-una-aleatoria-y-larga"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # --- Usuarios iniciales ---
    ADMIN_EMAIL: str = "admin@demo.com"
    ADMIN_PASSWORD: str = "admin123"
    ANALISTA_EMAIL: str = "analista@demo.com"
    ANALISTA_PASSWORD: str = "analista123"

    # --- Conector real: Google Trends ---
    GOOGLE_TRENDS_ENABLED: bool = True
    GOOGLE_TRENDS_GEO: str = ""
    GOOGLE_TRENDS_LANG: str = "es-419"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Devuelve una única instancia de configuración (patrón singleton)."""
    return Settings()


settings = get_settings()
