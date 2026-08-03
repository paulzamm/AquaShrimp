from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.alerta import AlertaCreate, AlertaResponse, AlertaUpdate

router = APIRouter(prefix="/api/alertas", tags=["Alertas"])


@router.get("", response_model=List[AlertaResponse])
def read_alertas(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    severidad: Optional[str] = None,
    id_sensor: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Retrieve list of alerts."""
    return services.alerta.get_alertas(
        db,
        skip=skip,
        limit=limit,
        estado=estado,
        severidad=severidad,
        id_sensor=id_sensor,
    )


@router.get("/{alerta_id}", response_model=AlertaResponse)
def read_alerta(
    alerta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Get a specific alert by ID."""
    db_alerta = services.alerta.get_alerta(db, alerta_id=alerta_id)
    if not db_alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada",
        )
    return db_alerta


@router.post("", response_model=AlertaResponse, status_code=status.HTTP_201_CREATED)
def create_alerta(
    alerta_in: AlertaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Operador", "Biologo"])
    ),
):
    """Create a new alert (Requires Administrador, Operador, or Biologo role)."""
    if alerta_in.id_sensor:
        sensor = services.sensor.get_sensor(db, sensor_id=alerta_in.id_sensor)
        if not sensor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sensor no encontrado",
            )
    if alerta_in.id_usuario:
        user = services.usuario.get_usuario(db, usuario_id=alerta_in.id_usuario)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no encontrado",
            )
    return services.alerta.create_alerta(db, alerta_in=alerta_in)


@router.put("/{alerta_id}", response_model=AlertaResponse)
def update_alerta(
    alerta_id: int,
    alerta_in: AlertaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Operador", "Biologo"])
    ),
):
    """Update an alert (Requires Administrador, Operador, or Biologo role)."""
    db_alerta = services.alerta.get_alerta(db, alerta_id=alerta_id)
    if not db_alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada",
        )
    if alerta_in.id_sensor:
        sensor = services.sensor.get_sensor(db, sensor_id=alerta_in.id_sensor)
        if not sensor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sensor no encontrado",
            )
    if alerta_in.id_usuario:
        user = services.usuario.get_usuario(db, usuario_id=alerta_in.id_usuario)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no encontrado",
            )
    return services.alerta.update_alerta(db, db_obj=db_alerta, alerta_in=alerta_in)


@router.delete("/{alerta_id}", response_model=AlertaResponse)
def delete_alerta(
    alerta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Delete an alert (Requires Administrador role)."""
    db_alerta = services.alerta.get_alerta(db, alerta_id=alerta_id)
    if not db_alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada",
        )
    return services.alerta.delete_alerta(db, alerta_id=alerta_id)
