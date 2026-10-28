# Microservicio de triaje

`POST /triage` recibe una alerta validada y responde con `TriageResponse` Pydantic. El modo demo (`USE_OLLAMA=false`) usa un clasificador heurístico identificado como `heuristic-demo`; no es un resultado LLM. Con `USE_OLLAMA=true` usa LangChain + `ChatOllama`. Si Ollama falla, la alerta se conserva y se devuelve fallback etiquetado.

Las alertas son datos no confiables. Los conectores públicos permanecen deshabilitados por defecto y no consultan IP privadas/reservadas. Para VirusTotal/AbuseIPDB/GeoIP real se requiere implementar/activar el proveedor y aceptar que los indicadores pueden salir del entorno.