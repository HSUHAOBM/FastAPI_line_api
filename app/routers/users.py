from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User, UserStatus, BindType
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.database import get_db

router = APIRouter()


@router.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    """
    新增使用者資料
    - 驗證是否有重複的Account 與 LINE uid
    """
    query = select(User).filter(
        (User.line_user_id == user.line_user_id) & (
            User.account_id == user.account_id)
    )

    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    client_host = request.client.host  # 獲取用戶 IP 地址

    new_user = User(
        **user.model_dump(),
        created_by=client_host
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get("/users/", response_model=list[UserResponse])
async def read_users(db: AsyncSession = Depends(get_db)):
    """
    查詢所有使用者資料
    """
    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()

    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    查詢單一使用者資料
    """
    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, request: Request, db: AsyncSession = Depends(get_db)):
    """
    更新使用者資料
    """
    query = select(User).filter(
        (User.line_user_id == user_update.line_user_id) & (
            User.account_id == user_update.account_id)
    )
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(existing_user, field, value)

    client_host = request.client.host
    existing_user.modified_by = client_host

    await db.commit()
    await db.refresh(existing_user)

    return existing_user


@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    刪除使用者資料
    """
    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return {"message": f"User with ID {user.id} deleted successfully!"}
