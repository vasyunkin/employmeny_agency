from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM

from src.domain.user import UserRole
from src.DAL.tables.base import Base


user_roles_enum = ENUM(
    UserRole,
    name='user_roles',
    create_type=False,
    values_callable=lambda obj: [e.value for e in obj]
)


class UserORM(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_login: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    user_role: Mapped[UserRole] = mapped_column(
        user_roles_enum,
        nullable=False,
        default=UserRole.APPLICANT,
        server_default="applicant",
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)