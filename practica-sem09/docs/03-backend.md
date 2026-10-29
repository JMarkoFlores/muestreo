# 3. Backend

## Endpoints principales

- `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`.
- `GET /api/alerts` con `page`, `page_size`, `severity`, `status`, `search`; `GET /api/alerts/{id}`.
- `POST /api/alerts/ingest` (servicio n8n con `X-API-Key`), `POST /api/alerts/{id}/enrichment`, `POST /api/alerts/{id}/triage-result`.
- `GET /api/dashboard/summary`: severidades, pendientes/procesadas, timeline, orígenes, MTTT, falsos positivos e incidentes abiertos.
- `GET/POST/PATCH /api/incidents`.
- `GET /api/reports/export/{pdf|docx|xlsx}`; filtra `severity` y audita la exportación.
- `GET /api/audit`: consulta de auditoría inmutable para administradores, analistas y lectores.
- `GET/POST/PATCH /api/users` solo administrador para gestión de perfiles y roles.

## Auth/RBAC

JWT Bearer. Roles: `administrador`, `analista`, `lector`. El backend aplica permisos, no solo la UI: lector consulta; analista modifica incidentes, exporta y consulta auditoría; administrador además gestiona usuarios. Contraseñas nunca se registran.

## Métricas

- **MTTT** = promedio de `completed_at - received_at` para alertas finalizadas; si no hay finalizadas, `sin datos`.
- **Tasa de falsos positivos** = incidentes revisados con `reviewed_verdict=falso_positivo` / incidentes con veredicto humano; si no hay revisión, `sin datos`.

Los reportes PDF, DOCX y XLSX se generan con datos consultados de PostgreSQL en cada solicitud.
