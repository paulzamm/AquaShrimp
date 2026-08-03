from sqlalchemy import text

from app.core.database import Base
from app.models import (
    Rol, Usuario, Piscina, Sensor, LecturaSensor,
    Alerta, AccionCorrectiva, RecomendacionAlimentacion,
    Cosecha, ReporteGerencial,
)
from seeds.seed_data import seed


def test_seed_populates_data(test_engine, test_session):
    seed(test_session)
    test_session.commit()

    assert test_session.query(Rol).count() == 3
    assert test_session.query(Usuario).count() == 3
    assert test_session.query(Piscina).count() == 3
    assert test_session.query(Sensor).count() == 9
    assert test_session.query(LecturaSensor).count() >= 10
    assert test_session.query(Alerta).count() >= 1
    assert test_session.query(AccionCorrectiva).count() >= 1
    assert test_session.query(RecomendacionAlimentacion).count() >= 1
    assert test_session.query(Cosecha).count() >= 1
    assert test_session.query(ReporteGerencial).count() >= 1


def test_seed_is_idempotent(test_engine, test_session):
    seed(test_session)
    test_session.commit()
    count_before = test_session.query(Rol).count()

    seed(test_session)
    test_session.commit()
    count_after = test_session.query(Rol).count()

    assert count_before == count_after
