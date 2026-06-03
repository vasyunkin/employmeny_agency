from dishka import FromDishka

from src.dal.facade import DALFacade
from src.domain.notification import Notification

from .notification_dto import (
    NotificationCreateIn,
    NotificationOut,
)
from .n_exceptions import (
    NotificationNotFound,
    ForbiddenNotificationAccess
)


class NotificationService:
    def __init__(self, dal: FromDishka[DALFacade]):
        self.dal = dal

    async def create(self, data: NotificationCreateIn) -> NotificationOut:
        async with self.dal.uow as uow:
            notification = Notification(
                user_id=data.user_id,
                notification_type=data.notification_type,
                message=data.message,
                match_id=data.match_id  # Добавлен match_id
            )

            created = await uow.notification.create(notification)
            await uow.commit()

            return NotificationOut.model_validate(created)

    async def get_by_id(
        self,
        notification_id: int,
        user_id: int
    ) -> NotificationOut:
        """Получить уведомление"""
        async with self.dal.uow as uow:
            notification = await uow.notification.get_by_id(notification_id)

            if not notification:
                raise NotificationNotFound(notification_id)

            if notification.user_id != user_id:
                raise ForbiddenNotificationAccess(notification_id, user_id)

            return NotificationOut.model_validate(notification)

    async def list_by_user(self, user_id: int) -> list[NotificationOut]:
        """Все уведомления пользователя"""
        async with self.dal.uow as uow:
            notifications = await uow.notification.list_by_user(user_id)
            return [NotificationOut.model_validate(n) for n in notifications]

    async def list_unread(self, user_id: int) -> list[NotificationOut]:
        """Только непрочитанные"""
        async with self.dal.uow as uow:
            notifications = await uow.notification.list_unread_by_user(user_id)
            return [NotificationOut.model_validate(n) for n in notifications]

    async def mark_as_read(
        self,
        notification_id: int,
        user_id: int
    ) -> None:
        """Отметить одно уведомление как прочитанное"""
        async with self.dal.uow as uow:
            notification = await uow.notification.get_by_id(notification_id)

            if not notification:
                raise NotificationNotFound(notification_id)

            if notification.user_id != user_id:
                raise ForbiddenNotificationAccess(notification_id, user_id)

            await uow.notification.mark_as_read(notification_id)
            await uow.commit()

    async def mark_all_as_read(self, user_id: int) -> None:
        """Отметить все уведомления пользователя как прочитанные"""
        async with self.dal.uow as uow:
            await uow.notification.mark_all_as_read(user_id)
            await uow.commit()