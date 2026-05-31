import pytest
from src.service.vacancy.v_exceptions import (
    VacancyNotFound,
    ForbiddenVacancyAccess
)
from src.service.vacancy.vacancy_dto import VacancyOut


class TestVacancyServiceCreate:

    @pytest.mark.asyncio
    async def test_create_success(self, vacancy_service, mock_uow, sample_vacancy, create_vacancy_data):
        mock_uow.vacancy.create.return_value = sample_vacancy

        result = await vacancy_service.create(employer_id=200, data=create_vacancy_data)

        assert isinstance(result, VacancyOut)
        assert result.title == create_vacancy_data.title
        mock_uow.vacancy.create.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()


class TestVacancyServiceGetById:

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, vacancy_service, mock_uow, sample_vacancy):
        sample_vacancy.employer_id = 200
        mock_uow.vacancy.get_by_id.return_value = sample_vacancy

        result = await vacancy_service.get_by_id(vacancy_id=1, employer_id=200)

        assert result.vacancy_id == 1
        mock_uow.vacancy.get_by_id.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, vacancy_service, mock_uow):
        mock_uow.vacancy.get_by_id.return_value = None

        with pytest.raises(VacancyNotFound) as exc_info:
            await vacancy_service.get_by_id(999, 200)

        assert exc_info.value.vacancy_id == 999

    @pytest.mark.asyncio
    async def test_get_by_id_forbidden(self, vacancy_service, mock_uow, sample_vacancy):
        sample_vacancy.employer_id = 200
        mock_uow.vacancy.get_by_id.return_value = sample_vacancy

        with pytest.raises(ForbiddenVacancyAccess) as exc_info:
            await vacancy_service.get_by_id(1, 999)

        assert exc_info.value.vacancy_id == 1
        assert exc_info.value.user_id == 999


class TestVacancyServiceListByEmployer:

    @pytest.mark.asyncio
    async def test_list_by_employer_success(self, vacancy_service, mock_uow, sample_vacancy):
        mock_uow.vacancy.list_by_employer.return_value = [sample_vacancy]

        result = await vacancy_service.list_by_employer(200)

        assert len(result) == 1
        assert isinstance(result[0], VacancyOut)


class TestVacancyServiceDeactivate:

    @pytest.mark.asyncio
    async def test_deactivate_success(self, vacancy_service, mock_uow, sample_vacancy):
        sample_vacancy.employer_id = 200
        mock_uow.vacancy.get_by_id.return_value = sample_vacancy

        await vacancy_service.deactivate(vacancy_id=1, employer_id=200)

        mock_uow.vacancy.get_by_id.assert_awaited_once_with(1)
        mock_uow.vacancy.deactivate.assert_awaited_once_with(1)
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_deactivate_not_found(self, vacancy_service, mock_uow):
        mock_uow.vacancy.get_by_id.return_value = None

        with pytest.raises(VacancyNotFound):
            await vacancy_service.deactivate(999, 200)