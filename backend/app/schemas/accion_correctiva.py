from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AccionCorrectivaBase(BaseModel):
    id_alerta: int
    id_usuario: int
    descripcion: str
    fecha_accion: Optional[datetime] = None
    resultado: Optional[str] = None
    estado: str = "pendiente"


class AccionCorrectivaCreate(AccionCorrectivaBase):
    pass


class AccionCorrectivaUpdate(BaseModel):
    id_alerta: Optional[int] = None
    id_usuario: Optional[int] = None
    descripcion: Optional[str] = None
    fecha_accion: Optional[datetime] = None
    resultado: Optional[str] = None
    estado: Optional[str] = None


class AccionCorrectivaResponse(AccionCorrectivaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
