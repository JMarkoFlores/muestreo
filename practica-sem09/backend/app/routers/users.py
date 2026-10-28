from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Role
from app.security import hash_password
from app.deps import require_roles
from app.services.audit import audit
from app.serializers import user_out
class UserCreate(BaseModel): username:str=Field(min_length=2,max_length=80); email:str; full_name:str; password:str=Field(min_length=8,max_length=200); role:str='lector'
class UserPatch(BaseModel): full_name:str|None=None; email:str|None=None; is_active:bool|None=None; role:str|None=None; password:str|None=Field(default=None,min_length=8,max_length=200)
router=APIRouter(prefix='/api/users',tags=['users'])
@router.get('')
def list_users(db:Session=Depends(get_db),user=Depends(require_roles('administrador'))): return [user_out(x) for x in db.query(User).order_by(User.username).all()]
@router.post('')
def create_user(data:UserCreate,db:Session=Depends(get_db),user=Depends(require_roles('administrador'))):
    if db.query(User).filter((User.username==data.username)|(User.email==data.email)).first(): raise HTTPException(409,'Usuario o email ya existe')
    role=db.query(Role).filter_by(name=data.role).first()
    if not role: raise HTTPException(422,'Rol no válido')
    u=User(username=data.username,email=data.email,full_name=data.full_name,password_hash=hash_password(data.password),roles=[role]); db.add(u); db.commit(); db.refresh(u); audit(db,user.username,'users','create','ok','user',u.id); return user_out(u)
@router.patch('/{user_id}')
def update_user(user_id:int,data:UserPatch,db:Session=Depends(get_db),user=Depends(require_roles('administrador'))):
    u=db.query(User).filter_by(id=user_id).first()
    if not u: raise HTTPException(404,'Usuario no encontrado')
    for k in ('full_name','email','is_active'):
        if getattr(data,k) is not None: setattr(u,k,getattr(data,k))
    if data.password: u.password_hash=hash_password(data.password)
    if data.role:
        role=db.query(Role).filter_by(name=data.role).first()
        if not role: raise HTTPException(422,'Rol no válido')
        u.roles=[role]
    db.commit(); db.refresh(u); audit(db,user.username,'users','update','ok','user',user_id); return user_out(u)
