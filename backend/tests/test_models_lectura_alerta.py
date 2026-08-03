import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.piscina import Piscina
from app.models.sensor import Sensor
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.lectura_sensor import LecturaSensor
from app.models.alerta import Alerta


def _make_sensor(session):
    piscina = Piscina(codigo=f"P-LA-{id(session)}", ubicacion="T", area_m2=100, profundidad=1.0)
    session.add(piscina)
    session.flush()
    sensor = Sensor(id_piscina=piscina.id, tipo="temperatura", unidad_medida="°C")
    session.add(sensor)
    session.flush()
    return sensor


def _make_usuario(session):
    rol = Rol(nombre_rol=f"Rol-{id(session)}")
    session.add(rol)
    session.flush()
    usuario = Usuario(
        id_rol=rol.id,
        nombre="Test User",
        correo=f"user-{id(session)}@test.com",
        contrasena_hash="hash",
    )
    session.add(usuario)
    session.flush()
    return usuario


class TestLecturaSensorModel:
    def test_create_lectura(self, test_session):
        sensor = _make_sensor(test_session)
        lectura = LecturaSensor(
            id_sensor=sensor.id, valor=28.5, unidad="°C"
        )
        test_session.add(lectura)
        test_session.flush()
        assert lectura.id is not None
        assert lectura.estado_validacion == "pendiente"
        assert lectura.fecha_hora is not None

    def test_lectura_sensor_relationship(self, test_session):
        sensor = _make_sensor(test_session)
        lectura = LecturaSensor(id_sensor=sensor.id, valor=7.2, unidad="pH")
        test_session.add(lectura)
        test_session.flush()
        assert lectura.sensor.tipo == "temperatura"
        assert lectura in sensor.lecturas

    def test_lectura_estado_validacion_constraint(self, test_session):
        sensor = _make_sensor(test_session)
        lectura = LecturaSensor(
            id_sensor=sensor.id, valor=20.0, unidad="°C", estado_validacion="invalido_enum"
        )
        test_session.add(lectura)
        with pytest.raises(IntegrityError):
            test_session.flush()


class TestAlertaModel:
    def test_create_alerta(self, test_session):
        sensor = _make_sensor(test_session)
        lectura = LecturaSensor(id_sensor=sensor.id, valor=35.0, unidad="°C")
        test_session.add(lectura)
        test_session.flush()

        alerta = Alerta(
            id_lectura=lectura.id,
            tipo_alerta="temperatura_alta",
            severidad="alta",
            descripcion="Temperatura supera umbral máximo",
        )
        test_session.add(alerta)
        test_session.flush()
        assert alerta.id is not None
        assert alerta.estado == "activa"
        assert alerta.fecha_generacion is not None

    def test_alerta_lectura_relationship(self, test_session):
        sensor = _make_sensor(test_session)
        lectura = LecturaSensor(id_sensor=sensor.id, valor=35.0, unidad="°C")
        test_session.add(lectura)
        test_session.flush()

        alerta = Alerta(
            id_lectura=lectura.id,
            tipo_alerta="temp_alta",
            severidad="critica",
            descripcion="Crítico",
        )
        test_session.add(alerta)
        test_session.flush()
        assert alerta.lectura.valor == 35.0
        assert alerta in lectura.alertas

    def test_alerta_sensor_and_usuario_relationships(self, test_session):
        sensor = _make_sensor(test_session)
        usuario = _make_usuario(test_session)
        lectura = LecturaSensor(id_sensor=sensor.id, valor=35.0, unidad="°C")
        test_session.add(lectura)
        test_session.flush()

        alerta = Alerta(
            id_lectura=lectura.id,
            id_sensor=sensor.id,
            id_usuario=usuario.id,
            tipo_alerta="temp_alta",
            severidad="media",
            descripcion="Alerta con sensor y usuario",
        )
        test_session.add(alerta)
        test_session.flush()
        assert alerta.sensor is sensor
        assert alerta in sensor.alertas
        assert alerta.usuario is usuario
        assert alerta in usuario.alertas

    def test_alerta_severidad_constraint(self, test_session):
        sensor = _make_sensor(test_session)
        lectura = LecturaSensor(id_sensor=sensor.id, valor=35.0, unidad="°C")
        test_session.add(lectura)
        test_session.flush()

        alerta = Alerta(
            id_lectura=lectura.id,
            tipo_alerta="temp_alta",
            severidad="invalida",
            descripcion="Test constraint",
        )
        test_session.add(alerta)
        with pytest.raises(IntegrityError):
            test_session.flush()

    def test_alerta_gravedad_alias(self, test_session):
        sensor = _make_sensor(test_session)
        lectura = LecturaSensor(id_sensor=sensor.id, valor=35.0, unidad="°C")
        test_session.add(lectura)
        test_session.flush()

        alerta = Alerta(
            id_lectura=lectura.id,
            tipo_alerta="temp_alta",
            gravedad="critica",
            descripcion="Test alias",
        )
        assert alerta.severidad == "critica"
        assert alerta.gravedad == "critica"
