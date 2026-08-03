from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.rol import RolCreate, RolResponse, RolUpdate

router = APIRouter(prefix="/api/roles", tags=["Roles"])


@router.get("", response_model=List[RolResponse])
def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Retrieve list of roles."""
    return services.rol.get_roles(db, skip=skip, limit=limit)


@router.get("/{rol_id}", response_model=RolResponse)
def read_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Get a specific role by ID."""
    db_rol = services.rol.get_rol(db, rol_id=rol_id)
    if not db_rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado",
        )
    return db_rol


@router.post("", response_model=RolResponse, status_code=status.HTTP_201_CREATED)
def create_rol(
    rol_in: RolCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Create a new role (Requires Administrador role)."""
    existing_rol = services.rol.get_rol_by_nombre(db, nombre_rol=rol_in.nombre_rol)
    if existing_rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un rol con ese nombre",
        )
    return services.rol.create_rol(db, rol_in=rol_in)


@router.put("/{rol_id}", response_model=RolResponse)
def update_rol(
    rol_id: int,
    rol_in: RolUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Update a role (Requires Administrador role)."""
    db_rol = services.rol.get_rol(db, rol_id=rol_id)
    if not db_rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado",
        )

    if rol_in.nombre_rol is not None and rol_in.nombre_rol != db_rol.nombre_rol:
        existing_rol = services.rol.get_rol_by_nombre(
            db, nombre_rol=rol_in.nombre_rol
        )
        if existing_rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un rol con ese nombre",
            )

    return services.rol.update_rol(db, db_obj=db_rol, rol_in=rol_in)


@router.delete("/{rol_id}", response_model=RolResponse)
def delete_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Delete a role (Requires Administrador role)."""
    db_rol = services.rol.get_rol(db, rol_id=rol_id)
    if not db_rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado",
        )
    return services.rol.delete_rol(db, rol_id=rol_id)
