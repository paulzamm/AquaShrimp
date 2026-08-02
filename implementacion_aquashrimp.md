
# AquaShrimp - Roadmap Oficial de Implementación

> Este documento define el orden obligatorio de implementación del proyecto AquaShrimp.
>
> Cualquier IA que participe en el desarrollo debe respetar este roadmap y NO avanzar a una fase posterior sin completar la anterior.

---

# Información General

## Proyecto

Sistema de monitoreo inteligente para piscinas de camarón mediante IoT, BPM y analítica de datos.

Stack tecnológico oficial:

- Frontend: Angular
- Backend: FastAPI
- Base de datos: PostgreSQL
- ORM: SQLAlchemy 2.0
- Migraciones: Alembic
- Contenedores: Docker + Docker Compose
- Servidor Web: Nginx
- Autenticación: JWT
- Control de versiones: Git + GitHub

---

# Arquitectura General

```
IoT Sensors
      │
      ▼
FastAPI REST API
      │
      ▼
PostgreSQL
      │
      ▼
Business Rules Engine
      │
      ├────► Alertas
      │
      ├────► Recomendaciones
      │
      ▼
Angular Dashboard
```

Toda comunicación debe pasar por la API.

El frontend nunca accede directamente a PostgreSQL.

---

# Orden Obligatorio de Desarrollo

```
FASE 0
 ↓
FASE 1
 ↓
FASE 2
 ↓
FASE 3
 ↓
FASE 4
 ↓
FASE 5
 ↓
FASE 6
 ↓
FASE 7
```

Nunca modificar este flujo.

---

# FASE 0
## Preparación del Proyecto

## Objetivos

Preparar completamente la estructura del proyecto.

### Tareas

- Crear repositorio Git
- Crear estructura monorepo
- Configurar ramas
- Crear README
- Configurar Docker inicial
- Documentación inicial
- Configurar convenciones de código

## Estructura esperada

```
aquashrimp/

backend/

frontend/

db/

infra/

docs/

README.md
```

## Entregables

Repositorio listo.

---

# FASE 1
# Base de Datos

## Objetivo

Construir completamente el modelo de datos.

## Entidades

Debe existir como mínimo:

- Usuario
- Rol
- Piscina
- Sensor
- LecturaSensor
- Alerta
- AccionCorrectiva
- RecomendacionAlimentacion
- Cosecha
- ReporteGerencial

## Requisitos

Implementar:

- PK
- FK
- CHECK
- NOT NULL
- Índices

## ORM

SQLAlchemy 2

## Migraciones

Alembic

## Docker

Debe existir un docker-compose con:

- PostgreSQL
- pgAdmin

## Seeds

Generar datos iniciales.

## Criterio de finalización

Toda la base debe levantarse únicamente mediante migraciones.

---

# FASE 2
# Backend

## Objetivo

Implementar toda la lógica del negocio.

## Arquitectura

```
routers/

services/

models/

schemas/

core/

middlewares/

utils/
```

## Funcionalidades

### Seguridad

- JWT
- Hash de contraseñas
- Roles

### CRUD

Implementar CRUD completo para todas las entidades.

### API REST

Todos los módulos deben exponer endpoints REST.

### Motor BPM

Después de recibir una lectura:

SI temperatura fuera de rango

↓

Crear alerta

↓

Registrar evento

↓

Notificar

SINO

↓

Generar recomendación

↓

Registrar historial

### Auditoría

Registrar:

- usuario
- fecha
- acción

### Documentación

Swagger automático.

### Pruebas

- Postman
- Pytest

## Criterio de finalización

Toda funcionalidad debe ser accesible desde la API.

---

# FASE 3
# Frontend

## Objetivo

Construir toda la interfaz Angular.

## Módulos

- Auth
- Dashboard
- Piscinas
- Alertas
- Alimentación
- Cosechas
- Reportes
- Usuarios

## Dashboard

Debe mostrar

- KPIs
- Alertas
- Lecturas
- Estado piscinas
- Gráficos

## Seguridad

- Guards
- Interceptors
- JWT

## Restricción

Nunca acceder directamente a PostgreSQL.

Todo consumo debe hacerse mediante FastAPI.

## Criterio de finalización

Todo el sistema debe funcionar conectado al backend.

---

# FASE 4
# Simulación IoT

## Objetivo

Construir un simulador de sensores que reproduzca el comportamiento de dispositivos IoT reales.
## Sensores simulados
- pH
- Oxígeno Disuelto
- Temperatura del Agua


## Flujo

Sensor Simulator

↓

Generador de Datos

↓

API REST

↓

Motor BPM

↓

Dashboard

## Funcionalidades

El simulador deberá:

- generar datos cada cierto intervalo configurable
- permitir iniciar y detener la simulación
- generar valores normales
- generar valores críticos
- introducir ruido aleatorio
- simular pérdida de comunicación
- simular fallos de sensores
- enviar datos mediante HTTP POST exactamente igual que un sensor real

Restricción importante

El resto del sistema no debe distinguir entre datos simulados y datos reales.

Toda comunicación debe seguir utilizando la API REST.

Criterio de finalización

El dashboard debe visualizar lecturas generadas por el Sensor Simulator como si provinieran de dispositivos físicos.

## Manejo de errores

- Reintentos
- Buffer temporal

## Criterio de finalización

Visualizar lecturas reales desde el dashboard.

---

# FASE 5
# Despliegue

## Objetivo

Separar la arquitectura en dos servidores.

Servidor 1

- PostgreSQL
- pgAdmin
- FastAPI

Servidor 2

- Angular
- Nginx

## Docker

Todos los servicios deben ejecutarse mediante Docker.

## Seguridad

- HTTPS
- Firewall
- Variables de entorno
- Backups

## Criterio de finalización

Frontend consumiendo correctamente la API del servidor remoto.

---

# FASE 6
# Calidad del Código

## Objetivo

Medir complejidad ciclomática.

## Herramientas

- Radon
- Lizard

## Analizar

Principalmente:

Business Rules Engine

## Reportar

- Complejidad
- Interpretación
- Refactorización

---

# FASE 7
# Validación Final

## Flujo completo

Sensor

↓

API

↓

BD

↓

Motor BPM

↓

Alerta

↓

Acción Correctiva

↓

Reporte

↓

Dashboard

## Indicadores

Medir

- Tiempo respuesta
- Disponibilidad
- Lecturas válidas
- Alertas generadas
- Acciones correctivas
- Reportes

## Demo

Mostrar

- Sensor enviando datos
- Dashboard actualizándose
- Alerta creada
- Acción correctiva
- Reportes

---

# Reglas para cualquier IA

Siempre seguir estas reglas.

## 1

Nunca crear código sin conocer la fase actual.

## 2

Nunca modificar una fase ya terminada sin autorización.

## 3

Antes de implementar cualquier módulo verificar dependencias.

## 4

Toda nueva funcionalidad debe respetar la arquitectura.

## 5

No generar soluciones temporales ("quick fixes").

## 6

Priorizar código limpio.

## 7

Seguir principios SOLID.

## 8

Evitar duplicación.

## 9

Documentar cualquier cambio importante.

## 10

Toda funcionalidad debe quedar lista para producción.

## 11
## Simulación IoT

Nunca desarrollar firmware para dispositivos físicos.

Nunca generar código para ESP32, Arduino, Raspberry Pi, NodeMCU o similares.

Toda funcionalidad IoT deberá implementarse mediante un módulo de simulación ejecutado dentro del backend.

El simulador deberá comportarse exactamente igual que un dispositivo IoT real, utilizando los mismos endpoints REST y el mismo formato de datos.

---

# Definición de Terminado (Definition of Done)

Una fase se considera terminada únicamente cuando:

- Compila sin errores.
- No existen errores de lint.
- No existen errores de tipado.
- Docker funciona correctamente.
- Existen pruebas.
- La documentación fue actualizada.
- El código fue versionado.
- La arquitectura no fue violada.

---

# Objetivo Final

Construir un sistema completamente funcional para el monitoreo inteligente de piscinas de camarón utilizando:

- Arquitectura distribuida
- IoT
- BPM
- API REST
- PostgreSQL
- Angular
- FastAPI
- Docker
- Buenas prácticas de ingeniería de software

Todo desarrollo futuro debe respetar este documento como guía oficial del proyecto.