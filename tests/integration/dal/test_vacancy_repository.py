"""
Тесты для SqlVacancyRepository.

Покрывает методы: create, get_by_id, list_by_employer, deactivate, search.
"""

import pytest

from src.domain.vacancy import Vacancy
from src.domain.user import User, UserRole


class TestVacancyRepositoryCreate:
    """Тесты метода create."""

    @pytest.mark.asyncio
    async def test_create_vacancy_success(self, facade):
        """Успешное создание вакансии."""
        repo = facade.uow.vacancy

        # Создаём работодателя
        employer = User(
            user_login="employer.test",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        )
        created_employer = await facade.uow.user.create(employer)

        vacancy = Vacancy(
            employer_id=created_employer.user_id,
            title="Senior Python Developer",
            salary=250000,
            requirements="Python, Django, 3+ years experience",
            responsibilities="Backend development, code review",
            is_active=True,
        )

        created_vacancy = await repo.create(vacancy)

        assert created_vacancy.vacancy_id is not None
        assert created_vacancy.employer_id == created_employer.user_id
        assert created_vacancy.title == "Senior Python Developer"
        assert created_vacancy.salary == 250000
        assert created_vacancy.is_active is True
        assert isinstance(created_vacancy, Vacancy)

    @pytest.mark.asyncio
    async def test_create_inactive_vacancy(self, facade):
        """Создание неактивной вакансии."""
        repo = facade.uow.vacancy

        employer = User(
            user_login="employer2.test",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        )
        created_employer = await facade.uow.user.create(employer)

        vacancy = Vacancy(
            employer_id=created_employer.user_id,
            title="Junior Developer",
            salary=120000,
            is_active=False,
        )

        created = await repo.create(vacancy)
        assert created.is_active is False


class TestVacancyRepositoryGetById:
    """Тесты метода get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, facade):
        """Успешное получение вакансии по ID."""
        repo = facade.uow.vacancy

        employer = User(
            user_login="employer3.test",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        )
        created_employer = await facade.uow.user.create(employer)

        vacancy = Vacancy(
            employer_id=created_employer.user_id,
            title="Backend Developer",
            salary=200000,
            requirements="FastAPI, PostgreSQL",
        )

        created = await repo.create(vacancy)
        found = await repo.get_by_id(created.vacancy_id)

        assert found is not None
        assert found.vacancy_id == created.vacancy_id
        assert found.title == "Backend Developer"
        assert found.employer_id == created_employer.user_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, facade):
        """Вакансия не найдена по несуществующему ID."""
        repo = facade.uow.vacancy
        result = await repo.get_by_id(999999)
        assert result is None


class TestVacancyRepositoryListByEmployer:
    """Тесты метода list_by_employer."""

    @pytest.mark.asyncio
    async def test_list_by_employer_success(self, facade):
        """Получение списка вакансий конкретного работодателя."""
        repo = facade.uow.vacancy

        employer = User(
            user_login="employer4.test",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        )
        created_employer = await facade.uow.user.create(employer)

        await repo.create(Vacancy(
            employer_id=created_employer.user_id,
            title="Python Developer",
            salary=180000
        ))
        await repo.create(Vacancy(
            employer_id=created_employer.user_id,
            title="Team Lead",
            salary=300000
        ))

        vacancies = await repo.list_by_employer(created_employer.user_id)

        assert len(vacancies) == 2
        for v in vacancies:
            assert v.employer_id == created_employer.user_id

    @pytest.mark.asyncio
    async def test_list_by_employer_empty(self, facade):
        """Работодатель без вакансий."""
        repo = facade.uow.vacancy

        employer = User(
            user_login="employer5.test",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        )
        created_employer = await facade.uow.user.create(employer)

        vacancies = await repo.list_by_employer(created_employer.user_id)
        assert len(vacancies) == 0


class TestVacancyRepositoryDeactivate:
    """Тесты метода deactivate."""

    @pytest.mark.asyncio
    async def test_deactivate_success(self, facade):
        """Успешная деактивация вакансии."""
        repo = facade.uow.vacancy

        employer = User(
            user_login="employer6.test",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        )
        created_employer = await facade.uow.user.create(employer)

        vacancy = Vacancy(
            employer_id=created_employer.user_id,
            title="Manager Position",
            salary=150000,
            is_active=True,
        )
        created = await repo.create(vacancy)

        await repo.deactivate(created.vacancy_id)

        updated = await repo.get_by_id(created.vacancy_id)
        assert updated is not None
        assert updated.is_active is False


class TestVacancyRepositorySearch:
    """Тесты метода search."""

    @pytest.mark.asyncio
    async def test_search_by_title(self, facade):
        """Поиск по названию вакансии."""
        repo = facade.uow.vacancy

        employer = User(
            user_login="employer7.test",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        )
        created_employer = await facade.uow.user.create(employer)

        await repo.create(Vacancy(employer_id=created_employer.user_id, title="Python Developer", salary=200000))
        await repo.create(Vacancy(employer_id=created_employer.user_id, title="Java Developer", salary=180000))
        await repo.create(Vacancy(employer_id=created_employer.user_id, title="Senior Python Engineer", salary=280000))

        results = await repo.search(title="Python")
        assert len(results) >= 2
        for v in results:
            assert "Python" in v.title

    @pytest.mark.asyncio
    async def test_search_by_min_salary(self, facade):
        """Поиск по минимальной зарплате."""
        repo = facade.uow.vacancy

        employer = User(
            user_login="employer8.test",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        )
        created_employer = await facade.uow.user.create(employer)

        await repo.create(Vacancy(employer_id=created_employer.user_id, title="Junior", salary=80000))
        await repo.create(Vacancy(employer_id=created_employer.user_id, title="Middle", salary=150000))
        await repo.create(Vacancy(employer_id=created_employer.user_id, title="Senior", salary=250000))

        results = await repo.search(min_salary=150000)
        assert len(results) >= 2
        for v in results:
            assert v.salary >= 150000

    @pytest.mark.asyncio
    async def test_search_only_active(self, facade):
        """Поиск только активных вакансий."""
        repo = facade.uow.vacancy

        employer = User(
            user_login="employer9.test",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        )
        created_employer = await facade.uow.user.create(employer)

        await repo.create(Vacancy(employer_id=created_employer.user_id, title="Active Vacancy", is_active=True))
        await repo.create(Vacancy(employer_id=created_employer.user_id, title="Inactive Vacancy", is_active=False))

        results = await repo.search(is_active=True)
        assert len(results) >= 1
        for v in results:
            assert v.is_active is True