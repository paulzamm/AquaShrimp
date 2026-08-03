import json
import logging
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.database import SessionLocal
from app.models.registro_auditoria import RegistroAuditoria

logger = logging.getLogger(__name__)


def infer_tabla_afectada(path: str) -> str:
    """Infer the target database table/entity based on the request URL path."""
    parts = [p for p in path.strip("/").split("/") if p]
    if len(parts) >= 2 and parts[0].lower() == "api":
        table = parts[1].lower().replace("-", "_")
        # special cases
        if table == "lecturas": return "lecturas_sensores"
        if table == "reportes": return "reportes_gerenciales"
        if table == "auth": return "usuarios"
        return table
    return "general"


def extract_registro_id(path: str) -> Optional[int]:
    """Extract integer resource ID from URL path if present (e.g. /api/piscinas/5)."""
    parts = [p for p in path.strip("/").split("/") if p]
    for part in reversed(parts):
        if part.isdigit():
            return int(part)
    return None


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that intercepts mutating HTTP requests (POST, PUT, DELETE, PATCH)
    and records audit logs into the database (registros_auditoria)."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in ("POST", "PUT", "DELETE", "PATCH"):
            return await call_next(request)

        response = await call_next(request)

        # Audit only successful mutating requests (200 <= status_code < 300)
        if 200 <= response.status_code < 300:
            try:
                # 1. Get authenticated user ID if present on request.state
                user = getattr(request.state, "user", None)
                id_usuario = user.id if user and hasattr(user, "id") else None

                # 2. Action description
                accion = f"{request.method} {request.url.path}"

                # 3. Affected table/entity
                tabla_afectada = infer_tabla_afectada(request.url.path)

                # 4. Optional registro_id from path
                registro_id = extract_registro_id(request.url.path)

                # 5. Client IP address
                client_ip = request.client.host if request.client else None
                x_forwarded_for = request.headers.get("x-forwarded-for")
                if x_forwarded_for:
                    ip_origen = x_forwarded_for.split(",")[0].strip()
                else:
                    ip_origen = client_ip or "127.0.0.1"

                # 6. Details payload
                detalles_dict = {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "ip_origen": ip_origen,
                }
                detalles = json.dumps(detalles_dict, ensure_ascii=False)

                # Always use a new SessionLocal to avoid reusing a closed session
                db_session = SessionLocal()
                try:
                    registro = RegistroAuditoria(
                        id_usuario=id_usuario,
                        accion=accion,
                        tabla_afectada=tabla_afectada,
                        registro_id=registro_id,
                        detalles=detalles,
                        ip_origen=ip_origen,
                    )
                    db_session.add(registro)
                    db_session.commit()
                finally:
                    db_session.close()

            except Exception as e:
                logger.warning(f"Error intercepting audit record: {e}")

        return response
