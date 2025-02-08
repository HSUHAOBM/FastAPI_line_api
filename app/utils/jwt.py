from jose import jwt
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel
from app.config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

# 設定 JWT 加密金鑰和過期時間
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token 有效時間（60 分鐘）


class Token(BaseModel):
    access_token: str
    token_type: str


def create_jwt_token(data: dict):
    """
    產生 JWT Token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


# 驗證 Token 的函式
def verify_jwt_token(token: str = Depends(oauth2_scheme)):
    """
    驗證 JWT Token 並返回解碼後的 payload
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        account_id = payload.get("account_id")
        if account_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload  # 回傳完整的 payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已過期")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
