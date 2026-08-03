from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RegistroAuditoriaBase(BaseModel):
    id_usuario: Optional[int] = None
    accion: str
    detalles: Optional[str] = None
    fecha_hora: Optional[datetime] = None


class RegistroAuditoriaCreate(RegistroAuditoriaBase):
    pass


class RegistroAuditoriaUpdate(BaseModel):
    pass


class RegistroAuditoriaResponse(RegistroAuditoriaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
