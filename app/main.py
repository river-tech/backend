from fastapi import FastAPI
from app.core.config import settings
from app.core.cors import setup_cors
from app.api import users_router
from app.api.auth_router import router as auth_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="USITech Backend API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Setup CORS
setup_cors(app)

# Include routers
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])


@app.get("/")
def read_root():
    return {
        "message": "Welcome to USITech Backend API",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_STR}/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
