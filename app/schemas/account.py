import enum
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from app.models.account import BindType


# 新增帳號請求結構
class AccountCreate(BaseModel):
    password: str = Field(..., min_length=8, max_length=255,
                          description="加密後的密碼，至少 8 個字元")
    manager_name: str = Field(..., max_length=30, description="負責人姓名")
    tel: str = Field(..., max_length=15, description="聯繫電話")
    ext: Optional[str] = Field(None, max_length=10, description="電話分機")
    email: EmailStr = Field(..., description="聯繫 Email，必須是有效的電子郵件格式")
    channel_token: str = Field(..., max_length=300,
                               description="LINE Channel Token")
    channel_secret: str = Field(..., max_length=100,
                                description="LINE Channel Secret")
    bind_type: BindType = Field(..., description="綁定類型 (email or secret)")

    bind_word: str = Field(..., max_length=50, description="綁定用的密碼或驗證碼")
    status: bool = Field(default=True, description="帳號狀態，預設為啟用")


# 更新帳號請求結構
class AccountUpdate(BaseModel):
    password: str = Field(..., min_length=8, max_length=255,
                          description="加密後的密碼，至少 8 個字元")
    manager_name: Optional[str] = Field(
        None, max_length=30, description="負責人姓名")
    tel: Optional[str] = Field(None, max_length=15, description="聯繫電話")
    ext: Optional[str] = Field(None, max_length=10, description="電話分機")
    channel_token: Optional[str] = Field(
        None, max_length=300, description="LINE Channel Token")
    channel_secret: Optional[str] = Field(
        None, max_length=100, description="LINE Channel Secret")
    bind_type: BindType = Field(..., description="綁定類型 (email or secret)")
    bind_word: Optional[str] = Field(
        None, max_length=50, description="綁定用的密碼或驗證碼")
    status: Optional[bool] = Field(None, description="帳號狀態")


class AccountResponse(BaseModel):
    id: int
    manager_name: Optional[str] = Field(None, description="負責人姓名")
    tel: Optional[str] = Field(None, description="聯繫電話")
    ext: Optional[str] = Field(None, description="電話分機")
    email: Optional[EmailStr] = Field(None, description="聯繫 Email")
    channel_token: Optional[str] = Field(
        None, description="LINE Channel Token")
    channel_secret: Optional[str] = Field(
        None, description="LINE Channel Secret")
    bind_type: BindType = Field(..., description="綁定類型 (email or secret)")
    bind_word: Optional[str] = Field(None, description="綁定用的密碼或驗證碼")
    status: bool = Field(..., description="帳號狀態")
    created_at: datetime = Field(..., description="記錄建立時間")
    created_by: Optional[str] = Field(None, description="記錄建立者")
    updated_at: Optional[datetime] = Field(None, description="記錄更新時間")
    modified_by: Optional[str] = Field(None, description="記錄修改者")

    class Config:
        orm_mode = True
        from_attributes = True


class PasswordChange(BaseModel):
    old_password: str = Field(..., description="舊密碼")
    new_password: str = Field(..., min_length=8,
                              max_length=255, description="新密碼，至少 8 個字元")
