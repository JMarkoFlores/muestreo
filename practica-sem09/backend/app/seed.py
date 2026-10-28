from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Role, Permission, Alert, EnrichmentData, TriageResult
from app.security import hash_password
from app.services.audit import audit
from datetime import datetime, timezone, timedelta
import hashlib

def seed():
    db:Session=SessionLocal()
    try:
        perms=['alerts.read','alerts.write','incidents.read','incidents.write','reports.export','users.manage','audit.read']
        pmap={p:db.query(Permission).filter_by(code=p).first() or Permission(code=p) for p in perms}
        for p in pmap.values(): db.add(p)
        db.flush()
        roles={}
        for name,codes in {'administrador':perms,'analista':['alerts.read','alerts.write','incidents.read','incidents.write','reports.export'],'lector':['alerts.read','incidents.read']}.items():
            role=db.query(Role).filter_by(name=name).first() or Role(name=name)
            role.permissions=[pmap[c] for c in codes]; db.add(role); roles[name]=role
        db.flush()
        users=[('admin','admin@soc-lite.local','Administrador SOC','admin-local-2026','administrador'),('analista','analista@soc-lite.local','Analista de demostración','analista-local-2026','analista'),('lector','lector@soc-lite.local','Lector de demostración','lector-local-2026','lector')]
        for username,email,full,password,role_name in users:
            u=db.query(User).filter_by(username=username).first() or User(username=username,email=email,full_name=full,password_hash=hash_password(password))
            u.roles=[roles[role_name]]; db.add(u)
        db.flush()
        if db.query(Alert).count()==0:
            base=datetime.now(timezone.utc)-timedelta(hours=4)
            samples=[('WAZUH-1001','wazuh','Inicio de sesión sospechoso','Múltiples fallos de autenticación en servidor', '198.51.100.23','10.0.0.5','high'),('OPN-2001','opnsense','Escaneo de puertos detectado','Conexiones a 20 puertos en 60 segundos','203.0.113.44','192.168.1.10','medium'),('WAZUH-1002','wazuh','Regla informativa','Cambio esperado de configuración','10.0.0.12','10.0.0.1','low'),('WAZUH-DUP','wazuh','Duplicado de prueba','Mismo evento para comprobar idempotencia','198.51.100.25','10.0.0.6','high')]
            for i,(eid,src,title,desc,sip,dip,sev) in enumerate(samples):
                key=hashlib.sha256(f'{src}:{eid}'.encode()).hexdigest()
                a=Alert(external_id=eid,source=src,title=title,description=desc,source_ip=sip,destination_ip=dip,severity=sev,status='completed' if sev!='low' else 'pending',raw_payload={'seed':True,'external_id':eid},dedup_key=key,received_at=base+timedelta(minutes=i*35))
                db.add(a); db.flush()
                if sev!='low':
                    a.enrichment=EnrichmentData(provider='simulado',data={'indicator':sip,'note':'Datos ficticios para práctica académica','is_private':False},is_simulated=True)
                    a.triage=TriageResult(severity=sev,verdict='sospechoso' if sev=='high' else 'requiere_revision',summary='Resultado de semilla ficticia para mostrar el dashboard.',recommendations=['Validar en consola del sensor','Revisar contexto histórico'],confidence=.78,provider='heuristic-demo')
            db.commit(); audit(db,'seed','system','seed','ok',details={'demo':True})
    finally: db.close()
if __name__=='__main__': seed()
