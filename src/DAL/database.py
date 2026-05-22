from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.DAL.repositories.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.main.config import PostgresConfig


def get_new_session_maker(
        posgres_config: PostgresConfig
    ) -> async_sessionmaker[AsyncSession]:
        engine = create_async_engine(posgres_config.build_dsn())
        return async_sessionmaker(engine, autoflush=False, expire_on_commit=False)


async def get_uow(session_maker: async_sessionmaker[AsyncSession]) -> SqlAlchemyUnitOfWork:
    async with session_maker() as session:
        uow = SqlAlchemyUnitOfWork(session)
        async with uow:
            yield uow