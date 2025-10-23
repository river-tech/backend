from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Purchase Management Schemas
class PurchaseOverviewResponse(BaseModel):
    total_purchases: int
    completed: int
    pending: int
    total_revenue: float

class PurchaseUserInfo(BaseModel):
    id: str
    name: str
    email: str

class PurchaseWorkflowInfo(BaseModel):
    id: str
    title: str
    price: float

class PurchaseListItem(BaseModel):
    id: str
    user: PurchaseUserInfo
    workflow: PurchaseWorkflowInfo
    amount: float
    status: str
    payment_method: str
    paid_at: Optional[str]

class PurchaseListResponse(BaseModel):
    purchases: List[PurchaseListItem]
    pagination: dict

class PurchaseDetailResponse(BaseModel):
    id: str
    user: PurchaseUserInfo
    workflow: PurchaseWorkflowInfo
    bank_name: Optional[str]
    transfer_code: Optional[str]
    status: str
    amount: float
    paid_at: Optional[str]

class PurchaseStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(ACTIVE|PENDING|REJECT)$")

class PurchaseStatusUpdateResponse(BaseModel):
    success: bool
    message: str
