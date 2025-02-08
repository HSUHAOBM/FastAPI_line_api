from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from app.models.account import BindType


class UserStatus(enum.Enum):
    BOUND = "bound"
    UNBOUND = "unbound"
    INACTIVE = "inactive"


class User(Base):
    __tablename__ = "user"  # 資料表名稱

    id = Column(Integer, primary_key=True, autoincrement=True,
                nullable=False, comment="流水號 (主鍵)")
    account_id = Column(
        Integer, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    line_user_id = Column(String(50), nullable=False, comment="LINE USER ID")
    user_code = Column(String(30), nullable=True, comment="綁定工號 (如會員編號)")
    user_name = Column(String(30), nullable=True, comment="綁定姓名")
    bind_type = Column(Enum(BindType), nullable=True,
                       comment="綁定類別 email or secret")
    bind_word = Column(String(50), nullable=True, comment="驗證的Email 或綁定用的暗號")
    status = Column(Enum(UserStatus), default=UserStatus.UNBOUND,
                    nullable=False, comment="狀態 (BOUND: 已綁定, UNBOUND: 未綁定, inactive: 失效)")
    bind_date = Column(DateTime, nullable=True, comment="綁定日期時間")
    modified_at = Column(DateTime, default=func.now(),
                         onupdate=func.now(), nullable=True, comment="修改日期")
    modified_by = Column(String(30), nullable=True, comment="修改者")
    created_at = Column(DateTime,  default=func.now(),
                        nullable=False, comment="記錄建立時間")
    created_by = Column(String(30), nullable=True, comment="記錄建立者")

    # 定義與 account 的多對一關係
    account = relationship("Account", back_populates="users")
    # 定義與 EmailVerifyCode 的一對多關係
    email_verify_codes = relationship("EmailVerifyCode", back_populates="user")
