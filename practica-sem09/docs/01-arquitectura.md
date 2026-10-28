# 1. Arquitectura del sistema

## Capas

1. **Presentación**: React/TypeScript/Vite servido por Nginx. Login, panel, alertas, incidentes, reportes y auditoría; la interfaz oculta acciones que el rol no debe ejecutar.
2. **Lógica de negocio**: FastAPI valida esquemas Pydantic, autentica JWT, aplica RBAC, normaliza/idempotencia, gestiona incidentes, auditoría y reportes.
3. **Enriquecimiento y triaje**: microservicio FastAPI separado. LangChain + Ollama son opcionales; la demo usa heurística explícitamente identificada.
4. **Orquestación**: n8n recibe el webhook, filtra, reintenta/timeouts, invoca persistencia y triage, enruta y registra integraciones.
5. **Datos**: PostgreSQL con volumen persistente y Alembic. n8n tiene su propio esquema/tablas en la misma base lógica, sin compartir migraciones.

## Interacciones

`simulator/send_alert.py` → `n8n /webhook/soc-lite-alert` → normalización/deduplicación → `backend /api/alerts/ingest` → PostgreSQL → `triage /triage` → `backend /api/alerts/{id}/triage-result` → dashboard React.

Se usa una red Docker privada `soc_lite_net`; solo se publican frontend, API, n8n y opcionalmente Ollama. PostgreSQL no publica puerto.

## Seguridad

Contraseñas Argon2 mediante pwdlib, JWT con secreto de entorno, claves de servicio en `X-API-Key`, CORS limitado, auditoría append-only por API (no hay modificar/eliminar), datos de alertas tratados como no confiables y sin respuesta automática.
