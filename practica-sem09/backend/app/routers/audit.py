from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AuditLog
from app.deps import require_roles

router=APIRouter(prefix='/api/audit',tags=['audit'])

@router.get('')
def list_audit(limit:int=Query(100,ge=1,le=500),db:Session=Depends(get_db),user=Depends(require_roles('administrador','analista','lector'))):
    return [{'id':x.id,'actor':x.actor,'occurred_at':x.occurred_at,'module':x.module,'action':x.action,'result':x.result,'resource_type':x.resource_type,'resource_id':x.resource_id,'correlation_id':x.correlation_id,'details':x.details} for x in db.query(AuditLog).order_by(AuditLog.occurred_at.desc()).limit(limit).all()]
