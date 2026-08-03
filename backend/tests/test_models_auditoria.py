import pytest
from sqlalchemy.exc import IntegrityError

from app.models.registro_auditoria import RegistroAuditoria
from app.models.rol import Rol
from app.models.usuario import Usuario


class TestRegistroAuditoriaModel:
    def test_create_registro_auditoria_con_usuario(self, test_session):
        rol = Rol(nombre_rol="Auditor")
        test_session.add(rol)
        test_session.flush()

        usuario = Usuario(
            id_rol=rol.id,
            nombre="Carlos López",
            correo="carlos@aquashrimp.com",
            contrasena_hash="hashed_pw",
        )
        test_session.add(usuario)
        test_session.flush()

        registro = RegistroAuditoria(
            id_usuario=usuario.id,
            accion="CREATE_PISCINA",
            detalles='{"codigo": "P-10", "area": 5000}',
        )
        test_session.add(registro)
        test_session.flush()

        assert registro.id is not None
        assert registro.accion == "CREATE_PISCINA"
        assert registro.detalles == '{"codigo": "P-10", "area": 5000}'
        assert registro.usuario == usuario
        assert registro in usuario.registros_auditoria
        assert registro.fecha_hora is not None

    def test_create_registro_auditoria_anonimo(self, test_session):
        registro = RegistroAuditoria(
            id_usuario=None,
            accion="LOGIN_FAILED",
            detalles='{"ip": "192.168.1.100", "intento": 3}',
        )
        test_session.add(registro)
        test_session.flush()

        assert registro.id is not None
        assert registro.id_usuario is None
        assert registro.usuario is None
        assert registro.accion == "LOGIN_FAILED"
        assert registro.fecha_hora is not None

    def test_accion_not_null(self, test_session):
        registro = RegistroAuditoria(
            id_usuario=None,
            detalles="Missing action",
        )
        test_session.add(registro)
        with pytest.raises(IntegrityError):
            test_session.flush()

    def test_usuario_ondelete_set_null(self, test_session):
        rol = Rol(nombre_rol="TempRol")
        test_session.add(rol)
        test_session.flush()

        usuario = Usuario(
            id_rol=rol.id,
            nombre="Usuario Temporal",
            correo="temp@aquashrimp.com",
            contrasena_hash="hash",
        )
        test_session.add(usuario)
        test_session.flush()

        registro = RegistroAuditoria(
            id_usuario=usuario.id,
            accion="DELETE_PISCINA",
            detalles="Piscina 1 eliminada",
        )
        test_session.add(registro)
        test_session.flush()

        test_session.delete(usuario)
        test_session.flush()

        assert registro.id_usuario is None
        assert registro.usuario is None
