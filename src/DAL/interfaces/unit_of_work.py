from typing import Protocol

from src.DAL.interfaces.user_repository import UserRepository
from src.DAL.interfaces.resume_repository import ResumeRepository
from src.DAL.interfaces.vacancy_repository import VacancyRepository
from src.DAL.interfaces.match_repository import MatchRepository
from src.DAL.interfaces.interview_slot_repository import InterviewSlotRepository
from src.DAL.interfaces.interview_repository import InterviewRepository
from src.DAL.interfaces.notification_repository import NotificationRepository


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