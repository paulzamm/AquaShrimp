import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash
from app.models.alerta import Alerta
from app.models.lectura_sensor import LecturaSensor
from app.models.piscina import Piscina
from app.models.recomendacion_alimentacion import RecomendacionAlimentacion
from app.models.rol import Rol
from app.models.sensor import Sensor
from app.models.usuario import Usuario


@pytest.fixture(autouse=True)
def clean_bpm_db(test_session: Session):
    """Cleanup data inserted during BPM tests."""
    yield
    test_session.rollback()
    test_session.query(RecomendacionAlimentacion).delete(synchronize_session=False)
    test_session.query(Alerta).delete(synchronize_session=False)
    test_session.query(LecturaSensor).delete(synchronize_session=False)
    test_session.query(Sensor).filter(
        Sensor.ubicacion.like("BPM-%")
    ).delete(synchronize_session=False)
    test_session.query(Piscina).filter(
        Piscina.codigo.like("P-BPM-%")
    ).delete(synchronize_session=False)
    test_session.query(Usuario).filter(
        Usuario.correo.like("%_bpm@aquashrimp.com")
    ).delete(synchronize_session=False)
    test_session.query(Rol).filter(
        Rol.nombre_rol.in_(["Administrador", "RolIntegrityTest"])
    ).delete(synchronize_session=False)
    test_session.commit()


def setup_bpm_auth_and_data(test_session: Session):
    admin_rol = test_session.query(Rol).filter(Rol.nombre_rol == "Administrador").first()
    if not admin_rol:
        admin_rol = Rol(nombre_rol="Administrador", descripcion="Admin role")
        test_session.add(admin_rol)

    test_session.flush()

    user = Usuario(
        id_rol=admin_rol.id,
        nombre="User BPM",
        correo="user_bpm@aquashrimp.com",
        contrasena_hash=get_password_hash("password123"),
        estado="activo",
    )
    test_session.add(user)
    test_session.flush()

    token = create_access_token({"sub": user.correo})
    headers = {"Authorization": f"Bearer {token}"}

    piscina = Piscina(
        codigo="P-BPM-01",
        ubicacion="Sector BPM",
        area_m2=1000.0,
        profundidad=2.0,
        estado="activa",
    )
    test_session.add(piscina)
    test_session.flush()

    sensor_ph = Sensor(
        id_piscina=piscina.id,
        tipo="ph",
        ubicacion="BPM-pH-Sensor",
        estado="activo",
        unidad_medida="pH",
    )
    sensor_oxigeno = Sensor(
        id_piscina=piscina.id,
        tipo="oxigeno_disuelto",
        ubicacion="BPM-DO-Sensor",
        estado="activo",
        unidad_medida="mg/L",
    )
    sensor_temp = Sensor(
        id_piscina=piscina.id,
        tipo="temperatura",
        ubicacion="BPM-Temp-Sensor",
        estado="activo",
        unidad_medida="°C",
    )
    test_session.add_all([sensor_ph, sensor_oxigeno, sensor_temp])
    test_session.commit()

    return {
        "headers": headers,
        "piscina": piscina,
        "sensor_ph": sensor_ph,
        "sensor_oxigeno": sensor_oxigeno,
        "sensor_temp": sensor_temp,
    }


def test_post_lectura_unauthenticated(client: TestClient):
    payload = {"id_sensor": 1, "valor": 7.0, "unidad": "pH"}
    response = client.post("/api/lecturas", json=payload)
    assert response.status_code == 401


def test_post_lectura_non_existent_sensor(client: TestClient, test_session: Session):
    data = setup_bpm_auth_and_data(test_session)
    payload = {"id_sensor": 999999, "valor": 7.0, "unidad": "pH"}
    response = client.post("/api/lecturas", json=payload, headers=data["headers"])
    assert response.status_code == 404
    assert response.json()["detail"] == "Sensor no encontrado"


def test_bpm_ph_normal_generates_recommendation(client: TestClient, test_session: Session):
    data = setup_bpm_auth_and_data(test_session)
    payload = {
        "id_sensor": data["sensor_ph"].id,
        "valor": 7.2,
        "unidad": "pH",
    }
    response = client.post("/api/lecturas", json=payload, headers=data["headers"])
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["id_sensor"] == data["sensor_ph"].id
    assert res_data["valor"] == 7.2

    # Verify no alert was created
    alerta = test_session.query(Alerta).filter(Alerta.id_lectura == res_data["id"]).first()
    assert alerta is None

    # Verify feeding recommendation was created
    rec = test_session.query(RecomendacionAlimentacion).filter(
        RecomendacionAlimentacion.id_piscina == data["piscina"].id
    ).first()
    assert rec is not None
    assert rec.cantidad_kg == 50.0
    assert rec.criterio == "Parámetros óptimos registrados."


def test_bpm_ph_low_generates_high_alert(client: TestClient, test_session: Session):
    data = setup_bpm_auth_and_data(test_session)
    payload = {
        "id_sensor": data["sensor_ph"].id,
        "valor": 5.8,
        "unidad": "pH",
    }
    response = client.post("/api/lecturas", json=payload, headers=data["headers"])
    assert response.status_code == 201
    res_data = response.json()

    alerta = test_session.query(Alerta).filter(Alerta.id_lectura == res_data["id"]).first()
    assert alerta is not None
    assert alerta.severidad == "alta"
    assert alerta.gravedad == "alta"
    assert alerta.tipo_alerta == "ph_fuera_de_rango"

    recs = test_session.query(RecomendacionAlimentacion).all()
    assert len(recs) == 0


def test_bpm_ph_high_generates_high_alert(client: TestClient, test_session: Session):
    data = setup_bpm_auth_and_data(test_session)
    payload = {
        "id_sensor": data["sensor_ph"].id,
        "valor": 9.2,
        "unidad": "pH",
    }
    response = client.post("/api/lecturas", json=payload, headers=data["headers"])
    assert response.status_code == 201
    res_data = response.json()

    alerta = test_session.query(Alerta).filter(Alerta.id_lectura == res_data["id"]).first()
    assert alerta is not None
    assert alerta.severidad == "alta"


def test_bpm_oxigeno_disuelto_critical_alert(client: TestClient, test_session: Session):
    data = setup_bpm_auth_and_data(test_session)
    payload = {
        "id_sensor": data["sensor_oxigeno"].id,
        "valor": 3.2,
        "unidad": "mg/L",
    }
    response = client.post("/api/lecturas", json=payload, headers=data["headers"])
    assert response.status_code == 201
    res_data = response.json()

    alerta = test_session.query(Alerta).filter(Alerta.id_lectura == res_data["id"]).first()
    assert alerta is not None
    assert alerta.severidad == "critica"
    assert alerta.gravedad == "critica"
    assert alerta.tipo_alerta == "oxigeno_bajo"


def test_bpm_temperatura_media_alert(client: TestClient, test_session: Session):
    data = setup_bpm_auth_and_data(test_session)
    payload_low = {
        "id_sensor": data["sensor_temp"].id,
        "valor": 22.0,
        "unidad": "°C",
    }
    resp_low = client.post("/api/lecturas", json=payload_low, headers=data["headers"])
    assert resp_low.status_code == 201
    alerta_low = test_session.query(Alerta).filter(Alerta.id_lectura == resp_low.json()["id"]).first()
    assert alerta_low is not None
    assert alerta_low.severidad == "media"

    payload_high = {
        "id_sensor": data["sensor_temp"].id,
        "valor": 35.0,
        "unidad": "°C",
    }
    resp_high = client.post("/api/lecturas", json=payload_high, headers=data["headers"])
    assert resp_high.status_code == 201
    alerta_high = test_session.query(Alerta).filter(Alerta.id_lectura == resp_high.json()["id"]).first()
    assert alerta_high is not None
    assert alerta_high.severidad == "media"


def test_integrity_error_global_handler(client: TestClient, test_session: Session):
    data = setup_bpm_auth_and_data(test_session)
    rol = Rol(nombre_rol="RolIntegrityTest", descripcion="test")
    test_session.add(rol)
    test_session.commit()

    user = Usuario(
        id_rol=rol.id,
        nombre="User Integrity",
        correo="integrity_bpm@aquashrimp.com",
        contrasena_hash=get_password_hash("pass"),
        estado="activo",
    )
    test_session.add(user)
    test_session.commit()

    response = client.delete(f"/api/roles/{rol.id}", headers=data["headers"])
    assert response.status_code == 400
    assert "integridad" in response.json()["detail"].lower() or "error" in response.json()["detail"].lower()
