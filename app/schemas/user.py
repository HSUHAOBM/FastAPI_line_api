from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from app.models.account import BindType
from app.models.user import UserStatus


class UserCreate(BaseModel):
    """
    用於新增使用者資料的結構
    """
    account_id: int = Field(..., description="對應的帳號 ID")
    line_user_id: str = Field(..., max_length=50, description="LINE USER ID")
    user_code: Optional[str] = Field(
        None, max_length=30, description="綁定工號 (如會員編號)")
    user_name: Optional[str] = Field(None, max_length=30, description="綁定姓名")
    bind_type: BindType = Field(..., description="綁定類型 (email or secret)")

    bind_word: Optional[str] = Field(
        None, max_length=50, description="驗證的Email 或綁定用的暗號")
    status: Optional[UserStatus] = Field(
        UserStatus.bound, description="使用者狀態 (1: 已綁定, 2: 未綁定, 3: 失效)")


class UserResponse(BaseModel):
    """
    用於回應的使用者資料結構
    """
    id: int = Field(..., description="使用者 ID")
    account_id: int = Field(..., description="對應的帳號 ID")
    line_user_id: str = Field(..., description="LINE USER ID")
    user_code: Optional[str] = Field(None, description="綁定工號 (如會員編號)")
    user_name: Optional[str] = Field(None, description="綁定姓名")
    bind_type: BindType = Field(..., description="綁定類型 (email or secret)")
    bind_word: Optional[str] = Field(None, description="驗證的Email 或綁定用的暗號")
    status: Optional[UserStatus] = Field(
        UserStatus.bound, description="使用者狀態 (1: 已綁定, 2: 未綁定, 3: 失效)")
    bind_date: Optional[datetime] = Field(None, description="綁定日期時間")
    modified_at: Optional[datetime] = Field(None, description="修改日期")
    modified_by: Optional[str] = Field(None, description="修改者")
    created_at: datetime = Field(..., description="記錄建立時間")
    created_by: Optional[str] = Field(None, description="記錄建立者")

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    """
    用於更新使用者資料的結構
    """
    user_code: Optional[str] = Field(
        None, max_length=30, description="綁定工號 (如會員編號)")
    user_name: Optional[str] = Field(None, max_length=30, description="綁定姓名")
    bind_type: BindType = Field(..., description="綁定類型 (email or secret)")
    bind_word: Optional[str] = Field(
        None, max_length=50, description="驗證的Email 或綁定用的暗號")
    status: Optional[UserStatus] = Field(
        UserStatus.bound, description="使用者狀態 (1: 已綁定, 2: 未綁定, 3: 失效)")
