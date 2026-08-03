from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.rol import Rol
from app.schemas.rol import RolCreate, RolUpdate


def get_rol(db: Session, rol_id: int) -> Optional[Rol]:
    """Retrieve a single role by ID."""
    return db.query(Rol).filter(Rol.id == rol_id).first()


def get_rol_by_nombre(db: Session, nombre_rol: str) -> Optional[Rol]:
    """Retrieve a single role by name."""
    return db.query(Rol).filter(Rol.nombre_rol == nombre_rol).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Rol]:
    """Retrieve multiple roles with pagination."""
    return db.query(Rol).offset(skip).limit(limit).all()


def create_rol(db: Session, rol_in: RolCreate) -> Rol:
    """Create a new role."""
    db_obj = Rol(
        nombre_rol=rol_in.nombre_rol,
        descripcion=rol_in.descripcion,
        permisos=rol_in.permisos,
        estado=rol_in.estado,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_rol(db: Session, db_obj: Rol, rol_in: RolUpdate) -> Rol:
    """Update an existing role."""
    update_data = rol_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_rol(db: Session, rol_id: int) -> Optional[Rol]:
    """Delete a role by ID."""
    db_obj = db.query(Rol).filter(Rol.id == rol_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
