from app.schemas.accion_correctiva import (
    AccionCorrectivaBase,
    AccionCorrectivaCreate,
    AccionCorrectivaResponse,
    AccionCorrectivaUpdate,
)
from app.schemas.alerta import (
    AlertaBase,
    AlertaCreate,
    AlertaResponse,
    AlertaUpdate,
)
from app.schemas.cosecha import (
    CosechaBase,
    CosechaCreate,
    CosechaResponse,
    CosechaUpdate,
)
from app.schemas.lectura_sensor import (
    LecturaSensorBase,
    LecturaSensorCreate,
    LecturaSensorResponse,
    LecturaSensorUpdate,
)
from app.schemas.piscina import (
    PiscinaBase,
    PiscinaCreate,
    PiscinaResponse,
    PiscinaUpdate,
)
from app.schemas.recomendacion_alimentacion import (
    RecomendacionAlimentacionBase,
    RecomendacionAlimentacionCreate,
    RecomendacionAlimentacionResponse,
    RecomendacionAlimentacionUpdate,
)
from app.schemas.registro_auditoria import (
    RegistroAuditoriaBase,
    RegistroAuditoriaCreate,
    RegistroAuditoriaResponse,
    RegistroAuditoriaUpdate,
)
from app.schemas.reporte_gerencial import (
    ReporteGerencialBase,
    ReporteGerencialCreate,
    ReporteGerencialResponse,
    ReporteGerencialUpdate,
)
from app.schemas.rol import (
    RolBase,
    RolCreate,
    RolResponse,
    RolUpdate,
)
from app.schemas.sensor import (
    SensorBase,
    SensorCreate,
    SensorResponse,
    SensorUpdate,
)
from app.schemas.usuario import (
    UsuarioBase,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)

__all__ = [
    "RolBase",
    "RolCreate",
    "RolUpdate",
    "RolResponse",
    "UsuarioBase",
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioResponse",
    "PiscinaBase",
    "PiscinaCreate",
    "PiscinaUpdate",
    "PiscinaResponse",
    "SensorBase",
    "SensorCreate",
    "SensorUpdate",
    "SensorResponse",
    "LecturaSensorBase",
    "LecturaSensorCreate",
    "LecturaSensorUpdate",
    "LecturaSensorResponse",
    "AlertaBase",
    "AlertaCreate",
    "AlertaUpdate",
    "AlertaResponse",
    "AccionCorrectivaBase",
    "AccionCorrectivaCreate",
    "AccionCorrectivaUpdate",
    "AccionCorrectivaResponse",
    "RecomendacionAlimentacionBase",
    "RecomendacionAlimentacionCreate",
    "RecomendacionAlimentacionUpdate",
    "RecomendacionAlimentacionResponse",
    "CosechaBase",
    "CosechaCreate",
    "CosechaUpdate",
    "CosechaResponse",
    "ReporteGerencialBase",
    "ReporteGerencialCreate",
    "ReporteGerencialUpdate",
    "ReporteGerencialResponse",
    "RegistroAuditoriaBase",
    "RegistroAuditoriaCreate",
    "RegistroAuditoriaUpdate",
    "RegistroAuditoriaResponse",
]
