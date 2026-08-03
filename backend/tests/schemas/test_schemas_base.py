from datetime import date, datetime
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.schemas.piscina import (
    PiscinaBase,
    PiscinaCreate,
    PiscinaResponse,
    PiscinaUpdate,
)
from app.schemas.rol import (
    RolBase,
    RolCreate,
    RolResponse,
    RolUpdate,
)
from app.schemas.sensor import (
    SensorBase,
    SensorCreate,
    SensorResponse,
    SensorUpdate,
)
from app.schemas.usuario import (
    UsuarioBase,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)


# ==========================================
# Tests for Rol Schemas
# ==========================================
def test_rol_base_valid():
    rol = RolBase(nombre_rol="Administrador", descripcion="Acceso total")
    assert rol.nombre_rol == "Administrador"
    assert rol.descripcion == "Acceso total"
    assert rol.permisos is None
    assert rol.estado == "activo"


def test_rol_base_missing_required():
    with pytest.raises(ValidationError):
        RolBase()


def test_rol_create_and_update():
    create_dto = RolCreate(nombre_rol="Biologo", permisos="read,write")
    assert create_dto.nombre_rol == "Biologo"

    update_dto = RolUpdate(descripcion="Nueva descripción")
    assert update_dto.descripcion == "Nueva descripción"
    assert update_dto.nombre_rol is None


def test_rol_response_from_attributes():
    now = datetime.now()
    mock_orm = MagicMock()
    mock_orm.id = 1
    mock_orm.nombre_rol = "Operador"
    mock_orm.descripcion = "Operador de campo"
    mock_orm.permisos = "read"
    mock_orm.estado = "activo"
    mock_orm.created_at = now
    mock_orm.updated_at = None

    response = RolResponse.model_validate(mock_orm)
    assert response.id == 1
    assert response.nombre_rol == "Operador"
    assert response.created_at == now
    assert response.updated_at is None


# ==========================================
# Tests for Usuario Schemas
# ==========================================
def test_usuario_create_valid():
    user = UsuarioCreate(
        nombre="Juan Perez",
        correo="juan.perez@example.com",
        id_rol=2,
        contrasena="secreto123",
    )
    assert user.nombre == "Juan Perez"
    assert user.correo == "juan.perez@example.com"
    assert user.id_rol == 2
    assert user.contrasena == "secreto123"
    assert user.estado == "activo"


def test_usuario_create_invalid_email():
    with pytest.raises(ValidationError):
        UsuarioCreate(
            nombre="Juan Perez",
            correo="email-invalido",
            id_rol=2,
            contrasena="secreto123",
        )


def test_usuario_create_missing_password():
    with pytest.raises(ValidationError):
        UsuarioCreate(
            nombre="Juan Perez",
            correo="juan@example.com",
            id_rol=2,
        )


def test_usuario_update():
    update_dto = UsuarioUpdate(nombre="Juan Updated")
    assert update_dto.nombre == "Juan Updated"
    assert update_dto.correo is None


def test_usuario_response_no_password():
    now = datetime.now()
    mock_orm = MagicMock()
    mock_orm.id = 10
    mock_orm.id_rol = 2
    mock_orm.nombre = "Maria Lopez"
    mock_orm.correo = "maria@example.com"
    mock_orm.contrasena_hash = "$2b$12$hashedpassword"
    mock_orm.estado = "activo"
    mock_orm.ultimo_acceso = now
    mock_orm.created_at = now
    mock_orm.updated_at = now

    response = UsuarioResponse.model_validate(mock_orm)
    assert response.id == 10
    assert response.id_rol == 2
    assert response.nombre == "Maria Lopez"
    assert response.correo == "maria@example.com"

    dumped = response.model_dump()
    assert "contrasena" not in dumped
    assert "contrasena_hash" not in dumped
    assert not hasattr(response, "contrasena")
    assert not hasattr(response, "contrasena_hash")


# ==========================================
# Tests for Piscina Schemas
# ==========================================
def test_piscina_create_valid():
    piscina = PiscinaCreate(
        codigo="P-101",
        ubicacion="Sector Norte",
        area_m2=500.5,
        profundidad=1.8,
        fecha_inicio_ciclo=date(2026, 1, 15),
    )
    assert piscina.codigo == "P-101"
    assert piscina.area_m2 == 500.5
    assert piscina.estado == "activa"
    assert piscina.fecha_inicio_ciclo == date(2026, 1, 15)


def test_piscina_missing_required():
    with pytest.raises(ValidationError):
        PiscinaCreate(codigo="P-102", ubicacion="Sector Sur")


def test_piscina_update():
    update_dto = PiscinaUpdate(estado="mantenimiento")
    assert update_dto.estado == "mantenimiento"
    assert update_dto.codigo is None


def test_piscina_response_from_attributes():
    now = datetime.now()
    mock_orm = MagicMock()
    mock_orm.id = 5
    mock_orm.codigo = "P-103"
    mock_orm.ubicacion = "Sector Este"
    mock_orm.area_m2 = 1000.0
    mock_orm.profundidad = 2.0
    mock_orm.estado = "activa"
    mock_orm.fecha_inicio_ciclo = None
    mock_orm.created_at = now
    mock_orm.updated_at = None

    response = PiscinaResponse.model_validate(mock_orm)
    assert response.id == 5
    assert response.codigo == "P-103"
    assert response.area_m2 == 1000.0


# ==========================================
# Tests for Sensor Schemas
# ==========================================
def test_sensor_create_valid():
    sensor = SensorCreate(
        id_piscina=5,
        tipo="oxigeno_disuelto",
        unidad_medida="mg/L",
        ubicacion="Centro",
        fecha_instalacion=date(2026, 2, 1),
    )
    assert sensor.id_piscina == 5
    assert sensor.tipo == "oxigeno_disuelto"
    assert sensor.unidad_medida == "mg/L"
    assert sensor.estado == "activo"


def test_sensor_missing_required():
    with pytest.raises(ValidationError):
        SensorCreate(id_piscina=5, tipo="ph")


def test_sensor_update():
    update_dto = SensorUpdate(estado="inactivo")
    assert update_dto.estado == "inactivo"
    assert update_dto.tipo is None


def test_sensor_response_from_attributes():
    now = datetime.now()
    mock_orm = MagicMock()
    mock_orm.id = 12
    mock_orm.id_piscina = 5
    mock_orm.tipo = "ph"
    mock_orm.ubicacion = "Norte"
    mock_orm.estado = "activo"
    mock_orm.unidad_medida = "pH"
    mock_orm.fecha_instalacion = date(2026, 1, 10)
    mock_orm.created_at = now
    mock_orm.updated_at = None

    response = SensorResponse.model_validate(mock_orm)
    assert response.id == 12
    assert response.tipo == "ph"
    assert response.unidad_medida == "pH"
