# Operación y límites

## Docker Desktop

Si aparece `Access is denied` en `dockerDesktopLinuxEngine`, abrir Docker Desktop, confirmar Linux containers, comprobar que el usuario pertenece al grupo local `docker-users`, cerrar/iniciar sesión y repetir `docker version`. No eliminar volúmenes de otros proyectos. Este proyecto usa nombres de volumen propios.

## Ollama

El modo demo no descarga modelo. Para integrado, comprueba disco/memoria antes de ejecutar:

```cmd
docker system df
docker compose --profile integrated up -d ollama
docker compose exec ollama ollama pull llama3.2:3b
docker compose up -d --build triage
```

La descarga es de aproximadamente 2–3 GB, variable por cuantización/caché. Si no hay recursos, conserva `USE_OLLAMA=false`.

## Integraciones externas

VirusTotal/AbuseIPDB/GeoIP, Slack/Telegram y osTicket/Redmine requieren credenciales, URLs, autorización y pruebas separadas. Los indicadores pueden salir a proveedores externos; documentar base legal/política. No usar IP privadas/reservadas en servicios públicos.
