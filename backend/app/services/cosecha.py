from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.cosecha import Cosecha
from app.schemas.cosecha import CosechaCreate, CosechaUpdate


def get_cosecha(db: Session, cosecha_id: int) -> Optional[Cosecha]:
    """Retrieve a single harvest by ID."""
    return db.query(Cosecha).filter(Cosecha.id == cosecha_id).first()


def get_cosechas(
    db: Session, skip: int = 0, limit: int = 100, id_piscina: Optional[int] = None
) -> List[Cosecha]:
    """Retrieve multiple harvests with pagination and optional pool filter."""
    query = db.query(Cosecha)
    if id_piscina:
        query = query.filter(Cosecha.id_piscina == id_piscina)
    return query.offset(skip).limit(limit).all()


def create_cosecha(db: Session, cosecha_in: CosechaCreate) -> Cosecha:
    """Create a new harvest."""
    data = cosecha_in.model_dump(exclude_unset=True)
    if "biomasa_total_kg" in data and ("biomasa_kg" not in data or data["biomasa_kg"] == 0.0):
        data["biomasa_kg"] = data.pop("biomasa_total_kg")
    if "peso_promedio_gramos" in data and ("talla_promedio" not in data or data["talla_promedio"] is None):
        data["talla_promedio"] = data.pop("peso_promedio_gramos")

    valid_fields = {
        "id_piscina",
        "fecha_cosecha",
        "biomasa_kg",
        "talla_promedio",
        "rendimiento",
        "observaciones",
    }
    create_data = {k: v for k, v in data.items() if k in valid_fields}
    db_obj = Cosecha(**create_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_cosecha(
    db: Session, db_obj: Cosecha, cosecha_in: CosechaUpdate
) -> Cosecha:
    """Update an existing harvest."""
    update_data = cosecha_in.model_dump(exclude_unset=True)
    if "biomasa_total_kg" in update_data and "biomasa_kg" not in update_data:
        update_data["biomasa_kg"] = update_data.pop("biomasa_total_kg")
    if "peso_promedio_gramos" in update_data and "talla_promedio" not in update_data:
        update_data["talla_promedio"] = update_data.pop("peso_promedio_gramos")

    valid_fields = {
        "id_piscina",
        "fecha_cosecha",
        "biomasa_kg",
        "talla_promedio",
        "rendimiento",
        "observaciones",
    }
    for field, value in update_data.items():
        if field in valid_fields:
            setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_cosecha(db: Session, cosecha_id: int) -> Optional[Cosecha]:
    """Delete a harvest by ID."""
    db_obj = db.query(Cosecha).filter(Cosecha.id == cosecha_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
