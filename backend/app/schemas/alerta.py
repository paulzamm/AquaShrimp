from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AlertaBase(BaseModel):
    id_lectura: Optional[int] = None
    id_sensor: Optional[int] = None
    id_usuario: Optional[int] = None
    tipo_alerta: str
    severidad: str = "media"
    descripcion: str
    fecha_generacion: Optional[datetime] = None
    estado: str = "activa"
    valor_medido: Optional[float] = None
    fecha_hora: Optional[datetime] = None
    resuelta_en: Optional[datetime] = None


class AlertaCreate(AlertaBase):
    pass


class AlertaUpdate(BaseModel):
    id_lectura: Optional[int] = None
    id_sensor: Optional[int] = None
    id_usuario: Optional[int] = None
    tipo_alerta: Optional[str] = None
    severidad: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_generacion: Optional[datetime] = None
    estado: Optional[str] = None
    valor_medido: Optional[float] = None
    fecha_hora: Optional[datetime] = None
    resuelta_en: Optional[datetime] = None


class AlertaResponse(AlertaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
