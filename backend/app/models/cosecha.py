from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.piscina import Piscina


class Cosecha(Base, TimestampMixin):
    __tablename__ = "cosechas"
    __table_args__ = (
        CheckConstraint("biomasa_kg > 0", name="ck_cosechas_biomasa_positiva"),
        CheckConstraint(
            "talla_promedio > 0 OR talla_promedio IS NULL",
            name="ck_cosechas_talla_positiva",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_piscina: Mapped[int] = mapped_column(
        ForeignKey("piscinas.id", ondelete="CASCADE")
    )
    fecha_cosecha: Mapped[date] = mapped_column()
    biomasa_kg: Mapped[float] = mapped_column(Float)
    talla_promedio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rendimiento: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    piscina: Mapped["Piscina"] = relationship(back_populates="cosechas")

    @property
    def biomasa_total_kg(self) -> float:
        return self.biomasa_kg

    @biomasa_total_kg.setter
    def biomasa_total_kg(self, value: float) -> None:
        self.biomasa_kg = value

    @property
    def peso_promedio_gramos(self) -> Optional[float]:
        return self.talla_promedio

    @peso_promedio_gramos.setter
    def peso_promedio_gramos(self, value: Optional[float]) -> None:
        self.talla_promedio = value
