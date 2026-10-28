from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import service_auth
from app.services.audit import audit
router=APIRouter(prefix='/api/internal',tags=['internal'])
@router.post('/audit')
def integration_audit(payload:dict,db:Session=Depends(get_db),_:bool=Depends(service_auth)):
    audit(db,payload.get('actor','service'),payload.get('module','integration'),payload.get('action','unknown'),payload.get('result','ok'),resource_type=payload.get('resource_type'),resource_id=payload.get('resource_id'),correlation_id=payload.get('correlation_id'))
    return {'status':'recorded'}
