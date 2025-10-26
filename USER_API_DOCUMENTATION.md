# USER API DOCUMENTATION
<!-- 
## Authentication APIs

### 1. User Registration
- **POST** `/api/auth/register`
- **Body**: `{ "name": string, "email": string, "password": string }`
- **Response**: `{ "access_token": string, "refresh_token": string, "token_type": "bearer", "expires_in": int }`

### 2. User Login
- **POST** `/api/auth/login`
- **Body**: `{ "email": string, "password": string }`
- **Response**: `{ "access_token": string, "refresh_token": string, "token_type": "bearer", "expires_in": int }`

### 3. Resend OTP
- **POST** `/api/auth/resend-otp`
- **Body**: `{ "email": string }`
- **Response**: `{ "success": true, "message": "OTP sent successfully" }`

### 4. Verify Reset OTP
- **POST** `/api/auth/verify-reset-otp`
- **Body**: `{ "email": string, "otp": string }`
- **Response**: `{ "success": true, "message": "OTP verified successfully" }`

### 5. Set New Password
- **POST** `/api/auth/set-new-password`
- **Body**: `{ "email": string, "otp_code": string, "new_password": string }`
- **Response**: `{ "success": true, "message": "Password updated successfully" }`

### 6. Change Password
- **PUT** `/api/auth/change-password`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "current_password": string, "new_password": string }`
- **Response**: `{ "success": true, "message": "Password changed successfully" }`

### 7. Refresh Token
- **POST** `/api/auth/refresh`
- **Body**: `{ "refresh_token": string }`
- **Response**: `{ "access_token": string, "refresh_token": string, "token_type": "bearer", "expires_in": int }`

### 8. Logout
- **POST** `/api/auth/logout`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": true, "message": "Logged out successfully" }` -->

## User Dashboard APIs
<!-- 
### 9. Get User Dashboard
- **GET** `/api/users/dashboard`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "total_purchases": int, "total_spent": float, "active_workflows": int, "saved_workflows": int }`

### 10. Get User Profile
- **GET** `/api/users/profile`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "id": string, "name": string, "email": string, "role": string, "avatar_url": string, "created_at": string, "updated_at": string }`

### 11. Update User Profile
- **PATCH** `/api/users/profile`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "name": string, "avatar_url": string }`
- **Response**: `{ "success": true, "message": "Profile updated successfully" }` -->

## Workflow APIs

### 12. Lấy danh sách tất cả Workflows
- **Endpoint:** `GET /api/workflows`
- **Headers:** _(Không cần Auth)_
- **Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "price": 0,
      "status": "string",
      "features": [],
      "downloads_count": 0,
      "wishlist_count": 0,
      "time_to_setup": 0,
      "video_demo": "string",
      "flow": {},
      "rating_avg": 0,
      "created_at": "string",
      "updated_at": "string",
      "categories": [],
      "image_urls": []
    }
  ],
  "total": 0
}
```

### 13. Lấy danh sách Workflows nổi bật (Featured)
- **Endpoint:** `GET /api/workflows/featured`
- **Headers:** _(Không cần Auth)_
- **Description:** Trả về top 10 workflows có downloads_count cao nhất, nếu bằng nhau thì sắp xếp theo rating_avg
- **Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "price": 0,
      "status": "string",
      "features": [],
      "downloads_count": 0,
      "wishlist_count": 0,
      "time_to_setup": 0,
      "video_demo": "string",
      "flow": {},
      "rating_avg": 0,
      "created_at": "string",
      "updated_at": "string",
      "categories": [],
      "image_urls": []
    }
  ]
}
```

### 14. Lấy Workflows liên quan
- **Endpoint:** `GET /api/workflows/{workflow_id}/related`
- **Headers:** _(Không cần Auth)_
- **Params:** 
  - `workflow_id` (string) – Id của workflow tham chiếu
- **Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "price": 0,
      "status": "string",
      "features": [],
      "downloads_count": 0,
      "wishlist_count": 0,
      "time_to_setup": 0,
      "video_demo": "string",
      "flow": {},
      "rating_avg": 0,
      "created_at": "string",
      "updated_at": "string",
      "categories": [],
      "image_urls": []
    }
  ]
}
```


<!-- ### 15. Get My Purchased Workflows
- **GET** `/api/my-workflow`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `[{ "id": string, "title": string, "description": string, "price": float, "status": string, "features": [...], "downloads_count": int, "time_to_setup": int, "video_demo": string, "flow": {...}, "rating_avg": float, "created_at": string, "updated_at": string, "categories": [...] }]` -->

### 16. Get Workflow Detail
- **GET** `/api/workflows/{workflow_id}`
- **Response**: `{ "id": string, "title": string, "description": string, "price": float, "status": string, "features": [...], "downloads_count": int, "time_to_setup": int, "video_demo": string, "flow": {...}, "rating_avg": float, "created_at": string, "updated_at": string, "categories": [...] }`

### 17. Search Workflows
- **GET** `/api/workflows/search`
- **Query**: `?q=&category=&page=&limit=`
- **Response**: `[{ "id": string, "title": string, "description": string, "price": float, "status": string, "features": [...], "downloads_count": int, "time_to_setup": int, "video_demo": string, "flow": {...}, "rating_avg": float, "created_at": string, "updated_at": string, "categories": [...] }]`

### 18. Add to Wishlist
- **POST** `/api/workflows/{workflow_id}/wishlist`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": true, "message": "Added to wishlist" }`

### 19. Remove from Wishlist
- **DELETE** `/api/workflows/{workflow_id}/wishlist`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": true, "message": "Removed from wishlist" }`
<!-- 
### 20. Create Workflow Review
- **POST** `/api/workflows/{workflow_id}/reviews`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "rating": int, "content": string, "parent_comment_id": string }`
- **Response**: `{ "success": true, "message": "Review created successfully" }`

### 21. Delete Workflow Review
- **DELETE** `/api/workflows/reviews/{review_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": true, "message": "Review deleted successfully" }`

### 22. Get Workflow Reviews
- **GET** `/api/workflows/{workflow_id}/reviews`
- **Response**: `[{ "id": string, "title": string, "description": string, "price": float, "status": string, "features": [...], "downloads_count": int, "time_to_setup": int, "video_demo": string, "flow": {...}, "rating_avg": float, "created_at": string, "updated_at": string, "categories": [...] }]` -->
<!-- 
### 23. Get Workflow Full Detail
- **GET** `/api/workflows/detail/{workflow_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "id": string, "title": string, "description": string, "price": float, "status": string, "features": [...], "downloads_count": int, "time_to_setup": int, "video_demo": string, "flow": {...}, "rating_avg": float, "created_at": string, "updated_at": string, "categories": [...] }` -->

## Wallet APIs

### 24. Get Wallet Info
- **GET** `/api/wallet`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "balance": float, "total_deposited": float, "total_spent": float }`

### 25. Get Wallet Transactions
- **GET** `/api/wallet/transactions`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `[{ "id": string, "transaction_type": string, "amount": float, "status": string, "bank_name": string, "bank_account": string, "transfer_code": string, "note": string, "created_at": string }]`

### 26. Create Deposit Request
- **POST** `/api/wallet/deposit`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "bank_name": string, "bank_account": string, "transfer_code": string, "amount": float }`
- **Response**: `{ "success": bool, "message": string, "transaction_id": string }`

### 27. Purchase Workflow with Wallet
- **POST** `/api/orders/{workflow_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": bool, "message": string, "wallet_balance": float, "purchase_id": string }`

### 28. Get Last Bank Info
- **GET** `/api/wallet/last-bank-info`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "bank_name": string, "bank_account": string }`

## Order APIs
<!-- 
### 29. Get My Purchases
- **GET** `/api/orders/my-purchases`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `[{ "id": string, "workflow_id": string, "workflow_title": string, "amount": float, "status": string, "payment_method": string, "paid_at": string, "created_at": string }]` -->

### 30. Get Purchase Invoice
- **GET** `/api/orders/{purchase_id}/invoice`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "invoice_number": string, "issued_at": string, "status": string, "billing_name": string, "billing_email": string, "workflow": {...}, "amount": float }`

## Notification APIs
<!-- 
### 31. Get My Notifications
- **GET** `/api/notifications`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `[{ "id": string, "user_id": string, "type": string, "title": string, "message": string, "is_unread": bool, "created_at": string }]`

### 32. Mark Notification as Read
- **PATCH** `/api/notifications/{notification_id}/read`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": bool, "message": string }`

### 33. Delete Notification
- **DELETE** `/api/notifications/{notification_id}`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": bool, "message": string }`

### 34. Delete All User Notifications
- **DELETE** `/api/notifications/all`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{ "success": bool, "message": string, "deleted_count": int }` -->

## Contact APIs

### 35. Submit Contact Form
- **POST** `/api/contact`
- **Body**: `{ "full_name": string, "email": string, "subject": string, "message": string }`
- **Response**: `{ "id": string, "status": string, "message": string }`

## Categories APIs

### 36. Get All Categories
- **GET** `/api/categories`
- **Response**: `[{ "id": string, "name": string, "image_url": string, "created_at": string }]`

## Wishlist APIs
<!-- 
### 37. Get My Wishlist
- **GET** `/api/wishlist`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `[{ "id": string, "title": string, "description": string, "price": float, "status": string, "features": [...], "downloads_count": int, "time_to_setup": int, "video_demo": string, "flow": {...}, "rating_avg": float, "created_at": string, "updated_at": string, "categories": [...] }]` -->
