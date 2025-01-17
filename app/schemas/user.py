from pydantic import BaseModel


# 定義請求的結構
class UserCreate(BaseModel):
    user_name: str
    user_id: str
    account_id: int


# 定義回應的結構
class UserResponse(BaseModel):
    id: int
    user_name: str
    user_id: str

    class Config:
        orm_mode = True  # 支援 ORM 轉換


class UserUpdate(BaseModel):
    user_name: str
