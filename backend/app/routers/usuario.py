from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


@router.get("", response_model=List[UsuarioResponse])
def read_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Retrieve list of users (Requires Administrador role)."""
    return services.usuario.get_usuarios(db, skip=skip, limit=limit)


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def read_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Get a specific user by ID."""
    db_usuario = services.usuario.get_usuario(db, usuario_id=usuario_id)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return db_usuario


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(
    usuario_in: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Create a new user (Requires Administrador role)."""
    db_rol = services.rol.get_rol(db, rol_id=usuario_in.id_rol)
    if not db_rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol especificado no existe",
        )

    existing_user = services.usuario.get_usuario_by_correo(
        db, correo=usuario_in.correo
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )

    return services.usuario.create_usuario(db, usuario_in=usuario_in)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def update_usuario(
    usuario_id: int,
    usuario_in: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Update a user (Requires Administrador role)."""
    db_usuario = services.usuario.get_usuario(db, usuario_id=usuario_id)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    if usuario_in.id_rol is not None:
        db_rol = services.rol.get_rol(db, rol_id=usuario_in.id_rol)
        if not db_rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El rol especificado no existe",
            )

    if usuario_in.correo is not None and usuario_in.correo != db_usuario.correo:
        existing_user = services.usuario.get_usuario_by_correo(
            db, correo=usuario_in.correo
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado",
            )

    return services.usuario.update_usuario(
        db, db_obj=db_usuario, usuario_in=usuario_in
    )


@router.delete("/{usuario_id}", response_model=UsuarioResponse)
def delete_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Delete a user (Requires Administrador role)."""
    db_usuario = services.usuario.get_usuario(db, usuario_id=usuario_id)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return services.usuario.delete_usuario(db, usuario_id=usuario_id)
