import asyncio
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

from src.dal.database import async_session_factory
from src.domain.user import User, UserRole
from src.dal.tables.map import map_tables

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=100000
)


async def seed_recruiter():
    print("Seeding initial recruiter...")

    login = "recruiter"
    raw_password = "1234"
    hashed_password = pwd_context.hash(raw_password)

    async with async_session_factory() as session:
        async with session.begin():
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.user_login == login)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"User '{login}' already exists. Skipping...")
                return

            recruiter = User(
                user_login=login,
                password_hash=hashed_password,
                first_name="System",
                last_name="Recruiter",
                user_role=UserRole.RECRUITER
            )

            session.add(recruiter)

    print(f"Successfully created recruiter!")
    print(f"Login: {login}")
    print(f"Password: {raw_password}")


if __name__ == "__main__":
    import sys

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(seed_recruiter())