from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from testcontainers.postgres import PostgresContainer


# ==================== Важные настройки ====================
@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def postgres_container():
    """Запускаем Postgres контейнер один раз на всю сессию тестов"""
    with PostgresContainer("postgres:15-alpine", driver="asyncpg") as postgres:
        yield {
            "host": postgres.get_container_host_ip(),
            "port": postgres.get_exposed_port(5432),
            "user": postgres.username,
            "password": postgres.password,
            "db": postgres.dbname,
        }


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def postgres_engine(postgres_container, request):
    """Создаём engine + таблицы"""
    DATABASE_URL = (
        f"postgresql+asyncpg://{postgres_container['user']}:{postgres_container['password']}@"
        f"{postgres_container['host']}:{postgres_container['port']}/{postgres_container['db']}"
    )

    engine = create_async_engine(DATABASE_URL, echo=False, future=True)

    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))

        # Пытаемся использовать SQL-скрипт, если есть
        sql_path = Path(request.config.rootpath) / "create-tables.sql"
        if sql_path.exists():
            sql_script = sql_path.read_text(encoding="utf-8")
            for stmt in sql_script.split(";"):
                cleaned = stmt.strip()
                if cleaned:
                    await conn.execute(text(cleaned))
        else:
            # Fallback — создаём через SQLAlchemy
            from src.DAL.tables.base import Base
            await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def db_session(postgres_engine):
    """Сессия для обычных тестов репозитория (с rollback)"""
    async_session = async_sessionmaker(
        bind=postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()   # Откатываем изменения после каждого теста


@pytest_asyncio.fixture(scope="function", loop_scope="function")
def async_session_maker(postgres_engine):
    """Фабрика сессий для UnitOfWork"""
    return async_sessionmaker(
        bind=postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )