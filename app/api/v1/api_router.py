from fastapi import APIRouter
from app.api.v1.auth import auth_router
from app.api.v1.users import users_router
from app.api.v1.admin import admin_router
from app.api.v1.dashboard import dashboard_router
from app.api.v1.edge import edge_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(admin_router)
api_router.include_router(dashboard_router)
api_router.include_router(edge_router)
