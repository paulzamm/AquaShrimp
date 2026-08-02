from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Rol(Base, TimestampMixin):
    __tablename__ = "roles"
    __table_args__ = (
        CheckConstraint("estado IN ('activo', 'inactivo')", name="ck_roles_estado"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_rol: Mapped[str] = mapped_column(String(50), unique=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    permisos: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo")

    # Relationships
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")
