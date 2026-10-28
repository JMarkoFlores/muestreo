from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Incident, Alert
from app.schemas import IncidentIn, IncidentPatch, IncidentOut
from app.deps import require_roles
from app.services.audit import audit

router=APIRouter(prefix='/api/incidents',tags=['incidents'])
@router.get('',response_model=list[IncidentOut])
def list_incidents(db:Session=Depends(get_db),user=Depends(require_roles('administrador','analista','lector'))): return db.query(Incident).order_by(Incident.updated_at.desc()).all()
@router.post('',response_model=IncidentOut)
def create(data:IncidentIn,db:Session=Depends(get_db),user=Depends(require_roles('administrador','analista'))):
    if not db.query(Alert).filter_by(id=data.alert_id).first(): raise HTTPException(404,'Alerta no encontrada')
    i=Incident(**data.model_dump()); db.add(i); db.commit(); db.refresh(i); audit(db,user.username,'incidents','create','ok','incident',i.id); return i
@router.patch('/{incident_id}',response_model=IncidentOut)
def update(incident_id:int,data:IncidentPatch,db:Session=Depends(get_db),user=Depends(require_roles('administrador','analista'))):
    i=db.query(Incident).filter_by(id=incident_id).first()
    if not i: raise HTTPException(404,'Incidente no encontrado')
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(i,k,v)
    db.commit(); db.refresh(i); audit(db,user.username,'incidents','update','ok','incident',incident_id); return i
