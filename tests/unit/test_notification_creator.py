import pytest

from src.domain.notification import Notification


class TestNotificationCreatorOnMatchCreated:
    """Тесты для метода on_match_created"""

    @pytest.mark.asyncio
    async def test_on_match_created_success(
            self,
            notification_creator,
            mock_uow,
            sample_match_for_notification
    ):
        """Успешное создание уведомлений при создании мэтча"""
        # Arrange
        match = sample_match_for_notification
        resume = match.resume
        vacancy = match.vacancy
        applicant_id = resume.applicant_id
        employer_id = vacancy.employer_id

        # Act
        await notification_creator.on_match_created(mock_uow, match)

        # Assert
        # Проверяем, что уведомление создано для соискателя
        assert mock_uow.notification.create.call_count == 2

        # Проверяем первое уведомление (соискатель)
        call1_args = mock_uow.notification.create.call_args_list[0][0][0]
        assert isinstance(call1_args, Notification)
        assert call1_args.user_id == applicant_id
        assert call1_args.notification_type == "match_created"
        assert vacancy.title in call1_args.message

        # Проверяем второе уведомление (работодатель)
        call2_args = mock_uow.notification.create.call_args_list[1][0][0]
        assert isinstance(call2_args, Notification)
        assert call2_args.user_id == employer_id
        assert call2_args.notification_type == "match_created"
        assert vacancy.title in call2_args.message

    @pytest.mark.asyncio
    async def test_on_match_created_with_missing_resume(
            self,
            notification_creator,
            mock_uow,
            sample_match
    ):
        """Мэтч без resume -> AttributeError (ожидаем failure в тесте)"""
        # Arrange
        match = sample_match
        match.resume = None
        match.vacancy = None

        # Act & Assert
        with pytest.raises(AttributeError):
            await notification_creator.on_match_created(mock_uow, match)

        mock_uow.notification.create.assert_not_called()


class TestNotificationCreatorOnAcceptanceChanged:
    """Тесты для метода on_acceptance_changed"""

    @pytest.mark.asyncio
    async def test_on_acceptance_changed_fail_applicant_rejected(
            self,
            notification_creator,
            mock_uow,
            sample_match_for_notification
    ):
        """Соискатель отказался -> уведомления о провале всем троим"""
        # Arrange
        match = sample_match_for_notification
        match.applicant_accepted = False
        match.employer_accepted = None

        resume = match.resume
        vacancy = match.vacancy
        applicant_id = resume.applicant_id
        employer_id = vacancy.employer_id
        recruiter_id = match.recruiter_id

        # Act
        await notification_creator.on_acceptance_changed(mock_uow, match)

        # Assert
        assert mock_uow.notification.create.call_count == 3

        # Проверяем всех трех получателей
        user_ids = []
        messages = []
        for call in mock_uow.notification.create.call_args_list:
            notification = call[0][0]
            user_ids.append(notification.user_id)
            messages.append(notification.message)
            assert notification.notification_type == "match_failed"

        assert set(user_ids) == {applicant_id, employer_id, recruiter_id}
        assert all(msg == "Сделка не состоялась" for msg in messages)

    @pytest.mark.asyncio
    async def test_on_acceptance_changed_fail_employer_rejected(
            self,
            notification_creator,
            mock_uow,
            sample_match_for_notification
    ):
        """Работодатель отказался -> уведомления о провале всем троим"""
        # Arrange
        match = sample_match_for_notification
        match.applicant_accepted = True
        match.employer_accepted = False

        resume = match.resume
        vacancy = match.vacancy
        applicant_id = resume.applicant_id
        employer_id = vacancy.employer_id
        recruiter_id = match.recruiter_id

        # Act
        await notification_creator.on_acceptance_changed(mock_uow, match)

        # Assert
        assert mock_uow.notification.create.call_count == 3

        user_ids = [call[0][0].user_id for call in mock_uow.notification.create.call_args_list]
        assert set(user_ids) == {applicant_id, employer_id, recruiter_id}

        # Проверяем тип уведомления
        for call in mock_uow.notification.create.call_args_list:
            assert call[0][0].notification_type == "match_failed"

    @pytest.mark.asyncio
    async def test_on_acceptance_changed_success_both_accepted(
            self,
            notification_creator,
            mock_uow,
            sample_match_for_notification
    ):
        """Обе стороны приняли -> уведомления об успехе всем троим"""
        # Arrange
        match = sample_match_for_notification
        match.applicant_accepted = True
        match.employer_accepted = True

        resume = match.resume
        vacancy = match.vacancy
        applicant_id = resume.applicant_id
        employer_id = vacancy.employer_id
        recruiter_id = match.recruiter_id

        # Act
        await notification_creator.on_acceptance_changed(mock_uow, match)

        # Assert
        assert mock_uow.notification.create.call_count == 3

        user_ids = []
        for call in mock_uow.notification.create.call_args_list:
            notification = call[0][0]
            user_ids.append(notification.user_id)
            assert notification.notification_type == "match_success"
            assert "Обе стороны согласились" in notification.message

        assert set(user_ids) == {applicant_id, employer_id, recruiter_id}

    @pytest.mark.asyncio
    async def test_on_acceptance_changed_partial_applicant_accepted(
            self,
            notification_creator,
            mock_uow,
            sample_match_for_notification
    ):
        """Только соискатель принял -> уведомления о частичном принятии всем троим"""
        # Arrange
        match = sample_match_for_notification
        match.applicant_accepted = True
        match.employer_accepted = None

        resume = match.resume
        vacancy = match.vacancy
        applicant_id = resume.applicant_id
        employer_id = vacancy.employer_id
        recruiter_id = match.recruiter_id

        # Act
        await notification_creator.on_acceptance_changed(mock_uow, match)

        # Assert
        assert mock_uow.notification.create.call_count == 3

        user_ids = []
        for call in mock_uow.notification.create.call_args_list:
            notification = call[0][0]
            user_ids.append(notification.user_id)
            assert notification.notification_type == "match_partial"
            assert "Одна из сторон приняла предложение" in notification.message

        assert set(user_ids) == {applicant_id, employer_id, recruiter_id}

    @pytest.mark.asyncio
    async def test_on_acceptance_changed_partial_employer_accepted(
            self,
            notification_creator,
            mock_uow,
            sample_match_for_notification
    ):
        """Только работодатель принял -> уведомления о частичном принятии всем троим"""
        # Arrange
        match = sample_match_for_notification
        match.applicant_accepted = None
        match.employer_accepted = True

        resume = match.resume
        vacancy = match.vacancy
        applicant_id = resume.applicant_id
        employer_id = vacancy.employer_id
        recruiter_id = match.recruiter_id

        # Act
        await notification_creator.on_acceptance_changed(mock_uow, match)

        # Assert
        assert mock_uow.notification.create.call_count == 3

        for call in mock_uow.notification.create.call_args_list:
            notification = call[0][0]
            assert notification.notification_type == "match_partial"

    @pytest.mark.asyncio
    async def test_on_acceptance_changed_no_change(
            self,
            notification_creator,
            mock_uow,
            sample_match_for_notification
    ):
        """Нет изменений (оба None) -> никаких уведомлений"""
        # Arrange
        match = sample_match_for_notification
        match.applicant_accepted = None
        match.employer_accepted = None

        # Act
        await notification_creator.on_acceptance_changed(mock_uow, match)

        # Assert
        mock_uow.notification.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_acceptance_changed_with_missing_resume(
            self,
            notification_creator,
            mock_uow,
            sample_match
    ):
        """Мэтч без resume и vacancy -> AttributeError"""
        # Arrange
        match = sample_match
        match.applicant_accepted = True
        match.employer_accepted = True
        match.resume = None
        match.vacancy = None

        # Act & Assert
        with pytest.raises(AttributeError):
            await notification_creator.on_acceptance_changed(mock_uow, match)

        mock_uow.notification.create.assert_not_called()