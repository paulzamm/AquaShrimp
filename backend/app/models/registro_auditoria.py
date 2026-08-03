from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class RegistroAuditoria(Base):
    __tablename__ = "registros_auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[Optional[int]] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    accion: Mapped[str] = mapped_column(String(100), nullable=False)
    tabla_afectada: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    registro_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    detalles: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_origen: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )

    # Relationships
    usuario: Mapped[Optional["Usuario"]] = relationship(
        back_populates="registros_auditoria"
    )
