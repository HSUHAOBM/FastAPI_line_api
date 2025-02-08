from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User, UserStatus, BindType
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.database import get_db
from app.utils.jwt import verify_jwt_token
from app.utils.response import success_response, fail_response

router = APIRouter()


@router.post("/users/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(verify_jwt_token)  # 驗證 JWT 並提取 token 資訊
):
    """
    新增使用者資料
    - 驗證是否有重複的Account 與 LINE uid
    """
    token_account_id = token_data.get("account_id")
    if token_account_id != user.account_id:
        return fail_response(message="您沒有權限新增其他帳號的使用者", status_code=403)

    query = select(User).filter(
        (User.line_user_id == user.line_user_id) & (
            User.account_id == user.account_id)
    )

    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        return fail_response(message="User already exists", status_code=400)

    client_host = request.client.host  # 獲取用戶 IP 地址

    new_user = User(
        **user.model_dump(),
        created_by=client_host
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    response_data = jsonable_encoder(UserResponse.model_validate(new_user))

    return success_response(data=response_data, message="User created successfully")


@router.get("/users/")
async def read_users(
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(verify_jwt_token)  # 驗證 JWT 並提取 token 資訊
):
    """
    查詢所有使用者資料
    """
    token_account_id = token_data.get("account_id")

    query = select(User).filter(User.account_id == token_account_id)
    result = await db.execute(query)
    users = result.scalars().all()

    response_data = jsonable_encoder(
        [UserResponse.model_validate(user) for user in users]
    )

    return success_response(data=response_data, message="Users retrieved successfully")


@router.get("/users/{user_id}")
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(verify_jwt_token)  # 驗證 JWT 並提取 token 資訊
):
    """
    查詢單一使用者資料
    """
    token_account_id = token_data.get("account_id")

    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or user.account_id != token_account_id:
        return fail_response(message="User not found or access denied", status_code=404)

    response_data = jsonable_encoder(UserResponse.model_validate(user))

    return success_response(data=response_data, message="User retrieved successfully")


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(verify_jwt_token)  # 驗證 JWT 並提取 token 資訊
):
    """
    更新使用者資料
    """
    token_account_id = token_data.get("account_id")

    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if not existing_user or existing_user.account_id != token_account_id:
        return fail_response(message="User not found or access denied", status_code=404)

    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(existing_user, field, value)

    client_host = request.client.host
    existing_user.modified_by = client_host

    await db.commit()
    await db.refresh(existing_user)

    response_data = jsonable_encoder(
        UserResponse.model_validate(existing_user))

    return success_response(data=response_data, message="User updated successfully")


@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(verify_jwt_token)  # 驗證 JWT 並提取 token 資訊
):
    """
    刪除使用者資料
    """
    token_account_id = token_data.get("account_id")

    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or user.account_id != token_account_id:
        return fail_response(message="User not found or access denied", status_code=404)

    await db.delete(user)
    await db.commit()

    return success_response(data={"message": f"User with ID {user.id} deleted successfully!"}, message="User deleted successfully")
