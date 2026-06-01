"""
Тесты для SqlResumeRepository.

Покрывает методы: create, get_by_id, list_by_applicant, deactivate,
exists_similar, search.
"""

import pytest

from src.domain.resume import Resume
from src.domain.user import User, UserRole


class TestResumeRepositoryCreate:
    """Тесты метода create."""

    @pytest.mark.asyncio
    async def test_create_resume_success(self, facade, test_user):
        """Успешное создание резюме."""
        repo = facade.uow.resume

        resume = Resume(
            applicant_id=test_user.user_id,          # ← используем реального пользователя
            desired_position="Python Developer",
            desired_salary=150000,
            experience_years=3,
            skills="Python, Django, SQLAlchemy",
            education="Высшее техническое",
            is_active=True,
        )

        created_resume = await repo.create(resume)

        assert created_resume.resume_id is not None
        assert created_resume.applicant_id == test_user.user_id
        assert created_resume.desired_position == "Python Developer"
        assert created_resume.experience_years == 3
        assert created_resume.is_active is True


    @pytest.mark.asyncio
    async def test_create_inactive_resume(self, facade, test_user):
        """Создание неактивного резюме."""
        repo = facade.uow.resume

        resume = Resume(
            applicant_id=test_user.user_id,
            desired_position="Frontend Developer",
            experience_years=2,
            skills="React, TypeScript",
            is_active=False,
        )

        created = await repo.create(resume)
        assert created.is_active is False


class TestResumeRepositoryGetById:
    """Тесты метода get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, facade, test_user):
        """Успешное получение резюме по ID."""
        repo = facade.uow.resume

        resume = Resume(
            applicant_id=test_user.user_id,
            desired_position="Backend Developer",
            experience_years=5,
            skills="Python, FastAPI",
        )

        created = await repo.create(resume)
        found = await repo.get_by_id(created.resume_id)

        assert found is not None
        assert found.resume_id == created.resume_id
        assert found.applicant_id == test_user.user_id


    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, facade):
        """Резюме не найдено по несуществующему ID."""
        repo = facade.uow.resume
        result = await repo.get_by_id(999999)
        assert result is None


class TestResumeRepositoryListByApplicant:
    """Тесты метода list_by_applicant."""

    @pytest.mark.asyncio
    async def test_list_by_applicant_success(self, facade, test_user):
        """Получение списка резюме конкретного соискателя."""
        repo = facade.uow.resume

        await repo.create(Resume(
            applicant_id=test_user.user_id,
            desired_position="Python Dev",
            experience_years=1
        ))
        await repo.create(Resume(
            applicant_id=test_user.user_id,
            desired_position="Senior Python Dev",
            experience_years=4
        ))

        resumes = await repo.list_by_applicant(test_user.user_id)

        assert len(resumes) == 2
        for r in resumes:
            assert r.applicant_id == test_user.user_id


class TestResumeRepositoryDeactivate:
    """Тесты метода deactivate."""

    @pytest.mark.asyncio
    async def test_deactivate_success(self, facade, test_user):
        """Успешная деактивация резюме."""
        repo = facade.uow.resume

        resume = Resume(
            applicant_id=test_user.user_id,
            desired_position="Manager",
            experience_years=4,
            is_active=True,
        )
        created = await repo.create(resume)

        await repo.deactivate(created.resume_id)

        updated = await repo.get_by_id(created.resume_id)
        assert updated is not None
        assert updated.is_active is False


class TestResumeRepositoryExistsSimilar:
    """Тесты метода exists_similar."""

    @pytest.mark.asyncio
    async def test_exists_similar_true(self, facade, test_user):
        """Существует похожее активное резюме."""
        repo = facade.uow.resume

        await repo.create(Resume(
            applicant_id=test_user.user_id,
            desired_position="Data Scientist",
            experience_years=3,
            is_active=True
        ))

        exists = await repo.exists_similar(test_user.user_id, "Data Scientist")
        assert exists is True


    @pytest.mark.asyncio
    async def test_exists_similar_false(self, facade, test_user):
        """Похожего активного резюме нет."""
        repo = facade.uow.resume

        await repo.create(Resume(
            applicant_id=test_user.user_id,
            desired_position="Data Scientist",
            is_active=False
        ))

        exists = await repo.exists_similar(test_user.user_id, "Data Scientist")
        assert exists is False


class TestResumeRepositorySearch:
    """Тесты метода search."""

    @pytest.mark.asyncio
    async def test_search_by_position(self, facade, test_user):
        """Поиск по названию должности."""
        repo = facade.uow.resume

        await repo.create(Resume(applicant_id=test_user.user_id, desired_position="Python Developer", experience_years=3))
        await repo.create(Resume(applicant_id=test_user.user_id, desired_position="Java Developer", experience_years=4))
        await repo.create(Resume(applicant_id=test_user.user_id, desired_position="Python Senior", experience_years=5))

        results = await repo.search(desired_position="Python")
        assert len(results) >= 2


    @pytest.mark.asyncio
    async def test_search_by_min_experience(self, facade, test_user):
        """Поиск с минимальным опытом."""
        repo = facade.uow.resume

        await repo.create(Resume(applicant_id=test_user.user_id, desired_position="Junior", experience_years=1))
        await repo.create(Resume(applicant_id=test_user.user_id, desired_position="Middle", experience_years=4))
        await repo.create(Resume(applicant_id=test_user.user_id, desired_position="Senior", experience_years=6))

        results = await repo.search(min_experience=4)
        assert len(results) >= 2
        for r in results:
            assert r.experience_years >= 4


    @pytest.mark.asyncio
    async def test_search_with_pagination(self, facade, test_user):
        """Поиск с limit и offset."""
        repo = facade.uow.resume

        for i in range(5):
            await repo.create(Resume(
                applicant_id=test_user.user_id,
                desired_position=f"Position {i}",
                experience_years=i
            ))

        results = await repo.search(limit=2, offset=2)
        assert len(results) == 2