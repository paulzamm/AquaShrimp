from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash
from app.models.accion_correctiva import AccionCorrectiva
from app.models.alerta import Alerta
from app.models.cosecha import Cosecha
from app.models.piscina import Piscina
from app.models.reporte_gerencial import ReporteGerencial
from app.models.rol import Rol
from app.models.sensor import Sensor
from app.models.usuario import Usuario


@pytest.fixture(autouse=True)
def clean_operaciones_db(test_session: Session):
    """Cleanup data inserted during operations CRUD tests."""
    yield
    test_session.rollback()
    test_session.query(AccionCorrectiva).delete(synchronize_session=False)
    test_session.query(Alerta).delete(synchronize_session=False)
    test_session.query(Cosecha).delete(synchronize_session=False)
    test_session.query(ReporteGerencial).delete(synchronize_session=False)
    test_session.query(Piscina).filter(
        Piscina.codigo.in_(["P-OP-01", "P-OP-02"])
    ).delete(synchronize_session=False)
    test_session.query(Usuario).filter(
        Usuario.correo.in_(
            [
                "admin_op@aquashrimp.com",
                "operador_op@aquashrimp.com",
                "biologo_op@aquashrimp.com",
            ]
        )
    ).delete(synchronize_session=False)
    test_session.commit()


def setup_auth_and_base_data(test_session: Session):
    """Create roles, users, pool, sensor for operations testing."""
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

    # Both "op" and "bio" test users share the same Técnico Acuícola role — the
    # backend only distinguishes Administrador / Técnico Acuícola / Gerencia.
    bio_rol = op_rol

    test_session.flush()

    admin_user = Usuario(
        id_rol=admin_rol.id,
        nombre="Admin Ops",
        correo="admin_op@aquashrimp.com",
        contrasena_hash=get_password_hash("password123"),
        estado="activo",
    )
    op_user = Usuario(
        id_rol=op_rol.id,
        nombre="Op Ops",
        correo="operador_op@aquashrimp.com",
        contrasena_hash=get_password_hash("password123"),
        estado="activo",
    )
    bio_user = Usuario(
        id_rol=bio_rol.id,
        nombre="Bio Ops",
        correo="biologo_op@aquashrimp.com",
        contrasena_hash=get_password_hash("password123"),
        estado="activo",
    )
    test_session.add_all([admin_user, op_user, bio_user])
    test_session.flush()

    piscina = Piscina(
        codigo="P-OP-01",
        ubicacion="Sector Norte",
        area_m2=1200.0,
        profundidad=1.8,
        estado="activa",
    )
    test_session.add(piscina)
    test_session.flush()

    sensor = Sensor(
        id_piscina=piscina.id,
        tipo="ph",
        unidad_medida="pH",
        estado="activo",
    )
    test_session.add(sensor)
    test_session.commit()

    admin_token = create_access_token({"sub": admin_user.correo})
    op_token = create_access_token({"sub": op_user.correo})
    bio_token = create_access_token({"sub": bio_user.correo})

    return {
        "admin_headers": {"Authorization": f"Bearer {admin_token}"},
        "op_headers": {"Authorization": f"Bearer {op_token}"},
        "bio_headers": {"Authorization": f"Bearer {bio_token}"},
        "admin_user": admin_user,
        "op_user": op_user,
        "bio_user": bio_user,
        "piscina": piscina,
        "sensor": sensor,
    }


# ---------------------------------------------------------------------------
# Test Suite: Alerta CRUD
# ---------------------------------------------------------------------------


class TestAlertaCRUD:
    def test_alerta_unauthenticated(self, client: TestClient):
        res = client.get("/api/alertas")
        assert res.status_code == 401

        res = client.post("/api/alertas", json={})
        assert res.status_code == 401

    def test_alerta_crud_flow(self, client: TestClient, test_session: Session):
        auth = setup_auth_and_base_data(test_session)
        headers = auth["op_headers"]
        admin_headers = auth["admin_headers"]
        sensor_id = auth["sensor"].id
        user_id = auth["op_user"].id

        # 1. Create Alerta
        payload = {
            "id_sensor": sensor_id,
            "id_usuario": user_id,
            "tipo_alerta": "pH Anormal",
            "severidad": "alta",
            "descripcion": "Nivel de pH fuera de rango detectado",
            "estado": "activa",
        }
        create_res = client.post("/api/alertas", json=payload, headers=headers)
        assert create_res.status_code == 201
        data = create_res.json()
        alerta_id = data["id"]
        assert data["severidad"] == "alta"
        assert data["tipo_alerta"] == "pH Anormal"

        # 2. Get Alertas (List)
        list_res = client.get(
            "/api/alertas?estado=activa&severidad=alta", headers=headers
        )
        assert list_res.status_code == 200
        items = list_res.json()
        assert len(items) >= 1
        assert items[0]["id"] == alerta_id

        # 3. Get Alerta by ID
        get_res = client.get(f"/api/alertas/{alerta_id}", headers=headers)
        assert get_res.status_code == 200
        assert get_res.json()["descripcion"] == "Nivel de pH fuera de rango detectado"

        # 4. Update Alerta
        update_payload = {"estado": "atendida", "descripcion": "Atendida por operador"}
        update_res = client.put(
            f"/api/alertas/{alerta_id}", json=update_payload, headers=headers
        )
        assert update_res.status_code == 200
        assert update_res.json()["estado"] == "atendida"
        assert update_res.json()["descripcion"] == "Atendida por operador"

        # 5. Delete Alerta (Admin required)
        del_res = client.delete(f"/api/alertas/{alerta_id}", headers=admin_headers)
        assert del_res.status_code == 200

        # Verify 404
        get_deleted = client.get(f"/api/alertas/{alerta_id}", headers=headers)
        assert get_deleted.status_code == 404

    def test_alerta_delete_requires_admin(
        self, client: TestClient, test_session: Session
    ):
        auth = setup_auth_and_base_data(test_session)
        headers = auth["op_headers"]

        create_res = client.post(
            "/api/alertas",
            json={
                "tipo_alerta": "Oxígeno Bajo",
                "severidad": "critica",
                "descripcion": "Crítico",
            },
            headers=headers,
        )
        alerta_id = create_res.json()["id"]

        del_res = client.delete(f"/api/alertas/{alerta_id}", headers=headers)
        assert del_res.status_code == 403

    def test_alerta_invalid_sensor(
        self, client: TestClient, test_session: Session
    ):
        auth = setup_auth_and_base_data(test_session)
        headers = auth["op_headers"]

        res = client.post(
            "/api/alertas",
            json={
                "id_sensor": 99999,
                "tipo_alerta": "Test",
                "severidad": "baja",
                "descripcion": "Sensor inexistente",
            },
            headers=headers,
        )
        assert res.status_code == 400
        assert "Sensor no encontrado" in res.json()["detail"]


# ---------------------------------------------------------------------------
# Test Suite: AccionCorrectiva CRUD
# ---------------------------------------------------------------------------


class TestAccionCorrectivaCRUD:
    def test_accion_correctiva_unauthenticated(self, client: TestClient):
        res = client.get("/api/acciones-correctivas")
        assert res.status_code == 401

        res = client.post("/api/acciones-correctivas", json={})
        assert res.status_code == 401

    def test_accion_correctiva_crud_flow(
        self, client: TestClient, test_session: Session
    ):
        auth = setup_auth_and_base_data(test_session)
        headers = auth["op_headers"]
        admin_headers = auth["admin_headers"]

        # Create base alerta
        alerta_res = client.post(
            "/api/alertas",
            json={
                "tipo_alerta": "pH Anormal",
                "severidad": "alta",
                "descripcion": "Alerta base para accion correctiva",
            },
            headers=headers,
        )
        alerta_id = alerta_res.json()["id"]
        user_id = auth["op_user"].id

        # 1. Create AccionCorrectiva
        payload = {
            "id_alerta": alerta_id,
            "id_usuario": user_id,
            "descripcion": "Aplicación de buffer corrector de pH",
            "estado": "en_progreso",
        }
        create_res = client.post(
            "/api/acciones-correctivas", json=payload, headers=headers
        )
        assert create_res.status_code == 201
        data = create_res.json()
        accion_id = data["id"]
        assert data["estado"] == "en_progreso"

        # 2. Get Acciones List
        list_res = client.get(
            f"/api/acciones-correctivas?id_alerta={alerta_id}&estado=en_progreso",
            headers=headers,
        )
        assert list_res.status_code == 200
        items = list_res.json()
        assert len(items) == 1
        assert items[0]["id"] == accion_id

        # 3. Get Accion by ID
        get_res = client.get(
            f"/api/acciones-correctivas/{accion_id}", headers=headers
        )
        assert get_res.status_code == 200
        assert (
            get_res.json()["descripcion"]
            == "Aplicación de buffer corrector de pH"
        )

        # 4. Update Accion
        update_res = client.put(
            f"/api/acciones-correctivas/{accion_id}",
            json={"estado": "completada", "resultado": "pH estabilizado en 7.5"},
            headers=headers,
        )
        assert update_res.status_code == 200
        assert update_res.json()["estado"] == "completada"
        assert update_res.json()["resultado"] == "pH estabilizado en 7.5"

        # 5. Delete Accion (Admin required)
        del_res = client.delete(
            f"/api/acciones-correctivas/{accion_id}", headers=admin_headers
        )
        assert del_res.status_code == 200

        # Verify 404
        get_deleted = client.get(
            f"/api/acciones-correctivas/{accion_id}", headers=headers
        )
        assert get_deleted.status_code == 404

    def test_accion_correctiva_invalid_alerta(
        self, client: TestClient, test_session: Session
    ):
        auth = setup_auth_and_base_data(test_session)
        headers = auth["op_headers"]

        res = client.post(
            "/api/acciones-correctivas",
            json={
                "id_alerta": 99999,
                "id_usuario": auth["op_user"].id,
                "descripcion": "Accion invalida",
            },
            headers=headers,
        )
        assert res.status_code == 400
        assert "Alerta no encontrada" in res.json()["detail"]


# ---------------------------------------------------------------------------
# Test Suite: Cosecha CRUD
# ---------------------------------------------------------------------------


class TestCosechaCRUD:
    def test_cosecha_unauthenticated(self, client: TestClient):
        res = client.get("/api/cosechas")
        assert res.status_code == 401

        res = client.post("/api/cosechas", json={})
        assert res.status_code == 401

    def test_cosecha_crud_flow(self, client: TestClient, test_session: Session):
        auth = setup_auth_and_base_data(test_session)
        headers = auth["bio_headers"]
        admin_headers = auth["admin_headers"]
        piscina_id = auth["piscina"].id

        # 1. Create Cosecha
        payload = {
            "id_piscina": piscina_id,
            "fecha_cosecha": "2026-08-01",
            "biomasa_kg": 3500.5,
            "talla_promedio": 16.2,
            "rendimiento": 0.88,
            "observaciones": "Cosecha parcial exitosa",
        }
        create_res = client.post("/api/cosechas", json=payload, headers=headers)
        assert create_res.status_code == 201
        data = create_res.json()
        cosecha_id = data["id"]
        assert data["biomasa_kg"] == 3500.5
        assert data["talla_promedio"] == 16.2

        # 2. Get Cosechas (List)
        list_res = client.get(
            f"/api/cosechas?id_piscina={piscina_id}", headers=headers
        )
        assert list_res.status_code == 200
        items = list_res.json()
        assert len(items) >= 1
        assert items[0]["id"] == cosecha_id

        # 3. Get Cosecha by ID
        get_res = client.get(f"/api/cosechas/{cosecha_id}", headers=headers)
        assert get_res.status_code == 200
        assert get_res.json()["observaciones"] == "Cosecha parcial exitosa"

        # 4. Update Cosecha
        update_payload = {
            "biomasa_kg": 3800.0,
            "observaciones": "Ajuste de biomasa final",
        }
        update_res = client.put(
            f"/api/cosechas/{cosecha_id}", json=update_payload, headers=headers
        )
        assert update_res.status_code == 200
        assert update_res.json()["biomasa_kg"] == 3800.0
        assert update_res.json()["observaciones"] == "Ajuste de biomasa final"

        # 5. Delete Cosecha (Admin required)
        del_res = client.delete(f"/api/cosechas/{cosecha_id}", headers=admin_headers)
        assert del_res.status_code == 200

        # Verify 404
        get_deleted = client.get(f"/api/cosechas/{cosecha_id}", headers=headers)
        assert get_deleted.status_code == 404

    def test_cosecha_invalid_piscina(
        self, client: TestClient, test_session: Session
    ):
        auth = setup_auth_and_base_data(test_session)
        headers = auth["bio_headers"]

        res = client.post(
            "/api/cosechas",
            json={
                "id_piscina": 99999,
                "fecha_cosecha": "2026-08-01",
                "biomasa_kg": 1000.0,
            },
            headers=headers,
        )
        assert res.status_code == 400
        assert "Piscina no encontrada" in res.json()["detail"]


# ---------------------------------------------------------------------------
# Test Suite: ReporteGerencial CRUD
# ---------------------------------------------------------------------------


class TestReporteGerencialCRUD:
    def test_reporte_gerencial_unauthenticated(self, client: TestClient):
        res = client.get("/api/reportes-gerenciales")
        assert res.status_code == 401

        res = client.post("/api/reportes-gerenciales", json={})
        assert res.status_code == 401

    def test_reporte_gerencial_crud_flow(
        self, client: TestClient, test_session: Session
    ):
        auth = setup_auth_and_base_data(test_session)
        headers = auth["admin_headers"]
        user_id = auth["admin_user"].id

        # 1. Create Reporte Gerencial
        payload = {
            "id_usuario": user_id,
            "tipo_reporte": "rendimiento",
            "periodo_inicio": "2026-07-01",
            "periodo_fin": "2026-07-31",
            "ruta_archivo": "/reports/rendimiento_2026_07.pdf",
        }
        create_res = client.post(
            "/api/reportes-gerenciales", json=payload, headers=headers
        )
        assert create_res.status_code == 201
        data = create_res.json()
        reporte_id = data["id"]
        assert data["tipo_reporte"] == "rendimiento"
        assert data["periodo_inicio"] == "2026-07-01"

        # 2. Get List
        list_res = client.get(
            f"/api/reportes-gerenciales?tipo_reporte=rendimiento&id_usuario={user_id}",
            headers=headers,
        )
        assert list_res.status_code == 200
        items = list_res.json()
        assert len(items) >= 1
        assert items[0]["id"] == reporte_id

        # 3. Get by ID
        get_res = client.get(
            f"/api/reportes-gerenciales/{reporte_id}", headers=headers
        )
        assert get_res.status_code == 200
        assert get_res.json()["ruta_archivo"] == "/reports/rendimiento_2026_07.pdf"

        # 4. Update Reporte
        update_res = client.put(
            f"/api/reportes-gerenciales/{reporte_id}",
            json={"ruta_archivo": "/reports/rendimiento_2026_07_v2.pdf"},
            headers=headers,
        )
        assert update_res.status_code == 200
        assert (
            update_res.json()["ruta_archivo"] == "/reports/rendimiento_2026_07_v2.pdf"
        )

        # 5. Delete Reporte
        del_res = client.delete(
            f"/api/reportes-gerenciales/{reporte_id}", headers=headers
        )
        assert del_res.status_code == 200

        # Verify 404
        get_deleted = client.get(
            f"/api/reportes-gerenciales/{reporte_id}", headers=headers
        )
        assert get_deleted.status_code == 404

    def test_reporte_gerencial_invalid_periodo(
        self, client: TestClient, test_session: Session
    ):
        auth = setup_auth_and_base_data(test_session)
        headers = auth["admin_headers"]

        payload = {
            "id_usuario": auth["admin_user"].id,
            "tipo_reporte": "alertas",
            "periodo_inicio": "2026-07-31",
            "periodo_fin": "2026-07-01",  # Invalid: fin < inicio
        }
        res = client.post(
            "/api/reportes-gerenciales", json=payload, headers=headers
        )
        assert res.status_code == 422

    def test_reporte_gerencial_invalid_usuario(
        self, client: TestClient, test_session: Session
    ):
        auth = setup_auth_and_base_data(test_session)
        headers = auth["admin_headers"]

        payload = {
            "id_usuario": 99999,
            "tipo_reporte": "alertas",
            "periodo_inicio": "2026-07-01",
            "periodo_fin": "2026-07-31",
        }
        res = client.post(
            "/api/reportes-gerenciales", json=payload, headers=headers
        )
        assert res.status_code == 400
        assert "Usuario no encontrado" in res.json()["detail"]
