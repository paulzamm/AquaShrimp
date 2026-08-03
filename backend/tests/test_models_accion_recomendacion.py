import pytest
from sqlalchemy.exc import IntegrityError

from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.piscina import Piscina
from app.models.sensor import Sensor
from app.models.lectura_sensor import LecturaSensor
from app.models.alerta import Alerta
from app.models.accion_correctiva import AccionCorrectiva
from app.models.recomendacion_alimentacion import RecomendacionAlimentacion


def _make_alerta(session, suffix=""):
    rol = Rol(nombre_rol=f"R-AR{suffix}")
    session.add(rol)
    session.flush()
    usuario = Usuario(id_rol=rol.id, nombre="T", correo=f"ar{suffix}@t.com", contrasena_hash="h")
    session.add(usuario)
    piscina = Piscina(codigo=f"P-AR{suffix}", ubicacion="T", area_m2=100, profundidad=1.0)
    session.add(piscina)
    session.flush()
    sensor = Sensor(id_piscina=piscina.id, tipo="ph", unidad_medida="pH")
    session.add(sensor)
    session.flush()
    lectura = LecturaSensor(id_sensor=sensor.id, valor=5.0, unidad="pH")
    session.add(lectura)
    session.flush()
    alerta = Alerta(
        id_lectura=lectura.id, tipo_alerta="ph_bajo", severidad="alta", descripcion="pH bajo"
    )
    session.add(alerta)
    session.flush()
    return alerta, usuario, piscina


class TestAccionCorrectivaModel:
    def test_create_accion(self, test_session):
        alerta, usuario, _ = _make_alerta(test_session, "ac1")
        accion = AccionCorrectiva(
            id_alerta=alerta.id,
            id_usuario=usuario.id,
            descripcion="Se ajustó el pH con cal",
        )
        test_session.add(accion)
        test_session.flush()
        assert accion.id is not None
        assert accion.estado == "pendiente"
        assert accion.estado_cierre == "pendiente"

    def test_accion_relationships(self, test_session):
        alerta, usuario, _ = _make_alerta(test_session, "ac2")
        accion = AccionCorrectiva(
            id_alerta=alerta.id, id_usuario=usuario.id, descripcion="Revisión"
        )
        test_session.add(accion)
        test_session.flush()
        assert accion.alerta.tipo_alerta == "ph_bajo"
        assert accion.usuario.nombre == "T"
        assert accion in alerta.acciones_correctivas
        assert accion in usuario.acciones_correctivas

    def test_accion_estado_constraint(self, test_session):
        alerta, usuario, _ = _make_alerta(test_session, "ac3")
        accion = AccionCorrectiva(
            id_alerta=alerta.id,
            id_usuario=usuario.id,
            descripcion="Prueba",
            estado="invalid_state",
        )
        test_session.add(accion)
        with pytest.raises(IntegrityError):
            test_session.flush()

    def test_accion_estado_valid_values(self, test_session):
        alerta, usuario, _ = _make_alerta(test_session, "ac3_valid")
        accion1 = AccionCorrectiva(
            id_alerta=alerta.id, id_usuario=usuario.id, descripcion="D1", estado="en_progreso"
        )
        accion2 = AccionCorrectiva(
            id_alerta=alerta.id, id_usuario=usuario.id, descripcion="D2", estado="completada"
        )
        test_session.add_all([accion1, accion2])
        test_session.flush()
        assert accion1.estado == "en_progreso"
        assert accion2.estado == "completada"

    def test_alerta_cascade_delete(self, test_session):
        alerta, usuario, _ = _make_alerta(test_session, "ac4")
        accion = AccionCorrectiva(
            id_alerta=alerta.id, id_usuario=usuario.id, descripcion="Accion"
        )
        test_session.add(accion)
        test_session.flush()
        accion_id = accion.id
        test_session.delete(alerta)
        test_session.flush()
        assert test_session.get(AccionCorrectiva, accion_id) is None


class TestRecomendacionAlimentacionModel:
    def test_create_recomendacion(self, test_session):
        _, usuario, piscina = _make_alerta(test_session, "rec1")
        rec = RecomendacionAlimentacion(
            id_piscina=piscina.id,
            id_usuario=usuario.id,
            cantidad_kg=25.5,
            frecuencia="3 veces al día",
            criterio="Temperatura estable entre 26-30°C",
        )
        test_session.add(rec)
        test_session.flush()
        assert rec.id is not None
        assert rec.estado == "pendiente"

    def test_recomendacion_relationships(self, test_session):
        _, usuario, piscina = _make_alerta(test_session, "rec2")
        rec = RecomendacionAlimentacion(
            id_piscina=piscina.id,
            id_usuario=usuario.id,
            cantidad_kg=10.0,
            frecuencia="2 veces",
            criterio="Normal",
        )
        test_session.add(rec)
        test_session.flush()
        assert rec.piscina.codigo == "P-ARrec2"
        assert rec in piscina.recomendaciones_alimentacion
        assert rec in piscina.recomendaciones
        assert rec in usuario.recomendaciones_alimentacion
        assert rec in usuario.recomendaciones

    def test_recomendacion_cantidad_positiva_constraint(self, test_session):
        _, usuario, piscina = _make_alerta(test_session, "rec3")
        rec = RecomendacionAlimentacion(
            id_piscina=piscina.id,
            id_usuario=usuario.id,
            cantidad_kg=-5.0,
            frecuencia="1 vez",
            criterio="Invalido",
        )
        test_session.add(rec)
        with pytest.raises(IntegrityError):
            test_session.flush()

    def test_recomendacion_estado_constraint(self, test_session):
        _, usuario, piscina = _make_alerta(test_session, "rec4")
        rec = RecomendacionAlimentacion(
            id_piscina=piscina.id,
            id_usuario=usuario.id,
            cantidad_kg=10.0,
            frecuencia="1 vez",
            criterio="Invalido",
            estado="descartada",  # Must raise IntegrityError since allowed values are ('pendiente', 'aplicada', 'rechazada')
        )
        test_session.add(rec)
        with pytest.raises(IntegrityError):
            test_session.flush()

    def test_recomendacion_estado_valid_values(self, test_session):
        _, usuario, piscina = _make_alerta(test_session, "rec5")
        rec1 = RecomendacionAlimentacion(
            id_piscina=piscina.id, id_usuario=usuario.id, cantidad_kg=5.0, frecuencia="1", criterio="C1", estado="aplicada"
        )
        rec2 = RecomendacionAlimentacion(
            id_piscina=piscina.id, id_usuario=usuario.id, cantidad_kg=5.0, frecuencia="1", criterio="C2", estado="rechazada"
        )
        test_session.add_all([rec1, rec2])
        test_session.flush()
        assert rec1.estado == "aplicada"
        assert rec2.estado == "rechazada"
