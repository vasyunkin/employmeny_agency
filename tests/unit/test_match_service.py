import pytest

from src.service.match.match_dto import (
    MatchCreateIn,
    MatchUpdateStatusIn,
    MatchUpdateAcceptanceIn,
    MatchOut,
    MatchDetailOut
)
from src.service.match.m_exceptions import (
    MatchAlreadyExists,
    MatchNotFound,
    ForbiddenMatchAccess
)


class TestMatchServiceCreate:
    """Тесты для метода create"""

    @pytest.mark.asyncio
    async def test_create_success(
        self,
        match_service,
        mock_uow,
        mock_notification_creator,
        sample_match,
        create_match_data
    ):
        """Успешное создание мэтча"""
        # Arrange
        recruiter_id = 300
        mock_uow.match.exists.return_value = False
        mock_uow.match.create.return_value = sample_match
        mock_uow.get_match_detail.return_value = sample_match

        # Act
        result = await match_service.create(recruiter_id, create_match_data)

        # Assert
        mock_uow.match.exists.assert_awaited_once_with(
            create_match_data.vacancy_id,
            create_match_data.resume_id
        )
        mock_uow.match.create.assert_awaited_once()
        mock_uow.get_match_detail.assert_awaited_once_with(sample_match.match_id)
        mock_notification_creator.on_match_created.assert_awaited_once_with(
            mock_uow, sample_match
        )
        mock_uow.commit.assert_awaited_once()

        assert isinstance(result, MatchOut)
        assert result.match_id == sample_match.match_id
        assert result.resume_id == create_match_data.resume_id
        assert result.vacancy_id == create_match_data.vacancy_id
        assert result.recruiter_id == recruiter_id

    @pytest.mark.asyncio
    async def test_create_already_exists(
        self,
        match_service,
        mock_uow,
        mock_notification_creator,
        create_match_data
    ):
        """Создание уже существующего мэтча -> ошибка"""
        # Arrange
        recruiter_id = 300
        mock_uow.match.exists.return_value = True

        # Act & Assert
        with pytest.raises(MatchAlreadyExists) as exc_info:
            await match_service.create(recruiter_id, create_match_data)

        assert exc_info.value.resume_id == create_match_data.resume_id
        assert exc_info.value.vacancy_id == create_match_data.vacancy_id
        mock_uow.match.create.assert_not_awaited()
        mock_notification_creator.on_match_created.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()


class TestMatchServiceGetById:
    """Тесты для метода get_by_id"""

    @pytest.mark.asyncio
    async def test_get_by_id_success(
        self,
        match_service,
        mock_uow,
        sample_match_detail
    ):
        """Успешное получение детального мэтча по ID"""
        # Arrange
        match_id = 1
        recruiter_id = 300
        mock_uow.get_match_detail.return_value = sample_match_detail

        # Act
        result = await match_service.get_by_id(match_id, recruiter_id)

        # Assert
        mock_uow.get_match_detail.assert_awaited_once_with(match_id)
        assert isinstance(result, MatchDetailOut)
        assert result.match_id == match_id
        assert result.recruiter_id == recruiter_id
        assert result.resume is not None
        assert result.vacancy is not None

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(
        self,
        match_service,
        mock_uow
    ):
        """Мэтч не найден -> ошибка MatchNotFound"""
        # Arrange
        match_id = 999
        recruiter_id = 300
        mock_uow.get_match_detail.return_value = None

        # Act & Assert
        with pytest.raises(MatchNotFound) as exc_info:
            await match_service.get_by_id(match_id, recruiter_id)

        assert exc_info.value.match_id == match_id

    @pytest.mark.asyncio
    async def test_get_by_id_forbidden_access(
        self,
        match_service,
        mock_uow,
        sample_match_detail
    ):
        """Попытка получить чужой мэтч -> ForbiddenMatchAccess"""
        # Arrange
        match_id = 1
        owner_id = 300
        stranger_id = 999
        sample_match_detail.recruiter_id = owner_id
        mock_uow.get_match_detail.return_value = sample_match_detail

        # Act & Assert
        with pytest.raises(ForbiddenMatchAccess) as exc_info:
            await match_service.get_by_id(match_id, stranger_id)

        assert exc_info.value.match_id == match_id
        assert exc_info.value.recruiter_id == stranger_id


class TestMatchServiceListByRecruiter:
    """Тесты для метода list_by_recruiter"""

    @pytest.mark.asyncio
    async def test_list_by_recruiter_success(
        self,
        match_service,
        mock_uow,
        sample_match
    ):
        """Успешное получение списка мэтчей рекрутера"""
        # Arrange
        recruiter_id = 300
        matches = [sample_match]
        mock_uow.match.list_by_recruiter.return_value = matches

        # Act
        result = await match_service.list_by_recruiter(recruiter_id)

        # Assert
        mock_uow.match.list_by_recruiter.assert_awaited_once_with(recruiter_id)
        assert len(result) == 1
        assert isinstance(result[0], MatchOut)
        assert result[0].recruiter_id == recruiter_id

    @pytest.mark.asyncio
    async def test_list_by_recruiter_empty(
        self,
        match_service,
        mock_uow
    ):
        """Рекрутер без мэтчей -> пустой список"""
        # Arrange
        recruiter_id = 300
        mock_uow.match.list_by_recruiter.return_value = []

        # Act
        result = await match_service.list_by_recruiter(recruiter_id)

        # Assert
        assert result == []


class TestMatchServiceUpdateStatus:
    """Тесты для метода update_status"""

    @pytest.mark.asyncio
    async def test_update_status_success(
        self,
        match_service,
        mock_uow,
        sample_match,
        update_match_status_data
    ):
        """Успешное обновление статуса мэтча"""
        # Arrange
        match_id = 1
        recruiter_id = 300
        sample_match.recruiter_id = recruiter_id
        mock_uow.match.get_by_id.return_value = sample_match
        mock_uow.match.update.return_value = sample_match

        # Act
        result = await match_service.update_status(
            match_id, recruiter_id, update_match_status_data
        )

        # Assert
        mock_uow.match.get_by_id.assert_awaited_once_with(match_id)
        mock_uow.match.update.assert_awaited_once_with(sample_match)
        mock_uow.commit.assert_awaited_once()

        assert result.is_active == update_match_status_data.is_active

    @pytest.mark.asyncio
    async def test_update_status_not_found(
        self,
        match_service,
        mock_uow,
        update_match_status_data
    ):
        """Обновление статуса несуществующего мэтча -> ошибка"""
        # Arrange
        match_id = 999
        recruiter_id = 300
        mock_uow.match.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(MatchNotFound) as exc_info:
            await match_service.update_status(
                match_id, recruiter_id, update_match_status_data
            )

        assert exc_info.value.match_id == match_id
        mock_uow.match.update.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_status_forbidden(
        self,
        match_service,
        mock_uow,
        sample_match,
        update_match_status_data
    ):
        """Обновление статуса чужого мэтча -> ошибка"""
        # Arrange
        match_id = 1
        owner_id = 300
        wrong_recruiter_id = 999
        sample_match.recruiter_id = owner_id
        mock_uow.match.get_by_id.return_value = sample_match

        # Act & Assert
        with pytest.raises(ForbiddenMatchAccess) as exc_info:
            await match_service.update_status(
                match_id, wrong_recruiter_id, update_match_status_data
            )

        assert exc_info.value.match_id == match_id
        assert exc_info.value.recruiter_id == wrong_recruiter_id
        mock_uow.match.update.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()


class TestMatchServiceUpdateAcceptance:
    """Тесты для метода update_acceptance (бизнес-логика статусов)"""

    @pytest.mark.asyncio
    async def test_update_acceptance_applicant_only_success(
        self,
        match_service,
        mock_uow,
        mock_notification_creator,
        sample_match,
        update_match_acceptance_applicant_data
    ):
        """Успешное обновление принятия только соискателем"""
        # Arrange
        match_id = 1
        recruiter_id = 300
        sample_match.recruiter_id = recruiter_id
        sample_match.applicant_accepted = None
        sample_match.employer_accepted = None
        sample_match.is_active = True

        mock_uow.get_match_detail.return_value = sample_match
        mock_uow.match.update.return_value = sample_match

        # Act
        result = await match_service.update_acceptance(
            match_id, recruiter_id, update_match_acceptance_applicant_data
        )

        # Assert
        mock_uow.get_match_detail.assert_awaited_once_with(match_id)
        assert result.applicant_accepted is True
        assert result.employer_accepted is None
        # Мэтч остается активным, т.к. нет второго подтверждения
        assert result.is_active is True

        mock_uow.match.update.assert_awaited_once()
        mock_notification_creator.on_acceptance_changed.assert_awaited_once_with(
            mock_uow, sample_match
        )
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_acceptance_both_true_deactivates_match(
        self,
        match_service,
        mock_uow,
        mock_notification_creator,
        sample_match,
        update_match_acceptance_both_data
    ):
        """Оба подтвердили мэтч -> мэтч деактивируется"""
        # Arrange
        match_id = 1
        recruiter_id = 300
        sample_match.recruiter_id = recruiter_id
        sample_match.applicant_accepted = True
        sample_match.employer_accepted = True
        sample_match.is_active = True

        mock_uow.get_match_detail.return_value = sample_match
        mock_uow.match.update.return_value = sample_match

        # Act
        result = await match_service.update_acceptance(
            match_id, recruiter_id, update_match_acceptance_both_data
        )

        # Assert
        assert result.is_active is False
        mock_notification_creator.on_acceptance_changed.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_acceptance_applicant_false_deactivates_match(
        self,
        match_service,
        mock_uow,
        mock_notification_creator,
        sample_match
    ):
        """Соискатель отказался -> мэтч деактивируется"""
        # Arrange
        match_id = 1
        recruiter_id = 300
        data = MatchUpdateAcceptanceIn(applicant_accepted=False)

        sample_match.recruiter_id = recruiter_id
        sample_match.applicant_accepted = None
        sample_match.employer_accepted = True
        sample_match.is_active = True

        mock_uow.get_match_detail.return_value = sample_match
        mock_uow.match.update.return_value = sample_match

        # Act
        result = await match_service.update_acceptance(
            match_id, recruiter_id, data
        )

        # Assert
        assert result.applicant_accepted is False
        assert result.is_active is False
        mock_notification_creator.on_acceptance_changed.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_acceptance_employer_false_deactivates_match(
        self,
        match_service,
        mock_uow,
        mock_notification_creator,
        sample_match
    ):
        """Работодатель отказался -> мэтч деактивируется"""
        # Arrange
        match_id = 1
        recruiter_id = 300
        data = MatchUpdateAcceptanceIn(employer_accepted=False)

        sample_match.recruiter_id = recruiter_id
        sample_match.applicant_accepted = True
        sample_match.employer_accepted = None
        sample_match.is_active = True

        mock_uow.get_match_detail.return_value = sample_match
        mock_uow.match.update.return_value = sample_match

        # Act
        result = await match_service.update_acceptance(
            match_id, recruiter_id, data
        )

        # Assert
        assert result.employer_accepted is False
        assert result.is_active is False

    @pytest.mark.asyncio
    async def test_update_acceptance_not_found(
        self,
        match_service,
        mock_uow,
        update_match_acceptance_applicant_data
    ):
        """Обновление принятия несуществующего мэтча -> ошибка"""
        # Arrange
        match_id = 999
        recruiter_id = 300
        mock_uow.get_match_detail.return_value = None

        # Act & Assert
        with pytest.raises(MatchNotFound) as exc_info:
            await match_service.update_acceptance(
                match_id, recruiter_id, update_match_acceptance_applicant_data
            )

        assert exc_info.value.match_id == match_id
        mock_uow.match.update.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_acceptance_forbidden(
        self,
        match_service,
        mock_uow,
        sample_match,
        update_match_acceptance_applicant_data
    ):
        """Обновление принятия чужого мэтча -> ошибка"""
        # Arrange
        match_id = 1
        owner_id = 300
        wrong_recruiter_id = 999
        sample_match.recruiter_id = owner_id
        mock_uow.get_match_detail.return_value = sample_match

        # Act & Assert
        with pytest.raises(ForbiddenMatchAccess) as exc_info:
            await match_service.update_acceptance(
                match_id, wrong_recruiter_id, update_match_acceptance_applicant_data
            )

        assert exc_info.value.match_id == match_id
        assert exc_info.value.recruiter_id == wrong_recruiter_id
        mock_uow.match.update.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()


class TestMatchServiceDelete:
    """Тесты для метода delete"""

    @pytest.mark.asyncio
    async def test_delete_success(
        self,
        match_service,
        mock_uow,
        sample_match
    ):
        """Успешное удаление мэтча"""
        # Arrange
        match_id = 1
        recruiter_id = 300
        sample_match.recruiter_id = recruiter_id
        mock_uow.match.get_by_id.return_value = sample_match

        # Act
        await match_service.delete(match_id, recruiter_id)

        # Assert
        mock_uow.match.get_by_id.assert_awaited_once_with(match_id)
        mock_uow.match.delete.assert_awaited_once_with(match_id)
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(
        self,
        match_service,
        mock_uow
    ):
        """Удаление несуществующего мэтча -> ошибка"""
        # Arrange
        match_id = 999
        recruiter_id = 300
        mock_uow.match.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(MatchNotFound) as exc_info:
            await match_service.delete(match_id, recruiter_id)

        assert exc_info.value.match_id == match_id
        mock_uow.match.delete.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_delete_forbidden(
        self,
        match_service,
        mock_uow,
        sample_match
    ):
        """Удаление чужого мэтча -> ошибка"""
        # Arrange
        match_id = 1
        owner_id = 300
        wrong_recruiter_id = 999
        sample_match.recruiter_id = owner_id
        mock_uow.match.get_by_id.return_value = sample_match

        # Act & Assert
        with pytest.raises(ForbiddenMatchAccess) as exc_info:
            await match_service.delete(match_id, wrong_recruiter_id)

        assert exc_info.value.match_id == match_id
        assert exc_info.value.recruiter_id == wrong_recruiter_id
        mock_uow.match.delete.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()