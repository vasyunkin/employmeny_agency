from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.DAL.interfaces.vacancy_repository import VacancyRepository
from src.domain.vacancy import Vacancy


class SqlVacancyRepository(VacancyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, vacancy: Vacancy) -> Vacancy:
        self._session.add(vacancy)
        await self._session.flush()
        return vacancy

    async def get_by_id(self, vacancy_id: int) -> Vacancy | None:
        return await self._session.get(Vacancy, vacancy_id)

    async def list_by_employer(self, employer_id: int) -> list[Vacancy]:
        stmt = select(Vacancy).where(
            Vacancy.employer_id == employer_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def deactivate(self, vacancy_id: int) -> None:
        stmt = (
            update(Vacancy)
            .where(Vacancy.vacancy_id == vacancy_id)
            .values(is_active=False)
        )
        await self._session.execute(stmt)

    async def search(
        self,
        title: Optional[str] = None,
        min_salary: Optional[float] = None,
        is_active: Optional[bool] = True,
        limit: int = 50,
        offset: int = 0
    ) -> list[Vacancy]:

        stmt = select(Vacancy)

        if title is not None:
            stmt = stmt.where(
                Vacancy.title.ilike(f"%{title}%")
            )

        if min_salary is not None:
            stmt = stmt.where(
                Vacancy.salary >= min_salary
            )

        if is_active is not None:
            stmt = stmt.where(
                Vacancy.is_active == is_active
            )

        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())