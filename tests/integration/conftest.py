import asyncio
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
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine(event_loop):
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def async_session_factory(engine):
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


@pytest.fixture(scope="session", autouse=True)
async def prepare_database(engine):
    map_tables()
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture
async def session(async_session_factory):
    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def facade(session):
    return DALFacade(session)