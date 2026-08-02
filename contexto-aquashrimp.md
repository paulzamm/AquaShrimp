# Contexto del Proyecto AquaShrimp

Sistema de Información Gerencial Acuícola para AquaShrimp Analytics S.A.
Universidad Técnica de Machala — Facultad de Ingeniería Civil — Carrera de Tecnologías de la Información
Asignatura: Sistemas de Información Gerencial

---

## 1. Resumen del proyecto

AquaShrimp Analytics S.A. es una empresa acuícola (camaronera) que opera con registros dispersos en Excel, anotaciones manuales y comunicación informal (llamadas, WhatsApp), lo que genera retrasos en decisiones, baja trazabilidad y riesgo de errores humanos.

**AquaShrimp** es un Sistema de Información Gerencial con soporte a decisiones que centraliza los datos operativos de las piscinas camaroneras, integra sensores IoT y automatiza el monitoreo y las recomendaciones de alimentación. Se alinea con:
- **ISO 9001**: enfoque basado en procesos, mejora continua, trazabilidad, gestión documental.
- **ISO/IEC 27001**: confidencialidad, integridad y disponibilidad de la información; control de riesgos.

---

## 2. Alcance académico (requisitos obligatorios de la cátedra)

- Investigar procesos de una empresa mediana/grande e implementar un SIG funcional, distribuido y orientado a decisiones.
- Modelar y optimizar procesos con **BPM**; al menos **un proceso automatizado**.
- Cumplir **ISO 9001** (calidad de procesos) e **ISO 27001** (riesgos de información).
- Plataforma **libre**; servidor principal y acceso remoto sobre Linux.
- Base de datos gestionada con motor relacional (Oracle en el enunciado original).
- **≥ 8 entidades principales** en la base de datos.
- Frontend en **JavaScript/Angular**, backend en **Go** (según enunciado original).
- Control de versiones con **GitHub**.
- **Transacciones** de base de datos.
- Operaciones de BD **solo a través de API REST**.
- **Arquitectura distribuida** en 2 servidores: (1) BD + API, (2) aplicación SIG.
- Servidores **reales o virtuales**, no entornos de desarrollo sueltos.
- Al menos **un proceso BPM funcional**.
- Al menos **un dispositivo IoT** integrado.
- Aplicar **métrica de complejidad de McCabe**.

> **Nota de adaptación del equipo:** el stack tecnológico real usado difiere del enunciado original y del primer entregable en PDF. El detalle de la sustitución está en la sección 4.

---

## 3. Stack tecnológico real (decisión del equipo)

| Componente | Documento original (PDF) | Stack real usado |
|---|---|---|
| Frontend | Angular sobre servidor CentOS | Angular (sin cambios) — contenedor Docker servido con nginx en CentOS Stream / Rocky Linux |
| Backend / API | API REST en **Go**, servidor Trisquel | **FastAPI** (Python) con ORM (SQLAlchemy) y migraciones (Alembic) |
| Base de datos | **Oracle Database** | **PostgreSQL** |
| Administración BD | — | **pgAdmin** (interfaz web, en contenedor) |
| Contenerización | No especificada | **Docker** (contenedores separados: frontend, API, base de datos) |
| SO servidor 1 (BD + API) | Trisquel | **Debian 12** o **Ubuntu Server LTS** (recomendado, ver justificación) |
| SO servidor 2 (App SIG / Angular) | CentOS | **CentOS Stream 9** (o Rocky Linux 9 como alternativa) |
| Control de versiones | GitHub | GitHub (sin cambios) |

**Justificación breve de los cambios:**
- *Oracle → PostgreSQL*: motor relacional libre, con integridad referencial, transacciones ACID y soporte completo para migraciones versionadas; cumple el mismo rol arquitectónico exigido.
- *Go → FastAPI*: framework Python que expone API REST, soporta async, documentación OpenAPI automática y capa ORM con migraciones — cumple el requisito de que toda operación de BD pase exclusivamente por la API.
- *Trisquel → Debian/Ubuntu*: se mantiene el principio de "plataforma libre" (Debian es, de hecho, la base del linaje del que deriva Trisquel); se gana mayor documentación, soporte de paquetes Docker oficiales y estabilidad LTS.
- CentOS se conserva para el segundo servidor, tal como en el diseño original.

## Simulación de Sensores IoT (Decisión del Proyecto)

Para este proyecto NO se utilizará hardware IoT físico.

Aunque la arquitectura representa un sistema IoT real, todos los sensores serán simulados completamente desde el backend mediante un módulo denominado Sensor Simulator.

El objetivo es reproducir el comportamiento de sensores reales sin depender de dispositivos físicos.

Los sensores simulados serán:

- Sensor de pH
- Sensor de Oxígeno Disuelto (DO)
- Sensor de Temperatura del Agua

Cada sensor generará lecturas periódicas utilizando datos sintéticos controlados, con capacidad para simular:

- valores normales
- valores críticos
- ruido aleatorio
- tendencias crecientes o decrecientes
- pérdida de comunicación
- fallos del sensor

Para el resto del sistema (API, reglas de negocio, dashboard y base de datos), estas lecturas deberán tratarse exactamente igual que si provinieran de sensores físicos.

En ningún momento deberá desarrollarse firmware para ESP32, Arduino, Raspberry Pi ni cualquier otro dispositivo físico.

---

## 4. Procesos del negocio (BPM)

### 4.1 Proceso AS-IS (situación actual, manual)

Actores: **Técnico acuícola**, **Gerencia**.

1. Evento de inicio.
2. Medir temperatura y pH manualmente (instrumentos físicos).
3. Anotar valores en hoja de campo.
4. Compuerta de decisión: ¿el dato parece correcto?
   - No → repetir medición o corregir el apunte.
   - Sí → registrar datos manualmente en Excel (después, no en tiempo real) — riesgo de error humano y duplicidad.
5. Comunicar por llamada o WhatsApp cualquier hallazgo relevante.
6. Gerencia recibe reporte tardío.
7. Gerencia analiza situación manualmente.
8. Decisión gerencial tomada tardíamente (fin del proceso).

**Problemas detectados:** dependencia manual, registros duplicados, retraso en reportes, riesgo de errores humanos, sin monitoreo en tiempo real, baja trazabilidad.

### 4.2 Proceso TO-BE (propuesto, automatizado — este es el proceso BPM funcional exigido)

Carriles (swimlanes): **Sensores IoT**, **AquaShrimp (sistema)**, **Técnico acuícola**, **Gerencia**.

1. Sensor Simulator genera una lectura sintética de:

- pH
- Oxígeno Disuelto
- Temperatura del Agua

2. El simulador envía la lectura al mismo endpoint REST que utilizaría un sensor físico.

3. AquaShrimp procesa la lectura sin distinguir si proviene de un sensor real o simulado.
4. **AquaShrimp** registra la lectura en PostgreSQL.
3. Compuerta: ¿dato válido? (rango físico coherente, formato correcto)
   - No → el técnico debe solicitar una nueva lectura.
   - Sí → continúa el flujo.
4. **AquaShrimp** valida rango y tendencia contra los umbrales configurados.
5. Compuerta: ¿nivel crítico?
   - **No crítico** → AquaShrimp recomienda alimentación automáticamente y actualiza el tablero gerencial.
   - **Crítico** → AquaShrimp emite una alerta priorizada → el **técnico** revisa la piscina y actúa → registra la acción correctiva → el sistema actualiza el tablero.
6. **Gerencia** consulta KPIs y trazabilidad cuando lo requiere.
7. Evento de finalización (ciclo cerrado con trazabilidad completa: lectura → alerta/recomendación → acción → cierre).

Este es el **proceso automatizado central** que debe demostrarse funcionando de extremo a extremo en la sustentación (sensor real → API → regla de negocio → alerta o recomendación → visible en dashboard).

### 4.3 Comparación AS-IS vs TO-BE

| Aspecto | AS-IS | TO-BE |
|---|---|---|
| Registro de datos | Manual, disperso (papel/Excel) | Automático, centralizado en PostgreSQL |
| Alertas | No existen, dependen de revisión humana | Automáticas, por reglas de negocio |
| Tiempo de respuesta | Lento (llamadas, WhatsApp) | Reducido (notificaciones + tablero) |
| Trazabilidad | Parcial | Completa (lectura → alerta → técnico → acción → cierre) |
| Integración | Baja, canales separados | Alta, flujo único sensor–API–BD–frontend |
| Toma de decisiones | Reactiva | Preventiva, basada en KPIs y tendencias |
| Seguridad | Informal | Roles, autenticación, auditoría, respaldos |
| Calidad de información | Riesgo de duplicidad/error | Validación automática, consistencia referencial |

---

## 5. Modelo de datos

### 5.1 Entidades principales (10 — supera el mínimo de 8 exigido)

| Entidad | Clave primaria | Descripción |
|---|---|---|
| Usuario | id_usuario | Credenciales, estado de cuenta, datos del personal que accede al sistema |
| Rol | id_rol | Permisos de administrador, técnico acuícola y gerencia |
| Piscina | id_piscina | Cada piscina camaronera monitoreada |
| Sensor | id_sensor | Dispositivo IoT asociado a una piscina y tipo de variable medida |
| LecturaSensor | id_lectura | Valores medidos con fecha y hora |
| Alerta | id_alerta | Evento crítico generado cuando una lectura supera umbrales |
| AccionCorrectiva | id_accion | Revisión y respuesta del técnico ante una alerta |
| RecomendacionAlimentacion | id_recomendacion | Sugerencia de alimentación según condiciones ambientales |
| Cosecha | id_cosecha | Fechas, biomasa estimada, producción y resultados de cada ciclo |
| ReporteGerencial | id_reporte | Indicadores, alertas, acciones y métricas históricas consolidadas |

Sensor.tipo

Valores permitidos:

- ph
- oxigeno_disuelto
- temperatura

Los sensores representan dispositivos IoT virtuales administrados por el módulo Sensor Simulator.

El diseño permite sustituirlos posteriormente por sensores físicos sin modificar la arquitectura.

### 5.2 Atributos detallados

- **Usuario**: `id_usuario (PK)`, `id_rol (FK)`, `nombre`, `correo`, `contrasena_hash`, `estado`, `fecha_creacion`, `ultimo_acceso`
- **Rol**: `id_rol (PK)`, `nombre_rol`, `descripcion`, `permisos`, `estado`
- **Piscina**: `id_piscina (PK)`, `codigo`, `ubicacion`, `area_m2`, `profundidad`, `estado`, `fecha_inicio_ciclo`
- **Sensor**: `id_sensor (PK)`, `id_piscina (FK)`, `tipo` *(ajustado a los sensores reales: `temperatura_agua`, `temperatura_ambiente`)*, `ubicacion`, `estado`, `fecha_instalacion`, `unidad_medida`
- **LecturaSensor**: `id_lectura (PK)`, `id_sensor (FK)`, `valor`, `unidad`, `fecha_hora`, `estado_validacion`, `observacion`
- **Alerta**: `id_alerta (PK)`, `id_lectura (FK)`, `tipo_alerta`, `severidad`, `descripcion`, `fecha_generacion`, `estado`
- **AccionCorrectiva**: `id_accion (PK)`, `id_alerta (FK)`, `id_usuario (FK)`, `descripcion`, `fecha_accion`, `resultado`, `estado_cierre`
- **RecomendacionAlimentacion**: `id_recomendacion (PK)`, `id_piscina (FK)`, `id_usuario (FK)`, `cantidad_kg`, `frecuencia`, `criterio`, `fecha_generacion`, `estado`
- **Cosecha**: `id_cosecha (PK)`, `id_piscina (FK)`, `fecha_cosecha`, `biomasa_kg`, `talla_promedio`, `rendimiento`, `observaciones`
- **ReporteGerencial**: `id_reporte (PK)`, `id_usuario (FK)`, `tipo_reporte`, `periodo_inicio`, `periodo_fin`, `fecha_generacion`, `ruta_archivo`

> **Nota:** dado que solo se cuenta con sensores de temperatura (agua) y temperatura/humedad ambiente (no hay oxígeno disuelto ni pH), el campo `tipo` de `Sensor` y los umbrales de `Alerta` deben restringirse a estas variables reales. El modelo queda preparado para escalar a más tipos de sensor en el futuro sin rediseño.

### 5.3 Relaciones y cardinalidades

| Relación | Cardinalidad | Propósito |
|---|---|---|
| Rol – Usuario | 1:N | Un rol puede asignarse a varios usuarios |
| Piscina – Sensor | 1:N | Una piscina puede tener varios sensores |
| Sensor – LecturaSensor | 1:N | Cada sensor genera múltiples lecturas |
| LecturaSensor – Alerta | 1:0..N | Una lectura puede originar una o varias alertas |
| Alerta – AccionCorrectiva | 1:0..N | Una alerta puede requerir una o varias acciones |
| Piscina – RecomendacionAlimentacion | 1:N | Recomendaciones generadas por piscina |
| Piscina – Cosecha | 1:N | Una piscina puede tener varios ciclos de cosecha |
| Usuario – ReporteGerencial | 1:N | Reportes asociados al usuario que los genera/consulta |

### 5.4 Motor de datos y capa de acceso

- **PostgreSQL** como base de datos relacional (sustituye a Oracle).
- **SQLAlchemy** como ORM en el backend FastAPI.
- **Alembic** para migraciones versionadas del esquema.
- **pgAdmin** (contenedor con interfaz web) para administración visual de la BD.
- Todas las operaciones de lectura/escritura pasan exclusivamente por la **API REST en FastAPI** — el frontend nunca accede directamente a la base de datos.
- Operaciones que afectan más de una tabla (p. ej. cerrar una alerta y registrar la acción correctiva) se ejecutan dentro de **transacciones explícitas** para garantizar atomicidad.

---

## 6. Arquitectura del sistema

### 6.1 Capas lógicas

1. **Capa de presentación**: Angular, contenedor Docker servido con nginx, desplegado en servidor CentOS/Rocky.
2. **Capa de negocio**: API REST en FastAPI, contenedor Docker, desplegado en servidor Debian/Ubuntu. Concentra validación de lecturas, evaluación de umbrales, generación de alertas, cálculo de recomendaciones, administración de usuarios y exposición de datos al tablero.
3. **Capa de persistencia**: PostgreSQL + pgAdmin, contenedores Docker en el mismo servidor Debian/Ubuntu que la API.

### 6.2 Arquitectura tecnológica (capas físicas)

- **Capa de campo**: sensores IoT (temperatura de agua, temperatura/humedad ambiente) → envían lecturas en JSON vía HTTP POST.
- **Capa de aplicación**:
  - Servidor 2 (CentOS/Rocky): aplicación Angular (frontend).
  - Servidor 1 (Debian/Ubuntu): API REST FastAPI (backend) + reglas de negocio.
- **Capa de datos**: PostgreSQL (persistencia transaccional) + pgAdmin, con auditoría, respaldos y reportes históricos.

### 6.3 Distribución en 2 servidores (requisito obligatorio)

- **Servidor 1** — Debian 12 / Ubuntu Server LTS: contenedores de PostgreSQL + pgAdmin + API FastAPI.
- **Servidor 2** — CentOS Stream 9 / Rocky Linux 9: contenedor de Angular (build servido con nginx), consumiendo la API del Servidor 1 por red.

### 6.4 Seguridad (controles transversales)

- Autenticación (JWT) y autorización por roles (técnico, gerencia, administrador).
- Registro de auditoría de operaciones (quién, qué, cuándo).
- Cifrado de comunicaciones (HTTPS).
- Respaldos periódicos de PostgreSQL (`pg_dump` programado).
- Validación de entradas en la API.
- Firewall con solo los puertos necesarios abiertos.

               Sensor Simulator

        ┌──────────────────────────┐
        │ Sensor pH                │
        │ Sensor Oxígeno           │
        │ Sensor Temperatura       │
        └──────────────┬───────────┘
                       │
                 HTTP POST (JSON)
                       │
                       ▼
              FastAPI REST API
                       │
                       ▼
                 Business Rules
                       │
                       ▼
                 PostgreSQL
                       │
                       ▼
              Angular Dashboard

---

## 7. Casos de uso principales

| ID | Caso de uso | Actor |
|---|---|---|
| CU-01 | Capturar lecturas ambientales (temperatura agua / temperatura y humedad ambiente) | Sensores IoT |
| CU-02 | Validar parámetros, detectar valores críticos y generar alertas | AquaShrimp / Técnico acuícola |
| CU-03 | Gestionar piscinas, revisiones y acciones correctivas | Técnico acuícola |
| CU-04 | Generar recomendaciones de alimentación según condiciones del cultivo | AquaShrimp / Técnico acuícola |
| CU-05 | Consultar tablero gerencial, KPIs y trazabilidad productiva | Gerencia |
| CU-06 | Generar reportes históricos para control y toma de decisiones | Gerencia / Administrador |
| CU-07 | Administrar usuarios, roles, permisos y umbrales de monitoreo | Administrador del sistema |

---

## 8. Riesgos de seguridad de la información (ISO/IEC 27001)

| Riesgo | Impacto | Probabilidad | Control de mitigación |
|---|---|---|---|
| Acceso no autorizado | Alto | Media | Autenticación robusta, roles, control de sesiones, auditoría, revisión periódica de cuentas |
| Pérdida o alteración de datos | Alto | Media | Respaldos programados, integridad referencial, validación de entradas, bitácoras de cambios |
| Interrupción del servicio | Medio | Media | Monitoreo de disponibilidad, separación de servidores, mantenimiento preventivo, contingencia manual |
| Exposición de comunicaciones | Medio | Baja | HTTPS, segmentación de red, tokens de acceso, configuración segura cliente-servidor |

---

## 9. Indicadores de éxito

| Indicador | Descripción | Meta |
|---|---|---|
| Respuesta ante alertas | Tiempo entre detección de condición crítica y atención del técnico | Reducir 50% |
| Registros centralizados | % de lecturas, alertas, acciones y reportes en PostgreSQL vs. dispersos | Centralizar 90% |
| Trazabilidad | % de alertas con responsable, fecha, acción y cierre documentado | 95% |
| Calidad de datos | % de lecturas válidas tras validación | Mantener 98% |
| Uso del tablero | Frecuencia de consulta gerencial de KPIs | 1 consulta diaria |
| Alimentación eficiente | Recomendaciones generadas vs. registradas como aplicadas | 100% |
| Disponibilidad | % de tiempo operativo de API, BD y app web | Mínimo 95% |

---

## 10. Elementos de calidad (ISO 9001) aplicados al diseño

- **Enfoque basado en procesos**: secuencia clara captura → validación → análisis → alerta → recomendación → acción correctiva → reporte, con entradas, responsables y salidas definidas por actividad.
- **Mejora continua**: histórico de lecturas, alertas y acciones permite comparar ciclos productivos y ajustar umbrales/reglas.
- **Trazabilidad y gestión documental**: cada alerta queda vinculada a lectura, piscina, técnico responsable, acción aplicada y fecha de cierre.

---

## 11. Requisitos técnicos obligatorios y su cumplimiento

| Requisito | Cómo se cumple |
|---|---|
| ≥ 8 entidades | 10 entidades definidas (sección 5.1) |
| Frontend Angular | Sí, contenedor Docker + nginx en CentOS/Rocky |
| Backend (Go en enunciado) | FastAPI, justificado como equivalente funcional |
| GitHub | Repositorio con ramas `main`/`develop`/`feature/*` |
| Transacciones en BD | SQLAlchemy con transacciones explícitas en operaciones multi-tabla |
| Operaciones BD solo vía API REST | Frontend consume únicamente la API FastAPI |
| Arquitectura distribuida 2 servidores | Servidor 1 (BD+API) / Servidor 2 (frontend) |
| Servidores reales/virtuales | VMs con Debian/Ubuntu y CentOS/Rocky |
| Proceso BPM funcional automatizado | Motor de reglas: lectura → validación → alerta o recomendación (sección 4.2) |
| Dispositivo IoT integrado | Sensor de temperatura (agua) + temperatura/humedad ambiente enviando datos vía HTTP POST |
| Métrica de McCabe | Aplicada sobre el módulo del motor de reglas de negocio (backend) |
| ISO 9001 | Enfoque por procesos, mejora continua, trazabilidad (sección 10) |
| ISO 27001 | Cuadro de riesgos y controles (sección 8) |

---

## 12. Pendientes / decisiones abiertas del equipo

- Confirmar con el profesor la sustitución de Oracle → PostgreSQL, Go → FastAPI y Trisquel → Debian/Ubuntu.
- Definir si los servidores serán VMs locales (VirtualBox/VMware) o instancias en la nube (para cumplir "servidores reales").
- Decidir el modelo exacto de sensor/microcontrolador (ESP32 + DHT22/DS18B20 u otro) para la integración IoT.
- Actualizar los mockups del documento original (login, dashboard, alertas, monitoreo, reportes) para reflejar únicamente temperatura y ambiente en vez de oxígeno/pH.


# Sensor Simulator

El sistema incluye un módulo interno denominado Sensor Simulator.

Este componente reemplaza temporalmente el hardware IoT.

Su responsabilidad es generar lecturas sintéticas para:

- pH
- Oxígeno Disuelto
- Temperatura

Cada lectura debe enviarse mediante la API REST utilizando exactamente el mismo contrato JSON que utilizaría un dispositivo físico.

El simulador deberá permitir:

- iniciar simulación
- detener simulación
- configurar frecuencia
- modificar rangos
- generar anomalías
- generar datos históricos

Toda la lógica de negocio debe funcionar sin conocer si los datos provienen de un sensor real o del simulador.
