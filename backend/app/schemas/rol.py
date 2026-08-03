from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RolBase(BaseModel):
    nombre_rol: str
    descripcion: Optional[str] = None
    permisos: Optional[str] = None
    estado: str = "activo"


class RolCreate(RolBase):
    pass


class RolUpdate(BaseModel):
    nombre_rol: Optional[str] = None
    descripcion: Optional[str] = None
    permisos: Optional[str] = None
    estado: Optional[str] = None


class RolResponse(RolBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
