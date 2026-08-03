from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class ReporteGerencialBase(BaseModel):
    id_usuario: int
    tipo_reporte: str
    periodo_inicio: date
    periodo_fin: date
    fecha_generacion: Optional[datetime] = None
    ruta_archivo: Optional[str] = None

    @model_validator(mode="after")
    def check_periodo(self) -> "ReporteGerencialBase":
        if self.periodo_inicio and self.periodo_fin and self.periodo_fin < self.periodo_inicio:
            raise ValueError("periodo_fin debe ser mayor o igual a periodo_inicio")
        return self


class ReporteGerencialCreate(ReporteGerencialBase):
    pass


class ReporteGerencialUpdate(BaseModel):
    id_usuario: Optional[int] = None
    tipo_reporte: Optional[str] = None
    periodo_inicio: Optional[date] = None
    periodo_fin: Optional[date] = None
    fecha_generacion: Optional[datetime] = None
    ruta_archivo: Optional[str] = None


class ReporteGerencialResponse(ReporteGerencialBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
