from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.reporte_gerencial import (
    ReporteGerencialCreate,
    ReporteGerencialResponse,
    ReporteGerencialUpdate,
)

router = APIRouter(
    prefix="/api/reportes-gerenciales", tags=["Reportes Gerenciales"]
)


@router.get("", response_model=List[ReporteGerencialResponse])
def read_reportes_gerenciales(
    skip: int = 0,
    limit: int = 100,
    tipo_reporte: Optional[str] = None,
    id_usuario: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Retrieve list of managerial reports."""
    return services.reporte_gerencial.get_reportes_gerenciales(
        db,
        skip=skip,
        limit=limit,
        tipo_reporte=tipo_reporte,
        id_usuario=id_usuario,
    )


@router.get("/{reporte_id}", response_model=ReporteGerencialResponse)
def read_reporte_gerencial(
    reporte_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Get a specific managerial report by ID."""
    db_reporte = services.reporte_gerencial.get_reporte_gerencial(
        db, reporte_id=reporte_id
    )
    if not db_reporte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte gerencial no encontrado",
        )
    return db_reporte


@router.post(
    "", response_model=ReporteGerencialResponse, status_code=status.HTTP_201_CREATED
)
def create_reporte_gerencial(
    reporte_in: ReporteGerencialCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Gerencia", "Técnico Acuícola"])
    ),
):
    """Create a new managerial report (Requires Administrador, Gerencia, or Técnico Acuícola role)."""
    usuario = services.usuario.get_usuario(db, usuario_id=reporte_in.id_usuario)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado",
        )
    return services.reporte_gerencial.create_reporte_gerencial(
        db, reporte_in=reporte_in
    )


@router.put("/{reporte_id}", response_model=ReporteGerencialResponse)
def update_reporte_gerencial(
    reporte_id: int,
    reporte_in: ReporteGerencialUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Gerencia", "Técnico Acuícola"])
    ),
):
    """Update a managerial report (Requires Administrador, Gerencia, or Técnico Acuícola role)."""
    db_reporte = services.reporte_gerencial.get_reporte_gerencial(
        db, reporte_id=reporte_id
    )
    if not db_reporte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte gerencial no encontrado",
        )
    if reporte_in.id_usuario:
        usuario = services.usuario.get_usuario(db, usuario_id=reporte_in.id_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no encontrado",
            )
    return services.reporte_gerencial.update_reporte_gerencial(
        db, db_obj=db_reporte, reporte_in=reporte_in
    )


@router.delete("/{reporte_id}", response_model=ReporteGerencialResponse)
def delete_reporte_gerencial(
    reporte_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Delete a managerial report (Requires Administrador role)."""
    db_reporte = services.reporte_gerencial.get_reporte_gerencial(
        db, reporte_id=reporte_id
    )
    if not db_reporte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte gerencial no encontrado",
        )
    return services.reporte_gerencial.delete_reporte_gerencial(
        db, reporte_id=reporte_id
    )
