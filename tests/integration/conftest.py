import pytest
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from src.DAL.tables.base import metadata
from src.DAL import tables
from src.DAL.tables.map import map_tables
from src.DAL.facade import DALFacade


TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5437/employment_test_db"
)


@pytest.fixture(scope="session")
def event_loop_policy():
    """Использовать единый event loop policy."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture
async def engine():
    """Создаёт движок для тестовой БД."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def session(engine):
    """Создаёт сессию для каждого теста с автоматическим откатом."""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        try:
            await session.rollback()
        except Exception:
            pass


@pytest.fixture(scope="session", autouse=True)
def setup_mapping():
    """Маппинг выполняется только один раз за всю сессию тестов"""
    map_tables()


@pytest.fixture
async def facade(session):
    return DALFacade(session)