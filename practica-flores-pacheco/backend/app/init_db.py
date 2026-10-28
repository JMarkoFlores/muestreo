from sqlalchemy import select
from .db import Base, SessionLocal, engine
from .models import User
from .security import hash_password

ADMIN_EMAIL = "admin@sentinelbank.com"


def main():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.email == ADMIN_EMAIL)):
            db.add(User(email=ADMIN_EMAIL, full_name="Administrador SOC", role="admin", password_hash=hash_password("postgres")))
            db.commit()
    print("Database schema initialized")


if __name__ == "__main__":
    main()
