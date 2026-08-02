# AquaShrimp 🦐

Sistema de Información Gerencial Acuícola para el monitoreo inteligente de piscinas camaroneras.

## Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| Frontend | Angular |
| Backend | FastAPI (Python) |
| Base de datos | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Migraciones | Alembic |
| Contenedores | Docker + Docker Compose |
| Autenticación | JWT |

## Requisitos

- Docker y Docker Compose
- Python 3.12+
- Node.js 18+ (para el frontend)

## Inicio Rápido

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/paulzamm/AquaShrimp.git
   cd AquaShrimp
   ```

2. Levantar los servicios de base de datos:
   ```bash
   docker compose -f infra/docker-compose.yml up -d
   ```

3. Instalar dependencias del backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

4. Ejecutar migraciones:
   ```bash
   alembic upgrade head
   ```

5. Cargar datos iniciales:
   ```bash
   python -m seeds.seed_data
   ```

## Estructura del Proyecto

```
aqua-shrimp/
├── backend/       # API FastAPI + SQLAlchemy
├── frontend/      # Angular (Fase 3)
├── db/            # Scripts SQL auxiliares
├── infra/         # Docker Compose
└── docs/          # Documentación
```

## Accesos de Desarrollo

- **pgAdmin**: http://localhost:5050 (admin@aquashrimp.com / root)
- **API**: http://localhost:8000 (Fase 2)
- **Swagger**: http://localhost:8000/docs (Fase 2)
