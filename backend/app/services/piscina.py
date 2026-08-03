from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.piscina import Piscina
from app.schemas.piscina import PiscinaCreate, PiscinaUpdate


def get_piscina(db: Session, piscina_id: int) -> Optional[Piscina]:
    """Retrieve a single pool by ID."""
    return db.query(Piscina).filter(Piscina.id == piscina_id).first()


def get_piscina_by_codigo(db: Session, codigo: str) -> Optional[Piscina]:
    """Retrieve a single pool by code."""
    return db.query(Piscina).filter(Piscina.codigo == codigo).first()


def get_piscinas(db: Session, skip: int = 0, limit: int = 100) -> List[Piscina]:
    """Retrieve multiple pools with pagination."""
    return db.query(Piscina).offset(skip).limit(limit).all()


def create_piscina(db: Session, piscina_in: PiscinaCreate) -> Piscina:
    """Create a new pool."""
    db_obj = Piscina(
        codigo=piscina_in.codigo,
        ubicacion=piscina_in.ubicacion,
        area_m2=piscina_in.area_m2,
        profundidad=piscina_in.profundidad,
        estado=piscina_in.estado,
        fecha_inicio_ciclo=piscina_in.fecha_inicio_ciclo,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_piscina(
    db: Session, db_obj: Piscina, piscina_in: PiscinaUpdate
) -> Piscina:
    """Update an existing pool."""
    update_data = piscina_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_piscina(db: Session, piscina_id: int) -> Optional[Piscina]:
    """Delete a pool by ID."""
    db_obj = db.query(Piscina).filter(Piscina.id == piscina_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
