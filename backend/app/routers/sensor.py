from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.sensor import SensorCreate, SensorResponse, SensorUpdate

router = APIRouter(prefix="/api/sensores", tags=["Sensores"])


@router.get("", response_model=List[SensorResponse])
def read_sensores(
    skip: int = 0,
    limit: int = 100,
    id_piscina: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Retrieve list of sensors with optional pool filtering."""
    return services.sensor.get_sensores(
        db, skip=skip, limit=limit, id_piscina=id_piscina
    )


@router.get("/{sensor_id}", response_model=SensorResponse)
def read_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Get a specific sensor by ID."""
    db_sensor = services.sensor.get_sensor(db, sensor_id=sensor_id)
    if not db_sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sensor no encontrado",
        )
    return db_sensor


@router.post("", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
def create_sensor(
    sensor_in: SensorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Técnico Acuícola"])
    ),
):
    """Create a new sensor (Requires Administrador or Técnico Acuícola role)."""
    db_piscina = services.piscina.get_piscina(db, piscina_id=sensor_in.id_piscina)
    if not db_piscina:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La piscina especificada no existe",
        )
    return services.sensor.create_sensor(db, sensor_in=sensor_in)


@router.put("/{sensor_id}", response_model=SensorResponse)
def update_sensor(
    sensor_id: int,
    sensor_in: SensorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["Administrador", "Técnico Acuícola"])
    ),
):
    """Update a sensor (Requires Administrador or Técnico Acuícola role)."""
    db_sensor = services.sensor.get_sensor(db, sensor_id=sensor_id)
    if not db_sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sensor no encontrado",
        )

    if sensor_in.id_piscina is not None:
        db_piscina = services.piscina.get_piscina(
            db, piscina_id=sensor_in.id_piscina
        )
        if not db_piscina:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La piscina especificada no existe",
            )

    return services.sensor.update_sensor(
        db, db_obj=db_sensor, sensor_in=sensor_in
    )


@router.delete("/{sensor_id}", response_model=SensorResponse)
def delete_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"])),
):
    """Delete a sensor (Requires Administrador role)."""
    db_sensor = services.sensor.get_sensor(db, sensor_id=sensor_id)
    if not db_sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sensor no encontrado",
        )
    return services.sensor.delete_sensor(db, sensor_id=sensor_id)
