from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LecturaSensorBase(BaseModel):
    id_sensor: int
    valor: float
    unidad: str
    fecha_hora: Optional[datetime] = None
    estado_validacion: str = "pendiente"
    observacion: Optional[str] = None


class LecturaSensorCreate(LecturaSensorBase):
    pass


class LecturaSensorUpdate(BaseModel):
    id_sensor: Optional[int] = None
    valor: Optional[float] = None
    unidad: Optional[str] = None
    fecha_hora: Optional[datetime] = None
    estado_validacion: Optional[str] = None
    observacion: Optional[str] = None


class LecturaSensorResponse(LecturaSensorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
