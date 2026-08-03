import pytest
from sqlalchemy.exc import IntegrityError

from app.models.piscina import Piscina
from app.models.sensor import Sensor


class TestPiscinaModel:
    def test_create_piscina(self, test_session):
        piscina = Piscina(
            codigo="P-001",
            ubicacion="Sector Norte",
            area_m2=5000.0,
            profundidad=1.5,
        )
        test_session.add(piscina)
        test_session.flush()
        assert piscina.id is not None
        assert piscina.estado == "activa"
        assert piscina.created_at is not None

    def test_piscina_codigo_unique(self, test_session):
        p1 = Piscina(codigo="P-DUP", ubicacion="A", area_m2=100, profundidad=1.0)
        p2 = Piscina(codigo="P-DUP", ubicacion="B", area_m2=200, profundidad=1.5)
        test_session.add_all([p1, p2])
        with pytest.raises(IntegrityError):
            test_session.flush()


class TestSensorModel:
    def test_create_sensor(self, test_session):
        piscina = Piscina(codigo="P-S01", ubicacion="Test", area_m2=100, profundidad=1.0)
        test_session.add(piscina)
        test_session.flush()

        sensor = Sensor(
            id_piscina=piscina.id,
            tipo="temperatura",
            unidad_medida="°C",
        )
        test_session.add(sensor)
        test_session.flush()
        assert sensor.id is not None
        assert sensor.estado == "activo"

    def test_sensor_piscina_relationship(self, test_session):
        piscina = Piscina(codigo="P-S02", ubicacion="Test", area_m2=100, profundidad=1.0)
        test_session.add(piscina)
        test_session.flush()

        sensor = Sensor(
            id_piscina=piscina.id, tipo="ph", unidad_medida="pH"
        )
        test_session.add(sensor)
        test_session.flush()
        assert sensor.piscina.codigo == "P-S02"
        assert sensor in piscina.sensores

    def test_sensor_tipo_not_null(self, test_session):
        piscina = Piscina(codigo="P-S03", ubicacion="Test", area_m2=100, profundidad=1.0)
        test_session.add(piscina)
        test_session.flush()

        sensor = Sensor(id_piscina=piscina.id, unidad_medida="X")
        test_session.add(sensor)
        with pytest.raises(IntegrityError):
            test_session.flush()
