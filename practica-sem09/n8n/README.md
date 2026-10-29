# Workflow n8n

Archivo importable: `soc-lite-demo.json`. Compatible con n8n `1.119.2`.

1. **Webhook alerta**: `POST /webhook/soc-lite-alert`; entrada Wazuh/OPNsense.
2. **Normalizar y filtrar**: Code node normaliza campos y descarta severidad `low`; deja `discarded=true` para trazabilidad.
3. **Persistir alerta pendiente**: HTTP al backend, que calcula `dedup_key`, aplica idempotencia y persiste en PostgreSQL. Timeout 10 s y salida controlada.
4. **HTTP · Microservicio LangChain**: llama `triage:8001/triage`; el microservicio usa Ollama si está activado o heurística demo etiquetada.
5. **Guardar resultado antes de notificar**: endpoint interno guarda enrichment/triage y cambia estado.
6. **PostgreSQL · confirmar resultado**: el backend ya actualiza `alerts` en PostgreSQL al guardar el resultado. El nodo nativo opcional puede confirmar el estado con la credencial `SOC-Lite PostgreSQL`; si no se configura, el guardado por API conserva el dato y el nodo tolera el error.
7. **Switch severidad**: enruta critical/high a notificación y ticket simulados; medium solo responde; low ya quedó descartada.
8. **Notificación y ticket**: en demo son HTTP simulados; en integrado se sustituyen por Slack/Telegram y osTicket/Redmine. No se ejecutan bloqueos.
9. **Registrar auditoría**: actor `service:n8n`, módulo `workflow`, acción y recurso.

## Importación y configuración

1. Abrir `http://localhost:5678`, iniciar sesión con los valores de `.env`.
2. `Workflows > Import from File`, seleccionar este JSON.
3. Verificar que los nombres DNS Docker `backend` y `triage` funcionan dentro de n8n. Si n8n corre fuera de Compose, usar `host.docker.internal`/URLs locales.
4. Crear en n8n la credencial PostgreSQL `SOC-Lite PostgreSQL` con host `postgres`, puerto `5432`, base/usuario/contraseña de `.env`; asociarla al nodo nativo. En la versión integrada sustituir los endpoints simulados de notificación/ticket. El backend requiere `X-API-Key` igual a `SERVICE_API_KEY`.
5. Guardar y activar. Probar con `python simulator/send_alert.py`.

La persistencia de negocio se realiza mediante el endpoint backend para asegurar validación, idempotencia y auditoría; PostgreSQL es la base real detrás del endpoint. El nodo nativo posterior confirma el estado cuando se configura la credencial interna. El nodo `Evitar triaje duplicado` evita llamar al microservicio cuando el backend responde `status=duplicate`. Las salidas HTTP tienen timeouts y modo tolerante para que la alerta permanezca persistida. El workflow es operativo en demo sin credenciales externas; la credencial DB interna mejora la comprobación nativa.


## Simulador Automático Cada 1 Minuto

Archivo importable: `soc-lite-simulator-cron.json`.

Este workflow automatiza la ejecución periódica equivalente a `simulator/send_alert.py`:
1. **Schedule Trigger (`Cada 1 minuto`)**: Dispara el workflow automáticamente cada 60 segundos.
2. **Code Node (`Generar Alertas`)**: Genera el mismo set de 3 alertas simuladas (alta, media y baja) con sufijo temporal dinámico único por minuto para evitar falsos duplicados.
3. **HTTP Request (`Enviar al Webhook de n8n`)**: Realiza `POST` a `http://localhost:5678/webhook/soc-lite-alert`, activando el flujo principal de ingesta, triaje y persistencia para que el dashboard reciba datos en tiempo real.

Se encuentra activo en n8n y puede pausarse o reactivarse en cualquier momento desde la interfaz web (`http://localhost:5678`).
