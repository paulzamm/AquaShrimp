from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.accion_correctiva import AccionCorrectiva
from app.schemas.accion_correctiva import (
    AccionCorrectivaCreate,
    AccionCorrectivaUpdate,
)


def get_accion_correctiva(db: Session, accion_id: int) -> Optional[AccionCorrectiva]:
    """Retrieve a single corrective action by ID."""
    return db.query(AccionCorrectiva).filter(AccionCorrectiva.id == accion_id).first()


def get_acciones_correctivas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    id_alerta: Optional[int] = None,
    id_usuario: Optional[int] = None,
    estado: Optional[str] = None,
) -> List[AccionCorrectiva]:
    """Retrieve multiple corrective actions with pagination and optional filters."""
    query = db.query(AccionCorrectiva)
    if id_alerta:
        query = query.filter(AccionCorrectiva.id_alerta == id_alerta)
    if id_usuario:
        query = query.filter(AccionCorrectiva.id_usuario == id_usuario)
    if estado:
        query = query.filter(AccionCorrectiva.estado == estado)
    return query.offset(skip).limit(limit).all()


def create_accion_correctiva(
    db: Session, accion_in: AccionCorrectivaCreate
) -> AccionCorrectiva:
    """Create a new corrective action."""
    data = accion_in.model_dump(exclude_unset=True)
    valid_fields = {
        "id_alerta",
        "id_usuario",
        "descripcion",
        "fecha_accion",
        "resultado",
        "estado",
    }
    create_data = {k: v for k, v in data.items() if k in valid_fields}
    db_obj = AccionCorrectiva(**create_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_accion_correctiva(
    db: Session, db_obj: AccionCorrectiva, accion_in: AccionCorrectivaUpdate
) -> AccionCorrectiva:
    """Update an existing corrective action."""
    update_data = accion_in.model_dump(exclude_unset=True)
    valid_fields = {
        "id_alerta",
        "id_usuario",
        "descripcion",
        "fecha_accion",
        "resultado",
        "estado",
    }
    for field, value in update_data.items():
        if field in valid_fields:
            setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_accion_correctiva(
    db: Session, accion_id: int
) -> Optional[AccionCorrectiva]:
    """Delete a corrective action by ID."""
    db_obj = db.query(AccionCorrectiva).filter(AccionCorrectiva.id == accion_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
