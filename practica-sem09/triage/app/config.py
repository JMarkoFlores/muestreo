from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file='.env',extra='ignore')
    ollama_base_url:str='http://ollama:11434'; ollama_model:str='llama3.2:3b'; use_ollama:bool=False; enable_external_enrichment:bool=False
    virustotal_api_key:str=''; abuseipdb_api_key:str=''; geoip_provider:str='simulado'
settings=Settings()
