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
