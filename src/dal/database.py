from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from src.dal.tables.map import map_tables
from src.main.config import PostgresConfig


postgres_config = PostgresConfig()
DATABASE_URL = postgres_config.build_dsn()

map_tables()


engine = create_async_engine(
    DATABASE_URL,
    echo=postgres_config.enable_logging,
    future=True,
)


async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)