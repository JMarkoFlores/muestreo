from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pwdlib import PasswordHash
from app.config import settings

password_hash = PasswordHash.recommended()
def hash_password(password: str) -> str: return password_hash.hash(password)
def verify_password(password: str, hashed: str) -> bool: return password_hash.verify(password, hashed)
def create_token(subject: str, roles: list[str]) -> str:
    exp=datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({'sub':subject,'roles':roles,'exp':exp}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
def decode_token(token: str):
    try: return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError: return None
