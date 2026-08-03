from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.schemas.alerta import AlertaCreate, AlertaUpdate


def get_alerta(db: Session, alerta_id: int) -> Optional[Alerta]:
    """Retrieve a single alert by ID."""
    return db.query(Alerta).filter(Alerta.id == alerta_id).first()


def get_alertas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    severidad: Optional[str] = None,
    id_sensor: Optional[int] = None,
) -> List[Alerta]:
    """Retrieve multiple alerts with pagination and optional filtering."""
    query = db.query(Alerta)
    if estado:
        query = query.filter(Alerta.estado == estado)
    if severidad:
        query = query.filter(Alerta.severidad == severidad)
    if id_sensor:
        query = query.filter(Alerta.id_sensor == id_sensor)
    return query.offset(skip).limit(limit).all()


def create_alerta(db: Session, alerta_in: AlertaCreate) -> Alerta:
    """Create a new alert."""
    data = alerta_in.model_dump(exclude_unset=True)
    valid_fields = {
        "id_lectura",
        "id_sensor",
        "id_usuario",
        "tipo_alerta",
        "severidad",
        "descripcion",
        "fecha_generacion",
        "estado",
    }
    create_data = {k: v for k, v in data.items() if k in valid_fields}
    db_obj = Alerta(**create_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_alerta(
    db: Session, db_obj: Alerta, alerta_in: AlertaUpdate
) -> Alerta:
    """Update an existing alert."""
    update_data = alerta_in.model_dump(exclude_unset=True)
    valid_fields = {
        "id_lectura",
        "id_sensor",
        "id_usuario",
        "tipo_alerta",
        "severidad",
        "descripcion",
        "fecha_generacion",
        "estado",
    }
    for field, value in update_data.items():
        if field in valid_fields:
            setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_alerta(db: Session, alerta_id: int) -> Optional[Alerta]:
    """Delete an alert by ID."""
    db_obj = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
