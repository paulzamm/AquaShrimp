from fastapi import APIRouter, Depends

from app.api.deps import get_current_active_user, require_roles
from app.models.usuario import Usuario
from app.schemas.simulador import (
    SimuladorEstadoResponse,
    SimuladorHistoricoEstadoResponse,
    SimuladorHistoricoRequest,
    SimuladorIniciarRequest,
)
from app.services.sensor_simulator import SimuladorConfig, simulador

router = APIRouter(prefix="/api/simulador", tags=["Simulador IoT"])


def _estado_actual() -> SimuladorEstadoResponse:
    return SimuladorEstadoResponse(
        activo=simulador.estado.activo,
        intervalo_segundos=simulador.config.intervalo_segundos,
        ciclos_ejecutados=simulador.estado.ciclos_ejecutados,
        ultima_ejecucion=simulador.estado.ultima_ejecucion,
        ultimo_error=simulador.estado.ultimo_error,
    )


@router.post("/iniciar", response_model=SimuladorEstadoResponse)
async def iniciar_simulador(
    body: SimuladorIniciarRequest,
    current_user: Usuario = Depends(require_roles(["Administrador", "Técnico Acuícola"])),
):
    """Inicia la simulación periódica de lecturas de sensores (Requires Administrador o Técnico Acuícola role)."""
    await simulador.start(
        SimuladorConfig(
            intervalo_segundos=body.intervalo_segundos,
            prob_valor_critico=body.prob_valor_critico,
            prob_perdida_comunicacion=body.prob_perdida_comunicacion,
            prob_fallo_sensor=body.prob_fallo_sensor,
        )
    )
    return _estado_actual()


@router.post("/detener", response_model=SimuladorEstadoResponse)
async def detener_simulador(
    current_user: Usuario = Depends(require_roles(["Administrador", "Técnico Acuícola"])),
):
    """Detiene la simulación (Requires Administrador o Técnico Acuícola role)."""
    await simulador.stop()
    return _estado_actual()


@router.get("/estado", response_model=SimuladorEstadoResponse)
def estado_simulador(current_user: Usuario = Depends(get_current_active_user)):
    """Consulta el estado actual del simulador."""
    return _estado_actual()


@router.post("/historico", response_model=SimuladorHistoricoEstadoResponse)
async def generar_historico(
    body: SimuladorHistoricoRequest,
    current_user: Usuario = Depends(require_roles(["Administrador", "Técnico Acuícola"])),
):
    """Genera datos históricos sintéticos en segundo plano (Requires Administrador o Técnico Acuícola role)."""
    await simulador.generar_historico(dias=body.dias, lecturas_por_dia=body.lecturas_por_dia)
    return SimuladorHistoricoEstadoResponse(
        en_progreso=simulador.historico.en_progreso,
        enviadas=simulador.historico.enviadas,
        total=simulador.historico.total,
        ultimo_error=simulador.historico.ultimo_error,
    )


@router.get("/historico", response_model=SimuladorHistoricoEstadoResponse)
def estado_historico(current_user: Usuario = Depends(get_current_active_user)):
    """Consulta el progreso de la generación de datos históricos."""
    return SimuladorHistoricoEstadoResponse(
        en_progreso=simulador.historico.en_progreso,
        enviadas=simulador.historico.enviadas,
        total=simulador.historico.total,
        ultimo_error=simulador.historico.ultimo_error,
    )
