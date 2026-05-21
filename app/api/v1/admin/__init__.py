from fastapi import APIRouter, Depends
from app.api.v1.dependencies.dependencies import require_admin_role
from .users import router as users_router
from .devices import router as devices_router
from .allocations import router as allocations_router

admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin_role)])

admin_router.include_router(users_router)
admin_router.include_router(devices_router)
admin_router.include_router(allocations_router)
