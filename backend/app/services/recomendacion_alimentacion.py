from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.recomendacion_alimentacion import RecomendacionAlimentacion
from app.schemas.recomendacion_alimentacion import (
    RecomendacionAlimentacionCreate,
    RecomendacionAlimentacionUpdate,
)


def get_recomendacion(
    db: Session, recomendacion_id: int
) -> Optional[RecomendacionAlimentacion]:
    """Retrieve a single feeding recommendation by ID."""
    return (
        db.query(RecomendacionAlimentacion)
        .filter(RecomendacionAlimentacion.id == recomendacion_id)
        .first()
    )


def get_recomendaciones(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    id_piscina: Optional[int] = None,
    estado: Optional[str] = None,
) -> List[RecomendacionAlimentacion]:
    """Retrieve multiple feeding recommendations with optional filtering and pagination."""
    query = db.query(RecomendacionAlimentacion)
    if id_piscina is not None:
        query = query.filter(RecomendacionAlimentacion.id_piscina == id_piscina)
    if estado is not None:
        query = query.filter(RecomendacionAlimentacion.estado == estado)
    return query.offset(skip).limit(limit).all()


def create_recomendacion(
    db: Session, recomendacion_in: RecomendacionAlimentacionCreate
) -> RecomendacionAlimentacion:
    """Create a new feeding recommendation."""
    db_obj = RecomendacionAlimentacion(
        id_piscina=recomendacion_in.id_piscina,
        id_usuario=recomendacion_in.id_usuario,
        cantidad_kg=recomendacion_in.cantidad_kg,
        frecuencia=recomendacion_in.frecuencia,
        criterio=recomendacion_in.criterio,
        fecha_generacion=recomendacion_in.fecha_generacion,
        estado=recomendacion_in.estado,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_recomendacion(
    db: Session,
    db_obj: RecomendacionAlimentacion,
    recomendacion_in: RecomendacionAlimentacionUpdate,
) -> RecomendacionAlimentacion:
    """Update an existing feeding recommendation."""
    update_data = recomendacion_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_recomendacion(
    db: Session, recomendacion_id: int
) -> Optional[RecomendacionAlimentacion]:
    """Delete a feeding recommendation by ID."""
    db_obj = (
        db.query(RecomendacionAlimentacion)
        .filter(RecomendacionAlimentacion.id == recomendacion_id)
        .first()
    )
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
