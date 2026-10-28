from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Alert, Incident, TriageResult
from app.deps import require_roles
from app.services.audit import audit

router=APIRouter(prefix='/api/dashboard',tags=['dashboard'])
@router.get('/summary')
def summary(db:Session=Depends(get_db),user=Depends(require_roles('administrador','analista','lector'))):
    total=db.query(Alert).count(); pending=db.query(Alert).filter(Alert.status.in_(['pending','processing'])).count(); processed=db.query(Alert).filter(Alert.status.in_(['completed','error'])).count()
    severities={s:db.query(Alert).filter(Alert.severity==s).count() for s in ['critical','high','medium','low']}
    open_incidents=db.query(Incident).filter(Incident.status.in_(['open','investigating'])).count()
    completed=db.query(Alert).filter(Alert.completed_at.isnot(None),Alert.received_at.isnot(None)).all()
    mttt=sum((a.completed_at-a.received_at).total_seconds() for a in completed)/len(completed) if completed else None
    reviewed=db.query(Incident).filter(Incident.reviewed_verdict.isnot(None)).all(); fp=sum(1 for i in reviewed if i.reviewed_verdict=='falso_positivo')/len(reviewed) if reviewed else None
    by_source=[{'source':s,'count':c} for s,c in db.query(Alert.source,func.count(Alert.id)).group_by(Alert.source).order_by(func.count(Alert.id).desc()).all()]
    days=[]
    for n in range(6,-1,-1):
        d=(datetime.now(timezone.utc)-timedelta(days=n)).date(); days.append({'date':str(d),'count':db.query(Alert).filter(func.date(Alert.received_at)==d).count()})
    audit(db,user.username,'dashboard','summary','ok'); return {'total':total,'pending':pending,'processed':processed,'by_severity':severities,'open_incidents':open_incidents,'mttt_seconds':mttt,'false_positive_rate':fp,'by_source':by_source,'timeline':days}
