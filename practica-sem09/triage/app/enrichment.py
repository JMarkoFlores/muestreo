import ipaddress
from typing import Any

def enrich(ip:str|None)->dict[str,Any]:
    if not ip: return {'indicator':None,'is_private':None,'consulted':[],'note':'Sin indicador IP'}
    try: obj=ipaddress.ip_address(ip); private=obj.is_private or obj.is_loopback or obj.is_reserved or obj.is_link_local
    except ValueError: return {'indicator':ip,'is_private':None,'consulted':[],'note':'Indicador IP no válido'}
    if private: return {'indicator':ip,'is_private':True,'consulted':[],'note':'No se consulta IP privada/reservada en servicios públicos'}
    # Demo: nunca realiza llamadas externas sin ENABLE_EXTERNAL_ENRICHMENT explícito.
    return {'indicator':ip,'is_private':False,'consulted':['VirusTotal (simulado)','AbuseIPDB (simulado)','GeoIP (simulado)'],'virustotal':{'reputation':'unknown'},'abuseipdb':{'confidence':0},'geoip':{'country':'ZZ','asn':'AS-DEMO'},'note':'Enriquecimiento simulado; no se enviaron indicadores externos'}
