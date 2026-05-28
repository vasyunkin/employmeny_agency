from sqlalchemy.ext.asyncio import AsyncSession


from src.DAL.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.DAL.interfaces.unit_of_work import UnitOfWork


class DALFacade:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._uow = SqlAlchemyUnitOfWork(session)

    @property
    def uow(self) -> UnitOfWork:
        return self._uow


async def get_dal(session: AsyncSession) -> DALFacade:
    return DALFacade(session)


async def get_uow(session: AsyncSession) -> UnitOfWork:
    dal = DALFacade(session)
    return dal.uow