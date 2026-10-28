# SOC-Lite

Aplicación académica para el triaje automático de alertas de seguridad orientada a una PYME. Integra ingesta Wazuh/OPNsense, n8n, un microservicio FastAPI + LangChain, backend FastAPI, PostgreSQL y frontend React/TypeScript.

> **Estado verificado:** los contenedores se construyeron y están ejecutándose en Docker Desktop. Se verificaron healthchecks, migración/seed, login/RBAC, ingesta, idempotencia, triaje, reportes, auditoría, frontend y el recorrido real del webhook n8n. Ollama y conectores externos permanecen opcionales/simulados.

## Arranque local (Windows CMD)

```cmd
copy .env.example .env
docker version
docker compose --env-file .env up --build -d
```

URLs: frontend `http://localhost:5173`, API/docs `http://localhost:8000/docs`, n8n `http://localhost:5678`, PostgreSQL solo en la red interna, Ollama opcional con `docker compose --profile integrated up -d ollama`.

Parar sin borrar datos: `docker compose stop`. Parar y eliminar contenedores/red: `docker compose down`. **No uses `down -v`** salvo que quieras borrar los volúmenes nombrados `soc_lite_postgres_data`, `soc_lite_n8n_data` y `soc_lite_ollama_data`.

## Demo

Credenciales ficticias, solo para entorno local:

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin-local-2026` | administrador |
| `analista` | `analista-local-2026` | analista |
| `lector` | `lector-local-2026` | lector |

Importa `n8n/soc-lite-demo.json`, activa el workflow y ejecuta:

```cmd
python simulator\send_alert.py --url http://localhost:5678/webhook/soc-lite-alert --count 3
```

Recorrido esperado: simulador → n8n → backend/API → PostgreSQL → triage heurístico demo → resultado → dashboard. La baja se conserva como descartada en el historial de n8n; las medias/altas se persisten.

## Estructura

- `backend/`: API, SQLAlchemy, Alembic, seed, RBAC, auditoría y exportaciones.
- `triage/`: FastAPI, Pydantic, LangChain/Ollama, enriquecimiento simulado y fallback.
- `frontend/`: React + TypeScript + Vite + CSS responsive.
- `n8n/`: workflow JSON y guía de configuración.
- `simulator/`: alertas ficticias.
- `docs/`: arquitectura, modelo, backend, frontend, workflow, datasets y stack.
- `TRACKING.md`: avance y bloqueos de sesión.

## Modo integrado

`USE_OLLAMA=true` y perfil `integrated` habilitan Ollama. Antes de descargar `llama3.2:3b` comprueba espacio; el modelo necesita aproximadamente 2–3 GB más caché, y el perfil no se activa por defecto. No se envían alertas a proveedores LLM externos. VirusTotal, AbuseIPDB y GeoIP permanecen desactivados; al activarlos pueden enviar indicadores a servicios externos y deben configurarse con consentimiento, claves y política de privacidad. IP privadas/reservadas no se consultan públicamente.

Slack/Telegram y osTicket/Redmine están representados en demo por endpoints simulados, sin bloqueos automáticos. Sustituye las URLs y credenciales en n8n solo en un entorno autorizado.

## Verificaciones

Pruebas ejecutadas y repetibles:

```cmd
python scripts\check_workflow.py
python scripts\smoke_test.py
python scripts\rbac_test.py
python -m json.tool n8n\soc-lite-demo.json > nul
docker compose ps
```

El workflow fue importado y activado en n8n durante la verificación. Se enviaron alertas nuevas al webhook y se comprobó en PostgreSQL que terminaron como `completed` con proveedor `heuristic-demo`; las repetidas devolvieron `duplicate` y la baja fue descartada.

La matriz de requisitos y el detalle de las pruebas están en `docs/08-matriz-requisitos.md`.
