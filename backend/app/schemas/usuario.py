from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    estado: str = "activo"


class UsuarioCreate(UsuarioBase):
    id_rol: int
    contrasena: str


class UsuarioUpdate(BaseModel):
    id_rol: Optional[int] = None
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    contrasena: Optional[str] = None
    estado: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    id: int
    id_rol: int
    ultimo_acceso: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
