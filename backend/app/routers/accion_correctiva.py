from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.accion_correctiva import (
    AccionCorrectivaCreate,
    AccionCorrectivaResponse,
    AccionCorrectivaUpdate,
)

router = APIRouter(prefix="/api/acciones-correctivas", tags=["Acciones Correctivas"])


@router.get("", response_model=List[AccionCorrectivaResponse])
def read_acciones_correctivas(
    skip: int = 0,
    limit: int = 100,
    id_alerta: Optional[int] = None,
    id_usuario: Optional[int] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Retrieve list of corrective actions."""
    return services.accion_correctiva.get_acciones_correctivas(
        db,
        skip=skip,
        limit=limit,
        id_alerta=id_alerta,
        id_usuario=id_usuario,
        estado=estado,
    )


@router.get("/{accion_id}", response_model=AccionCorrectivaResponse)
def read_accion_correctiva(
    accion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Get a specific corrective action by ID."""
    db_accion = services.accion_correctiva.get_accion_correctiva(
        db, accion_id=accion_id
    )
    if not db_accion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Acción correctiva no encontrada",
        )
    return db_accion


@router.post(
    "", response_model=AccionCorrectivaResponse, status_code=status.HTTP_201_CREATED
)
def create_accion_correctiva(
    accion_in: AccionCorrectivaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Operador", "Biologo"])
    ),
):
    """Create a new corrective action (Requires Administrador, Operador, or Biologo role)."""
    alerta = services.alerta.get_alerta(db, alerta_id=accion_in.id_alerta)
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alerta no encontrada",
        )
    usuario = services.usuario.get_usuario(db, usuario_id=accion_in.id_usuario)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado",
        )
    return services.accion_correctiva.create_accion_correctiva(db, accion_in=accion_in)


@router.put("/{accion_id}", response_model=AccionCorrectivaResponse)
def update_accion_correctiva(
    accion_id: int,
    accion_in: AccionCorrectivaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Operador", "Biologo"])
    ),
):
    """Update a corrective action (Requires Administrador, Operador, or Biologo role)."""
    db_accion = services.accion_correctiva.get_accion_correctiva(
        db, accion_id=accion_id
    )
    if not db_accion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Acción correctiva no encontrada",
        )
    if accion_in.id_alerta:
        alerta = services.alerta.get_alerta(db, alerta_id=accion_in.id_alerta)
        if not alerta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alerta no encontrada",
            )
    if accion_in.id_usuario:
        usuario = services.usuario.get_usuario(db, usuario_id=accion_in.id_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no encontrado",
            )
    return services.accion_correctiva.update_accion_correctiva(
        db, db_obj=db_accion, accion_in=accion_in
    )


@router.delete("/{accion_id}", response_model=AccionCorrectivaResponse)
def delete_accion_correctiva(
    accion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Delete a corrective action (Requires Administrador role)."""
    db_accion = services.accion_correctiva.get_accion_correctiva(
        db, accion_id=accion_id
    )
    if not db_accion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Acción correctiva no encontrada",
        )
    return services.accion_correctiva.delete_accion_correctiva(
        db, accion_id=accion_id
    )
