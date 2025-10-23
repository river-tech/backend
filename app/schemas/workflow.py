from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class WorkflowResponse(BaseModel):
    id: str
    title: str
    description: str
    price: float
    status: str
    features: List[str]
    downloads_count: int
    time_to_setup: Optional[int]
    video_demo: Optional[str]
    flow: Optional[Dict[str, Any]]
    rating_avg: Optional[float]
    created_at: str
    updated_at: str
    categories: List[str] = []

class WorkflowCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    features: List[str] = []
    time_to_setup: Optional[int] = Field(None, ge=1)
    video_demo: Optional[str] = None
    flow: Optional[Dict[str, Any]] = None
    category_ids: List[str] = []

class WorkflowUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)
    status: Optional[str] = None
    features: Optional[List[str]] = None
    time_to_setup: Optional[int] = Field(None, ge=1)
    video_demo: Optional[str] = None
    flow: Optional[Dict[str, Any]] = None
    category_ids: Optional[List[str]] = None

class CategoryResponse(BaseModel):
    id: str
    name: str
    image_url: Optional[str]
    created_at: str

class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    image_url: Optional[str] = None

class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    image_url: Optional[str] = None

class WorkflowCategoryResponse(BaseModel):
    id: str
    workflow_id: str
    category_id: str
    created_at: str

class WorkflowAssetResponse(BaseModel):
    id: str
    workflow_id: str
    asset_type: str
    asset_url: str
    created_at: str

class WorkflowAssetCreateRequest(BaseModel):
    workflow_id: str
    asset_type: str
    asset_url: str

class WorkflowAssetUpdateRequest(BaseModel):
    asset_type: Optional[str] = None
    asset_url: Optional[str] = None

# Admin Workflow Management Schemas
class AdminWorkflowListResponse(BaseModel):
    id: str
    title: str
    price: float
    status: str
    downloads_count: int
    sales_count: int
    revenue: float

class AdminWorkflowListRequest(BaseModel):
    search: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)

class AdminWorkflowOverviewResponse(BaseModel):
    total_workflows: int
    active_workflows: int
    total_sales: int
    total_revenue: float

class AdminWorkflowDetailResponse(BaseModel):
    id: str
    title: str
    description: str
    price: float
    features: List[str]
    time_to_setup: Optional[int]
    video_demo: Optional[str]
    flow: Optional[Dict[str, Any]]
    categories: List[dict]
    assets: List[dict]

class AdminWorkflowCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    features: List[str] = []
    time_to_setup: Optional[int] = Field(None, ge=1)
    video_demo: Optional[str] = None
    flow: Optional[Dict[str, Any]] = None  # JSON object trực tiếp
    category_ids: List[str] = []

class AdminWorkflowCreateResponse(BaseModel):
    id: str
    title: str
    success: bool

class AdminWorkflowUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)
    features: Optional[List[str]] = None
    time_to_setup: Optional[int] = Field(None, ge=1)
    video_demo: Optional[str] = None
    flow: Optional[Dict[str, Any]] = None
    category_ids: Optional[List[str]] = None

class AdminWorkflowUpdateResponse(BaseModel):
    success: bool
    message: str

class AdminWorkflowDeleteResponse(BaseModel):
    success: bool
    message: str

class AdminWorkflowAssetUploadRequest(BaseModel):
    asset_url: str = Field(..., min_length=1)
    kind: str = Field(..., pattern="^(image|video|file)$")

class AdminWorkflowAssetUploadResponse(BaseModel):
    success: bool
    asset_id: str
    asset_url: str

class AdminWorkflowAssetDeleteResponse(BaseModel):
    success: bool