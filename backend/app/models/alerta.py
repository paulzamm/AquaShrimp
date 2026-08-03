from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.accion_correctiva import AccionCorrectiva
    from app.models.lectura_sensor import LecturaSensor
    from app.models.sensor import Sensor
    from app.models.usuario import Usuario


class Alerta(Base, TimestampMixin):
    __tablename__ = "alertas"
    __table_args__ = (
        CheckConstraint(
            "severidad IN ('baja', 'media', 'alta', 'critica')",
            name="ck_alertas_severidad",
        ),
        CheckConstraint(
            "estado IN ('activa', 'atendida', 'cerrada')",
            name="ck_alertas_estado",
        ),
        Index("ix_alertas_estado", "estado"),
        Index("ix_alertas_fecha_generacion", "fecha_generacion"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_lectura: Mapped[Optional[int]] = mapped_column(
        ForeignKey("lecturas_sensores.id", ondelete="CASCADE"), nullable=True
    )
    id_sensor: Mapped[Optional[int]] = mapped_column(
        ForeignKey("sensores.id", ondelete="CASCADE"), nullable=True
    )
    id_usuario: Mapped[Optional[int]] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    tipo_alerta: Mapped[str] = mapped_column(String(50))
    severidad: Mapped[str] = mapped_column(String(20))
    descripcion: Mapped[str] = mapped_column(Text)
    fecha_generacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    estado: Mapped[str] = mapped_column(String(20), default="activa")

    @property
    def gravedad(self) -> str:
        return self.severidad

    @gravedad.setter
    def gravedad(self, value: str) -> None:
        self.severidad = value

    # Relationships
    lectura: Mapped[Optional["LecturaSensor"]] = relationship(back_populates="alertas")
    sensor: Mapped[Optional["Sensor"]] = relationship(back_populates="alertas")
    usuario: Mapped[Optional["Usuario"]] = relationship(back_populates="alertas")
