from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.piscina import Piscina
from app.models.rol import Rol
from app.models.sensor import Sensor
from app.models.usuario import Usuario

# ---------------------------------------------------------------------------
# Setup Fixtures & Helper Data
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clean_catalogos_db(test_session: Session):
    """Cleanup data inserted during catalogue CRUD tests."""
    yield
    test_session.rollback()
    test_session.query(Sensor).filter(
        Sensor.tipo.in_(["ph_test", "oxigeno_test"])
    ).delete(synchronize_session=False)
    test_session.query(Piscina).filter(
        Piscina.codigo.in_(["P-TEST-01", "P-TEST-02"])
    ).delete(synchronize_session=False)
    test_session.query(Usuario).filter(
        Usuario.correo.in_(
            [
                "admin_cat@aquashrimp.com",
                "op_cat@aquashrimp.com",
                "inactive_cat@aquashrimp.com",
                "newuser_cat@aquashrimp.com",
            ]
        )
    ).delete(synchronize_session=False)
    test_session.query(Rol).filter(
        Rol.nombre_rol.in_(
            [
                "Administrador",
                "Técnico Acuícola",
                "Rol_Test_01",
                "Rol_Test_02",
            ]
        )
    ).delete(synchronize_session=False)
    test_session.commit()


def setup_auth(test_session: Session):
    admin_rol = (
        test_session.query(Rol).filter(Rol.nombre_rol == "Administrador").first()
    )
    if not admin_rol:
        admin_rol = Rol(nombre_rol="Administrador", descripcion="Admin role")
        test_session.add(admin_rol)

    op_rol = test_session.query(Rol).filter(Rol.nombre_rol == "Técnico Acuícola").first()
    if not op_rol:
        op_rol = Rol(nombre_rol="Técnico Acuícola", descripcion="Operator role")
        test_session.add(op_rol)

    test_session.flush()

    admin_user = Usuario(
        id_rol=admin_rol.id,
        nombre="Admin Cat",
        correo="admin_cat@aquashrimp.com",
        contrasena_hash=get_password_hash("password123"),
        estado="activo",
    )
    op_user = Usuario(
        id_rol=op_rol.id,
        nombre="Op Cat",
        correo="op_cat@aquashrimp.com",
        contrasena_hash=get_password_hash("password123"),
        estado="activo",
    )
    inactive_user = Usuario(
        id_rol=op_rol.id,
        nombre="Inactive Cat",
        correo="inactive_cat@aquashrimp.com",
        contrasena_hash=get_password_hash("password123"),
        estado="inactivo",
    )
    test_session.add_all([admin_user, op_user, inactive_user])
    test_session.flush()

    admin_token = create_access_token({"sub": admin_user.correo})
    op_token = create_access_token({"sub": op_user.correo})
    inactive_token = create_access_token({"sub": inactive_user.correo})

    return {
        "admin_headers": {"Authorization": f"Bearer {admin_token}"},
        "op_headers": {"Authorization": f"Bearer {op_token}"},
        "inactive_headers": {"Authorization": f"Bearer {inactive_token}"},
        "admin_rol": admin_rol,
        "op_rol": op_rol,
    }


# ---------------------------------------------------------------------------
# Test Rol Endpoints (/api/roles)
# ---------------------------------------------------------------------------


def test_rol_crud_flow(client: TestClient, test_session: Session):
    auth = setup_auth(test_session)

    # 1. Create Rol
    payload = {
        "nombre_rol": "Rol_Test_01",
        "descripcion": "Rol de prueba",
        "permisos": "READ,WRITE",
        "estado": "activo",
    }
    response = client.post("/api/roles", json=payload, headers=auth["admin_headers"])
    assert response.status_code == 201
    data = response.json()
    assert data["nombre_rol"] == "Rol_Test_01"
    rol_id = data["id"]

    # 2. Create Duplicate Rol -> 400
    response_dup = client.post(
        "/api/roles", json=payload, headers=auth["admin_headers"]
    )
    assert response_dup.status_code == 400

    # 3. Get Roles List
    response_list = client.get("/api/roles", headers=auth["admin_headers"])
    assert response_list.status_code == 200
    roles = response_list.json()
    assert any(r["id"] == rol_id for r in roles)

    # 4. Get Single Rol by ID
    response_get = client.get(
        f"/api/roles/{rol_id}", headers=auth["admin_headers"]
    )
    assert response_get.status_code == 200
    assert response_get.json()["nombre_rol"] == "Rol_Test_01"

    # 5. Update Rol
    update_payload = {"descripcion": "Rol de prueba actualizado"}
    response_update = client.put(
        f"/api/roles/{rol_id}",
        json=update_payload,
        headers=auth["admin_headers"],
    )
    assert response_update.status_code == 200
    assert response_update.json()["descripcion"] == "Rol de prueba actualizado"

    # 6. Delete Rol
    response_del = client.delete(
        f"/api/roles/{rol_id}", headers=auth["admin_headers"]
    )
    assert response_del.status_code == 200

    # 7. Get Deleted Rol -> 404
    response_404 = client.get(
        f"/api/roles/{rol_id}", headers=auth["admin_headers"]
    )
    assert response_404.status_code == 404


def test_rol_rbac_permissions(client: TestClient, test_session: Session):
    auth = setup_auth(test_session)
    payload = {"nombre_rol": "Rol_Test_02", "estado": "activo"}

    # Non-admin user (Operador) -> 403 Forbidden
    response = client.post("/api/roles", json=payload, headers=auth["op_headers"])
    assert response.status_code == 403

    # Unauthenticated -> 401 Unauthorized
    response_unauth = client.post("/api/roles", json=payload)
    assert response_unauth.status_code == 401


# ---------------------------------------------------------------------------
# Test Usuario Endpoints (/api/usuarios)
# ---------------------------------------------------------------------------


def test_usuario_crud_flow(client: TestClient, test_session: Session):
    auth = setup_auth(test_session)
    admin_rol = auth["admin_rol"]

    # 1. Create Usuario
    user_payload = {
        "id_rol": admin_rol.id,
        "nombre": "Nuevo Usuario",
        "correo": "newuser_cat@aquashrimp.com",
        "contrasena": "Password123!",
        "estado": "activo",
    }
    response = client.post(
        "/api/usuarios", json=user_payload, headers=auth["admin_headers"]
    )
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["correo"] == "newuser_cat@aquashrimp.com"
    user_id = user_data["id"]

    # Verify password was hashed in DB
    db_user = test_session.query(Usuario).filter(Usuario.id == user_id).first()
    assert verify_password("Password123!", db_user.contrasena_hash)

    # 2. Duplicate correo -> 400
    resp_dup = client.post(
        "/api/usuarios", json=user_payload, headers=auth["admin_headers"]
    )
    assert resp_dup.status_code == 400

    # 3. Invalid id_rol -> 400
    invalid_rol_payload = user_payload.copy()
    invalid_rol_payload["correo"] = "another_cat@aquashrimp.com"
    invalid_rol_payload["id_rol"] = 999999
    resp_invalid_rol = client.post(
        "/api/usuarios",
        json=invalid_rol_payload,
        headers=auth["admin_headers"],
    )
    assert resp_invalid_rol.status_code == 400

    # 4. Get Usuarios List
    resp_list = client.get("/api/usuarios", headers=auth["admin_headers"])
    assert resp_list.status_code == 200
    assert any(u["id"] == user_id for u in resp_list.json())

    # 5. Update Usuario (Name & Password)
    update_payload = {"nombre": "Nuevo Usuario Modificado", "contrasena": "NewPass456!"}
    resp_update = client.put(
        f"/api/usuarios/{user_id}",
        json=update_payload,
        headers=auth["admin_headers"],
    )
    assert resp_update.status_code == 200
    assert resp_update.json()["nombre"] == "Nuevo Usuario Modificado"

    test_session.refresh(db_user)
    assert verify_password("NewPass456!", db_user.contrasena_hash)

    # 6. Delete Usuario
    resp_del = client.delete(
        f"/api/usuarios/{user_id}", headers=auth["admin_headers"]
    )
    assert resp_del.status_code == 200

    # 7. Get Deleted Usuario -> 404
    resp_404 = client.get(
        f"/api/usuarios/{user_id}", headers=auth["admin_headers"]
    )
    assert resp_404.status_code == 404


# ---------------------------------------------------------------------------
# Test Piscina Endpoints (/api/piscinas)
# ---------------------------------------------------------------------------


def test_piscina_crud_flow(client: TestClient, test_session: Session):
    auth = setup_auth(test_session)

    # 1. Create Piscina (as Operador)
    piscina_payload = {
        "codigo": "P-TEST-01",
        "ubicacion": "Sector Norte",
        "area_m2": 1500.5,
        "profundidad": 2.5,
        "estado": "activa",
        "fecha_inicio_ciclo": "2026-08-01",
    }
    response = client.post(
        "/api/piscinas", json=piscina_payload, headers=auth["op_headers"]
    )
    assert response.status_code == 201
    piscina_data = response.json()
    assert piscina_data["codigo"] == "P-TEST-01"
    piscina_id = piscina_data["id"]

    # 2. Create Duplicate Piscina -> 400
    resp_dup = client.post(
        "/api/piscinas", json=piscina_payload, headers=auth["op_headers"]
    )
    assert resp_dup.status_code == 400

    # 3. Get Piscinas List
    resp_list = client.get("/api/piscinas", headers=auth["op_headers"])
    assert resp_list.status_code == 200
    assert any(p["id"] == piscina_id for p in resp_list.json())

    # 4. Get Piscina by ID
    resp_get = client.get(
        f"/api/piscinas/{piscina_id}", headers=auth["op_headers"]
    )
    assert resp_get.status_code == 200
    assert resp_get.json()["ubicacion"] == "Sector Norte"

    # 5. Update Piscina
    update_payload = {"area_m2": 1800.0, "estado": "mantenimiento"}
    resp_update = client.put(
        f"/api/piscinas/{piscina_id}",
        json=update_payload,
        headers=auth["op_headers"],
    )
    assert resp_update.status_code == 200
    assert resp_update.json()["area_m2"] == 1800.0
    assert resp_update.json()["estado"] == "mantenimiento"

    # 6. Delete Piscina (Admin only)
    resp_del = client.delete(
        f"/api/piscinas/{piscina_id}", headers=auth["admin_headers"]
    )
    assert resp_del.status_code == 200

    # 7. Get Deleted Piscina -> 404
    resp_404 = client.get(
        f"/api/piscinas/{piscina_id}", headers=auth["op_headers"]
    )
    assert resp_404.status_code == 404


# ---------------------------------------------------------------------------
# Test Sensor Endpoints (/api/sensores)
# ---------------------------------------------------------------------------


def test_sensor_crud_flow(client: TestClient, test_session: Session):
    auth = setup_auth(test_session)

    # First, create a pool to associate sensors with
    piscina = Piscina(
        codigo="P-TEST-02",
        ubicacion="Sector Sur",
        area_m2=2000.0,
        profundidad=3.0,
        estado="activa",
    )
    test_session.add(piscina)
    test_session.flush()

    # 1. Create Sensor
    sensor_payload = {
        "id_piscina": piscina.id,
        "tipo": "ph",
        "ubicacion": "Esquina Noreste",
        "estado": "activo",
        "unidad_medida": "pH",
        "fecha_instalacion": "2026-08-01",
    }
    response = client.post(
        "/api/sensores", json=sensor_payload, headers=auth["op_headers"]
    )
    assert response.status_code == 201
    sensor_data = response.json()
    assert sensor_data["tipo"] == "ph"
    sensor_id = sensor_data["id"]

    # 2. Create Sensor with non-existent piscina -> 400
    invalid_sensor = sensor_payload.copy()
    invalid_sensor["id_piscina"] = 999999
    resp_invalid = client.post(
        "/api/sensores", json=invalid_sensor, headers=auth["op_headers"]
    )
    assert resp_invalid.status_code == 400

    # 3. Get Sensores List & Filter by Piscina
    resp_list = client.get(
        f"/api/sensores?id_piscina={piscina.id}", headers=auth["op_headers"]
    )
    assert resp_list.status_code == 200
    sensores = resp_list.json()
    assert len(sensores) >= 1
    assert all(s["id_piscina"] == piscina.id for s in sensores)

    # 4. Get Sensor by ID
    resp_get = client.get(
        f"/api/sensores/{sensor_id}", headers=auth["op_headers"]
    )
    assert resp_get.status_code == 200
    assert resp_get.json()["unidad_medida"] == "pH"

    # 5. Update Sensor
    update_payload = {"estado": "inactivo", "ubicacion": "Esquina Sureste"}
    resp_update = client.put(
        f"/api/sensores/{sensor_id}",
        json=update_payload,
        headers=auth["op_headers"],
    )
    assert resp_update.status_code == 200
    assert resp_update.json()["estado"] == "inactivo"

    # 6. Delete Sensor
    resp_del = client.delete(
        f"/api/sensores/{sensor_id}", headers=auth["admin_headers"]
    )
    assert resp_del.status_code == 200

    # 7. Get Deleted Sensor -> 404
    resp_404 = client.get(
        f"/api/sensores/{sensor_id}", headers=auth["op_headers"]
    )
    assert resp_404.status_code == 404


# ---------------------------------------------------------------------------
# Test Inactive User Access -> 403
# ---------------------------------------------------------------------------


def test_inactive_user_access(client: TestClient, test_session: Session):
    auth = setup_auth(test_session)
    response = client.get("/api/piscinas", headers=auth["inactive_headers"])
    assert response.status_code == 403
    assert response.json()["detail"] == "Usuario inactivo"
