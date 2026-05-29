from abc import abstractmethod
from typing import Protocol

from src.domain.notification import Notification


class NotificationRepository(Protocol):
    @abstractmethod
    async def create(self, notification: Notification) -> Notification:
        ...

    @abstractmethod
    async def get_by_id(self, notification_id: int) -> Notification | None:
        ...

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[Notification]:
        ...

    @abstractmethod
    async def list_unread_by_user(self, user_id: int) -> list[Notification]:
        ...

    @abstractmethod
    async def mark_as_read(self, notification_id: int) -> None:
        ...

    @abstractmethod
    async def mark_all_as_read(self, user_id: int) -> None:
        ...