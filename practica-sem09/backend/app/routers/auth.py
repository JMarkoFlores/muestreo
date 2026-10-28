from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenOut
from app.security import verify_password, create_token
from app.deps import get_current_user
from app.serializers import user_out
from app.services.audit import audit

router=APIRouter(prefix='/api/auth',tags=['auth'])
@router.post('/login',response_model=TokenOut)
def login(data:LoginRequest, db:Session=Depends(get_db)):
    user=db.query(User).filter(User.username==data.username).first()
    if not user or not verify_password(data.password,user.password_hash):
        audit(db,data.username,'auth','login','denied'); raise HTTPException(401,'Usuario o contraseña incorrectos')
    token=create_token(user.username,[r.name for r in user.roles]); audit(db,user.username,'auth','login','ok')
    return {'access_token':token,'user':user_out(user)}
@router.post('/logout')
def logout(user=Depends(get_current_user),db:Session=Depends(get_db)):
    audit(db,user.username,'auth','logout','ok'); return {'message':'Sesión cerrada'}
@router.get('/me')
def me(user=Depends(get_current_user)): return user_out(user)
