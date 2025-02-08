from fastapi.routing import APIRoute
from app.database import engine, SessionLocal
from app.utils.response import register_exception_handlers
from fastapi import FastAPI
from app.routers import users, account
from app.db.init_db import create_tables, drop_tables, init_admin
from fastapi.exceptions import RequestValidationError

from sqlalchemy.ext.asyncio import AsyncSession

# 定義 lifespan 方法


async def lifespan(app: FastAPI):
    """
    Lifespan 事件處理器，用於應用啟動和關閉時執行邏輯。
    """

    # 在啟動時初始化資料庫
    await drop_tables()
    await create_tables()

    # 初始化管理員帳號
    async with SessionLocal() as session:
        await init_admin(session)

    yield  # 中間的代碼可以留空，如果無關閉邏輯
    # 關閉時執行的清理操作（可選）
    print("Application is shutting down")

app = FastAPI(lifespan=lifespan)

app.include_router(account.router, prefix="/api", tags=["account"])
app.include_router(users.router, prefix="/api", tags=["users"])

# 註冊自定義的驗證錯誤處理器
register_exception_handlers(app)


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}
