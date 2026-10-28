# 2. Modelo PostgreSQL

## Tablas y relaciones

- `users` ↔ `roles` mediante `user_roles`; `roles` ↔ `permissions` mediante `role_permissions`.
- `alerts` es la entidad central. `dedup_key` único asegura idempotencia; índices por recepción, severidad, estado, origen e IP.
- `enrichment_data` 1:1 con `alerts`; marca `is_simulated`.
- `triage_results` 1:1 con `alerts`; conserva proveedor, modelo, confianza, resumen y error.
- `incidents` N:1 con `alerts` y opcionalmente con `users` como responsable.
- `audit_log` registra actor, zona horaria, módulo, acción, resultado, recurso, correlación y detalles sin secretos.

## Migración y seed

`backend/alembic/versions/0001_initial.py` crea tablas, claves foráneas, índices y restricciones. El arranque ejecuta `alembic upgrade head` y luego `python -m app.seed`; el seed es idempotente y crea usuarios demo y alertas ficticias de varias severidades, duplicado y caso pendiente. No se monta un SQL init paralelo para evitar conflictos.

Con datos reales, usa `docker compose exec backend alembic current` y `alembic upgrade head`.
