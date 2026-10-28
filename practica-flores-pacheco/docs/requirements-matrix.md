# Matriz de cumplimiento del laboratorio

| Requisito | Estado actual | Evidencia |
|---|---|---|
| FastAPI + PostgreSQL + Docker | Implementado | `backend/app`, `docker-compose.yml` |
| JWT y sesión | Implementado | `/api/v1/auth/login`, `/api/v1/auth/me`, manejo 401 frontend |
| Dashboard KPI | Implementado | Dashboard y `/api/v1/dashboard/stats` |
| Detección heurística | Implementado como MVP | `/api/v1/detections/analyze`, `detector.py` |
| Gestión de incidentes | Implementado | UI y endpoints POST/GET/PATCH |
| Usuarios y RBAC | RBAC base implementado | `/api/v1/users` protegido para admin; completar SSO/MFA en producción |
| Auditoría | Implementado como MVP | `audit_logs`, `/api/v1/audit`, eventos de login/detección/incidente/reporte |
| Reportes PDF/DOCX/XLSX/CSV | Implementado | `/api/v1/reports/export` |
| Dataset público y ETL | Parcial funcional | PhishTank documentado, endpoint con X-ETL-Key y workflow n8n |
| n8n | Implementado en Compose | Servicio `n8n`, tres JSON importables, pantalla web |
| IA LangChain/LangFlow | Diseño integrado, fallback seguro | `/api/v1/ai/status`, `docs/ai-flows.md`; proveedor LLM requiere configuración |
| Threat Intelligence | MVP funcional | Indicadores, dataset y pantalla de consulta |
| Migraciones Alembic | Pendiente | El MVP usa `create_all`; añadir antes de producción |
| MFA/SSO/refresh tokens | Pendiente | Requisito de endurecimiento de producción |
| Observabilidad Prometheus/Grafana/Loki | Pendiente | Requiere stack de operación adicional |
| TLS, Vault y secretos productivos | Pendiente | Los valores Docker son solo de laboratorio |

La etiqueta “Implementado” significa que el flujo se puede ejecutar en laboratorio; no implica certificación PCI-DSS, ISO 27001 o SOC 2.
