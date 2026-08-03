from datetime import date, datetime
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.schemas.accion_correctiva import (
    AccionCorrectivaBase,
    AccionCorrectivaCreate,
    AccionCorrectivaResponse,
    AccionCorrectivaUpdate,
)
from app.schemas.alerta import (
    AlertaBase,
    AlertaCreate,
    AlertaResponse,
    AlertaUpdate,
)
from app.schemas.cosecha import (
    CosechaBase,
    CosechaCreate,
    CosechaResponse,
    CosechaUpdate,
)
from app.schemas.lectura_sensor import (
    LecturaSensorBase,
    LecturaSensorCreate,
    LecturaSensorResponse,
    LecturaSensorUpdate,
)
from app.schemas.recomendacion_alimentacion import (
    RecomendacionAlimentacionBase,
    RecomendacionAlimentacionCreate,
    RecomendacionAlimentacionResponse,
    RecomendacionAlimentacionUpdate,
)
from app.schemas.registro_auditoria import (
    RegistroAuditoriaBase,
    RegistroAuditoriaCreate,
    RegistroAuditoriaResponse,
    RegistroAuditoriaUpdate,
)
from app.schemas.reporte_gerencial import (
    ReporteGerencialBase,
    ReporteGerencialCreate,
    ReporteGerencialResponse,
    ReporteGerencialUpdate,
)


# ==========================================
# Tests for LecturaSensor Schemas
# ==========================================
def test_lectura_sensor_create_valid():
    now = datetime.now()
    lectura = LecturaSensorCreate(
        id_sensor=1,
        valor=7.4,
        unidad="pH",
        fecha_hora=now,
        observacion="Lectura normal",
    )
    assert lectura.id_sensor == 1
    assert lectura.valor == 7.4
    assert lectura.unidad == "pH"
    assert lectura.estado_validacion == "pendiente"
    assert lectura.fecha_hora == now


def test_lectura_sensor_create_missing_required():
    with pytest.raises(ValidationError):
        LecturaSensorCreate(id_sensor=1)


def test_lectura_sensor_update():
    update_dto = LecturaSensorUpdate(estado_validacion="valida")
    assert update_dto.estado_validacion == "valida"
    assert update_dto.valor is None


def test_lectura_sensor_response_from_attributes():
    now = datetime.now()
    mock_orm = MagicMock()
    mock_orm.id = 100
    mock_orm.id_sensor = 1
    mock_orm.valor = 6.5
    mock_orm.unidad = "mg/L"
    mock_orm.fecha_hora = now
    mock_orm.estado_validacion = "valida"
    mock_orm.observacion = None
    mock_orm.created_at = now
    mock_orm.updated_at = None

    response = LecturaSensorResponse.model_validate(mock_orm)
    assert response.id == 100
    assert response.id_sensor == 1
    assert response.valor == 6.5
    assert response.estado_validacion == "valida"


# ==========================================
# Tests for Alerta Schemas
# ==========================================
def test_alerta_create_valid():
    alerta = AlertaCreate(
        id_sensor=1,
        tipo_alerta="oxigeno_bajo",
        severidad="alta",
        descripcion="Oxígeno en 2.1 mg/L",
    )
    assert alerta.id_sensor == 1
    assert alerta.tipo_alerta == "oxigeno_bajo"
    assert alerta.severidad == "alta"
    assert alerta.estado == "activa"


def test_alerta_create_missing_required():
    with pytest.raises(ValidationError):
        AlertaCreate(tipo_alerta="oxigeno_bajo")


def test_alerta_update():
    update_dto = AlertaUpdate(estado="atendida")
    assert update_dto.estado == "atendida"
    assert update_dto.tipo_alerta is None


def test_alerta_response_from_attributes():
    now = datetime.now()
    mock_orm = MagicMock()
    mock_orm.id = 50
    mock_orm.id_lectura = 10
    mock_orm.id_sensor = 2
    mock_orm.id_usuario = 3
    mock_orm.tipo_alerta="ph_alto"
    mock_orm.severidad = "critica"
    mock_orm.descripcion = "pH demasiado alto"
    mock_orm.fecha_generacion = now
    mock_orm.estado = "activa"
    mock_orm.valor_medido = None
    mock_orm.fecha_hora = None
    mock_orm.resuelta_en = None
    mock_orm.created_at = now
    mock_orm.updated_at = None

    response = AlertaResponse.model_validate(mock_orm)
    assert response.id == 50
    assert response.tipo_alerta == "ph_alto"
    assert response.severidad == "critica"


# ==========================================
# Tests for AccionCorrectiva Schemas
# ==========================================
def test_accion_correctiva_create_valid():
    accion = AccionCorrectivaCreate(
        id_alerta=50,
        id_usuario=2,
        descripcion="Aplicar 50kg de bicarbonato",
    )
    assert accion.id_alerta == 50
    assert accion.id_usuario == 2
    assert accion.descripcion == "Aplicar 50kg de bicarbonato"
    assert accion.estado == "pendiente"


def test_accion_correctiva_missing_required():
    with pytest.raises(ValidationError):
        AccionCorrectivaCreate(id_alerta=50)


def test_accion_correctiva_update():
    update_dto = AccionCorrectivaUpdate(estado="completada", resultado="Exitoso")
    assert update_dto.estado == "completada"
    assert update_dto.resultado == "Exitoso"
    assert update_dto.descripcion is None


def test_accion_correctiva_response_from_attributes():
    now = datetime.now()
    mock_orm = MagicMock()
    mock_orm.id = 5
    mock_orm.id_alerta = 50
    mock_orm.id_usuario = 2
    mock_orm.descripcion = "Acción preventiva"
    mock_orm.fecha_accion = now
    mock_orm.resultado = "OK"
    mock_orm.estado = "completada"
    mock_orm.created_at = now
    mock_orm.updated_at = None

    response = AccionCorrectivaResponse.model_validate(mock_orm)
    assert response.id == 5
    assert response.estado == "completada"


# ==========================================
# Tests for RecomendacionAlimentacion Schemas
# ==========================================
def test_recomendacion_alimentacion_create_valid():
    rec = RecomendacionAlimentacionCreate(
        id_piscina=3,
        id_usuario=1,
        cantidad_kg=45.0,
        frecuencia="3 veces al día",
        criterio="Biomasa estimada",
    )
    assert rec.id_piscina == 3
    assert rec.cantidad_kg == 45.0
    assert rec.frecuencia == "3 veces al día"
    assert rec.estado == "pendiente"


def test_recomendacion_alimentacion_alias_sync():
    rec = RecomendacionAlimentacionCreate(
        id_piscina=3,
        cantidad_sugerida_kg=30.0,
        justificacion="Tasa de crecimiento",
        aplicada=True,
    )
    assert rec.id_piscina == 3
    assert rec.cantidad_kg == 30.0
    assert rec.criterio == "Tasa de crecimiento"
    assert rec.estado == "aplicada"


def test_recomendacion_alimentacion_missing_required():
    with pytest.raises(ValidationError):
        RecomendacionAlimentacionCreate()


def test_recomendacion_alimentacion_response_from_attributes():
    now = datetime.now()
    mock_orm = MagicMock()
    mock_orm.id = 12
    mock_orm.id_piscina = 3
    mock_orm.id_usuario = 1
    mock_orm.cantidad_kg = 25.0
    mock_orm.frecuencia = "2 veces al día"
    mock_orm.criterio = "Normal"
    mock_orm.fecha_generacion = now
    mock_orm.estado = "aplicada"
    mock_orm.cantidad_sugerida_kg = None
    mock_orm.justificacion = None
    mock_orm.fecha_recomendacion = None
    mock_orm.aplicada = None
    mock_orm.created_at = now
    mock_orm.updated_at = None

    response = RecomendacionAlimentacionResponse.model_validate(mock_orm)
    assert response.id == 12
    assert response.cantidad_kg == 25.0


# ==========================================
# Tests for Cosecha Schemas
# ==========================================
def test_cosecha_create_valid():
    cosecha = CosechaCreate(
        id_piscina=1,
        fecha_cosecha=date(2026, 8, 1),
        biomasa_kg=1200.5,
        talla_promedio=14.5,
        rendimiento=0.85,
    )
    assert cosecha.id_piscina == 1
    assert cosecha.biomasa_kg == 1200.5
    assert cosecha.fecha_cosecha == date(2026, 8, 1)


def test_cosecha_alias_sync():
    cosecha = CosechaCreate(
        id_piscina=1,
        fecha_cosecha=date(2026, 8, 1),
        biomasa_total_kg=1500.0,
        peso_promedio_gramos=16.0,
    )
    assert cosecha.biomasa_kg == 1500.0
    assert cosecha.talla_promedio == 16.0


def test_cosecha_missing_required():
    with pytest.raises(ValidationError):
        CosechaCreate(id_piscina=1)


def test_cosecha_response_from_attributes():
    now = datetime.now()
    mock_orm = MagicMock()
    mock_orm.id = 8
    mock_orm.id_piscina = 1
    mock_orm.fecha_cosecha = date(2026, 8, 1)
    mock_orm.biomasa_kg = 1200.5
    mock_orm.talla_promedio = 14.5
    mock_orm.rendimiento = 0.85
    mock_orm.observaciones = "Excelente cosecha"
    mock_orm.estado = "completada"
    mock_orm.biomasa_total_kg = None
    mock_orm.peso_promedio_gramos = None
    mock_orm.created_at = now
    mock_orm.updated_at = None

    response = CosechaResponse.model_validate(mock_orm)
    assert response.id == 8
    assert response.biomasa_kg == 1200.5


# ==========================================
# Tests for ReporteGerencial Schemas
# ==========================================
def test_reporte_gerencial_create_valid():
    reporte = ReporteGerencialCreate(
        id_usuario=1,
        tipo_reporte="rendimiento",
        periodo_inicio=date(2026, 7, 1),
        periodo_fin=date(2026, 7, 31),
        ruta_archivo="/path/to/report.pdf",
    )
    assert reporte.id_usuario == 1
    assert reporte.tipo_reporte == "rendimiento"
    assert reporte.periodo_inicio == date(2026, 7, 1)
    assert reporte.periodo_fin == date(2026, 7, 31)


def test_reporte_gerencial_invalid_dates():
    with pytest.raises(ValidationError):
        ReporteGerencialCreate(
            id_usuario=1,
            tipo_reporte="rendimiento",
            periodo_inicio=date(2026, 7, 31),
            periodo_fin=date(2026, 7, 1),
        )


def test_reporte_gerencial_response_from_attributes():
    now = datetime.now()
    mock_orm = MagicMock()
    mock_orm.id = 3
    mock_orm.id_usuario = 1
    mock_orm.tipo_reporte = "alertas"
    mock_orm.periodo_inicio = date(2026, 7, 1)
    mock_orm.periodo_fin = date(2026, 7, 15)
    mock_orm.fecha_generacion = now
    mock_orm.ruta_archivo = "/reports/alertas.pdf"
    mock_orm.created_at = now
    mock_orm.updated_at = None

    response = ReporteGerencialResponse.model_validate(mock_orm)
    assert response.id == 3
    assert response.tipo_reporte == "alertas"


# ==========================================
# Tests for RegistroAuditoria Schemas
# ==========================================
def test_registro_auditoria_create_valid():
    now = datetime.now()
    audit = RegistroAuditoriaCreate(
        id_usuario=1,
        accion="LOGIN",
        detalles="Inicio de sesión desde IP 192.168.1.1",
        fecha_hora=now,
    )
    assert audit.id_usuario == 1
    assert audit.accion == "LOGIN"
    assert audit.detalles == "Inicio de sesión desde IP 192.168.1.1"


def test_registro_auditoria_update_empty():
    update_dto = RegistroAuditoriaUpdate()
    assert update_dto.model_dump() == {}


def test_registro_auditoria_response_from_attributes():
    now = datetime.now()
    mock_orm = MagicMock()
    mock_orm.id = 99
    mock_orm.id_usuario = 1
    mock_orm.accion = "DELETE_SENSOR"
    mock_orm.detalles = "Eliminado sensor ID 5"
    mock_orm.fecha_hora = now

    response = RegistroAuditoriaResponse.model_validate(mock_orm)
    assert response.id == 99
    assert response.accion == "DELETE_SENSOR"
    assert response.fecha_hora == now
