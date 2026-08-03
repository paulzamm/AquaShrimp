from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class ReporteGerencial(Base, TimestampMixin):
    __tablename__ = "reportes_gerenciales"
    __table_args__ = (
        CheckConstraint(
            "periodo_fin >= periodo_inicio",
            name="ck_reportes_periodo_valido",
        ),
        CheckConstraint(
            "tipo_reporte IN ('rendimiento', 'alertas', 'alimentacion')",
            name="ck_reportes_tipo",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT")
    )
    tipo_reporte: Mapped[str] = mapped_column(String(50))
    periodo_inicio: Mapped[date] = mapped_column()
    periodo_fin: Mapped[date] = mapped_column()
    fecha_generacion: Mapped[datetime] = mapped_column(server_default=func.now())
    ruta_archivo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    usuario: Mapped["Usuario"] = relationship(back_populates="reportes_gerenciales")
