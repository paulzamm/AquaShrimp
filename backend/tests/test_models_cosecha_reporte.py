import pytest
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.piscina import Piscina
from app.models.cosecha import Cosecha
from app.models.reporte_gerencial import ReporteGerencial


class TestCosechaModel:
    def test_create_cosecha(self, test_session):
        piscina = Piscina(codigo="P-CO1", ubicacion="T", area_m2=100, profundidad=1.0)
        test_session.add(piscina)
        test_session.flush()

        cosecha = Cosecha(
            id_piscina=piscina.id,
            fecha_cosecha=date(2026, 6, 15),
            biomasa_kg=4500.0,
            talla_promedio=18.5,
            rendimiento=0.90,
        )
        test_session.add(cosecha)
        test_session.flush()
        assert cosecha.id is not None

    def test_cosecha_piscina_relationship(self, test_session):
        piscina = Piscina(codigo="P-CO2", ubicacion="T", area_m2=100, profundidad=1.0)
        test_session.add(piscina)
        test_session.flush()

        cosecha = Cosecha(
            id_piscina=piscina.id, fecha_cosecha=date(2026, 7, 1), biomasa_kg=3000.0
        )
        test_session.add(cosecha)
        test_session.flush()
        assert cosecha.piscina.codigo == "P-CO2"
        assert cosecha in piscina.cosechas

    def test_cosecha_property_aliases(self, test_session):
        piscina = Piscina(codigo="P-CO3", ubicacion="T", area_m2=100, profundidad=1.0)
        test_session.add(piscina)
        test_session.flush()

        cosecha = Cosecha(
            id_piscina=piscina.id,
            fecha_cosecha=date(2026, 7, 15),
            biomasa_total_kg=5000.0,
            peso_promedio_gramos=20.0,
        )
        test_session.add(cosecha)
        test_session.flush()

        assert cosecha.biomasa_kg == 5000.0
        assert cosecha.biomasa_total_kg == 5000.0
        assert cosecha.talla_promedio == 20.0
        assert cosecha.peso_promedio_gramos == 20.0

    def test_cosecha_biomasa_positiva_constraint(self, test_session):
        piscina = Piscina(codigo="P-CO4", ubicacion="T", area_m2=100, profundidad=1.0)
        test_session.add(piscina)
        test_session.flush()

        cosecha = Cosecha(
            id_piscina=piscina.id, fecha_cosecha=date(2026, 7, 20), biomasa_kg=-10.0
        )
        test_session.add(cosecha)
        with pytest.raises(IntegrityError):
            test_session.flush()

<<<<<<< HEAD
    def test_cosecha_talla_positiva_constraint(self, test_session):
        piscina = Piscina(codigo="P-CO5", ubicacion="T", area_m2=100, profundidad=1.0)
        test_session.add(piscina)
        test_session.flush()

        cosecha = Cosecha(
            id_piscina=piscina.id, fecha_cosecha=date(2026, 7, 21), talla_promedio=0.0
        )
        test_session.add(cosecha)
        with pytest.raises(IntegrityError):
            test_session.flush()

=======
>>>>>>> 4ba2264577f2a0358d62cc905ca3f604f07dd993

class TestReporteGerencialModel:
    def test_create_reporte(self, test_session):
        rol = Rol(nombre_rol="R-RP1")
        test_session.add(rol)
        test_session.flush()
        usuario = Usuario(
            id_rol=rol.id, nombre="Gerente", correo="rp1@t.com", contrasena_hash="h"
        )
        test_session.add(usuario)
        test_session.flush()

        reporte = ReporteGerencial(
            id_usuario=usuario.id,
<<<<<<< HEAD
            tipo_reporte="rendimiento",
=======
            tipo_reporte="mensual",
>>>>>>> 4ba2264577f2a0358d62cc905ca3f604f07dd993
            periodo_inicio=date(2026, 6, 1),
            periodo_fin=date(2026, 6, 30),
        )
        test_session.add(reporte)
        test_session.flush()
        assert reporte.id is not None

    def test_reporte_usuario_relationship(self, test_session):
        rol = Rol(nombre_rol="R-RP2")
        test_session.add(rol)
        test_session.flush()
        usuario = Usuario(
            id_rol=rol.id, nombre="G2", correo="rp2@t.com", contrasena_hash="h"
        )
        test_session.add(usuario)
        test_session.flush()

        reporte = ReporteGerencial(
            id_usuario=usuario.id,
<<<<<<< HEAD
            tipo_reporte="alertas",
=======
            tipo_reporte="semanal",
>>>>>>> 4ba2264577f2a0358d62cc905ca3f604f07dd993
            periodo_inicio=date(2026, 7, 1),
            periodo_fin=date(2026, 7, 7),
        )
        test_session.add(reporte)
        test_session.flush()
        assert reporte.usuario.nombre == "G2"
        assert reporte in usuario.reportes
        assert reporte in usuario.reportes_gerenciales

    def test_reporte_periodo_constraint(self, test_session):
        rol = Rol(nombre_rol="R-RP3")
        test_session.add(rol)
        test_session.flush()
        usuario = Usuario(
            id_rol=rol.id, nombre="G3", correo="rp3@t.com", contrasena_hash="h"
        )
        test_session.add(usuario)
        test_session.flush()

        reporte = ReporteGerencial(
            id_usuario=usuario.id,
            tipo_reporte="rendimiento",
            periodo_inicio=date(2026, 7, 10),
            periodo_fin=date(2026, 7, 1),  # Invalid: fin < inicio
        )
        test_session.add(reporte)
        with pytest.raises(IntegrityError):
            test_session.flush()
<<<<<<< HEAD

    def test_reporte_tipo_invalido_constraint(self, test_session):
        rol = Rol(nombre_rol="R-RP4")
        test_session.add(rol)
        test_session.flush()
        usuario = Usuario(
            id_rol=rol.id, nombre="G4", correo="rp4@t.com", contrasena_hash="h"
        )
        test_session.add(usuario)
        test_session.flush()

        reporte = ReporteGerencial(
            id_usuario=usuario.id,
            tipo_reporte="invalido",
            periodo_inicio=date(2026, 7, 1),
            periodo_fin=date(2026, 7, 31),
        )
        test_session.add(reporte)
        with pytest.raises(IntegrityError):
            test_session.flush()
=======
>>>>>>> 4ba2264577f2a0358d62cc905ca3f604f07dd993
