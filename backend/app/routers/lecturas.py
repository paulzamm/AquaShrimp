from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.lectura_sensor import LecturaSensorCreate, LecturaSensorResponse

router = APIRouter(prefix="/api/lecturas", tags=["Lecturas"])


@router.get("", response_model=List[LecturaSensorResponse])
def read_lecturas(
    skip: int = 0,
    limit: int = 100,
    id_sensor: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Retrieve list of sensor readings."""
    return services.bpm.get_lecturas(db, skip=skip, limit=limit, id_sensor=id_sensor)


@router.get("/{lectura_id}", response_model=LecturaSensorResponse)
def read_lectura(
    lectura_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Get a specific reading by ID."""
    db_lectura = services.bpm.get_lectura(db, lectura_id=lectura_id)
    if not db_lectura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lectura no encontrada",
        )
    return db_lectura


@router.post("", response_model=LecturaSensorResponse, status_code=status.HTTP_201_CREATED)
def create_lectura(
    lectura_in: LecturaSensorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Ingest a sensor reading and execute the BPM engine (Alerts / Feeding Recommendations)."""
    return services.bpm.procesar_lectura(db, lectura_in=lectura_in)
