from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, model_validator


class RecomendacionAlimentacionBase(BaseModel):
    id_piscina: int
    id_usuario: Optional[int] = None
    cantidad_kg: float = 0.0
    frecuencia: Optional[str] = "diaria"
    criterio: Optional[str] = None
    fecha_generacion: Optional[datetime] = None
    estado: str = "pendiente"

    # Alias / alternate field names for compatibility
    cantidad_sugerida_kg: Optional[float] = None
    justificacion: Optional[str] = None
    fecha_recomendacion: Optional[datetime] = None
    aplicada: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def sync_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "cantidad_sugerida_kg" in data and ("cantidad_kg" not in data or data.get("cantidad_kg") == 0.0):
                data["cantidad_kg"] = data["cantidad_sugerida_kg"]
            if "justificacion" in data and ("criterio" not in data or data.get("criterio") is None):
                data["criterio"] = data["justificacion"]
            if "fecha_recomendacion" in data and ("fecha_generacion" not in data or data.get("fecha_generacion") is None):
                data["fecha_generacion"] = data["fecha_recomendacion"]
            if "aplicada" in data and ("estado" not in data or data.get("estado") == "pendiente"):
                data["estado"] = "aplicada" if data["aplicada"] else "pendiente"
        return data


class RecomendacionAlimentacionCreate(RecomendacionAlimentacionBase):
    pass


class RecomendacionAlimentacionUpdate(BaseModel):
    id_piscina: Optional[int] = None
    id_usuario: Optional[int] = None
    cantidad_kg: Optional[float] = None
    frecuencia: Optional[str] = None
    criterio: Optional[str] = None
    fecha_generacion: Optional[datetime] = None
    estado: Optional[str] = None
    cantidad_sugerida_kg: Optional[float] = None
    justificacion: Optional[str] = None
    fecha_recomendacion: Optional[datetime] = None
    aplicada: Optional[bool] = None


class RecomendacionAlimentacionResponse(RecomendacionAlimentacionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
