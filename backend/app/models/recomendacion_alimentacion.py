from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.piscina import Piscina
    from app.models.usuario import Usuario


class RecomendacionAlimentacion(Base, TimestampMixin):
    __tablename__ = "recomendaciones_alimentacion"
    __table_args__ = (
        CheckConstraint(
            "cantidad_kg > 0", name="ck_recomendaciones_cantidad_positiva"
        ),
        CheckConstraint(
            "estado IN ('pendiente', 'aplicada', 'descartada')",
            name="ck_recomendaciones_estado",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_piscina: Mapped[int] = mapped_column(
        ForeignKey("piscinas.id", ondelete="CASCADE")
    )
    id_usuario: Mapped[Optional[int]] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True
    )
    cantidad_kg: Mapped[float] = mapped_column(Float)
    frecuencia: Mapped[str] = mapped_column(String(50))
    criterio: Mapped[str] = mapped_column(Text)
    fecha_generacion: Mapped[datetime] = mapped_column(server_default=func.now())
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")

    # Relationships
    piscina: Mapped["Piscina"] = relationship(back_populates="recomendaciones")
    usuario: Mapped[Optional["Usuario"]] = relationship(
        back_populates="recomendaciones"
    )
