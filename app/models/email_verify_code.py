from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class EmailVerifyCode(Base):
    __tablename__ = "email_verify_code"  # 資料表名稱

    id = Column(Integer, primary_key=True, autoincrement=True,
                nullable=False, comment="流水號 (主鍵)")
    account_id = Column(
        Integer, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("user.id"),
                     nullable=False, comment="對應的用戶 ID")
    email = Column(String(50), unique=True, nullable=False, comment="EMAIL")
    verify_code = Column(String(10), nullable=False, comment="驗證碼")
    efficient_time = Column(DateTime, nullable=False, comment="有效時間")
    created_at = Column(DateTime, nullable=False, comment="建立時間")
    created_by = Column(String(30), default=func.now(),
                        nullable=True, comment="建立者")

    # 定義與 User 的多對一關係
    user = relationship("User", back_populates="email_verify_codes")
