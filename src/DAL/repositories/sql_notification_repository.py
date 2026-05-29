from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.DAL.interfaces.notification_repository import NotificationRepository
from src.domain.notification import Notification


class SqlNotificationRepository(NotificationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, notification: Notification) -> Notification:
        self._session.add(notification)
        await self._session.flush()
        return notification

    async def get_by_id(self, notification_id: int) -> Notification | None:
        return await self._session.get(Notification, notification_id)

    async def list_by_user(self, user_id: int) -> list[Notification]:
        stmt = select(Notification).where(
            Notification.user_id == user_id
        ).order_by(Notification.notification_id.desc())

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_unread_by_user(self, user_id: int) -> list[Notification]:
        stmt = select(Notification).where(
            (Notification.user_id == user_id) &
            (Notification.is_read == False)
        ).order_by(Notification.notification_id.desc())

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def mark_as_read(self, notification_id: int) -> None:
        stmt = (
            update(Notification)
            .where(Notification.notification_id == notification_id)
            .values(is_read=True)
        )
        await self._session.execute(stmt)

    async def mark_all_as_read(self, user_id: int) -> None:
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id)
            .values(is_read=True)
        )
        await self._session.execute(stmt)