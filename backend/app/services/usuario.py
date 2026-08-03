from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


def get_usuario(db: Session, usuario_id: int) -> Optional[Usuario]:
    """Retrieve a single user by ID."""
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def get_usuario_by_correo(db: Session, correo: str) -> Optional[Usuario]:
    """Retrieve a single user by email."""
    return db.query(Usuario).filter(Usuario.correo == correo).first()


def get_usuarios(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
    """Retrieve multiple users with pagination."""
    return db.query(Usuario).offset(skip).limit(limit).all()


def create_usuario(db: Session, usuario_in: UsuarioCreate) -> Usuario:
    """Create a new user, hashing the plain password."""
    contrasena_hash = get_password_hash(usuario_in.contrasena)
    db_obj = Usuario(
        id_rol=usuario_in.id_rol,
        nombre=usuario_in.nombre,
        correo=usuario_in.correo,
        contrasena_hash=contrasena_hash,
        estado=usuario_in.estado,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_usuario(
    db: Session, db_obj: Usuario, usuario_in: UsuarioUpdate
) -> Usuario:
    """Update an existing user, re-hashing password if provided."""
    update_data = usuario_in.model_dump(exclude_unset=True)
    if "contrasena" in update_data:
        raw_password = update_data.pop("contrasena")
        if raw_password:
            db_obj.contrasena_hash = get_password_hash(raw_password)

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_usuario(db: Session, usuario_id: int) -> Optional[Usuario]:
    """Delete a user by ID."""
    db_obj = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
