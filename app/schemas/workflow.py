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
    status: Optional[str] = "active"
    features: List[str] = []
    downloads_count: int = 0
    wishlist_count: int = 0
    time_to_setup: Optional[int] = None
    video_demo: Optional[str] = None
    flow: Optional[Dict[str, Any]] = None
    rating_avg: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    categories: List[str] = []
    image_urls: List[str] = []
    is_like: Optional[bool] = None
    is_buy: Optional[bool] = None

class WorkflowDetailResponse(BaseModel):
    id: str
    title: str
    description: str
    price: float
    status: Optional[str] = "active"
    features: List[str] = []
    downloads_count: int = 0
    wishlist_count: int = 0
    time_to_setup: Optional[int] = None
    video_demo: Optional[str] = None
    flow: Optional[Dict[str, Any]] = None
    rating_avg: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    categories: List[str] = []
    image_urls: List[str] = []
    is_like: Optional[bool] = None
    is_buy: Optional[bool] = None

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

class ReviewCreateRequest(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5 stars")
    content: str = Field(..., min_length=1, max_length=1000, description="Review content")
    parent_comment_id: Optional[UUID] = Field(None, description="Parent comment ID for replies")

class ReviewResponse(BaseModel):
    id: str
    user: dict
    rating: Optional[int] = None
    comment: str
    created_at: str
    parent_comment_id: Optional[str] = None
    is_me: bool = False

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
    categories: List[str]
    price: float
    sales_count: int
    created_at: str
    status: str

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
    rating: Optional[float] = None
    features: List[str]
    time_to_setup: Optional[int]
    video_demo: Optional[str]
    flow: Optional[Dict[str, Any]]
    status: str
    created_at: Optional[str]
    sales_count: int
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