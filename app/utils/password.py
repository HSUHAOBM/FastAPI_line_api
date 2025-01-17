import bcrypt
import re
from fastapi import HTTPException

# 密碼驗證正則表達式
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$"


def validate_password(password: str):
    """
    驗證密碼是否符合規範：
    至少 1 個大寫字母，1 個小寫字母，1 個數字，最少 8 位元。
    """
    if not re.match(PASSWORD_REGEX, password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long, "
                   "contain at least one uppercase letter, one lowercase letter, and one number.",
        )


def hash_password(password: str) -> str:
    """
    使用 bcrypt 對密碼進行加密。
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    驗證用戶輸入的密碼是否正確。

    Args:
        plain_password (str): 用戶輸入的明文密碼。
        hashed_password (str): 儲存在資料庫中的加密密碼。

    Returns:
        bool: 如果密碼正確，返回 True；否則返回 False。
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
