import json,sys
p='n8n/soc-lite-demo.json'
with open(p,encoding='utf-8') as f: w=json.load(f)
names={n['name'] for n in w['nodes']}; required={'Webhook alerta','Normalizar y filtrar','Persistir alerta pendiente (PostgreSQL vía API)','HTTP · Microservicio LangChain','Guardar resultado antes de notificar','Switch severidad','Notificar alta (simulado)','Crear ticket (simulado)','Registrar auditoría'}
missing=required-names
if missing: raise SystemExit(f'Faltan nodos: {missing}')
print(f'Workflow JSON válido: {len(w["nodes"])} nodos; pasos obligatorios presentes')
