import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash
from app.models.piscina import Piscina
from app.models.registro_auditoria import RegistroAuditoria
from app.models.rol import Rol
from app.models.usuario import Usuario


@pytest.fixture
def audit_test_setup(test_session: Session):
    """Setup test roles, admin user, and auth headers for audit tests."""
    # Ensure Admin role exists
    admin_rol = (
        test_session.query(Rol).filter(Rol.nombre_rol == "Administrador").first()
    )
    if not admin_rol:
        admin_rol = Rol(nombre_rol="Administrador", descripcion="Admin role")
        test_session.add(admin_rol)
        test_session.flush()

    # Ensure Admin user exists
    user = (
        test_session.query(Usuario)
        .filter(Usuario.correo == "audit_admin@aquashrimp.com")
        .first()
    )
    if not user:
        user = Usuario(
            id_rol=admin_rol.id,
            nombre="Audit Admin",
            correo="audit_admin@aquashrimp.com",
            contrasena_hash=get_password_hash("secret123"),
            estado="activo",
        )
        test_session.add(user)
        test_session.flush()

    token = create_access_token(data={"sub": user.correo})
    headers = {"Authorization": f"Bearer {token}"}
    return {"user": user, "headers": headers}


class TestAuditoriaMiddleware:
    def test_post_creates_audit_log(
        self, client: TestClient, test_session: Session, audit_test_setup: dict
    ):
        """Verify that a successful POST request generates a RegistroAuditoria record."""
        headers = audit_test_setup["headers"]
        user = audit_test_setup["user"]

        initial_count = test_session.query(RegistroAuditoria).count()

        response = client.post(
            "/api/piscinas",
            json={
                "codigo": "P-AUDIT-01",
                "ubicacion": "Sector Norte Audit",
                "area_m2": 1500.5,
                "profundidad": 2.5,
                "estado": "activa",
                "fecha_inicio_ciclo": "2026-08-01",
            },
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        created_piscina_id = data["id"]

        logs = (
            test_session.query(RegistroAuditoria)
            .order_by(RegistroAuditoria.id.desc())
            .all()
        )
        assert len(logs) > initial_count

        latest_log = logs[0]
        assert latest_log.id_usuario == user.id
        assert "POST" in latest_log.accion
        assert latest_log.tabla_afectada == "piscinas"
        assert latest_log.ip_origen is not None
        assert latest_log.detalles is not None

    def test_put_creates_audit_log(
        self, client: TestClient, test_session: Session, audit_test_setup: dict
    ):
        """Verify that a successful PUT request generates a RegistroAuditoria record with registro_id."""
        headers = audit_test_setup["headers"]
        user = audit_test_setup["user"]

        # Create a test pool directly
        piscina = Piscina(
            codigo="P-AUDIT-02",
            ubicacion="Sector Sur Audit",
            area_m2=1200.0,
            profundidad=2.0,
            estado="activa",
        )
        test_session.add(piscina)
        test_session.commit()

        initial_count = test_session.query(RegistroAuditoria).count()

        response = client.put(
            f"/api/piscinas/{piscina.id}",
            json={"estado": "inactiva"},
            headers=headers,
        )

        assert response.status_code == 200

        logs = (
            test_session.query(RegistroAuditoria)
            .order_by(RegistroAuditoria.id.desc())
            .all()
        )
        assert len(logs) > initial_count

        latest_log = logs[0]
        assert latest_log.id_usuario == user.id
        assert "PUT" in latest_log.accion
        assert latest_log.tabla_afectada == "piscinas"
        assert latest_log.registro_id == piscina.id

    def test_delete_creates_audit_log(
        self, client: TestClient, test_session: Session, audit_test_setup: dict
    ):
        """Verify that a successful DELETE request generates a RegistroAuditoria record."""
        headers = audit_test_setup["headers"]
        user = audit_test_setup["user"]

        # Create a test pool to delete
        piscina = Piscina(
            codigo="P-AUDIT-03",
            ubicacion="Sector Este Audit",
            area_m2=1000.0,
            profundidad=1.8,
            estado="inactiva",
        )
        test_session.add(piscina)
        test_session.commit()

        initial_count = test_session.query(RegistroAuditoria).count()

        response = client.delete(
            f"/api/piscinas/{piscina.id}",
            headers=headers,
        )

        assert response.status_code == 200

        logs = (
            test_session.query(RegistroAuditoria)
            .order_by(RegistroAuditoria.id.desc())
            .all()
        )
        assert len(logs) > initial_count

        latest_log = logs[0]
        assert latest_log.id_usuario == user.id
        assert "DELETE" in latest_log.accion
        assert latest_log.tabla_afectada == "piscinas"
        assert latest_log.registro_id == piscina.id

    def test_get_does_not_create_audit_log(
        self, client: TestClient, test_session: Session, audit_test_setup: dict
    ):
        """Verify that non-mutating GET requests do NOT generate audit records."""
        headers = audit_test_setup["headers"]

        initial_count = test_session.query(RegistroAuditoria).count()

        response = client.get("/api/piscinas", headers=headers)
        assert response.status_code == 200

        final_count = test_session.query(RegistroAuditoria).count()
        assert final_count == initial_count

    def test_failed_request_does_not_create_audit_log(
        self, client: TestClient, test_session: Session, audit_test_setup: dict
    ):
        """Verify that a failed mutating request (e.g. 400 Bad Request) does NOT generate audit records."""
        headers = audit_test_setup["headers"]

        initial_count = test_session.query(RegistroAuditoria).count()

        # Send invalid body (missing required fields)
        response = client.post(
            "/api/piscinas",
            json={"invalid_field": "test"},
            headers=headers,
        )

        assert response.status_code == 422  # Validation Error

        final_count = test_session.query(RegistroAuditoria).count()
        assert final_count == initial_count
