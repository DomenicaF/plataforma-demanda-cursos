"""Esquemas Pydantic para la validación de entrada/salida de la API."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ------------------------- Autenticación -------------------------
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    full_name: str | None = None
    email: str


class UserOut(BaseModel):
    id: int
    full_name: str | None
    email: EmailStr
    role: str

    model_config = {"from_attributes": True}


# ------------------------- Fuentes de datos (RF-01) -------------------------
class DataSourceBase(BaseModel):
    name: str
    source_type: str = Field(default="csv", description="csv | google_trends")
    url: str | None = None
    data_format: str | None = None
    update_frequency_hours: int | None = 24
    config: dict | str | None = None
    is_active: bool = True
    platform_id: int | None = None


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceUpdate(BaseModel):
    name: str | None = None
    source_type: str | None = None
    url: str | None = None
    data_format: str | None = None
    update_frequency_hours: int | None = None
    config: dict | str | None = None
    is_active: bool | None = None
    platform_id: int | None = None


class DataSourceOut(BaseModel):
    id: int
    name: str
    source_type: str
    url: str | None
    data_format: str | None
    update_frequency_hours: int | None
    config: str | None
    is_active: bool
    last_run_at: datetime | None

    model_config = {"from_attributes": True}


# ------------------------- ETL -------------------------
class ETLRunOut(BaseModel):
    id: int
    data_source_id: int | None
    started_at: datetime | None
    finished_at: datetime | None
    status: str
    records_extracted: int
    records_transformed: int
    records_loaded: int
    duration_seconds: float | None
    error_message: str | None


# ------------------------- Tablero / análisis -------------------------
class CategoryOut(BaseModel):
    id: int
    name: str
