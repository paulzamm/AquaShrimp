import pytest
from sqlalchemy.exc import IntegrityError

from app.models.rol import Rol
from app.models.usuario import Usuario


class TestRolModel:
    def test_create_rol(self, test_session):
        rol = Rol(nombre_rol="Administrador", descripcion="Admin del sistema")
        test_session.add(rol)
        test_session.flush()
        assert rol.id is not None
        assert rol.nombre_rol == "Administrador"
        assert rol.estado == "activo"
        assert rol.created_at is not None

    def test_rol_nombre_unique(self, test_session):
        rol1 = Rol(nombre_rol="Técnico")
        rol2 = Rol(nombre_rol="Técnico")
        test_session.add_all([rol1, rol2])
        with pytest.raises(IntegrityError):
            test_session.flush()

    def test_rol_nombre_not_null(self, test_session):
        rol = Rol()
        test_session.add(rol)
        with pytest.raises(IntegrityError):
            test_session.flush()

    def test_rol_estado_default(self, test_session):
        rol = Rol(nombre_rol="Gerencia")
        test_session.add(rol)
        test_session.flush()
        assert rol.estado == "activo"


class TestUsuarioModel:
    def test_create_usuario(self, test_session):
        rol = Rol(nombre_rol="Admin")
        test_session.add(rol)
        test_session.flush()

        usuario = Usuario(
            id_rol=rol.id,
            nombre="Juan Pérez",
            correo="juan@aquashrimp.com",
            contrasena_hash="hashed_password",
        )
        test_session.add(usuario)
        test_session.flush()
        assert usuario.id is not None
        assert usuario.estado == "activo"
        assert usuario.created_at is not None

    def test_usuario_correo_unique(self, test_session):
        rol = Rol(nombre_rol="TestRol")
        test_session.add(rol)
        test_session.flush()

        u1 = Usuario(id_rol=rol.id, nombre="A", correo="dup@test.com", contrasena_hash="h")
        u2 = Usuario(id_rol=rol.id, nombre="B", correo="dup@test.com", contrasena_hash="h")
        test_session.add_all([u1, u2])
        with pytest.raises(IntegrityError):
            test_session.flush()

    def test_usuario_rol_relationship(self, test_session):
        rol = Rol(nombre_rol="RelTest")
        test_session.add(rol)
        test_session.flush()

        usuario = Usuario(
            id_rol=rol.id, nombre="Test", correo="rel@test.com", contrasena_hash="h"
        )
        test_session.add(usuario)
        test_session.flush()
        assert usuario.rol.nombre_rol == "RelTest"
        assert usuario in rol.usuarios
