from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated, Optional
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse, PasswordChange, AccountUpdate, LoginRequest
from app.database import get_db
from app.utils.jwt import create_jwt_token, verify_jwt_token, Token
from app.utils.password import validate_password, hash_password, verify_password
from app.utils.response import success_response, fail_response

router = APIRouter()


@router.post("/accounts/", response_model=AccountResponse)
async def create_account(account: AccountCreate, request: Request, db: AsyncSession = Depends(get_db)):
    """
    新增帳號資料
    - 驗證是否有重複的 Email
    - 加密密碼並儲存
    """
    # 獲取用戶 IP 地址
    client_host = request.client.host

    # 檢查 Email 是否已存在
    query = select(Account).filter(Account.email == account.email)
    result = await db.execute(query)
    existing_account = result.scalars().first()

    if existing_account:
        return fail_response(message="Account already exists", errors={"email": "Email already registered"})

    # 驗證密碼格式
    validate_password(account.password)
    # 加密密碼
    account.password = hash_password(account.password)

    # 新增帳號，將所有參數解包並新增 created_by
    new_account = Account(
        **account.model_dump(),  # 使用 model_dump 方法取代 dict
        created_by=client_host  # 記錄創建者的 IP 地址
    )
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)

    response_data = jsonable_encoder(
        AccountResponse.model_validate(new_account))

    return success_response(
        data=response_data,
        message="Account created successfully"
    )


@router.get("/accounts/")
async def read_accounts(db: AsyncSession = Depends(get_db)):
    """
    查詢所有帳號資料
    """
    query = select(Account)
    result = await db.execute(query)
    accounts = result.scalars().all()

    # 轉換成 JSON 可序列化的格式
    response_data = jsonable_encoder(
        [AccountResponse.model_validate(account) for account in accounts]
    )

    return success_response(
        data=response_data,
        message="Accounts retrieved successfully"
    )


@router.get("/accounts/{account_id}")
async def read_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """
    查詢單一帳號資料
    """
    query = select(Account).filter(Account.id == account_id)
    result = await db.execute(query)
    account = result.scalars().first()

    if not account:
        return fail_response(message="Account not found", status_code=404)

    response_data = jsonable_encoder(AccountResponse.model_validate(account))

    return success_response(
        data=response_data,
        message="Account retrieved successfully"
    )


@router.get("/accounts/{account_id}")
async def read_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(verify_jwt_token)  # 驗證 JWT 並提取 token 資訊
):
    """
    查詢單一帳號資料
    - 僅限用戶查詢自己的帳號資料
    """
    # 從 token 中提取的 account_id 必須與路由中的 account_id 一致
    token_account_id = token_data.get("account_id")
    if token_account_id != account_id:
        raise HTTPException(
            status_code=403,
            detail="您沒有權限查看其他用戶的資料"
        )

    # 查詢目標帳號
    query = select(Account).filter(Account.id == account_id)
    result = await db.execute(query)
    account = result.scalars().first()

    if not account:
        return fail_response(message="Account not found", status_code=404)

    # 返回序列化的帳號資料
    response_data = jsonable_encoder(AccountResponse.model_validate(account))

    return success_response(
        data=response_data,
        message="Account retrieved successfully"
    )


@router.delete("/accounts/{account_id}", response_model=dict)
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """
    刪除帳號資料
    """
    query = select(Account).filter(Account.id == account_id)
    result = await db.execute(query)
    account = result.scalars().first()

    if not account:
        return fail_response(message="Account not found", status_code=404)

    # 確認刪除操作
    await db.delete(account)
    await db.commit()

    return success_response(
        data={"message": f"Account with ID {account.id} deleted successfully!"},
        message="Account deleted successfully"
    )


@router.put("/accounts/{account_id}/password", response_model=dict)
async def change_password(
    account_id: int,
    password_data: PasswordChange,
    request: Request,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(verify_jwt_token)  # 驗證 JWT 並提取 token 資訊
):
    """
    修改帳號密碼
    - 驗證用戶身份（只能修改自己的密碼）
    - 驗證舊密碼
    - 設定新密碼
    """
    # 從 token 中提取的 account_id 必須與路由中的 account_id 一致
    token_account_id = token_data.get("account_id")
    if token_account_id != account_id:
        raise HTTPException(
            status_code=403,
            detail="您沒有權限修改其他用戶的密碼"
        )

    # 查詢目標帳號
    query = select(Account).filter(Account.id == account_id)
    result = await db.execute(query)
    account = result.scalars().first()

    if not account:
        return fail_response(message="Account not found", status_code=404)

    # 驗證舊密碼
    if not verify_password(password_data.old_password, account.password):
        return fail_response(message="Old password is incorrect", status_code=400)

    # 驗證新密碼格式
    validate_password(password_data.new_password)

    # 更新密碼
    account.password = hash_password(password_data.new_password)

    # 獲取用戶 IP 地址
    client_host = request.client.host
    # 更新修改時間和修改人
    account.modified_by = client_host  # 記錄用戶的 IP

    await db.commit()
    await db.refresh(account)

    return success_response(
        data={},
        message="Password updated successfully"
    )


# 登入 API
@router.post("/login")
async def login(request: LoginRequest, req: Request, db: AsyncSession = Depends(get_db)):
    """
    使用 Email + Password 登入，成功則回傳 JWT Token
    """
    query = select(Account).filter(Account.email == request.email)
    result = await db.execute(query)
    account = result.scalars().first()

    if not account or not verify_password(request.password, account.password):
        return fail_response(message="帳號或密碼錯誤", status_code=401)

    # 產生 JWT Token
    token = create_jwt_token({"sub": account.email, "account_id": account.id})
    return {
        "access_token": token,
        "token_type": "bearer"
    }
    # return success_response(
    #     data={"token": token, "token_type": "bearer",
    #           "account_id": account.id, "email": account.email},
    #     message="登入成功"
    # )


# 自定義表單類，用於替代默認的 OAuth2PasswordRequestForm
class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    @property
    def email(self) -> str:
        # 將 `email` 視為 `account`
        return self.username


@router.post("/token", response_model=Token, include_in_schema=False)
async def login_for_access_token(form_data: Annotated[CustomOAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):

    query = select(Account).filter(Account.email == form_data.email)
    result = await db.execute(query)

    account = result.scalars().first()

    if not account or not verify_password(form_data.password, account.password):
        return fail_response(message="帳號或密碼錯誤", status_code=401)

    token = create_jwt_token({"sub": account.email, "account_id": account.id})
    return Token(access_token=token, token_type="bearer")


@router.get("/protected/")
async def protected_route(token_data: dict = Depends(verify_jwt_token)):
    """
    測試 API，只有持有有效 Token 的使用者才能存取
    """
    account_id = token_data.get("account_id")

    return success_response(data={"account_id": account_id}, message="Token 驗證成功")
