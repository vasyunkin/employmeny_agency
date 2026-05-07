import pytest
import pytest_asyncio
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer

from src.DAL.tables.map import map_tables


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine", driver="asyncpg") as postgres:
        yield {
            "host": postgres.get_container_host_ip(),
            "port": postgres.get_exposed_port(5432),
            "user": postgres.username,
            "password": postgres.password,
            "db": postgres.dbname,
        }


@pytest_asyncio.fixture(scope="session")
async def postgres_engine(postgres_container):
    """Создаём тестовую БД через create-tables.sql"""
    DATABASE_URL = (
        f"postgresql+asyncpg://{postgres_container['user']}:{postgres_container['password']}@"
        f"{postgres_container['host']}:{postgres_container['port']}/{postgres_container['db']}"
    )

    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        # Полная очистка и создание схемы
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))

        # Выполняем твой create-tables.sql
        sql_path = Path(__file__).parent.parent.parent / "create-tables.sql"
        sql_script = sql_path.read_text(encoding="utf-8")

        for statement in sql_script.split(";"):
            cleaned = statement.strip()
            if cleaned and not cleaned.startswith("--"):
                await conn.execute(text(cleaned))

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(postgres_engine):
    """Сессия для каждого теста"""
    async_session = async_sessionmaker(
        bind=postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session() as session:
        map_tables()           # imperative mapping
        yield session
        await session.rollback()   # откатываем все изменения теста