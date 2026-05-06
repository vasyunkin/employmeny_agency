from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    """Запускаем контейнер Postgres"""
    with PostgresContainer("postgres:15-alpine", driver="asyncpg") as postgres:
        yield {
            "host": postgres.get_container_host_ip(),
            "port": postgres.get_exposed_port(5432),
            "user": postgres.username,
            "password": postgres.password,
            "db": postgres.dbname,
        }


@pytest_asyncio.fixture(scope="session")
async def postgres_engine(postgres_container, request):
    """Создаем engine и накатываем таблицы"""
    DATABASE_URL = (
        f"postgresql+asyncpg://{postgres_container['user']}:{postgres_container['password']}@"
        f"{postgres_container['host']}:{postgres_container['port']}/{postgres_container['db']}"
    )

    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))

        sql_path = Path(request.config.rootpath) / "create-tables.sql"
        if sql_path.exists():
            sql_script = sql_path.read_text(encoding="utf-8")
            for statement in sql_script.split(";"):
                cleaned = statement.strip()
                if cleaned:
                    await conn.execute(text(cleaned))
        else:
            # Если нет sql-скрипта — создаём таблицы через metadata
            from src.DAL.tables.base import Base
            from src.DAL.tables.user_orm import UserORM  # для импорта модели
            await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(postgres_engine):
    """Сессия с автоматическим rollback после теста"""
    async_session = async_sessionmaker(
        bind=postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
def async_session_maker(postgres_engine):
    """Фабрика сессий для UnitOfWork"""
    return async_sessionmaker(
        bind=postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
