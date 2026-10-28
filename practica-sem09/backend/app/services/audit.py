from sqlalchemy.orm import Session
from app.models import AuditLog

def audit(db: Session, actor: str, module: str, action: str, result: str, resource_type=None, resource_id=None, correlation_id=None, details=None):
    db.add(AuditLog(actor=actor,module=module,action=action,result=result,resource_type=resource_type,resource_id=str(resource_id) if resource_id is not None else None,correlation_id=correlation_id,details=details or {}))
    db.commit()
