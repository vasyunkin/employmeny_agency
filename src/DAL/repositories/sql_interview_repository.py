from sqlalchemy import select, update, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.DAL.interfaces.interview_repository import InterviewRepository
from src.domain.interview import Interview


class SqlInterviewRepository(InterviewRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, interview: Interview) -> Interview:
        self._session.add(interview)
        await self._session.flush()
        return interview

    async def get_by_id(self, interview_id: int) -> Interview | None:
        return await self._session.get(Interview, interview_id)

    async def get_by_match_id(self, match_id: int) -> Interview | None:
        stmt = select(Interview).where(
            Interview.match_id == match_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_slot(self, slot_id: int) -> bool:
        stmt = select(
            exists().where(Interview.slot_id == slot_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def update_applicant_feedback(
        self,
        interview_id: int,
        feedback: bool
    ) -> None:
        stmt = (
            update(Interview)
            .where(Interview.interview_id == interview_id)
            .values(feedback_applicant=feedback)
        )
        await self._session.execute(stmt)

    async def update_employer_feedback(
        self,
        interview_id: int,
        feedback: bool
    ) -> None:
        stmt = (
            update(Interview)
            .where(Interview.interview_id == interview_id)
            .values(feedback_employer=feedback)
        )
        await self._session.execute(stmt)