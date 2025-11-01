# ADMIN API DOCUMENTATION

## Admin Authentication

### 1. Admin Login
- **POST** `/api/auth/login`
- **Body**: `{ "email": "admin@usitech.com", "password": "1234" }`
- **Response**: `{ "success": true, "token": string, "user": {...} }`

## User Management APIs

### 2. Search Users
- **POST** `/api/admin/users/search`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "name": string, "is_banned": boolean }`
- **Response**: `[{ "id": uuid, "name": string, "email": string, "status": string, "purchases_count": int, "total_spent": number }]`

### 3. Get User Detail
- **GET** `/api/admin/users/{user_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "id": uuid, "name": string, "email": string, "status": string, "total_purchases": int, "total_spent": number, "purchase_history": [...] }`

### 4. Ban/Unban User
- **PATCH** `/api/admin/users/{user_id}/ban`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "is_deleted": boolean }`
- **Response**: `{ "success": true, "message": string }`

### 5. Get Users Overview
- **GET** `/api/admin/users/overview`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "total_users": int, "active_users": int, "total_purchases": int, "total_spent": number }`

## Workflow Management APIs

### 6. Get All Workflows
- **GET** `/api/admin/workflows`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `[ { "id": uuid, "title": string, "status": string, "price": number, "created_at": datetime } ]`

### 7. Get Workflow Overview
- **GET** `/api/admin/workflows/overview`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "total_workflows": int, "active_workflows": int, "total_sales": int, "total_revenue": number }`

### 8. Get Workflow Detail
- **GET** `/api/admin/workflows/{workflow_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "id": uuid, "title": string, "description": string, "price": number, "features": [...], "categories": [...], "assets": [...] }`

### 9. Create Workflow (JSON)
- **POST** `/api/admin/workflows/create`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "title": string, "description": string, "price": number, "features": [...], "time_to_setup": int, "video_demo": string, "flow": {...}, "category_ids": [...] }`
- **Response**: `{ "id": uuid, "title": string, "success": true }`

### 10. Create Workflow (File Upload)
- **POST** `/api/admin/workflows/create-with-file`
- **Headers**: `Authorization: Bearer <token>`, `Content-Type: multipart/form-data`
- **Body**: `FormData { "title": string, "description": string, "price": number, "features": [...], "time_to_setup": int, "video_demo": string, "flow_file": File, "category_ids": [...] }`
- **Response**: `{ "id": uuid, "title": string, "success": true }`

### 11. Update Workflow
- **PUT** `/api/admin/workflows/{workflow_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "title": string, "description": string, "price": number, "features": [...], "time_to_setup": int, "video_demo": string, "flow": {...}, "category_ids": [...] }`
- **Response**: `{ "success": true, "message": "Workflow updated successfully" }`

### 12. Deactivate Workflow
- **DELETE** `/api/admin/workflows/{workflow_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": true, "message": "Workflow deactivated successfully" }`

### 13. Activate Workflow
- **PATCH** `/api/admin/workflows/{workflow_id}/activate`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": true, "message": "Workflow activated successfully" }`

### 14. Upload Workflow Asset
- **POST** `/api/admin/workflows/{workflow_id}/assets`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "asset_url": string, "kind": "image|video|file" }`
- **Response**: `{ "success": true, "asset_id": uuid, "asset_url": string }`

### 15. Delete Workflow Asset
- **DELETE** `/api/admin/workflows/{workflow_id}/assets/{asset_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": true }`

## Purchase Management APIs

### 16. Get Purchases Overview
- **GET** `/api/admin/purchases/overview`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "total_purchases": int, "completed": int, "pending": int, "total_revenue": number }`

### 17. Get All Purchases
- **GET** `/api/admin/purchases`
- **Headers**: `Authorization: Bearer <token>`
- **Query**: `?search=`
- **Response**: `[{ "id": uuid, "user": {...}, "workflow": {...}, "amount": number, "status": string, "payment_method": string, "paid_at": datetime }]`

### 18. Get Purchase Detail
- **GET** `/api/admin/purchases/{purchase_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "id": uuid, "user": {...}, "workflow": {...}, "bank_name": string, "transfer_code": string, "status": string, "amount": number, "paid_at": datetime }`

### 19. Update Purchase Status
- **PATCH** `/api/admin/purchases/{purchase_id}/status`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "status": "ACTIVE|PENDING|REJECT" }`
- **Response**: `{ "success": true, "message": string }`

## Notification Management APIs

### 20. Get Admin Notifications
- **GET** `/api/admin/notifications`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
```json
{
  "notifications": [
    {
      "id": "uuid",
      "title": "string",
      "message": "string",
      "type": "SUCCESS | WARNING | ERROR",
      "is_unread": true
    }
  ]
}
```

---

### 21. Create Notification
- **POST** `/api/admin/notifications`
- **Headers**: `Authorization: Bearer <token>`
- **Body**:
```json
{
  "user_id": "uuid",
  "title": "string",
  "message": "string",
  "type": "SUCCESS | WARNING | ERROR"
}
```
- **Response**:
```json
{
  "success": true,
  "message": "Notification created successfully",
  "notification_id": "uuid"
}
```

---

### 22. Broadcast Notification to All Users
- **POST** `/api/admin/notifications/broadcast`
- **Headers**: `Authorization: Bearer <token>`
- **Body**:
```json
{
  "title": "string",
  "message": "string",
  "type": "SUCCESS | WARNING | ERROR"
}
```
- **Response**:
```json
{
  "success": true,
  "message": "Notification broadcast to all users"
}
```

---

### 22a. Create Notification for Current Admin
- **POST** `/api/admin/notifications/self`
- **Headers**: `Authorization: Bearer <token>`
- **Body**:
```json
{
  "title": "string",
  "message": "string",
  "type": "SUCCESS | WARNING | ERROR"
}
```
- **Response**:
```json
{ "success": true, "message": "Notification created for current admin" }
```

---

### 22b. Broadcast Notification to All Admins
- **POST** `/api/admin/notifications/admins/broadcast`
- **Headers**: `Authorization: Bearer <token>`
- **Body**:
```json
{
  "title": "string",
  "message": "string",
  "type": "SUCCESS | WARNING | ERROR"
}
```
- **Response**:
```json
{ "success": true, "message": "Notification broadcasted successfully to X admins" }
```

### 23. Mark Notification as Read
- **PATCH** `/api/admin/notifications/{notification_id}/read`
- **Headers**: `Authorization: Bearer <token>`
- **Path Params**:
  - `notification_id` (uuid): ID của thông báo cần đánh dấu đã đọc
- **Response**:
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

---

### 24. Mark All Notifications as Read
- **PATCH** `/api/admin/notifications/read-all`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
```json
{
  "success": true,
  "message": "All notifications marked as read"
}
```

---

### 25. Delete Notification
- **DELETE** `/api/admin/notifications/{notification_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Path Params**:
  - `notification_id` (uuid): ID của thông báo cần xóa
- **Response**:
```json
{
  "success": true,
  "message": "Notification deleted successfully"
}
```

---

### 26. Delete All Notifications
- **DELETE** `/api/admin/notifications/all`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
```json
{
  "success": true,
  "deleted_count": 42
}
```


## Category Management APIs

### 27. Get All Categories
- **GET** `/api/admin/categories`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `[{ "id": uuid, "name": string, "image_url": string }]`

### 28. Create Category
- **POST** `/api/admin/categories`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "name": string, "image_url": string }`
- **Response**: `{ "id": uuid, "name": string, "success": true }`

### 29. Delete Category
- **DELETE** `/api/admin/categories/{category_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": true, "message": "Category deleted successfully" }`

## Admin Settings APIs

### 30. Get All Admins
- **GET** `/api/admin/settings/admins`
- **Headers**: `Authorization: Bearer <admin token>`
- **Response**: `[{ "id": string, "name": string, "email": string, "role": "ADMIN", "created_at": string ISO8601 }]`

### 31. Create Admin
- **POST** `/api/admin/settings/admins`
- **Headers**: `Authorization: Bearer <admin token>`
- **Body**: `{ "name": string, "email": string, "password": string (>= 6) }`
- **Response**: `{ "id": string, "success": true, "message": "Admin created successfully" }`

### 32. Update Admin
- **PUT** `/api/admin/settings/admins/{admin_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "name": string, "email": string, "password": string }`
- **Response**: `{ "success": true, "message": "Admin updated successfully" }`

### 33. Delete Admin
- **DELETE** `/api/admin/settings/admins/{admin_id}`
- **Headers**: `Authorization: Bearer <admin token>`
- **Body**: `{ "adminPassword": string }` (mật khẩu của admin đang đăng nhập để xác nhận)
- **Responses**:
  - 200: `{ "success": true, "message": "Admin deleted successfully" }`
  - 400: `{ "detail": "Cannot delete your own account" }`
  - 401: `{ "detail": "Invalid admin password" }`
  - 404: `{ "detail": "Admin not found" }`

### 34. Get System Statistics
- **GET** `/api/admin/settings/statistics`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "total_users": int, "total_workflows": int, "total_purchases": int, "total_revenue": number }`

### 35. Update System Settings
- **PUT** `/api/admin/settings/system`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "site_name": string, "site_description": string, "maintenance_mode": boolean }`
- **Response**: `{ "success": true, "message": "Settings updated successfully" }`

### 36. Get Admin Profile
- **GET** `/api/admin/profile`
- **Headers**: `Authorization: Bearer <admin token>`
- **Response**: `{ "id": string, "name": string, "email": string, "role": "ADMIN", "created_at": string ISO8601 }`

### 37. Update Admin Profile
- **PUT** `/api/admin/profile`
- **Headers**: `Authorization: Bearer <admin token>`
- **Body**: `{ "name": string }`
- **Response**: `{ "id": string, "name": string, "email": string, "role": "ADMIN", "created_at": string ISO8601 }`

### 38. Change Admin Password
- **PATCH** `/api/admin/settings/password`
- **Headers**: `Authorization: Bearer <admin token>`
- **Body**: `{ "currentPassword": string, "newPassword": string (>= 6) }`
- **Responses**:
  - 200: `{ "success": true, "message": "Password changed successfully" }`
  - 401: `{ "detail": "Current password is incorrect" }`
  - 422: `{ "detail": "New password must be at least 6 characters" }`

### 39. Get Deposit Overview
- **GET** `/api/admin/wallet/deposits/overview`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
```json
{
  "total": 100,
  "total_amount": 100000000,
  "completed": 80,
  "pending": 15,
  "rejected": 5
}
```

### 40. Reject Deposit Transaction
- **PATCH** `/api/admin/wallet/deposits/{transaction_id}/reject`
- **Headers**: `Authorization: Bearer <token>`
- **Path Params**:
  - `transaction_id` (uuid): ID của giao dịch nạp tiền
- **Response**:
```json
{ "success": true, "message": "Deposit transaction rejected." }
```
- **Errors**:
  - 404: `{ "detail": "Deposit transaction not found" }`
  - 400: `{ "detail": "Only pending deposits can be rejected" }`
