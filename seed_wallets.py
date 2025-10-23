#!/usr/bin/env python3
"""
Script để tạo ví và nạp 100,000 VND cho tất cả user hiện có
"""
import requests
import json
from app.db.database import SessionLocal
from app.models.user import User
from app.models.wallet import Wallet, WalletTransaction
from app.models.enums import TransactionType, TransactionStatus
import uuid
from datetime import datetime

def create_wallet_for_user(user_id, email):
    """Tạo ví cho user"""
    try:
        # Tạo ví với 100,000 VND
        wallet = Wallet(
            id=uuid.uuid4(),
            user_id=user_id,
            balance=100000.0,
            total_deposited=100000.0,
            total_spent=0.0
        )
        
        return wallet
    except Exception as e:
        print(f"❌ Error creating wallet for {email}: {e}")
        return None

def create_deposit_transaction(wallet_id, amount, note):
    """Tạo transaction nạp tiền"""
    try:
        transaction = WalletTransaction(
            id=uuid.uuid4(),
            wallet_id=wallet_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            status=TransactionStatus.SUCCESS,
            note=note
        )
        return transaction
    except Exception as e:
        print(f"❌ Error creating transaction: {e}")
        return None

def main():
    """Main function"""
    db = SessionLocal()
    
    try:
        # Lấy tất cả users
        users = db.query(User).all()
        print(f"📋 Found {len(users)} users in database")
        
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                # Kiểm tra xem user đã có ví chưa
                existing_wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                
                if existing_wallet:
                    print(f"✅ User {user.email} already has wallet with {existing_wallet.balance:,} VND")
                    continue
                
                # Tạo ví mới
                wallet = create_wallet_for_user(user.id, user.email)
                if not wallet:
                    error_count += 1
                    continue
                
                db.add(wallet)
                db.flush()  # Get wallet ID
                
                # Tạo transaction nạp tiền
                transaction = create_deposit_transaction(
                    wallet.id, 
                    100000.0, 
                    f"Initial wallet balance for {user.email} - 100,000 VND"
                )
                
                if transaction:
                    db.add(transaction)
                
                db.commit()
                print(f"✅ Created wallet for {user.email} with 100,000 VND")
                success_count += 1
                
            except Exception as e:
                print(f"❌ Error processing user {user.email}: {e}")
                db.rollback()
                error_count += 1
        
        print(f"\n🎉 Completed!")
        print(f"✅ Successfully processed: {success_count} users")
        print(f"❌ Errors: {error_count} users")
        
        # Hiển thị kết quả cuối cùng
        print(f"\n📊 Final wallet status:")
        wallets = db.query(Wallet).all()
        for wallet in wallets:
            user = db.query(User).filter(User.id == wallet.user_id).first()
            if user:
                print(f"- {user.email}: {wallet.balance:,} VND (Deposited: {wallet.total_deposited:,}, Spent: {wallet.total_spent:,})")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
