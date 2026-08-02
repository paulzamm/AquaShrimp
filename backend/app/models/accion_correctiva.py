from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class AccionCorrectiva(Base, TimestampMixin):
    __tablename__ = "acciones_correctivas"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))

    usuario: Mapped["Usuario"] = relationship(back_populates="acciones_correctivas")
