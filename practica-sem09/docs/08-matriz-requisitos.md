# Matriz de requisitos y verificaciones

| Requisito | Componente | Forma de prueba | Estado |
|---|---|---|---|
| Login/hash/RBAC | backend + frontend | `scripts/smoke_test.py` y `scripts/rbac_test.py` | Verificado en Docker |
| Webhook y normalización | n8n | workflow importado, activado y simulador real | Verificado en Docker |
| Duplicados/idempotencia | backend + n8n | repetir `external_id`/payload y comprobar `status=duplicate` | Verificado en Docker |
| Filtrado severidad baja | n8n | simulador `--count 3`, respuesta `discarded=true` | Verificado en Docker |
| Estados y errores | alerts/triage | forzar timeout Ollama y revisar `error`/fallback | Implementado, pendiente ejecución |
| Enriquecimiento privado | triage | POST con `10.0.0.2`, comprobar no consulta pública | Implementado, pendiente ejecución |
| Ollama/LangChain | triage | `USE_OLLAMA=true`, `/health`, `/triage` | Preparado, requiere modelo y recursos |
| Dashboard PostgreSQL | frontend/backend | `/api/dashboard/summary` y frontend HTTP 200 | Verificado en Docker |
| Incidentes/revisión | backend/frontend | crear PATCH con analista | Implementado, pendiente ejecución |
| PDF/DOCX/XLSX | backend | `scripts/smoke_test.py` valida firmas y ZIP | Verificado en Docker |
| Auditoría | backend | smoke test y consulta PostgreSQL de acciones | Verificado en Docker |
| Workflow importable | n8n | `check_workflow.py`, importación CLI y webhook real | Verificado en Docker |
| E2E simulador→dashboard | todos | simulator + webhook + PostgreSQL + consulta de estados | Verificado en Docker |
| Persistencia | compose | reiniciar sin `down -v` y consultar seed | Preparado, pendiente ejecución |

## Relación ISO/NIST

- ISO/IEC 27001:2022: control de acceso, gestión de activos/datos, logging/monitorización, gestión de incidentes y continuidad se reflejan en RBAC, auditoría, incidentes, healthchecks y volúmenes. Referencia oficial: [ISO/IEC 27001:2022](https://www.iso.org/standard/27001.html).
- NIST Cybersecurity Framework 2.0 (2024): Govern (roles/políticas), Identify (inventario/contexto), Protect (auth), Detect (ingesta/triage), Respond (incidentes y recomendaciones humanas), Recover (persistencia/operación). Referencia oficial: [NIST CSF 2.0](https://www.nist.gov/cyberframework).

SOC-Lite es una práctica educativa y por sí sola no garantiza certificación ISO, cumplimiento legal ni cobertura completa del CSF. Faltan gobierno, evaluación de riesgos, evidencias, controles organizativos y validación independiente.
