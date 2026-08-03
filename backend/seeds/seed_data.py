"""Seed script to populate the database with initial data."""

from datetime import date, datetime, timedelta

import bcrypt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.piscina import Piscina
from app.models.sensor import Sensor
from app.models.lectura_sensor import LecturaSensor
from app.models.alerta import Alerta
from app.models.accion_correctiva import AccionCorrectiva
from app.models.recomendacion_alimentacion import RecomendacionAlimentacion
from app.models.cosecha import Cosecha
from app.models.reporte_gerencial import ReporteGerencial

# Fix passlib 1.7.4 compatibility with bcrypt >= 4.0.0
_orig_hashpw = bcrypt.hashpw
bcrypt.hashpw = lambda p, s: _orig_hashpw(p[:72], s)
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("about", (), {"__version__": getattr(bcrypt, "__version__", "4.0.0")})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed(session: Session) -> None:
    """Populate the database with initial data. Idempotent — skips if roles exist."""

    if session.query(Rol).first() is not None:
        return

    # --- Roles ---
    roles = [
        Rol(nombre_rol="Administrador", descripcion="Administrador del sistema", permisos='["all"]'),
        Rol(nombre_rol="Técnico Acuícola", descripcion="Técnico de campo", permisos='["lecturas","alertas","acciones"]'),
        Rol(nombre_rol="Gerencia", descripcion="Gerente de operaciones", permisos='["dashboard","reportes"]'),
    ]
    session.add_all(roles)
    session.flush()

    # --- Usuarios ---
    usuarios = [
        Usuario(
            id_rol=roles[0].id, nombre="Carlos Mendoza",
            correo="admin@aquashrimp.com",
            contrasena_hash=pwd_context.hash("admin123"),
        ),
        Usuario(
            id_rol=roles[1].id, nombre="María López",
            correo="tecnico@aquashrimp.com",
            contrasena_hash=pwd_context.hash("tecnico123"),
        ),
        Usuario(
            id_rol=roles[2].id, nombre="Roberto Guzmán",
            correo="gerente@aquashrimp.com",
            contrasena_hash=pwd_context.hash("gerente123"),
        ),
    ]
    session.add_all(usuarios)
    session.flush()

    # --- Piscinas ---
    piscinas = [
        Piscina(codigo="P-001", ubicacion="Sector Norte - Lote A", area_m2=5000.0, profundidad=1.5, fecha_inicio_ciclo=date(2026, 5, 1)),
        Piscina(codigo="P-002", ubicacion="Sector Norte - Lote B", area_m2=4500.0, profundidad=1.4, fecha_inicio_ciclo=date(2026, 5, 15)),
        Piscina(codigo="P-003", ubicacion="Sector Sur - Lote C", area_m2=6000.0, profundidad=1.6, estado="mantenimiento"),
    ]
    session.add_all(piscinas)
    session.flush()

    # --- Sensores (3 per piscina = 9 total) ---
    sensor_types = [
        ("ph", "pH"),
        ("oxigeno_disuelto", "mg/L"),
        ("temperatura", "°C"),
    ]
    sensores = []
    for piscina in piscinas:
        for tipo, unidad in sensor_types:
            sensor = Sensor(
                id_piscina=piscina.id, tipo=tipo, unidad_medida=unidad,
                ubicacion=f"Centro de {piscina.codigo}",
                fecha_instalacion=date(2026, 4, 20),
            )
            sensores.append(sensor)
    session.add_all(sensores)
    session.flush()

    # --- Lecturas (mix of normal and critical) ---
    now = datetime(2026, 7, 15, 8, 0, 0)
    lecturas_data = [
        # Normal readings for P-001
        (sensores[0], 7.2, "pH", "valida"),
        (sensores[1], 6.5, "mg/L", "valida"),
        (sensores[2], 28.0, "°C", "valida"),
        # Normal readings for P-002
        (sensores[3], 7.5, "pH", "valida"),
        (sensores[4], 5.8, "mg/L", "valida"),
        (sensores[5], 29.0, "°C", "valida"),
        # Critical readings for P-001
        (sensores[0], 5.2, "pH", "valida"),  # pH too low
        (sensores[2], 35.5, "°C", "valida"),  # Temperature too high
        # Normal readings for P-002
        (sensores[3], 7.8, "pH", "valida"),
        (sensores[4], 6.2, "mg/L", "valida"),
        (sensores[5], 27.5, "°C", "valida"),
        # Invalid reading
        (sensores[2], -5.0, "°C", "invalida"),
    ]
    lecturas = []
    for i, (sensor, valor, unidad, estado) in enumerate(lecturas_data):
        lectura = LecturaSensor(
            id_sensor=sensor.id, valor=valor, unidad=unidad,
            fecha_hora=now + timedelta(minutes=i * 15),
            estado_validacion=estado,
        )
        lecturas.append(lectura)
    session.add_all(lecturas)
    session.flush()

    # --- Alertas ---
    alertas = [
        Alerta(
            id_lectura=lecturas[6].id, tipo_alerta="ph_bajo",
            severidad="alta", descripcion="pH de 5.2 por debajo del umbral mínimo (6.5)",
        ),
        Alerta(
            id_lectura=lecturas[7].id, tipo_alerta="temperatura_alta",
            severidad="critica", descripcion="Temperatura de 35.5°C supera el umbral máximo (33°C)",
        ),
    ]
    session.add_all(alertas)
    session.flush()

    # --- Acciones Correctivas ---
    accion = AccionCorrectiva(
        id_alerta=alertas[0].id, id_usuario=usuarios[1].id,
        descripcion="Se aplicó cal agrícola para elevar el pH. Dosis: 50 kg/ha.",
        resultado="pH estabilizado a 7.0 después de 4 horas",
        estado="completada",
    )
    session.add(accion)
    session.flush()

    # --- Recomendaciones de Alimentación ---
    recomendaciones = [
        RecomendacionAlimentacion(
            id_piscina=piscinas[0].id, id_usuario=usuarios[1].id,
            cantidad_kg=25.0, frecuencia="3 veces al día",
            criterio="Temperatura estable 26-30°C, pH normal",
            estado="aplicada",
        ),
        RecomendacionAlimentacion(
            id_piscina=piscinas[1].id,
            cantidad_kg=20.0, frecuencia="2 veces al día",
            criterio="Condiciones normales, densidad media",
        ),
    ]
    session.add_all(recomendaciones)
    session.flush()

    # --- Cosecha ---
    cosecha = Cosecha(
        id_piscina=piscinas[0].id,
        fecha_cosecha=date(2026, 7, 10),
        biomasa_kg=4200.0, talla_promedio=18.0,
        rendimiento=0.84,
        observaciones="Ciclo de 70 días. Rendimiento dentro de lo esperado.",
    )
    session.add(cosecha)
    session.flush()

    # --- Reporte Gerencial ---
    reporte = ReporteGerencial(
        id_usuario=usuarios[2].id,
        tipo_reporte="rendimiento",
        periodo_inicio=date(2026, 6, 1),
        periodo_fin=date(2026, 6, 30),
        ruta_archivo="/reportes/2026/junio_mensual.pdf",
    )
    session.add(reporte)
    session.flush()


def main() -> None:
    """CLI entry point: populate the real database."""
    from app.core.database import SessionLocal

    session = SessionLocal()
    try:
        seed(session)
        session.commit()
        print("✅ Seed data loaded successfully.")
    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
