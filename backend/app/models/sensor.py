from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.lectura_sensor import LecturaSensor
    from app.models.piscina import Piscina


class Sensor(Base, TimestampMixin):
    __tablename__ = "sensores"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('ph', 'oxigeno_disuelto', 'temperatura')",
            name="ck_sensores_tipo",
        ),
        CheckConstraint(
            "estado IN ('activo', 'inactivo', 'fallo')",
            name="ck_sensores_estado",
        ),
        Index("ix_sensores_piscina_tipo", "id_piscina", "tipo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_piscina: Mapped[int] = mapped_column(
        ForeignKey("piscinas.id", ondelete="CASCADE")
    )
    tipo: Mapped[str] = mapped_column(String(50))
    ubicacion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo")
    fecha_instalacion: Mapped[Optional[date]] = mapped_column(nullable=True)
    unidad_medida: Mapped[str] = mapped_column(String(20))

    # Relationships
    piscina: Mapped["Piscina"] = relationship(back_populates="sensores")
    lecturas: Mapped[list["LecturaSensor"]] = relationship(
        back_populates="sensor", cascade="all, delete-orphan"
    )
