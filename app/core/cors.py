from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


def setup_cors(app):
    """
    ✅ Setup CORS middleware for the FastAPI app
    Cho phép truy cập API từ frontend (Next.js, Swagger UI, v.v.)
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            # Local dev URLs
            "http://localhost:3000",   # Next.js default port
            "http://localhost:3001",   # Alternative
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://172.0.0.1:3002",
            "http://172.0.0.1:3003",
            "http://172.0.0.1:4000",
            "http://172.0.0.1:5000",
            "http://172.0.0.1:5173",
            "http://172.0.0.1:8080",
            "http://172.0.0.1:8081",
            "http://172.0.0.1:9000",
            "http://172.25.67.101:3000",
            "http://172.25.67.101:3001",
            "http://172.25.67.101:3002",
            "http://172.25.67.101:3003",
            "http://172.25.67.101:4000",
            "http://172.25.67.101:5000",
            "http://172.25.67.101:5173",
            "http://172.25.67.101:8080",
            "http://172.25.67.101:8081",
            "http://172.25.67.101:9000",

            # Local network access (same WiFi)
            "http://172.25.67.101:3000",
            "http://172.25.67.101:3001",

            # Swagger UI
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        allow_credentials=True,
        allow_methods=["*"],  # 👉 Cho phép mọi method (GET, POST, PUT, PATCH, DELETE, OPTIONS)
        allow_headers=["*"],  # 👉 Cho phép mọi header (Authorization, Content-Type,...)
    )