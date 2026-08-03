from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, model_validator


class CosechaBase(BaseModel):
    id_piscina: int
    fecha_cosecha: date
    biomasa_kg: float = 0.0
    talla_promedio: Optional[float] = None
    rendimiento: Optional[float] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = "completada"

    # Alias field names for compatibility
    biomasa_total_kg: Optional[float] = None
    peso_promedio_gramos: Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def sync_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "biomasa_total_kg" in data and ("biomasa_kg" not in data or data.get("biomasa_kg") == 0.0):
                data["biomasa_kg"] = data["biomasa_total_kg"]
            if "peso_promedio_gramos" in data and ("talla_promedio" not in data or data.get("talla_promedio") is None):
                data["talla_promedio"] = data["peso_promedio_gramos"]
        return data


class CosechaCreate(CosechaBase):
    pass


class CosechaUpdate(BaseModel):
    id_piscina: Optional[int] = None
    fecha_cosecha: Optional[date] = None
    biomasa_kg: Optional[float] = None
    talla_promedio: Optional[float] = None
    rendimiento: Optional[float] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = None
    biomasa_total_kg: Optional[float] = None
    peso_promedio_gramos: Optional[float] = None


class CosechaResponse(CosechaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
