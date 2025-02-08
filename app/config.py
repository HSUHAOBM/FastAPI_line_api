import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mysecretkey")  # 請改為更安全的值


settings = Settings()
