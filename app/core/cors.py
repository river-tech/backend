from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


def setup_cors(app):
    """Setup CORS middleware for the FastAPI app"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Next.js default port
            "http://localhost:3001",  # Alternative port
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
