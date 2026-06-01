import pytest

from src.service.notification.notification_dto import (
    NotificationCreateIn,
    NotificationOut
)
from src.service.notification.n_exceptions import (
    NotificationNotFound,
    ForbiddenNotificationAccess
)


class TestNotificationServiceCreate:
    """Тесты для метода create"""

    @pytest.mark.asyncio
    async def test_create_success(
            self,
            notification_service,
            mock_uow,
            sample_notification,
            create_notification_data
    ):
        """Успешное создание уведомления"""
        # Arrange
        mock_uow.notification.create.return_value = sample_notification

        # Act
        result = await notification_service.create(create_notification_data)

        # Assert
        mock_uow.notification.create.assert_awaited_once()
        call_args = mock_uow.notification.create.call_args[0][0]
        assert call_args.user_id == create_notification_data.user_id
        assert call_args.notification_type == create_notification_data.notification_type
        assert call_args.message == create_notification_data.message

        mock_uow.commit.assert_awaited_once()

        assert isinstance(result, NotificationOut)
        assert result.notification_id == sample_notification.notification_id
        assert result.user_id == sample_notification.user_id
        assert result.notification_type == sample_notification.notification_type
        assert result.message == sample_notification.message
        assert result.is_read == sample_notification.is_read


class TestNotificationServiceGetById:
    """Тесты для метода get_by_id"""

    @pytest.mark.asyncio
    async def test_get_by_id_success(
            self,
            notification_service,
            mock_uow,
            sample_notification
    ):
        """Успешное получение уведомления по ID"""
        # Arrange
        notification_id = 1
        user_id = 100
        mock_uow.notification.get_by_id.return_value = sample_notification

        # Act
        result = await notification_service.get_by_id(notification_id, user_id)

        # Assert
        mock_uow.notification.get_by_id.assert_awaited_once_with(notification_id)
        assert result.notification_id == notification_id
        assert result.user_id == user_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(
            self,
            notification_service,
            mock_uow
    ):
        """Уведомление не найдено -> ошибка NotificationNotFound"""
        # Arrange
        notification_id = 999
        user_id = 100
        mock_uow.notification.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotificationNotFound) as exc_info:
            await notification_service.get_by_id(notification_id, user_id)

        assert exc_info.value.notification_id == notification_id

    @pytest.mark.asyncio
    async def test_get_by_id_forbidden_access(
            self,
            notification_service,
            mock_uow,
            sample_notification
    ):
        """Попытка получить чужое уведомление -> ForbiddenNotificationAccess"""
        # Arrange
        notification_id = 1
        owner_id = 100
        stranger_id = 999
        sample_notification.user_id = owner_id
        mock_uow.notification.get_by_id.return_value = sample_notification

        # Act & Assert
        with pytest.raises(ForbiddenNotificationAccess) as exc_info:
            await notification_service.get_by_id(notification_id, stranger_id)

        assert exc_info.value.notification_id == notification_id
        assert exc_info.value.user_id == stranger_id


class TestNotificationServiceListByUser:
    """Тесты для метода list_by_user"""

    @pytest.mark.asyncio
    async def test_list_by_user_success(
            self,
            notification_service,
            mock_uow,
            sample_notification
    ):
        """Успешное получение списка уведомлений пользователя"""
        # Arrange
        user_id = 100
        notifications = [sample_notification]
        mock_uow.notification.list_by_user.return_value = notifications

        # Act
        result = await notification_service.list_by_user(user_id)

        # Assert
        mock_uow.notification.list_by_user.assert_awaited_once_with(user_id)
        assert len(result) == 1
        assert isinstance(result[0], NotificationOut)
        assert result[0].user_id == user_id

    @pytest.mark.asyncio
    async def test_list_by_user_empty(
            self,
            notification_service,
            mock_uow
    ):
        """Пользователь без уведомлений -> пустой список"""
        # Arrange
        user_id = 100
        mock_uow.notification.list_by_user.return_value = []

        # Act
        result = await notification_service.list_by_user(user_id)

        # Assert
        assert result == []


class TestNotificationServiceListUnread:
    """Тесты для метода list_unread"""

    @pytest.mark.asyncio
    async def test_list_unread_success(
            self,
            notification_service,
            mock_uow,
            sample_notification
    ):
        """Успешное получение непрочитанных уведомлений"""
        # Arrange
        user_id = 100
        notifications = [sample_notification]  # is_read=False
        mock_uow.notification.list_unread_by_user.return_value = notifications

        # Act
        result = await notification_service.list_unread(user_id)

        # Assert
        mock_uow.notification.list_unread_by_user.assert_awaited_once_with(user_id)
        assert len(result) == 1
        assert result[0].is_read is False

    @pytest.mark.asyncio
    async def test_list_unread_empty(
            self,
            notification_service,
            mock_uow
    ):
        """Нет непрочитанных уведомлений -> пустой список"""
        # Arrange
        user_id = 100
        mock_uow.notification.list_unread_by_user.return_value = []

        # Act
        result = await notification_service.list_unread(user_id)

        # Assert
        assert result == []


class TestNotificationServiceMarkAsRead:
    """Тесты для метода mark_as_read"""

    @pytest.mark.asyncio
    async def test_mark_as_read_success(
            self,
            notification_service,
            mock_uow,
            sample_notification
    ):
        """Успешная отметка уведомления как прочитанного"""
        # Arrange
        notification_id = 1
        user_id = 100
        sample_notification.user_id = user_id
        mock_uow.notification.get_by_id.return_value = sample_notification

        # Act
        await notification_service.mark_as_read(notification_id, user_id)

        # Assert
        mock_uow.notification.get_by_id.assert_awaited_once_with(notification_id)
        mock_uow.notification.mark_as_read.assert_awaited_once_with(notification_id)
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_mark_as_read_not_found(
            self,
            notification_service,
            mock_uow
    ):
        """Отметка несуществующего уведомления -> ошибка"""
        # Arrange
        notification_id = 999
        user_id = 100
        mock_uow.notification.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotificationNotFound) as exc_info:
            await notification_service.mark_as_read(notification_id, user_id)

        assert exc_info.value.notification_id == notification_id
        mock_uow.notification.mark_as_read.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_mark_as_read_forbidden(
            self,
            notification_service,
            mock_uow,
            sample_notification
    ):
        """Отметка чужого уведомления -> ошибка"""
        # Arrange
        notification_id = 1
        owner_id = 100
        stranger_id = 999
        sample_notification.user_id = owner_id
        mock_uow.notification.get_by_id.return_value = sample_notification

        # Act & Assert
        with pytest.raises(ForbiddenNotificationAccess) as exc_info:
            await notification_service.mark_as_read(notification_id, stranger_id)

        assert exc_info.value.notification_id == notification_id
        assert exc_info.value.user_id == stranger_id
        mock_uow.notification.mark_as_read.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()


class TestNotificationServiceMarkAllAsRead:
    """Тесты для метода mark_all_as_read"""

    @pytest.mark.asyncio
    async def test_mark_all_as_read_success(
            self,
            notification_service,
            mock_uow
    ):
        """Успешная отметка всех уведомлений как прочитанных"""
        # Arrange
        user_id = 100

        # Act
        await notification_service.mark_all_as_read(user_id)

        # Assert
        mock_uow.notification.mark_all_as_read.assert_awaited_once_with(user_id)
        mock_uow.commit.assert_awaited_once()