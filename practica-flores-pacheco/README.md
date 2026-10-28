# SentinelBank Antiphishing SOC

MVP demostrativo de una plataforma defensiva antiphishing: dashboard React, API FastAPI, PostgreSQL, autenticación JWT, motor heurístico y workflows exportables de n8n.

> **Aviso:** es un entorno de laboratorio. No conectes feeds, correo, Slack ni datos bancarios reales sin revisar secretos, licencias, controles de red y cumplimiento.

## Requisitos

- Docker Desktop con Compose.
- Alternativamente: Python 3.11+, PostgreSQL 15+ y Node.js 20+.

## Ejecución recomendada con Docker

Desde la carpeta raíz:

```cmd
docker compose up -d --build
```

Si aparece `invalid file request node_modules/.ignored`, ya se incluyen archivos `.dockerignore`. Repite desde la raíz:

```cmd
docker compose down
docker compose build --no-cache
docker compose up -d
```

Servicios:

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health
- n8n: http://localhost:5678 (usuario `admin`, contraseña `postgres`)
- PostgreSQL: localhost:5432, base `antiphishing`, usuario `postgres`, contraseña `postgres`

Credenciales demo:

- Usuario: `admin@sentinelbank.com`
- Contraseña: `postgres`

## Ejecución manual

Terminal 1, con PostgreSQL activo:

```cmd
cd backend
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/antiphishing
set JWT_SECRET=cambia-esta-clave-local
uvicorn app.main:app --reload --port 8000
```

Terminal 2:

```cmd
cd frontend
npm install
npm run dev
```

## Verificación rápida

```cmd
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

Para probar desde Swagger: ejecuta `POST /api/v1/auth/login`, copia el token, pulsa **Authorize** y escribe `Bearer <token>`. Después ejecuta `POST /api/v1/detections/analyze`.

## Módulos de la interfaz

El menú permite acceder a Dashboard, Detecciones, Incidentes, Workflows n8n, Threat Intelligence, IA/LangChain, Usuarios, Auditoría y Reportes. La pantalla de Workflows enlaza a n8n y muestra los JSON ubicados en `n8n/workflows`.

Al ejecutar `docker compose up -d --build`, el contenedor n8n importa automáticamente los tres JSON desde `n8n/workflows` una sola vez por volumen: ingesta de dataset, alertas y reporte programado. Abre `http://localhost:5678`, verifica los workflows importados y actívalos después de configurar SMTP y las variables `ETL_API_KEY`, `ALERT_API_KEY`, `REPORTS_USER` y `REPORTS_PASSWORD`. Si quieres volver a importar desde cero, elimina únicamente el volumen `n8ndata` y recrea n8n.

## Estructura

- `backend/app`: API, modelos, seguridad y detector.
- `frontend/src`: consola SOC y dashboard.
- `n8n/workflows`: JSON importables de ingesta y alertas.
- `docs/architecture.md`: arquitectura, Mermaid, seguridad y roadmap.

## Limitaciones conocidas del MVP

- El detector es heurístico y no consulta WHOIS/DNS/TLS ni ejecuta contenido remoto.
- El modelo usa tablas creadas al iniciar; para producción añadir Alembic.
- El JWT es access-token; añadir refresh-token rotation y MFA para producción.
- Cambia `JWT_SECRET`, la contraseña demo y todos los webhooks antes de desplegar.
