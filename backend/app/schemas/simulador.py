from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SimuladorIniciarRequest(BaseModel):
    intervalo_segundos: float = Field(default=10.0, gt=0, le=3600)
    prob_valor_critico: float = Field(default=0.1, ge=0, le=1)
    prob_perdida_comunicacion: float = Field(default=0.05, ge=0, le=1)
    prob_fallo_sensor: float = Field(default=0.03, ge=0, le=1)


class SimuladorEstadoResponse(BaseModel):
    activo: bool
    intervalo_segundos: float
    ciclos_ejecutados: int
    ultima_ejecucion: Optional[datetime] = None
    ultimo_error: Optional[str] = None


class SimuladorHistoricoRequest(BaseModel):
    dias: int = Field(gt=0, le=90)
    lecturas_por_dia: int = Field(default=24, gt=0, le=96)


class SimuladorHistoricoEstadoResponse(BaseModel):
    en_progreso: bool
    enviadas: int
    total: int
    ultimo_error: Optional[str] = None
