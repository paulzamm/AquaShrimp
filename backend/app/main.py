from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.routers import (
    accion_correctiva,
    alerta,
    auth,
    cosecha,
    lecturas,
    piscina,
    reporte_gerencial,
    rol,
    sensor,
    usuario,
)

app = FastAPI(
    title="AquaShrimp API",
    description="API REST para el sistema de gestión de camaroneras Aqua-Shrimp",
    version="1.0.0",
)


@app.exception_handler(IntegrityError)
def integrity_error_handler(request: Request, exc: IntegrityError):
    """Global exception handler for IntegrityError returning 400 Bad Request."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Error de integridad en la base de datos u operación no permitida."},
    )


# Include Routers
app.include_router(auth.router)
app.include_router(rol.router)
app.include_router(usuario.router)
app.include_router(piscina.router)
app.include_router(sensor.router)
app.include_router(lecturas.router)
app.include_router(alerta.router)
app.include_router(accion_correctiva.router)
app.include_router(cosecha.router)
app.include_router(reporte_gerencial.router)

# Configuration for CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API operational status and DB connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "db": "disconnected", "error": str(e)},
        )
