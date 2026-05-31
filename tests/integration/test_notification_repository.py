"""
Тесты для SqlNotificationRepository.
"""

import pytest

from src.domain.notification import Notification

class TestNotificationRepositoryCreate:
    """Тесты метода create."""

    @pytest.mark.asyncio
    async def test_create_notification_success(self, facade, test_user):
        """Успешное создание уведомления."""
        repo = facade.uow.notification

        notification = Notification(
            user_id=test_user.user_id,
            notification_type="match_created",
            message="Ваше резюме было сопоставлено с новой вакансией!",
        )

        created = await repo.create(notification)

        assert created.notification_id is not None
        assert created.user_id == test_user.user_id
        assert created.notification_type == "match_created"
        assert created.is_read is False


class TestNotificationRepositoryGetById:
    """Тесты метода get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, facade, test_user):
        repo = facade.uow.notification

        notification = Notification(
            user_id=test_user.user_id,
            notification_type="test",
            message="Test message",
        )
        created = await repo.create(notification)

        found = await repo.get_by_id(created.notification_id)

        assert found is not None
        assert found.notification_id == created.notification_id
        assert found.user_id == test_user.user_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, facade):
        repo = facade.uow.notification
        result = await repo.get_by_id(999999)
        assert result is None


class TestNotificationRepositoryListByUser:
    """Тесты метода list_by_user."""

    @pytest.mark.asyncio
    async def test_list_by_user_success(self, facade, test_user):
        repo = facade.uow.notification

        await repo.create(Notification(user_id=test_user.user_id, message="Message 1"))
        await repo.create(Notification(user_id=test_user.user_id, message="Message 2"))
        await repo.create(Notification(user_id=test_user.user_id, message="Message 3"))

        notifications = await repo.list_by_user(test_user.user_id)

        assert len(notifications) == 3
        # Проверка сортировки по убыванию notification_id
        assert notifications[0].notification_id > notifications[1].notification_id

    @pytest.mark.asyncio
    async def test_list_by_user_empty(self, facade, test_user):
        repo = facade.uow.notification
        notifications = await repo.list_by_user(test_user.user_id)
        assert len(notifications) == 0


class TestNotificationRepositoryListUnread:
    """Тесты метода list_unread_by_user."""

    @pytest.mark.asyncio
    async def test_list_unread_by_user(self, facade, test_user):
        repo = facade.uow.notification

        # Создаём прочитанные и непрочитанные уведомления
        await repo.create(Notification(user_id=test_user.user_id, message="Unread 1", is_read=False))
        await repo.create(Notification(user_id=test_user.user_id, message="Unread 2", is_read=False))
        await repo.create(Notification(user_id=test_user.user_id, message="Read", is_read=True))

        unread = await repo.list_unread_by_user(test_user.user_id)

        assert len(unread) == 2
        for n in unread:
            assert n.is_read is False

    @pytest.mark.asyncio
    async def test_list_unread_empty(self, facade, test_user):
        repo = facade.uow.notification
        unread = await repo.list_unread_by_user(test_user.user_id)
        assert len(unread) == 0


class TestNotificationRepositoryMarkAsRead:
    """Тесты методов пометки как прочитанное."""

    @pytest.mark.asyncio
    async def test_mark_as_read_single(self, facade, test_user):
        repo = facade.uow.notification

        notification = Notification(user_id=test_user.user_id, message="Test notification")
        created = await repo.create(notification)

        await repo.mark_as_read(created.notification_id)

        updated = await repo.get_by_id(created.notification_id)
        assert updated.is_read is True

    @pytest.mark.asyncio
    async def test_mark_all_as_read(self, facade, test_user):
        repo = facade.uow.notification

        await repo.create(Notification(user_id=test_user.user_id, message="Msg 1", is_read=False))
        await repo.create(Notification(user_id=test_user.user_id, message="Msg 2", is_read=False))
        await repo.create(Notification(user_id=test_user.user_id, message="Msg 3", is_read=False))

        await repo.mark_all_as_read(test_user.user_id)

        unread = await repo.list_unread_by_user(test_user.user_id)
        assert len(unread) == 0