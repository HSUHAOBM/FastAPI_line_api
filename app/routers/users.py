from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.post("/users/", response_model=UserResponse)
async def create_user_api(user: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).filter(User.user_id == user.user_id)
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(**user.dict())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get("/users/", response_model=list[UserResponse])
async def read_users(db: AsyncSession = Depends(get_db)):
    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.user_name = user_update.user_name
    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return {"message": f"User {user.user_name} deleted successfully!"}
