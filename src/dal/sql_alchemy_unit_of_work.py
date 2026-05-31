from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.dal.interfaces.unit_of_work import UnitOfWork
from src.dal.interfaces.user_repository import UserRepository
from src.dal.interfaces.resume_repository import ResumeRepository
from src.dal.interfaces.vacancy_repository import VacancyRepository
from src.dal.interfaces.match_repository import MatchRepository
from src.dal.interfaces.interview_slot_repository import InterviewSlotRepository
from src.dal.interfaces.interview_repository import InterviewRepository
from src.dal.interfaces.notification_repository import NotificationRepository
from src.dal.repositories.sql_user_repository import SQLUserRepository
from src.dal.repositories.sql_resume_repository import SqlResumeRepository
from src.dal.repositories.sql_vacancy_repository import SqlVacancyRepository
from src.dal.repositories.sql_match_repository import SqlMatchRepository
from src.dal.repositories.sql_interview_slot_repository import SqlInterviewSlotRepository
from src.dal.repositories.sql_interview_repository import SqlInterviewRepository
from src.dal.repositories.sql_notification_repository import SqlNotificationRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session

        self._user = None
        self._resume = None
        self._vacancy = None
        self._match = None
        self._interview_slot = None
        self._interview = None
        self._notification = None


    @property
    def user(self) -> UserRepository:
        if self._user is None:
            self._user = SQLUserRepository(self._session)
        return self._user

    @property
    def resume(self) -> ResumeRepository:
        if self._resume is None:
            self._resume = SqlResumeRepository(self._session)
        return self._resume

    @property
    def vacancy(self) -> VacancyRepository:
        if self._vacancy is None:
            self._vacancy = SqlVacancyRepository(self._session)
        return self._vacancy

    @property
    def match(self) -> MatchRepository:
        if self._match is None:
            self._match = SqlMatchRepository(self._session)
        return self._match

    @property
    def interview_slot(self) -> InterviewSlotRepository:
        if self._interview_slot is None:
            self._interview_slot = SqlInterviewSlotRepository(self._session)
        return self._interview_slot

    @property
    def interview(self) -> InterviewRepository:
        if self._interview is None:
            self._interview = SqlInterviewRepository(self._session)
        return self._interview

    @property
    def notification(self) -> NotificationRepository:
        if self._notification is None:
            self._notification = SqlNotificationRepository(self._session)
        return self._notification


    async def get_match_detail(self, match_id: int) -> Optional["Match"]:
        match = await self._match.get_by_id(match_id)
        if match:
            resume = await self.resume.get_by_id(match.resume_id)
            vacancy = await self.vacancy.get_by_id(match.vacancy_id)

            if resume:
                match.resume = resume
            if vacancy:
                match.vacancy = vacancy

        return match


    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()

        await self._session.close()