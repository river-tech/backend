# USITech Backend API

## 📁 Cấu trúc dự án

```
app/
├── api/                    # API Routes
│   ├── auth_router.py      # Authentication APIs
│   ├── wallet_router.py    # Wallet APIs
│   ├── workflows_router.py # Workflow APIs
│   ├── orders_router.py    # Order APIs
│   ├── users_router.py     # User APIs
│   ├── categories_router.py # Category APIs
│   ├── wishlist_router.py  # Wishlist APIs
│   ├── notifications_router.py # Notification APIs
│   ├── contact_router.py   # Contact APIs
│   ├── admin_auth_router.py    # Admin Auth APIs
│   ├── admin_users_router.py   # Admin User Management APIs
│   └── admin_workflows_router.py # Admin Workflow Management APIs
├── core/                   # Core Configuration
│   ├── config.py          # App settings
│   ├── cors.py            # CORS setup
│   └── database.py         # Database connection
├── models/                 # Database Models
│   ├── user.py            # User model
│   ├── workflow.py        # Workflow model
│   ├── category.py        # Category model
│   ├── wallet.py          # Wallet models
│   ├── purchase.py        # Purchase model
│   ├── invoice.py         # Invoice model
│   └── enums.py           # Enum definitions
├── schemas/                # Pydantic Schemas
│   ├── admin.py           # Admin schemas
│   ├── wallet.py          # Wallet schemas
│   ├── workflow.py        # Workflow schemas
│   ├── user.py            # User schemas
│   └── order.py           # Order schemas
├── services/              # Business Logic
│   ├── auth_service.py    # Authentication service
│   ├── wallet_service.py  # Wallet service
│   ├── workflow_service.py # Workflow service
│   ├── order_service.py   # Order service
│   ├── user_service.py    # User service
│   └── email_service.py   # Email service
└── main.py                # FastAPI app entry point
```

## 🚀 API Endpoints

### Authentication
- `POST /api/auth/register` - Đăng ký user
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/logout` - Đăng xuất
- `PUT /api/auth/change-password` - Đổi mật khẩu

### Wallet
- `GET /api/wallet/` - Thông tin ví
- `GET /api/wallet/transactions` - Lịch sử giao dịch
- `GET /api/wallet/last-bank-info` - Thông tin ngân hàng gần nhất
- `POST /api/wallet/deposit` - Nạp tiền
- `POST /api/wallet/orders/{workflow_id}` - Mua workflow bằng ví

### Workflows
- `GET /api/workflows/` - Danh sách workflows
- `GET /api/workflows/{id}` - Chi tiết workflow
- `POST /api/workflows/` - Tạo workflow (admin)
- `PUT /api/workflows/{id}` - Cập nhật workflow (admin)
- `DELETE /api/workflows/{id}` - Xóa workflow (admin)

### Admin
- `POST /api/admin/auth/login` - Đăng nhập admin
- `GET /api/admin/users/` - Danh sách users
- `PUT /api/admin/users/{id}` - Cập nhật user
- `DELETE /api/admin/users/{id}` - Xóa user

## 🔧 Cài đặt

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate    # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
python run.py
```

## 📊 Database

- PostgreSQL
- Alembic migrations
- SQLAlchemy ORM

## 🔐 Authentication

- JWT tokens
- Role-based access (USER/ADMIN)
- Password hashing với SHA-256

## 💰 Wallet System

- Số dư ví
- Lịch sử giao dịch
- Nạp tiền qua banking
- Mua workflow bằng ví