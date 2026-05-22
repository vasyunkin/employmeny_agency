from typing import Optional

from sqlalchemy import select, update, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.DAL.interfaces.match_repository import MatchRepository
from src.domain.match import Match, MatchStatus


class SqlMatchRepository(MatchRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, match: Match) -> Match:
        self._session.add(match)
        await self._session.flush()
        return match

    async def update(self, match: Match) -> None:
        stmt = (
            update(Match)
            .where(Match.match_id == match.match_id)
            .values(
                resume_id=match.resume_id,
                vacancy_id=match.vacancy_id,
                recruiter_id=match.recruiter_id,
                match_status=match.match_status
            )
        )
        await self._session.execute(stmt)

    async def delete(self, match_id: int) -> None:
        stmt = delete(Match).where(Match.match_id == match_id)
        await self._session.execute(stmt)

    async def get_by_id(self, match_id: int) -> Match | None:
        return await self._session.get(Match, match_id)

    async def exists(self, vacancy_id: int, resume_id: int) -> bool:
        stmt = select(
            exists().where(
                (Match.vacancy_id == vacancy_id) &
                (Match.resume_id == resume_id)
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def get_by_resume_and_vacancy(
        self,
        resume_id: int,
        vacancy_id: int
    ) -> Match | None:
        stmt = select(Match).where(
            (Match.resume_id == resume_id) &
            (Match.vacancy_id == vacancy_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_recruiter(self, recruiter_id: int) -> list[Match]:
        stmt = select(Match).where(
            Match.recruiter_id == recruiter_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_resume(self, resume_id: int) -> list[Match]:
        stmt = select(Match).where(
            Match.resume_id == resume_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_vacancy(self, vacancy_id: int) -> list[Match]:
        stmt = select(Match).where(
            Match.vacancy_id == vacancy_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def search(
        self,
        recruiter_id: Optional[int] = None,
        status: Optional[MatchStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Match]:

        stmt = select(Match)

        if recruiter_id is not None:
            stmt = stmt.where(
                Match.recruiter_id == recruiter_id
            )

        if status is not None:
            stmt = stmt.where(
                Match.match_status == status
            )

        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())