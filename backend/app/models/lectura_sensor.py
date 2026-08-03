from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.alerta import Alerta
    from app.models.sensor import Sensor


class LecturaSensor(Base, TimestampMixin):
    __tablename__ = "lecturas_sensores"
    __table_args__ = (
        CheckConstraint(
            "estado_validacion IN ('pendiente', 'valida', 'invalida')",
            name="ck_lecturas_estado_validacion",
        ),
        Index("ix_lecturas_sensor_fecha", "id_sensor", "fecha_hora"),
        Index("ix_lecturas_fecha_hora", "fecha_hora"),
        Index("ix_lecturas_id_sensor", "id_sensor"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_sensor: Mapped[int] = mapped_column(
        ForeignKey("sensores.id", ondelete="CASCADE")
    )
    valor: Mapped[float] = mapped_column(Float)
    unidad: Mapped[str] = mapped_column(String(20))
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    estado_validacion: Mapped[str] = mapped_column(
        String(20), default="pendiente"
    )
    observacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    sensor: Mapped["Sensor"] = relationship(back_populates="lecturas")
    alertas: Mapped[list["Alerta"]] = relationship(
        back_populates="lectura", cascade="all, delete-orphan"
    )
