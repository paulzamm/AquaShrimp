from datetime import timedelta

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwt
import pytest
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_current_user, require_roles
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.rol import Rol
from app.models.usuario import Usuario

# ---------------------------------------------------------------------------
# Test Core Security Module
# ---------------------------------------------------------------------------


def test_password_hashing():
    raw_password = "SecretPassword123!"
    hashed = get_password_hash(raw_password)

    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data=data, expires_delta=timedelta(minutes=15))

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "test@example.com"
    assert "exp" in payload


# ---------------------------------------------------------------------------
# Fixture & Teardown to maintain clean session for other test files
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clean_auth_db(test_session: Session):
    yield
    test_session.rollback()
    test_session.query(Usuario).filter(
        Usuario.correo.in_(
            ["admin_auth@aquashrimp.com", "inactive_auth@aquashrimp.com"]
        )
    ).delete(synchronize_session=False)
    test_session.query(Rol).filter(
        Rol.nombre_rol.in_(["Administrador_AuthTest", "Operador_AuthTest"])
    ).delete(synchronize_session=False)
    test_session.commit()


def setup_roles_and_users(session: Session):
    rol_admin = Rol(
        nombre_rol="Administrador_AuthTest", descripcion="Admin role"
    )
    rol_op = Rol(nombre_rol="Operador_AuthTest", descripcion="Operator role")
    session.add_all([rol_admin, rol_op])
    session.flush()

    active_user = Usuario(
        id_rol=rol_admin.id,
        nombre="Admin User",
        correo="admin_auth@aquashrimp.com",
        contrasena_hash=get_password_hash("admin123"),
        estado="activo",
    )
    inactive_user = Usuario(
        id_rol=rol_op.id,
        nombre="Inactive User",
        correo="inactive_auth@aquashrimp.com",
        contrasena_hash=get_password_hash("op123"),
        estado="inactivo",
    )
    session.add_all([active_user, inactive_user])
    session.flush()

    return {
        "admin_role": rol_admin,
        "operator_role": rol_op,
        "active_user": active_user,
        "inactive_user": inactive_user,
    }


# ---------------------------------------------------------------------------
# Test Login Endpoint (/api/auth/login)
# ---------------------------------------------------------------------------


def test_login_success(client: TestClient, test_session: Session):
    setup_roles_and_users(test_session)
    response = client.post(
        "/api/auth/login",
        data={"username": "admin_auth@aquashrimp.com", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, test_session: Session):
    setup_roles_and_users(test_session)
    response = client.post(
        "/api/auth/login",
        data={"username": "admin_auth@aquashrimp.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Correo o contraseña incorrectos"


def test_login_user_not_found(client: TestClient, test_session: Session):
    setup_roles_and_users(test_session)
    response = client.post(
        "/api/auth/login",
        data={"username": "nonexistent@aquashrimp.com", "password": "admin123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Correo o contraseña incorrectos"


def test_login_inactive_user(client: TestClient, test_session: Session):
    setup_roles_and_users(test_session)
    response = client.post(
        "/api/auth/login",
        data={"username": "inactive_auth@aquashrimp.com", "password": "op123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Usuario inactivo"


# ---------------------------------------------------------------------------
# Test Security Dependencies & RBAC
# ---------------------------------------------------------------------------


def test_get_current_user_valid(client: TestClient, test_session: Session):
    setup_roles_and_users(test_session)
    token = create_access_token({"sub": "admin_auth@aquashrimp.com"})
    headers = {"Authorization": f"Bearer {token}"}

    app_test = FastAPI()

    @app_test.get("/test-user")
    def dummy_route(current_user: Usuario = Depends(get_current_user)):
        return {"correo": current_user.correo, "nombre": current_user.nombre}

    from app.core.database import get_db

    app_test.dependency_overrides[get_db] = lambda: test_session
    with TestClient(app_test) as tc:
        resp = tc.get("/test-user", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["correo"] == "admin_auth@aquashrimp.com"


def test_get_current_user_invalid_token(client: TestClient, test_session: Session):
    token = "invalid.token.str"
    headers = {"Authorization": f"Bearer {token}"}

    app_test = FastAPI()

    @app_test.get("/test-user")
    def dummy_route(current_user: Usuario = Depends(get_current_user)):
        return {"correo": current_user.correo}

    from app.core.database import get_db

    app_test.dependency_overrides[get_db] = lambda: test_session
    with TestClient(app_test) as tc:
        resp = tc.get("/test-user", headers=headers)
        assert resp.status_code == 401


def test_rbac_require_roles_success(client: TestClient, test_session: Session):
    setup_roles_and_users(test_session)
    token = create_access_token({"sub": "admin_auth@aquashrimp.com"})
    headers = {"Authorization": f"Bearer {token}"}

    app_test = FastAPI()

    @app_test.get("/admin-only")
    def admin_route(
        current_user: Usuario = Depends(
            require_roles(["Administrador_AuthTest"])
        ),
    ):
        return {"message": "Welcome Admin"}

    from app.core.database import get_db

    app_test.dependency_overrides[get_db] = lambda: test_session
    with TestClient(app_test) as tc:
        resp = tc.get("/admin-only", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["message"] == "Welcome Admin"


def test_rbac_require_roles_forbidden(client: TestClient, test_session: Session):
    setup_roles_and_users(test_session)
    token = create_access_token({"sub": "admin_auth@aquashrimp.com"})
    headers = {"Authorization": f"Bearer {token}"}

    app_test = FastAPI()

    @app_test.get("/op-only")
    def operator_route(
        current_user: Usuario = Depends(require_roles(["Operador_AuthTest"])),
    ):
        return {"message": "Welcome Operator"}

    from app.core.database import get_db

    app_test.dependency_overrides[get_db] = lambda: test_session
    with TestClient(app_test) as tc:
        resp = tc.get("/op-only", headers=headers)
        assert resp.status_code == 403
        assert (
            resp.json()["detail"]
            == "No tiene permisos suficientes para realizar esta acción"
        )
