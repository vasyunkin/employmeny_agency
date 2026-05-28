import pytest

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from src.DAL.tables.base import metadata
from src.DAL import tables
from src.DAL.facade import DALFacade


TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5437/employment_test_db"
)


engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)


async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture
async def session():
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def facade(session):
    return DALFacade(session)