# 🚀 USITech Workflow API Documentation

## 📋 **API Endpoints Overview**

### 🔍 **Public Endpoints (No Authentication Required)**

#### **1. GET /api/workflows**
- **Description:** Liệt kê tất cả workflow đã được xuất bản
- **Parameters:** 
  - `skip` (int, optional): Số bản ghi bỏ qua (default: 0)
  - `limit` (int, optional): Số bản ghi trả về (default: 20, max: 100)
- **Response:** List of workflows with basic info

#### **2. GET /api/workflows/feature**
- **Description:** Liệt kê tất cả workflow feature (rating >= 4.0)
- **Parameters:** 
  - `skip` (int, optional): Số bản ghi bỏ qua (default: 0)
  - `limit` (int, optional): Số bản ghi trả về (default: 20, max: 100)
- **Response:** List of featured workflows

#### **3. GET /api/workflows/{workflow_id}/related**
- **Description:** Lấy danh sách 3 workflow liên quan cùng danh mục
- **Parameters:** 
  - `workflow_id` (UUID): ID của workflow
- **Response:** List of related workflows with thumbnails

#### **4. GET /api/workflows/{workflow_id}**
- **Description:** Lấy chi tiết thông tin một workflow
- **Parameters:** 
  - `workflow_id` (UUID): ID của workflow
- **Response:** Detailed workflow information

#### **5. GET /api/workflows/search**
- **Description:** Tìm kiếm workflow theo từ khóa
- **Parameters:** 
  - `q` (string, required): Từ khóa tìm kiếm
  - `skip` (int, optional): Số bản ghi bỏ qua (default: 0)
  - `limit` (int, optional): Số bản ghi trả về (default: 20, max: 100)
- **Response:** List of matching workflows

#### **6. GET /api/workflows/{workflow_id}/reviews**
- **Description:** Lấy danh sách các đánh giá của workflow
- **Parameters:** 
  - `workflow_id` (UUID): ID của workflow
  - `skip` (int, optional): Số bản ghi bỏ qua (default: 0)
  - `limit` (int, optional): Số bản ghi trả về (default: 20, max: 100)
- **Response:** List of reviews with user info

### 🔐 **User Endpoints (Authentication Required)**

#### **7. POST /api/workflows/{workflow_id}/wishlist**
- **Description:** Thêm workflow vào danh sách yêu thích
- **Headers:** `Authorization: Bearer <token>`
- **Parameters:** 
  - `workflow_id` (UUID): ID của workflow
- **Response:** Success message

#### **8. DELETE /api/workflows/{workflow_id}/wishlist**
- **Description:** Xóa workflow khỏi danh sách yêu thích
- **Headers:** `Authorization: Bearer <token>`
- **Parameters:** 
  - `workflow_id` (UUID): ID của workflow
- **Response:** Success message

#### **9. POST /api/workflows/{workflow_id}/reviews**
- **Description:** Thêm đánh giá (review) mới cho workflow
- **Headers:** `Authorization: Bearer <token>`
- **Parameters:** 
  - `workflow_id` (UUID): ID của workflow
- **Body:** 
  ```json
  {
    "rating": 5,
    "comment": "Great workflow!",
    "parent_comment_id": "uuid" // optional for replies
  }
  ```
- **Response:** Success message

#### **10. DELETE /api/workflows/reviews/{review_id}**
- **Description:** Xoá một đánh giá hoặc bình luận
- **Headers:** `Authorization: Bearer <token>`
- **Parameters:** 
  - `review_id` (UUID): ID của review
- **Response:** Success message

#### **11. GET /api/workflows/my-workflow**
- **Description:** Lấy danh sách workflow mà người dùng đã mua
- **Headers:** `Authorization: Bearer <token>`
- **Response:** List of purchased workflows

#### **12. GET /api/workflows/detail/{workflow_id}**
- **Description:** Lấy chi tiết đầy đủ của một workflow (bao gồm video hướng dẫn, file tải, hướng dẫn cài đặt...)
- **Headers:** `Authorization: Bearer <token>`
- **Parameters:** 
  - `workflow_id` (UUID): ID của workflow
- **Response:** Full workflow details (only for purchased workflows)

### 🔧 **Admin/Cron Endpoints**

#### **13. POST /api/workflows/verify-transaction**
- **Description:** Xác minh giao dịch chuyển khoản từ email ngân hàng dựa trên transfer_code
- **Body:** 
  ```json
  {
    "transfer_code": "ABC123456"
  }
  ```
- **Response:** Transaction verification result

## 📊 **Response Schemas**

### **WorkflowListResponse**
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "category": ["string"],
  "features": ["string"],
  "rating_avg": 4.5,
  "downloads_count": 100,
  "price": 99.99
}
```

### **WorkflowDetailResponse**
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "category": ["string"],
  "images": ["string"],
  "features": ["string"],
  "rating_avg": 4.5,
  "rating_count": 25,
  "downloads_count": 100,
  "wishlist_count": 15,
  "price": 99.99,
  "time_to_setup": 30
}
```

### **WorkflowFullDetailResponse**
```json
{
  "id": "uuid",
  "title": "string",
  "category": ["string"],
  "status": "active",
  "purchased_at": "2024-01-01T00:00:00Z",
  "video_demo_url": "string",
  "last_updated": "2024-01-01T00:00:00Z",
  "document": "string",
  "flow": {}
}
```

### **ReviewResponse**
```json
{
  "id": "uuid",
  "user": {
    "name": "string",
    "avatar_url": "string"
  },
  "rating": 5,
  "comment": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "parent_comment_id": "uuid"
}
```

### **MyWorkflowResponse**
```json
{
  "id": "uuid",
  "workflow": {
    "id": "uuid",
    "title": "string"
  },
  "purchase_date": "2024-01-01T00:00:00Z",
  "price": 99.99,
  "status": "Active"
}
```

## 🚀 **Features Implemented**

### ✅ **Search & Filter**
- Full-text search across title and description
- Featured workflows (rating >= 4.0)
- Related workflows based on categories
- Pagination support

### ✅ **User Interactions**
- Wishlist management (add/remove)
- Review system with ratings and comments
- Nested comments (replies)
- Purchase tracking

### ✅ **Content Management**
- Workflow categories
- Asset management (images, videos, documents)
- Category relationships
- Status management (active/expired)

### ✅ **Business Logic**
- Purchase verification
- Transaction matching
- Invoice generation
- Rating calculations

## 🔧 **Database Relationships**

- **Users** → Favorites, Comments, Purchases
- **Workflows** → Categories, Assets, Comments, Favorites, Purchases
- **Categories** → Workflows (many-to-many)
- **Purchases** → Invoices
- **Comments** → Users, Workflows, Parent Comments

## 📈 **Performance Optimizations**

- **Eager Loading:** Using `joinedload` for related data
- **Indexing:** Proper database indexes on foreign keys
- **Pagination:** Limit results to prevent large responses
- **Query Optimization:** Efficient joins and filters

**All 13 API endpoints are fully implemented and ready for use!** 🎯
