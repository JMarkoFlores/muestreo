from fastapi import FastAPI
from .schemas import AlertData, TriageResponse
from .config import settings
from .enrichment import enrich
from .llm import heuristic, ollama
app=FastAPI(title='SOC-Lite Triage Service',version='1.0.0')
@app.get('/health')
def health(): return {'status':'ok','service':'triage','provider':'ollama' if settings.use_ollama else 'heuristic-demo','external_enrichment':settings.enable_external_enrichment}
@app.post('/triage',response_model=TriageResponse)
def triage(alert:AlertData):
    enrichment=enrich(alert.source_ip)
    if settings.use_ollama:
        try: return ollama(alert,enrichment)
        except Exception as exc:
            result=heuristic(alert,enrichment); result.error_message=f'Ollama no disponible: {type(exc).__name__}; se usó fallback heurístico DEMO'; return result
    return heuristic(alert,enrichment)
