# Task 6 Report: Motor BPM e Ingesta IoT (Core del Negocio)

## Summary
Successfully implemented Task 6 for Phase 2 of the Aqua-Shrimp system. The core Business Process Management (BPM) engine for IoT telemetry ingestion was created along with REST endpoints, threshold validation rules, automated alert/feeding recommendation generation, global exception handling, and full test suite coverage.

## Changes Introduced

1. **BPM Engine Service (`backend/app/services/bpm.py`)**:
   - Implemented `procesar_lectura(db, lectura_in)`:
     - Persists `LecturaSensor` record in database.
     - **BPM Rule 1 (Alerts)**:
       - `ph` < 6.5 or > 8.5 -> Generates `Alerta` with `severidad="alta"` (`ph_fuera_de_rango`).
       - `oxigeno_disuelto` < 4.0 -> Generates `Alerta` with `severidad="critica"` (`oxigeno_bajo`).
       - `temperatura` < 24.0 or > 32.0 -> Generates `Alerta` with `severidad="media"` (`temperatura_fuera_de_rango`).
     - **BPM Rule 2 (Feeding Recommendation)**:
       - If no alerts are generated (all telemetry parameters optimal), generates a `RecomendacionAlimentacion` assigned to the sensor's pool (`id_piscina`) with `cantidad_kg=50.0` and `criterio="Parámetros óptimos registrados."`.
   - Implemented `get_lectura` and `get_lecturas` service query functions.
   - Exported `bpm` module in `backend/app/services/__init__.py`.

2. **Lecturas API Router (`backend/app/routers/lecturas.py`)**:
   - Endpoint `POST /api/lecturas`:
     - Requires authentication (`get_current_active_user`).
     - Accepts `LecturaSensorCreate` schema.
     - Invokes BPM engine (`bpm.procesar_lectura`).
     - Returns `LecturaSensorResponse` with status `201 CREATED`.
   - Endpoints `GET /api/lecturas` and `GET /api/lecturas/{lectura_id}` for reading telemetry data.

3. **Global Exception Handler & Routers (`backend/app/main.py`)**:
   - Included `lecturas.router` in FastAPI app instance.
   - Added global exception handler for `sqlalchemy.exc.IntegrityError` to return `400 Bad Request` instead of unhandled 500 error when foreign key constraints or DB integrity constraints fail.
   - Verified clean UTF-8 encoding across `main.py`, `routers/piscina.py`, and `routers/usuario.py`.

4. **Testing (`backend/tests/api/test_bpm.py`)**:
   - Built comprehensive API test suite covering:
     - Authentication enforcement (401 Unauthorized for unauthenticated requests).
     - Non-existent sensor validation (404 Not Found).
     - Optimal pH reading -> persistence + feeding recommendation creation + no alerts.
     - Low & High pH readings -> `Alerta` with `severidad="alta"`, `tipo_alerta="ph_fuera_de_rango"`, no feeding recommendation.
     - Low Oxygen reading -> `Alerta` with `severidad="critica"`, `tipo_alerta="oxigeno_bajo"`.
     - Out of bounds Temperature readings -> `Alerta` with `severidad="media"`, `tipo_alerta="temperatura_fuera_de_rango"`.
     - Global `IntegrityError` exception handler returning HTTP 400.

## Commit
- `967cadb`: feat(bpm): implement BPM engine and IoT telemetry ingestion endpoint

## Verification Results
- `pytest tests/api/test_bpm.py -v`: 8 passed in 2.12s.
- `pytest tests/ -v`: 116 passed cleanly in full test suite.
