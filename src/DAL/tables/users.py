from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.dialects.postgresql import ENUM

from src.domain.user import User, UserRole
from src.DAL.tables.base import metadata, mapper_registry


user_roles_enum = ENUM(
    UserRole,
    name='user_roles',
    create_type=True,
    values_callable=lambda obj: [e.value for e in obj]
)


users_table = Table(
    'users',
    metadata,
    Column("user_id", Integer, primary_key=True),
    Column("user_login", String, unique=True, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("user_role", user_roles_enum, nullable=False, server_default="applicant"),
    Column("first_name", String(50), nullable=False),
    Column("last_name", String(50), nullable=False),
)


def map_users_table() -> None:
    mapper_registry.map_imperatively(User, users_table)