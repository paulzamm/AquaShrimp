from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.sensor import Sensor


class LecturaSensor(Base, TimestampMixin):
    __tablename__ = "lecturas_sensores"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_sensor: Mapped[Optional[int]] = mapped_column(
        ForeignKey("sensores.id", ondelete="CASCADE"), nullable=True
    )

    sensor: Mapped[Optional["Sensor"]] = relationship(back_populates="lecturas")
