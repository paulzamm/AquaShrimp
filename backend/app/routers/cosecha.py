from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.cosecha import CosechaCreate, CosechaResponse, CosechaUpdate

router = APIRouter(prefix="/api/cosechas", tags=["Cosechas"])


@router.get("", response_model=List[CosechaResponse])
def read_cosechas(
    skip: int = 0,
    limit: int = 100,
    id_piscina: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Retrieve list of harvests."""
    return services.cosecha.get_cosechas(
        db, skip=skip, limit=limit, id_piscina=id_piscina
    )


@router.get("/{cosecha_id}", response_model=CosechaResponse)
def read_cosecha(
    cosecha_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Get a specific harvest by ID."""
    db_cosecha = services.cosecha.get_cosecha(db, cosecha_id=cosecha_id)
    if not db_cosecha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cosecha no encontrada",
        )
    return db_cosecha


@router.post("", response_model=CosechaResponse, status_code=status.HTTP_201_CREATED)
def create_cosecha(
    cosecha_in: CosechaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Técnico Acuícola"])
    ),
):
    """Create a new harvest (Requires Administrador or Técnico Acuícola role)."""
    piscina = services.piscina.get_piscina(db, piscina_id=cosecha_in.id_piscina)
    if not piscina:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Piscina no encontrada",
        )
    return services.cosecha.create_cosecha(db, cosecha_in=cosecha_in)


@router.put("/{cosecha_id}", response_model=CosechaResponse)
def update_cosecha(
    cosecha_id: int,
    cosecha_in: CosechaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Técnico Acuícola"])
    ),
):
    """Update a harvest (Requires Administrador or Técnico Acuícola role)."""
    db_cosecha = services.cosecha.get_cosecha(db, cosecha_id=cosecha_id)
    if not db_cosecha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cosecha no encontrada",
        )
    if cosecha_in.id_piscina:
        piscina = services.piscina.get_piscina(db, piscina_id=cosecha_in.id_piscina)
        if not piscina:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Piscina no encontrada",
            )
    return services.cosecha.update_cosecha(
        db, db_obj=db_cosecha, cosecha_in=cosecha_in
    )


@router.delete("/{cosecha_id}", response_model=CosechaResponse)
def delete_cosecha(
    cosecha_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Delete a harvest (Requires Administrador role)."""
    db_cosecha = services.cosecha.get_cosecha(db, cosecha_id=cosecha_id)
    if not db_cosecha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cosecha no encontrada",
        )
    return services.cosecha.delete_cosecha(db, cosecha_id=cosecha_id)
