from datetime import datetime, timezone
from hashlib import sha256
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from app.database import get_db
from app.models import Alert, EnrichmentData, TriageResult
from app.schemas import AlertIn
from app.deps import get_current_user, require_roles, service_auth
from app.serializers import alert_out
from app.services.audit import audit

router=APIRouter(prefix='/api/alerts',tags=['alerts'])

def dedup_key(data:AlertIn): return sha256(f'{data.source}|{data.external_id or ""}|{data.title}|{data.source_ip or ""}|{data.destination_ip or ""}'.encode()).hexdigest()
@router.get('')
def list_alerts(page:int=Query(1,ge=1),page_size:int=Query(50,ge=1,le=500),severity:str|None=None,status:str|None=None,search:str|None=None,db:Session=Depends(get_db),user=Depends(require_roles('administrador','analista','lector'))):
    q=db.query(Alert).options(joinedload(Alert.triage),joinedload(Alert.enrichment))
    if severity: q=q.filter(Alert.severity==severity)
    if status: q=q.filter(Alert.status==status)
    if search: q=q.filter(or_(Alert.title.ilike(f'%{search}%'),Alert.source_ip.ilike(f'%{search}%'),Alert.external_id.ilike(f'%{search}%')))
    total=q.count(); rows=q.order_by(Alert.received_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    return {'items':[alert_out(a) for a in rows],'page':page,'page_size':page_size,'total':total,'pages':(total+page_size-1)//page_size}
@router.get('/{alert_id}')
def get_alert(alert_id:int,db:Session=Depends(get_db),user=Depends(require_roles('administrador','analista','lector'))):
    a=db.query(Alert).options(joinedload(Alert.triage),joinedload(Alert.enrichment)).filter_by(id=alert_id).first()
    if not a: raise HTTPException(404,'Alerta no encontrada')
    audit(db,user.username,'alerts','detail','ok','alert',alert_id); return alert_out(a)
@router.post('/ingest')
def ingest(data:AlertIn, db:Session=Depends(get_db), _:bool=Depends(service_auth)):
    if data.severity not in {'low','medium','high','critical'}: raise HTTPException(422,'Severidad no válida')
    key=dedup_key(data); existing=db.query(Alert).filter_by(dedup_key=key).first()
    if existing:
        audit(db,'service:n8n','ingestion','duplicate','ok','alert',existing.id,details={'dedup_key':key}); return {'id':existing.id,'status':'duplicate','dedup_key':key}
    a=Alert(**data.model_dump(exclude={'raw_payload'}),raw_payload=data.raw_payload,dedup_key=key,received_at=datetime.now(timezone.utc),status='pending')
    db.add(a); db.commit(); db.refresh(a); audit(db,'service:n8n','ingestion','alert_received','ok','alert',a.id,details={'source':data.source})
    return {'id':a.id,'status':'pending','dedup_key':key}
@router.post('/{alert_id}/enrichment')
def save_enrichment(alert_id:int,payload:dict,db:Session=Depends(get_db),_:bool=Depends(service_auth)):
    a=db.query(Alert).filter_by(id=alert_id).first()
    if not a: raise HTTPException(404,'Alerta no encontrada')
    if a.enrichment: a.enrichment.data=payload.get('data',payload); a.enrichment.provider=payload.get('provider','simulado')
    else: a.enrichment=EnrichmentData(provider=payload.get('provider','simulado'),data=payload.get('data',payload),is_simulated=payload.get('is_simulated',True))
    a.status='processing'; db.commit(); return {'status':'enrichment_saved'}
@router.post('/{alert_id}/triage-result')
def save_triage(alert_id:int,payload:dict,db:Session=Depends(get_db),_:bool=Depends(service_auth)):
    a=db.query(Alert).filter_by(id=alert_id).first()
    if not a: raise HTTPException(404,'Alerta no encontrada')
    t=a.triage or TriageResult(alert_id=alert_id)
    failure=payload.get('error_message') or payload.get('error')
    values={'severity':payload.get('severity') or a.severity,'verdict':payload.get('verdict') or 'error','summary':payload.get('summary') or 'No fue posible completar el triaje; revisar manualmente.','recommendations':payload.get('recommendations') or ['Reintentar el triaje','Revisar la alerta manualmente'],'confidence':payload.get('confidence') or 0.0,'provider':payload.get('provider') or 'triage-error','model':payload.get('model'),'error_message':failure}
    for k,v in values.items(): setattr(t,k,v)
    a.triage=t; a.status='error' if failure else 'completed'; a.completed_at=datetime.now(timezone.utc); db.add(t); db.commit(); audit(db,'service:triage','triage','completed' if not failure else 'error','ok','alert',alert_id); return {'status':a.status,'id':alert_id}
