from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, exists

from typing import Optional

from src.dal.interfaces.resume_repository import ResumeRepository
from src.domain.resume import Resume


class SqlResumeRepository(ResumeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, resume: Resume) -> Resume:
        self._session.add(resume)
        await self._session.flush()
        return resume

    async def get_by_id(self, resume_id: int) -> Resume | None:
        return await self._session.get(Resume, resume_id)

    async def list_by_applicant(self, applicant_id: int) -> list[Resume]:
        stmt = select(Resume).where(Resume.applicant_id == applicant_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def deactivate(self, resume_id: int) -> None:
        stmt = (
            update(Resume)
            .where(Resume.resume_id == resume_id)
            .values(is_active=False)
        )
        await self._session.execute(stmt)

    async def exists_similar(
        self,
        applicant_id: int,
        desired_position: str
    ) -> bool:
        stmt = select(
            exists().where(
                (Resume.applicant_id == applicant_id) &
                (Resume.desired_position == desired_position) &
                (Resume.is_active == True)
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def search(
            self,
            desired_position: Optional[str] = None,
            min_experience: Optional[int] = None,
            is_active: Optional[bool] = True,
            limit: int = 10,
            offset: int = 0
    ) -> list[Resume]:

        stmt = select(Resume)

        if desired_position is not None:
            stmt = stmt.where(
                Resume.desired_position.ilike(f"%{desired_position}%")
            )

        if min_experience is not None:
            stmt = stmt.where(
                Resume.experience_years >= min_experience
            )

        if is_active is not True:
            stmt = stmt.where(
                Resume.is_active == is_active
            )

        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

