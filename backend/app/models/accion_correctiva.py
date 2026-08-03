from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.alerta import Alerta
    from app.models.usuario import Usuario


class AccionCorrectiva(Base, TimestampMixin):
    __tablename__ = "acciones_correctivas"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente', 'en_progreso', 'completada')",
            name="ck_acciones_estado",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_alerta: Mapped[int] = mapped_column(
        ForeignKey("alertas.id", ondelete="CASCADE")
    )
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT")
    )
    descripcion: Mapped[str] = mapped_column(Text)
    fecha_accion: Mapped[datetime] = mapped_column(server_default=func.now())
    resultado: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")

    @property
    def estado_cierre(self) -> str:
        return self.estado

    @estado_cierre.setter
    def estado_cierre(self, value: str) -> None:
        self.estado = value

    # Relationships
    alerta: Mapped["Alerta"] = relationship(back_populates="acciones_correctivas")
    usuario: Mapped["Usuario"] = relationship(back_populates="acciones_correctivas")
