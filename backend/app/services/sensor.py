from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.sensor import Sensor
from app.schemas.sensor import SensorCreate, SensorUpdate


def get_sensor(db: Session, sensor_id: int) -> Optional[Sensor]:
    """Retrieve a single sensor by ID."""
    return db.query(Sensor).filter(Sensor.id == sensor_id).first()


def get_sensores(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    id_piscina: Optional[int] = None,
) -> List[Sensor]:
    """Retrieve multiple sensors with optional pool filtering and pagination."""
    query = db.query(Sensor)
    if id_piscina is not None:
        query = query.filter(Sensor.id_piscina == id_piscina)
    return query.offset(skip).limit(limit).all()


def create_sensor(db: Session, sensor_in: SensorCreate) -> Sensor:
    """Create a new sensor."""
    db_obj = Sensor(
        id_piscina=sensor_in.id_piscina,
        tipo=sensor_in.tipo,
        ubicacion=sensor_in.ubicacion,
        estado=sensor_in.estado,
        unidad_medida=sensor_in.unidad_medida,
        fecha_instalacion=sensor_in.fecha_instalacion,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_sensor(
    db: Session, db_obj: Sensor, sensor_in: SensorUpdate
) -> Sensor:
    """Update an existing sensor."""
    update_data = sensor_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_sensor(db: Session, sensor_id: int) -> Optional[Sensor]:
    """Delete a sensor by ID."""
    db_obj = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
