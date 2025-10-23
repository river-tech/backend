from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class OrderResponse(BaseModel):
    id: str
    user_id: str
    workflow_id: str
    amount: float
    status: str
    payment_method: str
    paid_at: Optional[str]
    created_at: str

class OrderCreateRequest(BaseModel):
    workflow_id: str
    payment_method: str = "CARD"

class InvoiceResponse(BaseModel):
    invoice_number: str
    issued_at: str
    status: str
    billing_name: str
    billing_email: str
    workflow: dict
    amount: float

class PurchaseResponse(BaseModel):
    id: str
    user_id: str
    workflow_id: str
    amount: float
    status: str
    payment_method: str
    paid_at: Optional[str]
    created_at: str
    workflow: dict

class PurchaseCreateRequest(BaseModel):
    workflow_id: str
    payment_method: str = "CARD"
