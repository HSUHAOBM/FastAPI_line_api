from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from app.database import Base


class Account(Base):
    __tablename__ = "account"

    # 主鍵
    id = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, comment="公司代號 (自動增長主鍵)"
    )

    # 公司基本資訊
    password = Column(String(255), nullable=False, comment="加密後的密碼")
    manager_name = Column(String(30), nullable=True, comment="負責人姓名")
    tel = Column(String(15), nullable=True, comment="聯繫電話")
    ext = Column(String(10), nullable=True, comment="電話分機")
    email = Column(
        String(50), unique=True, nullable=True, comment="聯繫 Email（唯一）"
    )

    # LINE 設定
    channel_token = Column(String(300), nullable=True,
                           comment="LINE Channel Token")
    channel_secret = Column(String(100), nullable=True,
                            comment="LINE Channel Secret")
    bind_type = Column(
        String(1), nullable=True, comment="綁定類別 (1: Email, 2: 暗號)"
    )
    bind_word = Column(String(50), nullable=True, comment="綁定用的密碼或驗證碼")

    # 狀態
    status = Column(Boolean, default=True, nullable=False,
                    comment="狀態 (True: 啟用, False: 停用)")

    # 時間戳與操作記錄
    created_at = Column(DateTime,  default=func.now(),
                        nullable=False, comment="記錄建立時間")
    created_by = Column(String(30), nullable=True, comment="記錄建立者")
    updated_at = Column(DateTime, default=func.now(),
                        onupdate=func.now(), nullable=True, comment="記錄更新時間")
    modified_by = Column(String(30), nullable=True, comment="記錄修改者")

    # 定義與 User 的一對多關係
    users = relationship("User", back_populates="account")
