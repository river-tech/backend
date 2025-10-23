from typing import Optional
from app.models.user import User
from app.db.database import SessionLocal

class AuthService:
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        db = SessionLocal()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
