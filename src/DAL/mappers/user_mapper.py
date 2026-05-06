from src.domain.user import User
from src.DAL.tables.user_orm import UserORM


def to_domain(user_orm: UserORM) -> User:
    return User(
        user_id=user_orm.user_id,
        user_login=user_orm.user_login,
        password_hash=user_orm.password_hash,
        first_name=user_orm.first_name,
        last_name=user_orm.last_name,
        user_role=user_orm.user_role,
    )


def from_domain(user: User) -> UserORM:
    return UserORM(
        user_login=user.user_login,
        password_hash=user.password_hash,
        first_name=user.first_name,
        last_name=user.last_name,
        user_role=user.user_role,
    )