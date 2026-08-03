from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.accion_correctiva import AccionCorrectiva
    from app.models.alerta import Alerta
    from app.models.recomendacion_alimentacion import RecomendacionAlimentacion
    from app.models.reporte_gerencial import ReporteGerencial
    from app.models.rol import Rol


class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('activo', 'inactivo', 'suspendido')",
            name="ck_usuarios_estado",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_rol: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    nombre: Mapped[str] = mapped_column(String(100))
    correo: Mapped[str] = mapped_column(String(150), unique=True)
    contrasena_hash: Mapped[str] = mapped_column(String(255))
    estado: Mapped[str] = mapped_column(String(20), default="activo")
    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    rol: Mapped["Rol"] = relationship(back_populates="usuarios")
    alertas: Mapped[list["Alerta"]] = relationship(back_populates="usuario")
    acciones_correctivas: Mapped[list["AccionCorrectiva"]] = relationship(
        back_populates="usuario"
    )
    recomendaciones: Mapped[list["RecomendacionAlimentacion"]] = relationship(
        back_populates="usuario"
    )
    reportes: Mapped[list["ReporteGerencial"]] = relationship(
        back_populates="usuario"
    )
