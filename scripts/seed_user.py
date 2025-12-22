from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import User
from app.core.security import hash_password

EMAIL = "jywan@test.com"
PASSWORD = "test"

def main():
    db: Session = SessionLocal()
    try:
        exists = db.query(User).filter(User.email == EMAIL).first()
        if exists:
            print("user already exists:", EMAIL)
            return
        u = User(email=EMAIL, password_hash=hash_password(PASSWORD))
        db.add(u)
        db.commit()
        db.refresh(u)
        print("Create test user:", u.id, u.email)
    finally:
        db.close()

if __name__ == "__main__":
    main()