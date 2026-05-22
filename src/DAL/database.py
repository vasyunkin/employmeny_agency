from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker
)

from src.DAL.repositories.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.main.config import PostgresConfig


postgres_config = PostgresConfig()
DATABASE_URL = postgres_config.build_dsn()


engine = create_async_engine(
    DATABASE_URL,
    echo=postgres_config.enable_logging,
    future=True,
)


async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_uow():
    async with async_session_factory() as session:
        uow = SqlAlchemyUnitOfWork(session)

        try:
            yield uow
            await uow.commit()
        except Exception:
            await uow.rollback()
            raise
        finally:
            await session.close()