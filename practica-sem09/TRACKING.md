# Seguimiento SOC-Lite

Fecha de inicio: 2026-10-19 (America/Lima)

## Hecho
- [x] Inspección inicial: workspace vacío; Docker Compose v2.39.1 disponible.
- [x] Diseño de arquitectura y compose con PostgreSQL, backend, triage, n8n, frontend y perfil Ollama.
- [x] Código, migración, seed, workflow y documentación creados.
- [x] Validación estática: Python `compileall`, parser JSON workflow y `docker compose config` correctos.
- [x] Prueba directa de heurística/enriquecimiento: resultado `high/sospechoso` y no consulta de IP privada.
- [x] Construcción de imágenes con Docker Desktop.
- [x] Arranque y healthchecks de PostgreSQL, backend, triage, n8n y frontend.
- [x] Smoke test de login/RBAC, dashboard, ingesta, duplicados, triage, incidentes, PDF/DOCX/XLSX y auditoría.
- [x] Importación, activación y ejecución real del workflow n8n con simulador.
- [x] Compilación frontend dentro de Docker/Vite; healthcheck corregido a `127.0.0.1`.
- [x] Verificación final repetible: smoke, RBAC y workflow JSON pasan.

## Pendientes / limitaciones
- Ollama no se descargó ni ejecutó con modelo: la demo usa `heuristic-demo` y el fallback queda documentado.
- VirusTotal, AbuseIPDB, GeoIP, Slack/Telegram y osTicket/Redmine permanecen simulados/desactivados; requieren claves, autorización y pruebas independientes.
- El nodo nativo PostgreSQL de confirmación en n8n conserva una credencial pendiente; la persistencia real de negocio se verificó mediante la API backend contra PostgreSQL. El workflow no bloquea por esa integración opcional.
- `npm install` local sigue condicionado por EPERM de caché npm; la compilación de producción sí fue ejecutada dentro de Docker.
- Credenciales demo son solo locales y deben cambiarse antes de cualquier entorno compartido.

## Próximo comando de continuación
```cmd
docker version
docker compose --env-file .env up --build -d
```
