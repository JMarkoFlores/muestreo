import json, urllib.request, urllib.error

def call(url,method='GET',body=None,headers=None):
 data=None if body is None else json.dumps(body).encode(); req=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json',**(headers or {})},method=method)
 try:
  with urllib.request.urlopen(req,timeout=15) as r:return r.status,r.read()
 except urllib.error.HTTPError as e:return e.code,e.read()
admin=call('http://localhost:8000/api/auth/login','POST',{'username':'lector','password':'lector-local-2026'})
assert admin[0]==200
jwt=json.loads(admin[1])['access_token']; status,body=call('http://localhost:8000/api/incidents','POST',{'alert_id':1,'title':'lector debe ser rechazado'},{'Authorization':f'Bearer {jwt}'})
assert status==403,(status,body)
print('RBAC PASS: lector no puede crear incidentes')
