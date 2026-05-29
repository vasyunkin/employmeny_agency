from typing import Protocol

from src.dal.interfaces.user_repository import UserRepository
from src.dal.interfaces.resume_repository import ResumeRepository
from src.dal.interfaces.vacancy_repository import VacancyRepository
from src.dal.interfaces.match_repository import MatchRepository
from src.dal.interfaces.interview_slot_repository import InterviewSlotRepository
from src.dal.interfaces.interview_repository import InterviewRepository
from src.dal.interfaces.notification_repository import NotificationRepository


class UnitOfWork(Protocol):
    @property
    def user(self) -> UserRepository:
        ...

    @property
    def resume(self) -> ResumeRepository:
        ...

    @property
    def vacancy(self) -> VacancyRepository:
        ...

    @property
    def match(self) -> MatchRepository:
        ...

    @property
    def interview_slot(self) -> InterviewSlotRepository:
        ...

    @property
    def interview(self) -> InterviewRepository:
        ...

    @property
    def notification(self) -> NotificationRepository:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...