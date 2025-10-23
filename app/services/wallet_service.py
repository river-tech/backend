from typing import Optional
from app.models.wallet import Wallet, WalletTransaction
from app.db.database import SessionLocal

class WalletService:
    @staticmethod
    def get_wallet_by_user_id(user_id: str) -> Optional[Wallet]:
        db = SessionLocal()
        try:
            return db.query(Wallet).filter(Wallet.user_id == user_id).first()
        finally:
            db.close()
    
    @staticmethod
    def create_wallet(user_id: str) -> Wallet:
        db = SessionLocal()
        try:
            wallet = Wallet(user_id=user_id)
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
            return wallet
        finally:
            db.close()
