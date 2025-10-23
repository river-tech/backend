from typing import List, Optional
from app.models.purchase import Purchase
from app.db.database import SessionLocal

class OrderService:
    @staticmethod
    def get_orders_by_user_id(user_id: str) -> List[Purchase]:
        db = SessionLocal()
        try:
            return db.query(Purchase).filter(Purchase.user_id == user_id).all()
        finally:
            db.close()
    
    @staticmethod
    def get_order_by_id(order_id: str) -> Optional[Purchase]:
        db = SessionLocal()
        try:
            return db.query(Purchase).filter(Purchase.id == order_id).first()
        finally:
            db.close()
