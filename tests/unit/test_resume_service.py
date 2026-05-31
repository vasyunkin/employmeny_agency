import pytest

from src.service.resume.resume_dto import ResumeCreateIn, ResumeUpdateIn, ResumeOut
from src.service.resume.r_exceptions import (
    ResumeAlreadyExists,
    ResumeNotFound,
    ForbiddenResumeAccess
)


class TestResumeServiceCreate:
    """Тесты для метода create"""

    @pytest.mark.asyncio
    async def test_create_success(
            self,
            resume_service,
            mock_uow,
            sample_resume,
            create_resume_data
    ):
        """Успешное создание резюме"""
        # Arrange
        applicant_id = 100
        mock_uow.resume.exists_similar.return_value = False
        mock_uow.resume.create.return_value = sample_resume

        # Act
        result = await resume_service.create(applicant_id, create_resume_data)

        # Assert
        mock_uow.resume.exists_similar.assert_awaited_once_with(
            applicant_id, create_resume_data.desired_position
        )
        mock_uow.resume.create.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

        assert isinstance(result, ResumeOut)
        assert result.resume_id == sample_resume.resume_id
        assert result.applicant_id == applicant_id
        assert result.desired_position == create_resume_data.desired_position

    @pytest.mark.asyncio
    async def test_create_already_exists(
            self,
            resume_service,
            mock_uow,
            create_resume_data
    ):
        """Создание резюме с уже существующей должностью -> ошибка"""
        # Arrange
        applicant_id = 100
        mock_uow.resume.exists_similar.return_value = True

        # Act & Assert
        with pytest.raises(ResumeAlreadyExists) as exc_info:
            await resume_service.create(applicant_id, create_resume_data)

        assert create_resume_data.desired_position in str(exc_info.value)
        mock_uow.resume.create.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()


class TestResumeServiceGetById:
    """Тесты для метода get_by_id"""

    @pytest.mark.asyncio
    async def test_get_by_id_success(
            self,
            resume_service,
            mock_uow,
            sample_resume
    ):
        """Успешное получение резюме по ID (владелец совпадает)"""
        # Arrange
        resume_id = 1
        applicant_id = 100
        sample_resume.applicant_id = applicant_id
        mock_uow.resume.get_by_id.return_value = sample_resume

        # Act
        result = await resume_service.get_by_id(resume_id, applicant_id)

        # Assert
        mock_uow.resume.get_by_id.assert_awaited_once_with(resume_id)
        assert result.resume_id == resume_id
        assert result.applicant_id == applicant_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(
            self,
            resume_service,
            mock_uow
    ):
        """Резюме не найдено -> ошибка ResumeNotFound"""
        # Arrange
        resume_id = 999
        applicant_id = 100
        mock_uow.resume.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ResumeNotFound) as exc_info:
            await resume_service.get_by_id(resume_id, applicant_id)

        assert exc_info.value.resume_id == resume_id

    @pytest.mark.asyncio
    async def test_get_by_id_forbidden_access(
            self, resume_service, mock_uow, sample_resume
    ):
        """Попытка получить чужое резюме → ForbiddenResumeAccess"""
        resume_id = 5
        owner_id = 100
        stranger_id = 999

        sample_resume.applicant_id = owner_id  # лучше создавать новый объект
        mock_uow.resume.get_by_id.return_value = sample_resume

        with pytest.raises(ForbiddenResumeAccess) as exc_info:
            await resume_service.get_by_id(resume_id, stranger_id)

        assert exc_info.value.resume_id == resume_id
        assert exc_info.value.user_id == stranger_id


class TestResumeServiceListByApplicant:
    """Тесты для метода list_by_applicant"""

    @pytest.mark.asyncio
    async def test_list_by_applicant_success(
            self,
            resume_service,
            mock_uow,
            sample_resume
    ):
        """Успешное получение списка резюме соискателя"""
        # Arrange
        applicant_id = 100
        resumes = [sample_resume]
        mock_uow.resume.list_by_applicant.return_value = resumes

        # Act
        result = await resume_service.list_by_applicant(applicant_id)

        # Assert
        mock_uow.resume.list_by_applicant.assert_awaited_once_with(applicant_id)
        assert len(result) == 1
        assert isinstance(result[0], ResumeOut)

    @pytest.mark.asyncio
    async def test_list_by_applicant_empty(
            self,
            resume_service,
            mock_uow
    ):
        """Соискатель без резюме -> пустой список"""
        # Arrange
        applicant_id = 100
        mock_uow.resume.list_by_applicant.return_value = []

        # Act
        result = await resume_service.list_by_applicant(applicant_id)

        # Assert
        assert result == []


class TestResumeServiceDeactivate:
    """Тесты для метода deactivate"""

    @pytest.mark.asyncio
    async def test_deactivate_success(
            self,
            resume_service,
            mock_uow,
            sample_resume
    ):
        """Успешная деактивация резюме"""
        # Arrange
        resume_id = 1
        applicant_id = 100
        sample_resume.applicant_id = applicant_id
        mock_uow.resume.get_by_id.return_value = sample_resume

        # Act
        await resume_service.deactivate(resume_id, applicant_id)

        # Assert
        mock_uow.resume.get_by_id.assert_awaited_once_with(resume_id)
        mock_uow.resume.deactivate.assert_awaited_once_with(resume_id)
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_deactivate_not_found(
            self,
            resume_service,
            mock_uow
    ):
        """Деактивация несуществующего резюме -> ошибка"""
        # Arrange
        resume_id = 999
        applicant_id = 100
        mock_uow.resume.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ResumeNotFound) as exc_info:
            await resume_service.deactivate(resume_id, applicant_id)

        assert exc_info.value.resume_id == resume_id
        mock_uow.resume.deactivate.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()


class TestResumeServiceUpdate:
    """Тесты для метода update"""

    @pytest.mark.asyncio
    async def test_update_success(
            self,
            resume_service,
            mock_uow,
            sample_resume,
            update_resume_data
    ):
        """Успешное обновление резюме"""
        # Arrange
        resume_id = 1
        applicant_id = 100
        sample_resume.applicant_id = applicant_id
        mock_uow.resume.get_by_id.return_value = sample_resume

        # Act
        result = await resume_service.update(
            resume_id, applicant_id, update_resume_data
        )

        # Assert
        mock_uow.resume.get_by_id.assert_awaited_once_with(resume_id)
        mock_uow.commit.assert_awaited_once()
        mock_uow.session.refresh.assert_awaited_once_with(sample_resume)

        assert result.desired_salary == update_resume_data.desired_salary
        assert result.experience_years == update_resume_data.experience_years

    @pytest.mark.asyncio
    async def test_update_forbidden(
            self,
            resume_service,
            mock_uow,
            sample_resume,
            update_resume_data
    ):
        """Обновление чужого резюме -> ошибка"""
        # Arrange
        resume_id = 1
        owner_id = 100
        wrong_applicant_id = 999
        sample_resume.applicant_id = owner_id
        mock_uow.resume.get_by_id.return_value = sample_resume

        # Act & Assert
        with pytest.raises(ForbiddenResumeAccess) as exc_info:
            await resume_service.update(
                resume_id, wrong_applicant_id, update_resume_data
            )

        assert exc_info.value.resume_id == resume_id
        assert exc_info.value.user_id == wrong_applicant_id
        mock_uow.commit.assert_not_awaited()