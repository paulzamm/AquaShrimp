from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.recomendacion_alimentacion import (
    RecomendacionAlimentacionCreate,
    RecomendacionAlimentacionResponse,
    RecomendacionAlimentacionUpdate,
)

router = APIRouter(
    prefix="/api/recomendaciones-alimentacion", tags=["Recomendaciones de Alimentación"]
)


@router.get("", response_model=List[RecomendacionAlimentacionResponse])
def read_recomendaciones(
    skip: int = 0,
    limit: int = 100,
    id_piscina: Optional[int] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Retrieve list of feeding recommendations."""
    return services.recomendacion_alimentacion.get_recomendaciones(
        db, skip=skip, limit=limit, id_piscina=id_piscina, estado=estado
    )


@router.get("/{recomendacion_id}", response_model=RecomendacionAlimentacionResponse)
def read_recomendacion(
    recomendacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Get a specific feeding recommendation by ID."""
    db_recomendacion = services.recomendacion_alimentacion.get_recomendacion(
        db, recomendacion_id=recomendacion_id
    )
    if not db_recomendacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recomendación de alimentación no encontrada",
        )
    return db_recomendacion


@router.post(
    "", response_model=RecomendacionAlimentacionResponse, status_code=status.HTTP_201_CREATED
)
def create_recomendacion(
    recomendacion_in: RecomendacionAlimentacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Técnico Acuícola"])
    ),
):
    """Create a new feeding recommendation (Requires Administrador or Técnico Acuícola role)."""
    piscina = services.piscina.get_piscina(db, piscina_id=recomendacion_in.id_piscina)
    if not piscina:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Piscina no encontrada",
        )
    if recomendacion_in.id_usuario is not None:
        usuario = services.usuario.get_usuario(db, usuario_id=recomendacion_in.id_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no encontrado",
            )
    return services.recomendacion_alimentacion.create_recomendacion(
        db, recomendacion_in=recomendacion_in
    )


@router.put("/{recomendacion_id}", response_model=RecomendacionAlimentacionResponse)
def update_recomendacion(
    recomendacion_id: int,
    recomendacion_in: RecomendacionAlimentacionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Técnico Acuícola"])
    ),
):
    """Update a feeding recommendation (Requires Administrador or Técnico Acuícola role)."""
    db_recomendacion = services.recomendacion_alimentacion.get_recomendacion(
        db, recomendacion_id=recomendacion_id
    )
    if not db_recomendacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recomendación de alimentación no encontrada",
        )
    if recomendacion_in.id_piscina is not None:
        piscina = services.piscina.get_piscina(
            db, piscina_id=recomendacion_in.id_piscina
        )
        if not piscina:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Piscina no encontrada",
            )
    if recomendacion_in.id_usuario is not None:
        usuario = services.usuario.get_usuario(db, usuario_id=recomendacion_in.id_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no encontrado",
            )
    return services.recomendacion_alimentacion.update_recomendacion(
        db, db_obj=db_recomendacion, recomendacion_in=recomendacion_in
    )


@router.delete("/{recomendacion_id}", response_model=RecomendacionAlimentacionResponse)
def delete_recomendacion(
    recomendacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Delete a feeding recommendation (Requires Administrador role)."""
    db_recomendacion = services.recomendacion_alimentacion.get_recomendacion(
        db, recomendacion_id=recomendacion_id
    )
    if not db_recomendacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recomendación de alimentación no encontrada",
        )
    return services.recomendacion_alimentacion.delete_recomendacion(
        db, recomendacion_id=recomendacion_id
    )
