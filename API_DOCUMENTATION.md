# USITech Backend API Documentation

## 🚀 **API Overview**
- **Base URL**: `http://localhost:8000`
- **API Version**: `v1`
- **API Prefix**: `/api/v1`
- **Documentation**: `/docs` (Swagger UI)

## 📋 **Available APIs**

### **1. Authentication APIs** (`/api/v1/auth`)

#### **1.1 User Registration**
- **Endpoint**: `POST /api/v1/auth/register`
- **Description**: Register a new user account
- **Request Body**:
  ```json
  {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "password": "securepassword123"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role": "USER",
    "is_deleted": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
  ```

#### **1.2 User Login**
- **Endpoint**: `POST /api/v1/auth/login`
- **Description**: Authenticate user and return JWT tokens
- **Request Body**:
  ```json
  {
    "email": "john.doe@example.com",
    "password": "securepassword123"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
  ```

#### **1.3 User Logout**
- **Endpoint**: `POST /api/v1/auth/logout`
- **Description**: Invalidate current access token
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `200 OK`
  ```json
  {
    "message": "Successfully logged out",
    "success": true
  }
  ```

#### **1.4 Resend OTP**
- **Endpoint**: `POST /api/v1/auth/resend-otp`
- **Description**: Resend OTP code for email verification
- **Request Body**:
  ```json
  {
    "email": "john.doe@example.com"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "message": "OTP sent successfully",
    "success": true
  }
  ```

#### **1.5 Refresh Token**
- **Endpoint**: `GET /api/v1/auth/refresh`
- **Description**: Get new access token using refresh token
- **Headers**: `Authorization: Bearer <refresh_token>`
- **Response**: `200 OK`
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
  ```

#### **1.6 Change Password**
- **Endpoint**: `PUT /api/v1/auth/change-password`
- **Description**: Change password for authenticated user
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "current_password": "oldpassword123",
    "new_password": "newpassword123"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "message": "Password changed successfully",
    "success": true
  }
  ```

#### **1.7 Forgot Password**
- **Endpoint**: `POST /api/v1/auth/forgot-password`
- **Description**: Send OTP for password reset
- **Request Body**:
  ```json
  {
    "email": "john.doe@example.com"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "message": "Password reset OTP sent successfully",
    "success": true
  }
  ```

#### **1.8 Verify Reset OTP**
- **Endpoint**: `POST /api/v1/auth/verify-reset-otp`
- **Description**: Verify OTP code for password reset
- **Request Body**:
  ```json
  {
    "email": "john.doe@example.com",
    "otp_code": "123456"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "message": "OTP verified successfully",
    "success": true
  }
  ```

#### **1.9 Set New Password**
- **Endpoint**: `POST /api/v1/auth/set-new-password`
- **Description**: Set new password after OTP verification
- **Request Body**:
  ```json
  {
    "email": "john.doe@example.com",
    "otp_code": "123456",
    "new_password": "newpassword123"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "message": "Password reset successfully",
    "success": true
  }
  ```

### **2. User Management APIs** (`/api/v1/users`)

#### **2.1 Create User**
- **Endpoint**: `POST /api/v1/users/`
- **Description**: Create a new user (Admin only)
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "username": "username",
    "password": "password123",
    "is_active": true
  }
  ```
- **Response**: `200 OK` - User object

#### **2.2 Get Users**
- **Endpoint**: `GET /api/v1/users/`
- **Description**: Get list of users with pagination
- **Query Parameters**:
  - `skip`: Number of records to skip (default: 0)
  - `limit`: Maximum number of records (default: 100)
- **Response**: `200 OK` - Array of user objects

#### **2.3 Get User by ID**
- **Endpoint**: `GET /api/v1/users/{user_id}`
- **Description**: Get user by ID
- **Path Parameters**:
  - `user_id`: User ID (integer)
- **Response**: `200 OK` - User object

#### **2.4 Update User**
- **Endpoint**: `PUT /api/v1/users/{user_id}`
- **Description**: Update user information
- **Path Parameters**:
  - `user_id`: User ID (integer)
- **Request Body**:
  ```json
  {
    "email": "newemail@example.com",
    "username": "newusername",
    "password": "newpassword123",
    "is_active": true
  }
  ```
- **Response**: `200 OK` - Updated user object

#### **2.5 Delete User**
- **Endpoint**: `DELETE /api/v1/users/{user_id}`
- **Description**: Delete user by ID
- **Path Parameters**:
  - `user_id`: User ID (integer)
- **Response**: `200 OK`
  ```json
  {
    "message": "User deleted successfully"
  }
  ```

### **3. System APIs**

#### **3.1 Health Check**
- **Endpoint**: `GET /health`
- **Description**: Check system health
- **Response**: `200 OK`
  ```json
  {
    "status": "healthy"
  }
  ```

#### **3.2 Root Endpoint**
- **Endpoint**: `GET /`
- **Description**: API information
- **Response**: `200 OK`
  ```json
  {
    "message": "Welcome to USITech Backend API",
    "version": "1.0.0",
    "docs": "/api/v1/docs"
  }
  ```

## 🔐 **Authentication**

### **JWT Token Structure**
- **Access Token**: Valid for 30 minutes
- **Refresh Token**: Valid for 7 days
- **Token Type**: Bearer
- **Algorithm**: HS256

### **Authorization Header**
```
Authorization: Bearer <access_token>
```

## 📊 **Database Schema**

### **Users Table**
- `id`: UUID (Primary Key)
- `name`: VARCHAR(120)
- `avatar_url`: TEXT
- `email`: VARCHAR(150) UNIQUE
- `password_hash`: TEXT
- `role`: ENUM('USER', 'ADMIN')
- `is_deleted`: BOOLEAN
- `created_at`: TIMESTAMPTZ

### **Other Tables**
- `notifications` - User notifications
- `contact_messages` - Contact form messages
- `workflows` - Workflow templates
- `categories` - Workflow categories
- `workflow_categories` - Many-to-many relationship
- `workflow_assets` - Workflow media files
- `favorites` - User favorites
- `comments` - Workflow comments
- `purchases` - Purchase transactions
- `invoices` - Invoice records

## 🚀 **Getting Started**

### **1. Start the Server**
```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **2. Access Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### **3. Test Authentication Flow**
1. Register a new user: `POST /api/v1/auth/register`
2. Login: `POST /api/v1/auth/login`
3. Use access token for authenticated requests
4. Refresh token when needed: `GET /api/v1/auth/refresh`

## 📝 **Error Handling**

### **Common Error Responses**
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Invalid or expired token
- `404 Not Found` - Resource not found
- `422 Validation Error` - Invalid input format
- `500 Internal Server Error` - Server error

### **Error Response Format**
```json
{
  "error": "Error Type",
  "message": "Detailed error message"
}
```

## 🔧 **Development**

### **Dependencies**
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT (PyJWT)
- Pydantic
- Uvicorn

### **Environment Variables**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `ALGORITHM` - JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
