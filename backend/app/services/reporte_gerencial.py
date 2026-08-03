from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.reporte_gerencial import ReporteGerencial
from app.schemas.reporte_gerencial import (
    ReporteGerencialCreate,
    ReporteGerencialUpdate,
)


def get_reporte_gerencial(
    db: Session, reporte_id: int
) -> Optional[ReporteGerencial]:
    """Retrieve a single managerial report by ID."""
    return db.query(ReporteGerencial).filter(ReporteGerencial.id == reporte_id).first()


def get_reportes_gerenciales(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    tipo_reporte: Optional[str] = None,
    id_usuario: Optional[int] = None,
) -> List[ReporteGerencial]:
    """Retrieve multiple managerial reports with pagination and optional filters."""
    query = db.query(ReporteGerencial)
    if tipo_reporte:
        query = query.filter(ReporteGerencial.tipo_reporte == tipo_reporte)
    if id_usuario:
        query = query.filter(ReporteGerencial.id_usuario == id_usuario)
    return query.offset(skip).limit(limit).all()


def create_reporte_gerencial(
    db: Session, reporte_in: ReporteGerencialCreate
) -> ReporteGerencial:
    """Create a new managerial report."""
    data = reporte_in.model_dump(exclude_unset=True)
    valid_fields = {
        "id_usuario",
        "tipo_reporte",
        "periodo_inicio",
        "periodo_fin",
        "fecha_generacion",
        "ruta_archivo",
    }
    create_data = {k: v for k, v in data.items() if k in valid_fields}
    db_obj = ReporteGerencial(**create_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_reporte_gerencial(
    db: Session, db_obj: ReporteGerencial, reporte_in: ReporteGerencialUpdate
) -> ReporteGerencial:
    """Update an existing managerial report."""
    update_data = reporte_in.model_dump(exclude_unset=True)
    valid_fields = {
        "id_usuario",
        "tipo_reporte",
        "periodo_inicio",
        "periodo_fin",
        "fecha_generacion",
        "ruta_archivo",
    }
    for field, value in update_data.items():
        if field in valid_fields:
            setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_reporte_gerencial(
    db: Session, reporte_id: int
) -> Optional[ReporteGerencial]:
    """Delete a managerial report by ID."""
    db_obj = db.query(ReporteGerencial).filter(ReporteGerencial.id == reporte_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
