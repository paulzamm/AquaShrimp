from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.piscina import PiscinaCreate, PiscinaResponse, PiscinaUpdate

router = APIRouter(prefix="/api/piscinas", tags=["Piscinas"])


@router.get("", response_model=List[PiscinaResponse])
def read_piscinas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Retrieve list of pools."""
    return services.piscina.get_piscinas(db, skip=skip, limit=limit)


@router.get("/{piscina_id}", response_model=PiscinaResponse)
def read_piscina(
    piscina_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Get a specific pool by ID."""
    db_piscina = services.piscina.get_piscina(db, piscina_id=piscina_id)
    if not db_piscina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Piscina no encontrada",
        )
    return db_piscina


@router.post("", response_model=PiscinaResponse, status_code=status.HTTP_201_CREATED)
def create_piscina(
    piscina_in: PiscinaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Técnico Acuícola"])
    ),
):
    """Create a new pool (Requires Administrador or Técnico Acuícola role)."""
    existing_piscina = services.piscina.get_piscina_by_codigo(
        db, codigo=piscina_in.codigo
    )
    if existing_piscina:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una piscina con ese código",
        )
    return services.piscina.create_piscina(db, piscina_in=piscina_in)


@router.put("/{piscina_id}", response_model=PiscinaResponse)
def update_piscina(
    piscina_id: int,
    piscina_in: PiscinaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Técnico Acuícola"])
    ),
):
    """Update a pool (Requires Administrador or Técnico Acuícola role)."""
    db_piscina = services.piscina.get_piscina(db, piscina_id=piscina_id)
    if not db_piscina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Piscina no encontrada",
        )

    if (
        piscina_in.codigo is not None
        and piscina_in.codigo != db_piscina.codigo
    ):
        existing_piscina = services.piscina.get_piscina_by_codigo(
            db, codigo=piscina_in.codigo
        )
        if existing_piscina:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una piscina con ese código",
            )

    return services.piscina.update_piscina(
        db, db_obj=db_piscina, piscina_in=piscina_in
    )


@router.delete("/{piscina_id}", response_model=PiscinaResponse)
def delete_piscina(
    piscina_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Delete a pool (Requires Administrador role)."""
    db_piscina = services.piscina.get_piscina(db, piscina_id=piscina_id)
    if not db_piscina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Piscina no encontrada",
        )
    return services.piscina.delete_piscina(db, piscina_id=piscina_id)
