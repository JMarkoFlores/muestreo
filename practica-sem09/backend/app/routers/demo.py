from fastapi import APIRouter, Depends
from app.deps import service_auth
router=APIRouter(prefix='/demo',tags=['demo'])
@router.post('/notification')
def notification(payload:dict, _:bool=Depends(service_auth)): return {'status':'simulated','kind':'notification','payload':payload}
@router.post('/ticket')
def ticket(payload:dict, _:bool=Depends(service_auth)): return {'status':'simulated','kind':'ticket','ticket_id':f'DEMO-{payload.get("alert_id","NA")}','payload':payload}
@router.post('/audit')
def integration_audit(payload:dict, _:bool=Depends(service_auth)): return {'status':'recorded','payload':payload}
