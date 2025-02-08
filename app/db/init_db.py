from app.utils.password import hash_password
from app.models.account import Account, BindType, RoleType
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base, engine


async def create_tables():
    """
    建立所有資料表。
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("所有資料表已成功建立！")


async def drop_tables():
    """
    刪除所有資料表。
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("所有資料表已成功刪除！")


async def init_admin(db: AsyncSession):
    """
    檢查數據庫中是否已有管理員帳號，若無則創建預設管理員帳號
    """
    query = select(Account).filter(Account.role == RoleType.ADMIN)
    result = await db.execute(query)
    admin_exists = result.scalars().first()

    if not admin_exists:
        print("⚠️ 未檢測到 Admin 帳號，正在創建預設管理員帳號...")

        admin_account = Account(
            email="admin@example.com",
            password=hash_password("Admin123!"),
            role=RoleType.ADMIN,
            status=True,
            created_by="system", bind_type=BindType.EMAIL
        )

        db.add(admin_account)
        await db.commit()
        print("✅ 預設管理員帳號創建成功！")
    else:
        print("✅ 管理員帳號已存在，無需初始化。")
