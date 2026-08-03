from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.models.lectura_sensor import LecturaSensor
from app.models.recomendacion_alimentacion import RecomendacionAlimentacion
from app.models.sensor import Sensor
from app.schemas.lectura_sensor import LecturaSensorCreate


def get_lectura(db: Session, lectura_id: int) -> Optional[LecturaSensor]:
    """Retrieve a single reading by ID."""
    return db.query(LecturaSensor).filter(LecturaSensor.id == lectura_id).first()


def get_lecturas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    id_sensor: Optional[int] = None,
) -> List[LecturaSensor]:
    """Retrieve multiple readings with optional sensor filtering and pagination."""
    query = db.query(LecturaSensor)
    if id_sensor is not None:
        query = query.filter(LecturaSensor.id_sensor == id_sensor)
    return query.offset(skip).limit(limit).all()


def procesar_lectura(db: Session, lectura_in: LecturaSensorCreate) -> LecturaSensor:
    """Ingest a sensor reading, save it to DB, and evaluate BPM rules (Alerts & Feeding Recommendations)."""
    sensor = db.query(Sensor).filter(Sensor.id == lectura_in.id_sensor).first()
    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sensor no encontrado",
        )

    lectura_kwargs = lectura_in.model_dump(exclude_unset=True)
    if lectura_kwargs.get("fecha_hora") is None:
        lectura_kwargs.pop("fecha_hora", None)

    db_lectura = LecturaSensor(**lectura_kwargs)
    db.add(db_lectura)
    db.flush()

    tipo = sensor.tipo.lower() if sensor.tipo else ""
    valor = db_lectura.valor
    alerta_generada = False

    if tipo == "ph":
        if valor < 6.5 or valor > 8.5:
            alerta = Alerta(
                id_lectura=db_lectura.id,
                id_sensor=sensor.id,
                tipo_alerta="ph_fuera_de_rango",
                severidad="alta",
                descripcion=f"Nivel de pH fuera de rango aceptable (6.5 - 8.5): {valor}",
                estado="activa",
            )
            db.add(alerta)
            alerta_generada = True
    elif tipo == "oxigeno_disuelto":
        if valor < 4.0:
            alerta = Alerta(
                id_lectura=db_lectura.id,
                id_sensor=sensor.id,
                tipo_alerta="oxigeno_bajo",
                severidad="critica",
                descripcion=f"Nivel de oxígeno disuelto bajo (< 4.0 mg/L): {valor}",
                estado="activa",
            )
            db.add(alerta)
            alerta_generada = True
    elif tipo == "temperatura":
        if valor < 24.0 or valor > 32.0:
            alerta = Alerta(
                id_lectura=db_lectura.id,
                id_sensor=sensor.id,
                tipo_alerta="temperatura_fuera_de_rango",
                severidad="media",
                descripcion=f"Temperatura fuera de rango aceptable (24.0 - 32.0 °C): {valor}",
                estado="activa",
            )
            db.add(alerta)
            alerta_generada = True

    if not alerta_generada:
        recomendacion = RecomendacionAlimentacion(
            id_piscina=sensor.id_piscina,
            cantidad_kg=50.0,
            frecuencia="diaria",
            criterio="Parámetros óptimos registrados.",
            estado="pendiente",
        )
        db.add(recomendacion)

    db.commit()
    db.refresh(db_lectura)
    return db_lectura
