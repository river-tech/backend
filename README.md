# USITech Backend

FastAPI backend với PostgreSQL cho dự án USITech.

## Cài đặt

### Sử dụng Docker (Khuyến nghị)

1. Cài đặt Docker và Docker Compose
2. Chạy lệnh:
```bash
docker-compose up --build
```

### Cài đặt thủ công

1. Cài đặt Python 3.11+
2. Cài đặt PostgreSQL
3. Tạo database:
```sql
CREATE DATABASE usitech_db;
CREATE USER usitech_user WITH PASSWORD 'usitech_password';
GRANT ALL PRIVILEGES ON DATABASE usitech_db TO usitech_user;
```

4. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

5. Tạo file .env từ env.example:
```bash
cp env.example .env
```

6. Chạy migrations:
```bash
alembic upgrade head
```

7. Chạy server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- **Base URL**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/api/v1/docs`

### Authentication
- `POST /api/v1/auth/login` - Đăng nhập
- `GET /api/v1/auth/me` - Thông tin user hiện tại

### Users
- `POST /api/v1/users/` - Tạo user mới
- `GET /api/v1/users/` - Lấy danh sách users
- `GET /api/v1/users/{user_id}` - Lấy thông tin user
- `PUT /api/v1/users/{user_id}` - Cập nhật user
- `DELETE /api/v1/users/{user_id}` - Xóa user

## Cấu trúc thư mục

```
backend/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Core configuration
│   ├── db/            # Database configuration
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── main.py        # FastAPI app
├── alembic/           # Database migrations
├── tests/             # Tests
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
└── docker-compose.yml # Docker Compose setup
```

## Development

### Chạy tests
```bash
pytest
```

### Tạo migration mới
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```
