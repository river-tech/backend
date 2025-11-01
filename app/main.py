from fastapi import FastAPI
from app.core.config import settings
from app.core.cors import setup_cors
from app.api.auth_router import router as auth_router
from app.api.workflows_router import router as workflows_router
from app.api.categories_router import router as categories_router
from app.api.wishlist_router import router as wishlist_router
from app.api.orders_router import router as orders_router
from app.api.notifications_router import router as notifications_router
from app.api.contact_router import router as contact_router
from app.api.users_router import router as users_router
from app.api.admin_router import router as admin_router
from app.api.admin_users_router import router as admin_users_router
from app.api.admin_workflows_router import router as admin_workflows_router
from app.api.admin_purchases_router import router as admin_purchases_router
from app.api.admin_notifications_router import router as admin_notifications_router
from app.api.admin_categories_router import router as admin_categories_router
from app.api.admin_wallet_router import router as admin_wallet_router
from app.api.wallet_router import router as wallet_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="USITech Backend API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Setup CORS
setup_cors(app)

# Include routers
app.include_router(auth_router)
app.include_router(workflows_router)
app.include_router(categories_router, prefix="/api/categories", tags=["Categories"])
app.include_router(wishlist_router, prefix="/api/wishlist", tags=["Wishlist"])
app.include_router(orders_router, prefix="/api/orders", tags=["Orders"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(contact_router, prefix="/api/contact", tags=["Contact"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(wallet_router, prefix="/api/wallet", tags=["Wallet"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(admin_users_router, tags=["Admin - User Management"])
app.include_router(admin_workflows_router, tags=["Admin - Workflow Management"])
app.include_router(admin_purchases_router, tags=["Admin - Purchase Management"])
app.include_router(admin_notifications_router, tags=["Admin - Notifications"])
app.include_router(admin_categories_router, tags=["Admin - Categories"])
app.include_router(admin_wallet_router, tags=["Admin - Wallet"])


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
