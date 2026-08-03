from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PiscinaBase(BaseModel):
    codigo: str
    ubicacion: str
    area_m2: float
    profundidad: float
    estado: str = "activa"
    fecha_inicio_ciclo: Optional[date] = None


class PiscinaCreate(PiscinaBase):
    pass


class PiscinaUpdate(BaseModel):
    codigo: Optional[str] = None
    ubicacion: Optional[str] = None
    area_m2: Optional[float] = None
    profundidad: Optional[float] = None
    estado: Optional[str] = None
    fecha_inicio_ciclo: Optional[date] = None


class PiscinaResponse(PiscinaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
