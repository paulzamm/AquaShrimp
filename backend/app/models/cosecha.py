from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.piscina import Piscina


class Cosecha(Base, TimestampMixin):
    __tablename__ = "cosechas"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_piscina: Mapped[Optional[int]] = mapped_column(
        ForeignKey("piscinas.id", ondelete="CASCADE"), nullable=True
    )

    piscina: Mapped[Optional["Piscina"]] = relationship(back_populates="cosechas")
