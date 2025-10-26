from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class WalletResponse(BaseModel):
    balance: float
    total_deposited: float
    total_spent: float

class WalletInfoResponse(BaseModel):
    balance: float
    total_deposited: float
    total_spent: float

class WalletTransactionResponse(BaseModel):
    id: UUID
    transaction_type: str
    amount: float
    status: str
    bank_name: Optional[str]
    bank_account: Optional[str]
    transfer_code: Optional[str]
    note: Optional[str]
    created_at: datetime

class DepositRequest(BaseModel):
    bank_name: str = Field(..., min_length=1, description="Bank name is required")
    bank_account: str = Field(..., min_length=1, description="Bank account is required")
    transfer_code: str = Field(..., min_length=1, description="Transfer code is required")
    amount: float = Field(..., gt=0, description="Amount must be a positive number")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if not isinstance(v, (int, float)):
            raise ValueError('Amount must be a number')
        return float(v)
    
    @field_validator('bank_name', 'bank_account', 'transfer_code')
    @classmethod
    def validate_string_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

class DepositResponse(BaseModel):
    success: bool
    message: str
    transaction_id: UUID

class PurchaseWithWalletRequest(BaseModel):
    use_wallet: bool = True

class PurchaseWithWalletResponse(BaseModel):
    success: bool
    message: str
    wallet_balance: float
    purchase_id: UUID

class LastBankInfoResponse(BaseModel):
    bank_name: Optional[str]
    bank_account: Optional[str]

class AdminActivateDepositRequest(BaseModel):
    transaction_id: UUID = Field(..., description="Transaction ID to activate")

class AdminActivateDepositResponse(BaseModel):
    success: bool
    message: str
    transaction_id: UUID
    user_id: UUID
    amount: float
    new_wallet_balance: float
