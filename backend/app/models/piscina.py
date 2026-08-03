from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.cosecha import Cosecha
    from app.models.recomendacion_alimentacion import RecomendacionAlimentacion
    from app.models.sensor import Sensor


class Piscina(Base, TimestampMixin):
    __tablename__ = "piscinas"
    __table_args__ = (
        CheckConstraint("area_m2 > 0", name="ck_piscinas_area_positiva"),
        CheckConstraint("profundidad > 0", name="ck_piscinas_profundidad_positiva"),
        CheckConstraint(
            "estado IN ('activa', 'inactiva', 'mantenimiento')",
            name="ck_piscinas_estado",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    ubicacion: Mapped[str] = mapped_column(String(200))
    area_m2: Mapped[float] = mapped_column(Float)
    profundidad: Mapped[float] = mapped_column(Float)
    estado: Mapped[str] = mapped_column(String(20), default="activa")
    fecha_inicio_ciclo: Mapped[Optional[date]] = mapped_column(nullable=True)

    # Relationships
    sensores: Mapped[list["Sensor"]] = relationship(
        back_populates="piscina", cascade="all, delete-orphan"
    )
    recomendaciones_alimentacion: Mapped[list["RecomendacionAlimentacion"]] = relationship(
        back_populates="piscina", cascade="all, delete-orphan"
    )
    cosechas: Mapped[list["Cosecha"]] = relationship(
        back_populates="piscina", cascade="all, delete-orphan"
    )

    @property
    def recomendaciones(self) -> list["RecomendacionAlimentacion"]:
        return self.recomendaciones_alimentacion
