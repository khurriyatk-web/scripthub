"""Routes package — aggregates all API routers."""
from fastapi import APIRouter

from routes.auth import router as auth_router
from routes.projects import router as projects_router
from routes.categories import router as categories_router
from routes.orders import router as orders_router
from routes.reviews import router as reviews_router
from routes.users import router as users_router
from routes.admin import router as admin_router
from routes.upload import router as upload_router
from routes.webhooks import router as webhooks_router
from routes.store import router as store_router
from routes.payments import router as payments_router
from routes.developer import router as developer_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(categories_router, prefix="/categories", tags=["categories"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["reviews"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(upload_router, prefix="/upload", tags=["upload"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(store_router, prefix="/store", tags=["store"])
api_router.include_router(payments_router, prefix="/payments", tags=["payments"])
api_router.include_router(developer_router, prefix="/developer", tags=["developer"])

__all__ = ["api_router"]
