from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    """Запускаем контейнер Postgres через testcontainers"""
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
        # Очистка и создание схемы
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))

        # Чтение твоего SQL скрипта
        sql_path = Path(request.config.rootpath) / "create-tables.sql"
        sql_script = sql_path.read_text(encoding="utf-8")

        for statement in sql_script.split(";"):
            cleaned_statement = statement.strip()
            if cleaned_statement:
                await conn.execute(text(cleaned_statement))

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(postgres_engine):
    """Сессия с откатом для изоляции тестов"""
    async_session = async_sessionmaker(
        bind=postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()
