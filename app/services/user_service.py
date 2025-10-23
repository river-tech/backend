from typing import List, Optional
from app.models.user import User
from app.db.database import SessionLocal

class UserService:
    @staticmethod
    def get_all_users() -> List[User]:
        db = SessionLocal()
        try:
            return db.query(User).all()
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
