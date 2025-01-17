from app.routers.users import router as users_router
from app.routers.account import router as account_router


# 匯入所有路由
__all__ = ["users_router", "account_router"]
