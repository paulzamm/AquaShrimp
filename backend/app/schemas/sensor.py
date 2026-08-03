from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SensorBase(BaseModel):
    id_piscina: int
    tipo: str
    ubicacion: Optional[str] = None
    estado: str = "activo"
    unidad_medida: str
    fecha_instalacion: Optional[date] = None


class SensorCreate(SensorBase):
    pass


class SensorUpdate(BaseModel):
    id_piscina: Optional[int] = None
    tipo: Optional[str] = None
    ubicacion: Optional[str] = None
    estado: Optional[str] = None
    unidad_medida: Optional[str] = None
    fecha_instalacion: Optional[date] = None


class SensorResponse(SensorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
