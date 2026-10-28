"""Smoke test SOC-Lite tras arrancar Compose. Solo usa biblioteca estándar."""
import io, json, sys, time, urllib.error, urllib.request, zipfile

API = 'http://localhost:8000'
SERVICE = 'soc-lite-service-local'

def call(url, method='GET', body=None, headers=None):
    data = None if body is None else json.dumps(body).encode()
    h = {'Content-Type': 'application/json', **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read()
        content = r.headers.get('content-type', '')
        return r.status, (json.loads(raw) if 'json' in content else raw)

def expect(condition, message):
    if not condition: raise AssertionError(message)

def main():
    for endpoint in ('/health',):
        status, data = call(API + endpoint); expect(status == 200 and data['status'] == 'ok', 'health backend')
    status, login = call(API + '/api/auth/login', 'POST', {'username':'admin','password':'admin-local-2026'})
    expect(status == 200 and login['user']['roles'] == ['administrador'], 'login admin/RBAC')
    token = login['access_token']; auth = {'Authorization': f'Bearer {token}'}
    status, summary = call(API + '/api/dashboard/summary', headers=auth); expect(status == 200 and 'by_severity' in summary, 'dashboard')
    alert = {'external_id':f'SMOKE-E2E-{int(time.time())}','source':'wazuh','title':'Brute force smoke test','description':'failed login repeated','source_ip':'8.8.8.8','destination_ip':'10.0.0.9','severity':'high','raw_payload':{'test':True}}
    status, created = call(API + '/api/alerts/ingest', 'POST', alert, {'X-API-Key':SERVICE}); expect(status == 200 and created['status'] == 'pending', 'ingestion')
    status, duplicate = call(API + '/api/alerts/ingest', 'POST', alert, {'X-API-Key':SERVICE}); expect(status == 200 and duplicate['status'] == 'duplicate', 'idempotencia')
    alert_id = created['id']
    triage_payload = {'severity':'high','verdict':'sospechoso','summary':'Smoke test heurístico','recommendations':['Revisar manualmente'],'confidence':0.72,'provider':'heuristic-demo','enrichment':{'is_private':False}}
    status, saved = call(f'{API}/api/alerts/{alert_id}/triage-result', 'POST', triage_payload, {'X-API-Key':SERVICE}); expect(status == 200 and saved['status'] == 'completed', 'resultado triage')
    status, detail = call(f'{API}/api/alerts/{alert_id}', headers=auth); expect(status == 200 and detail['triage']['provider'] == 'heuristic-demo', 'detalle')
    status, incident = call(API + '/api/incidents', 'POST', {'alert_id':alert_id,'title':'Incidente smoke','notes':'Revisión humana','reviewed_verdict':'falso_positivo'}, auth); expect(status == 200, 'incidente')
    status, incidents = call(API + '/api/incidents', headers=auth); expect(any(x['id'] == incident['id'] for x in incidents), 'listado incidentes')
    for fmt, signature in [('pdf', b'%PDF'), ('docx', b'PK'), ('xlsx', b'PK')]:
        status, blob = call(f'{API}/api/reports/export/{fmt}', headers=auth); expect(status == 200 and blob.startswith(signature), f'export {fmt}')
        with zipfile.ZipFile(io.BytesIO(blob)) if fmt in ('docx','xlsx') else _NullContext() as z:
            if fmt in ('docx','xlsx'): expect(z.testzip() is None, f'zip {fmt}')
    status, audit = call(API + '/api/audit', headers=auth); expect(status == 200 and len(audit) > 0, 'auditoría')
    print('SMOKE PASS: health, login/RBAC, dashboard, ingestion, duplicate, triage, detail, incident, PDF/DOCX/XLSX y audit')

class _NullContext:
    def __enter__(self): return self
    def __exit__(self, *args): return False

if __name__ == '__main__':
    try: main()
    except Exception as exc:
        print(f'SMOKE FAIL: {type(exc).__name__}: {exc}', file=sys.stderr); raise
