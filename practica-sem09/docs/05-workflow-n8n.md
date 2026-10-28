# 5. Workflow n8n

El JSON está en `n8n/soc-lite-demo.json`; el detalle por nodo, entradas, salidas, credenciales, timeouts y tratamiento de errores está en `n8n/README.md`. Se importan 14 nodos: webhook, código de normalización, filtro, persistencia backend/PostgreSQL, guardia anti-duplicado, HTTP triage LangChain, guardado de resultado, confirmación PostgreSQL nativa, switch por severidad, notificación, ticket, auditoría y respuesta.

La demo simula Slack/Telegram y osTicket/Redmine; no contacta sistemas externos. El resultado se guarda antes de notificar. El microservicio es quien contiene LangChain: no se inventa un nodo LangChain n8n.

En integración sustituye endpoints simulados y registra credenciales de n8n. Las alertas duplicadas se resuelven por `dedup_key` en backend y las salidas HTTP usan timeouts/salida tolerante para registrar errores sin borrar la alerta.
