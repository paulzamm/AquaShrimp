# AquaShrimp — Fase 0 + Fase 1 Design Spec

## Purpose

Establish the project foundation (Fase 0) and build the complete data model (Fase 1) for AquaShrimp, a shrimp farm management SIG (Sistema de Información Gerencial).

## Success Criteria

- Git repository initialized, connected to GitHub, with `main`/`develop`/`feature/*` branch strategy
- Monorepo structure created with `backend/`, `frontend/`, `db/`, `infra/`, `docs/`
- Docker Compose running PostgreSQL 16 + pgAdmin 4 reliably
- 10 SQLAlchemy 2.0 models with full constraints (PK, FK, CHECK, NOT NULL, indexes)
- Alembic migrations auto-generated from models, creating all tables in one `alembic upgrade head`
- Seed script populating realistic initial data
- pytest tests verifying database connectivity, model creation, constraints, and relationships

---

## Architecture

### Project Structure

```
aqua-shrimp/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # Pydantic Settings
│   │   │   └── database.py        # Engine, Session, Base
│   │   ├── models/
│   │   │   ├── __init__.py        # Re-exports all models
│   │   │   ├── base.py            # TimestampMixin
│   │   │   ├── rol.py
│   │   │   ├── usuario.py
│   │   │   ├── piscina.py
│   │   │   ├── sensor.py
│   │   │   ├── lectura_sensor.py
│   │   │   ├── alerta.py
│   │   │   ├── accion_correctiva.py
│   │   │   ├── recomendacion_alimentacion.py
│   │   │   ├── cosecha.py
│   │   │   └── reporte_gerencial.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   ├── routers/
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   └── __init__.py
│   │   ├── middlewares/
│   │   │   └── __init__.py
│   │   └── utils/
│   │       └── __init__.py
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── seeds/
│   │   ├── __init__.py
│   │   └── seed_data.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_models.py
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   └── .gitkeep
├── db/
│   └── .gitkeep
├── infra/
│   └── docker-compose.yml
├── docs/
│   └── superpowers/
├── .gitignore
├── .editorconfig
└── README.md
```

### Docker Services (Fase 1)

| Service | Image | Port | Volume |
|---------|-------|------|--------|
| `postgres` | `postgres:16-alpine` | `5432:5432` | `aquashrimp_pgdata` (named volume) |
| `pgadmin` | `dpage/pgadmin4:latest` | `5050:80` | `aquashrimp_pgadmin` (named volume) |

Credentials: user `admin`, password `root`, database `aquashrimp_db`.

pgAdmin login: `admin@aquashrimp.com` / `root`.

---

## Data Model

### SQLAlchemy 2.0 Patterns

- `DeclarativeBase` with `Mapped[]` type annotations and `mapped_column()`
- `TimestampMixin` providing `created_at` (server_default=now) and `updated_at` (onupdate=now)
- All relationships use `back_populates` (explicit bidirectional)
- Enums as `String` + CHECK constraints (not native PostgreSQL ENUM)
- Integer autoincremental primary keys

### 10 Entities

#### 1. Rol
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK, autoincrement |
| `nombre_rol` | String(50) | NOT NULL, UNIQUE |
| `descripcion` | String(255) | nullable |
| `permisos` | Text (JSON string) | nullable |
| `estado` | String(20) | NOT NULL, default='activo', CHECK IN ('activo','inactivo') |

#### 2. Usuario
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK, autoincrement |
| `id_rol` | Integer | FK → roles.id, NOT NULL |
| `nombre` | String(100) | NOT NULL |
| `correo` | String(150) | NOT NULL, UNIQUE |
| `contrasena_hash` | String(255) | NOT NULL |
| `estado` | String(20) | NOT NULL, default='activo', CHECK IN ('activo','inactivo','suspendido') |
| `ultimo_acceso` | DateTime | nullable |

#### 3. Piscina
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK, autoincrement |
| `codigo` | String(20) | NOT NULL, UNIQUE |
| `ubicacion` | String(200) | NOT NULL |
| `area_m2` | Float | NOT NULL, CHECK > 0 |
| `profundidad` | Float | NOT NULL, CHECK > 0 |
| `estado` | String(20) | NOT NULL, default='activa', CHECK IN ('activa','inactiva','mantenimiento') |
| `fecha_inicio_ciclo` | Date | nullable |

#### 4. Sensor
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK, autoincrement |
| `id_piscina` | Integer | FK → piscinas.id (CASCADE), NOT NULL |
| `tipo` | String(50) | NOT NULL, CHECK IN ('ph','oxigeno_disuelto','temperatura') |
| `ubicacion` | String(200) | nullable |
| `estado` | String(20) | NOT NULL, default='activo', CHECK IN ('activo','inactivo','fallo') |
| `fecha_instalacion` | Date | nullable |
| `unidad_medida` | String(20) | NOT NULL |

Index on `(id_piscina, tipo)`.

#### 5. LecturaSensor
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK, autoincrement |
| `id_sensor` | Integer | FK → sensores.id (CASCADE), NOT NULL |
| `valor` | Float | NOT NULL |
| `unidad` | String(20) | NOT NULL |
| `fecha_hora` | DateTime | NOT NULL, default=now, INDEX |
| `estado_validacion` | String(20) | NOT NULL, default='pendiente', CHECK IN ('pendiente','valida','invalida') |
| `observacion` | Text | nullable |

Index on `fecha_hora`. Index on `id_sensor`.

#### 6. Alerta
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK, autoincrement |
| `id_lectura` | Integer | FK → lecturas_sensor.id (CASCADE), NOT NULL |
| `tipo_alerta` | String(50) | NOT NULL |
| `severidad` | String(20) | NOT NULL, CHECK IN ('baja','media','alta','critica') |
| `descripcion` | Text | NOT NULL |
| `fecha_generacion` | DateTime | NOT NULL, default=now |
| `estado` | String(20) | NOT NULL, default='activa', CHECK IN ('activa','atendida','cerrada') |

Index on `estado`. Index on `fecha_generacion`.

#### 7. AccionCorrectiva
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK, autoincrement |
| `id_alerta` | Integer | FK → alertas.id (CASCADE), NOT NULL |
| `id_usuario` | Integer | FK → usuarios.id (RESTRICT), NOT NULL |
| `descripcion` | Text | NOT NULL |
| `fecha_accion` | DateTime | NOT NULL, default=now |
| `resultado` | Text | nullable |
| `estado_cierre` | String(20) | NOT NULL, default='pendiente', CHECK IN ('pendiente','en_progreso','cerrada') |

#### 8. RecomendacionAlimentacion
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK, autoincrement |
| `id_piscina` | Integer | FK → piscinas.id (CASCADE), NOT NULL |
| `id_usuario` | Integer | FK → usuarios.id (RESTRICT), nullable |
| `cantidad_kg` | Float | NOT NULL, CHECK > 0 |
| `frecuencia` | String(50) | NOT NULL |
| `criterio` | Text | NOT NULL |
| `fecha_generacion` | DateTime | NOT NULL, default=now |
| `estado` | String(20) | NOT NULL, default='pendiente', CHECK IN ('pendiente','aplicada','descartada') |

#### 9. Cosecha
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK, autoincrement |
| `id_piscina` | Integer | FK → piscinas.id (CASCADE), NOT NULL |
| `fecha_cosecha` | Date | NOT NULL |
| `biomasa_kg` | Float | NOT NULL, CHECK > 0 |
| `talla_promedio` | Float | nullable, CHECK > 0 |
| `rendimiento` | Float | nullable |
| `observaciones` | Text | nullable |

#### 10. ReporteGerencial
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | PK, autoincrement |
| `id_usuario` | Integer | FK → usuarios.id (RESTRICT), NOT NULL |
| `tipo_reporte` | String(50) | NOT NULL |
| `periodo_inicio` | Date | NOT NULL |
| `periodo_fin` | Date | NOT NULL |
| `fecha_generacion` | DateTime | NOT NULL, default=now |
| `ruta_archivo` | String(500) | nullable |

CHECK: `periodo_fin >= periodo_inicio`.

### Relationships Summary

```
Rol 1──N Usuario
Usuario 1──N AccionCorrectiva
Usuario 1──N RecomendacionAlimentacion (nullable FK)
Usuario 1──N ReporteGerencial
Piscina 1──N Sensor (CASCADE)
Piscina 1──N RecomendacionAlimentacion (CASCADE)
Piscina 1──N Cosecha (CASCADE)
Sensor 1──N LecturaSensor (CASCADE)
LecturaSensor 1──N Alerta (CASCADE)
Alerta 1──N AccionCorrectiva (CASCADE)
```

---

## Seed Data

| Entity | Count | Details |
|--------|-------|---------|
| Roles | 3 | Administrador, Técnico Acuícola, Gerencia |
| Usuarios | 3 | One per role, passwords hashed with passlib/bcrypt |
| Piscinas | 3 | P-001, P-002, P-003 with realistic area/depth |
| Sensores | 9 | 3 per piscina (ph, oxigeno_disuelto, temperatura) |
| Lecturas | ~15 | Mix of normal and critical values |
| Alertas | 2 | Triggered by critical readings |
| AccionesCorrectivas | 1 | Response to an alert |
| Recomendaciones | 2 | Auto-generated feeding recommendations |
| Cosechas | 1 | Completed production cycle |
| Reportes | 1 | Sample managerial report |

---

## Testing Strategy

Tests with pytest using a separate test database or SQLite in-memory for speed:
- **Connection test**: verify engine connects to PostgreSQL
- **Table creation**: verify all 10 tables are created
- **CRUD per entity**: insert, query, update, delete
- **Constraint tests**: CHECK violations raise IntegrityError, FK violations raise IntegrityError, UNIQUE violations raise IntegrityError
- **Relationship tests**: navigate relationships (e.g., piscina.sensores, sensor.lecturas)

---

## Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary keys | Integer autoincremental | Simpler, better performance for academic context |
| Enum strategy | String + CHECK | More portable than native ENUM, easier migrations |
| Timestamps | Mixin | DRY, consistent across all models |
| Docker base | postgres:16-alpine | Lightweight, latest stable |
| Test DB | SQLite in-memory for unit tests | Fast, no Docker dependency for tests |
| Git strategy | main/develop/feature/* | Standard GitFlow for team collaboration |
| PostgreSQL credentials | admin/root | User preference for dev environment |
| Ports | 5432 (PG) / 5050 (pgAdmin) | User confirmed availability |
