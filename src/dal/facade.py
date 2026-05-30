from typing import Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.dal.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.dal.interfaces.unit_of_work import UnitOfWork


class DALFacade:
    def __init__(self, session_or_factory: Union[AsyncSession, async_sessionmaker]):
        self._session_factory: Optional[async_sessionmaker] = None      # для production
        self._session: Optional[AsyncSession] = None                    # для тестов
        self._uow: Optional[SqlAlchemyUnitOfWork] = None

        if isinstance(session_or_factory, async_sessionmaker):
            self._session_factory = session_or_factory
        else:
            self._session = session_or_factory
            self._uow = SqlAlchemyUnitOfWork(self._session)

    def _get_session(self) -> AsyncSession:
        if self._session is not None:
            return self._session

        if self._session_factory is not None:
            self._session = self._session_factory()
            return self._session

        raise RuntimeError("No session or session factory provided")

    @property
    def uow(self) -> UnitOfWork:
        if self._uow is None:
            session = self._get_session()
            self._uow = SqlAlchemyUnitOfWork(session)
        return self._uow


async def get_dal_facade() -> DALFacade:
    from src.dal.database import async_session_factory
    return DALFacade(async_session_factory)