from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.security import decode_token
from app.config import settings

bearer=HTTPBearer(auto_error=False)
def get_current_user(credentials: HTTPAuthorizationCredentials=Depends(bearer), db: Session=Depends(get_db)):
    if not credentials: raise HTTPException(status_code=401, detail='Autenticación requerida')
    payload=decode_token(credentials.credentials)
    if not payload or not payload.get('sub'): raise HTTPException(status_code=401, detail='Token inválido o caducado')
    user=db.query(User).filter(User.username==payload['sub'],User.is_active==True).first()
    if not user: raise HTTPException(status_code=401, detail='Usuario no disponible')
    return user

def require_roles(*allowed):
    def checker(user=Depends(get_current_user)):
        names={r.name for r in user.roles}
        if not names.intersection(allowed): raise HTTPException(status_code=403, detail='Permisos insuficientes')
        return user
    return checker

def service_auth(x_api_key: str=Header(default='')):
    if x_api_key != settings.service_api_key: raise HTTPException(status_code=401, detail='Clave de servicio inválida')
    return True
