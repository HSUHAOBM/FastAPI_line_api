from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse, PasswordChange, AccountUpdate
from app.database import get_db
from app.utils.password import validate_password, hash_password, verify_password

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

    # 驗證密碼格式
    validate_password(account.password)
    # 加密密碼
    account.password = hash_password(account.password)

    if existing_account:
        raise HTTPException(status_code=400, detail="Account already exists")

    # 新增帳號，將所有參數解包並新增 created_by
    new_account = Account(
        **account.model_dump(),  # 使用 model_dump 方法取代 dict
        created_by=client_host  # 記錄創建者的 IP 地址
    )
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)

    return new_account


@router.get("/accounts/", response_model=list[AccountResponse])
async def read_accounts(db: AsyncSession = Depends(get_db)):
    """
    查詢所有帳號資料
    """
    query = select(Account)
    result = await db.execute(query)
    accounts = result.scalars().all()

    return accounts


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def read_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """
    查詢單一帳號資料
    """
    query = select(Account).filter(Account.id == account_id)
    result = await db.execute(query)
    account = result.scalars().first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@router.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(account_id: int, account_update: AccountUpdate, request: Request, db: AsyncSession = Depends(get_db)):
    """
    更新帳號資料
    - 驗證密碼是否正確
    """
    query = select(Account).filter(Account.id == account_id)
    result = await db.execute(query)
    existing_account = result.scalars().first()

    if not existing_account:
        raise HTTPException(status_code=404, detail="Account not found")

    # 驗證密碼是否正確
    if not verify_password(account_update.password, existing_account.password):
        raise HTTPException(status_code=403, detail="Incorrect password")

    # 更新其他欄位，僅更新有提供的值
    for field, value in account_update.model_dump(exclude={"password"}, exclude_unset=True).items():
        setattr(existing_account, field, value)

    # 獲取用戶 IP 地址
    client_host = request.client.host
    # 更新修改時間和修改人
    existing_account.modified_by = client_host  # 記錄用戶的 IP

    await db.commit()
    await db.refresh(existing_account)

    return existing_account


@router.delete("/accounts/{account_id}", response_model=dict)
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """
    刪除帳號資料
    """
    query = select(Account).filter(Account.id == account_id)
    result = await db.execute(query)
    account = result.scalars().first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # 確認刪除操作
    await db.delete(account)
    await db.commit()

    return {"message": f"Account with ID {account.id} deleted successfully!"}


@router.put("/accounts/{account_id}/password", response_model=dict)
async def change_password(account_id: int, password_data: PasswordChange, request: Request, db: AsyncSession = Depends(get_db)):
    """
    修改帳號密碼
    - 驗證舊密碼
    - 設定新密碼
    """
    query = select(Account).filter(Account.id == account_id)
    result = await db.execute(query)
    account = result.scalars().first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # 驗證舊密碼
    if not verify_password(password_data.old_password, account.password):
        raise HTTPException(
            status_code=400, detail="Old password is incorrect"
        )

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

    return {"message": "Password updated successfully"}
