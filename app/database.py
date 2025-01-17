from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator
from dotenv import load_dotenv
import os

# 加載 .env 檔案
load_dotenv()

# 從環境變數讀取 DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
# # 使用非同步的 PostgreSQL URL
# DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

# 創建非同步引擎
engine = create_async_engine(DATABASE_URL, echo=True)

# 創建非同步的 SessionLocal
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

# 創建 Base 類
Base = declarative_base()


# 定義共用資料庫會話依賴
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()  # 非同步關閉資料庫連線
