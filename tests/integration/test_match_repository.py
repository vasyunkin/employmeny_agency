"""
Тесты для SqlMatchRepository.
"""

import pytest

from src.domain.match import Match, MatchStatus
from src.domain.user import UserRole


class TestMatchRepositoryCreate:
    """Тесты метода create."""

    @pytest.mark.asyncio
    async def test_create_match_success(self, facade, test_resume, test_vacancy, test_recruiter):
        """Успешное создание матча."""
        repo = facade.uow.match

        match = Match(
            resume_id=test_resume.resume_id,
            vacancy_id=test_vacancy.vacancy_id,
            recruiter_id=test_recruiter.user_id,
        )

        created_match = await repo.create(match)

        assert created_match.match_id is not None
        assert created_match.resume_id == test_resume.resume_id
        assert created_match.vacancy_id == test_vacancy.vacancy_id
        assert created_match.recruiter_id == test_recruiter.user_id
        assert created_match.match_status == MatchStatus.CREATED


class TestMatchRepositoryGetById:
    """Тесты метода get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, facade, test_resume, test_vacancy, test_recruiter):
        """Получение матча по ID."""
        repo = facade.uow.match

        match = Match(
            resume_id=test_resume.resume_id,
            vacancy_id=test_vacancy.vacancy_id,
            recruiter_id=test_recruiter.user_id,
        )
        created = await repo.create(match)

        found = await repo.get_by_id(created.match_id)

        assert found is not None
        assert found.match_id == created.match_id
        assert found.resume_id == test_resume.resume_id


    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, facade):
        """Матч не найден."""
        repo = facade.uow.match
        result = await repo.get_by_id(999999)
        assert result is None


class TestMatchRepositoryExists:
    """Тесты метода exists."""

    @pytest.mark.asyncio
    async def test_exists_true(self, facade, test_resume, test_vacancy, test_recruiter):
        """Матч уже существует."""
        repo = facade.uow.match

        match = Match(
            resume_id=test_resume.resume_id,
            vacancy_id=test_vacancy.vacancy_id,
            recruiter_id=test_recruiter.user_id,
        )
        await repo.create(match)

        exists = await repo.exists(test_vacancy.vacancy_id, test_resume.resume_id)
        assert exists is True

    @pytest.mark.asyncio
    async def test_exists_false(self, facade):
        """Матч не существует."""
        repo = facade.uow.match
        exists = await repo.exists(999, 999)
        assert exists is False


class TestMatchRepositoryGetByResumeAndVacancy:
    """Тесты метода get_by_resume_and_vacancy."""

    @pytest.mark.asyncio
    async def test_get_by_resume_and_vacancy_success(self, facade, test_resume, test_vacancy, test_recruiter):
        """Поиск матча по resume + vacancy."""
        repo = facade.uow.match

        match = Match(
            resume_id=test_resume.resume_id,
            vacancy_id=test_vacancy.vacancy_id,
            recruiter_id=test_recruiter.user_id,
        )
        await repo.create(match)

        found = await repo.get_by_resume_and_vacancy(test_resume.resume_id, test_vacancy.vacancy_id)

        assert found is not None
        assert found.resume_id == test_resume.resume_id
        assert found.vacancy_id == test_vacancy.vacancy_id


class TestMatchRepositoryListMethods:
    """Тесты методов list_*."""

    @pytest.mark.asyncio
    async def test_list_by_recruiter(self, facade, test_resume, test_vacancy, test_recruiter):
        """Список матчей рекрутера."""
        repo = facade.uow.match

        await repo.create(Match(resume_id=test_resume.resume_id, vacancy_id=test_vacancy.vacancy_id, recruiter_id=test_recruiter.user_id))

        matches = await repo.list_by_recruiter(test_recruiter.user_id)
        assert len(matches) == 1

    @pytest.mark.asyncio
    async def test_list_by_resume(self, facade, test_resume, test_vacancy, test_recruiter):
        """Список матчей по резюме."""
        repo = facade.uow.match

        await repo.create(Match(resume_id=test_resume.resume_id, vacancy_id=test_vacancy.vacancy_id, recruiter_id=test_recruiter.user_id))

        matches = await repo.list_by_resume(test_resume.resume_id)
        assert len(matches) == 1


class TestMatchRepositoryUpdateAndDelete:
    """Тесты update и delete."""

    @pytest.mark.asyncio
    async def test_update_status(self, facade, test_resume, test_vacancy, test_recruiter):
        """Обновление статуса матча."""
        repo = facade.uow.match

        match = Match(
            resume_id=test_resume.resume_id,
            vacancy_id=test_vacancy.vacancy_id,
            recruiter_id=test_recruiter.user_id,
        )
        created = await repo.create(match)

        created.match_status = MatchStatus.APPROVED
        await repo.update(created)

        updated = await repo.get_by_id(created.match_id)
        assert updated.match_status == MatchStatus.APPROVED

    @pytest.mark.asyncio
    async def test_delete_match(self, facade, test_resume, test_vacancy, test_recruiter):
        """Удаление матча."""
        repo = facade.uow.match

        match = Match(
            resume_id=test_resume.resume_id,
            vacancy_id=test_vacancy.vacancy_id,
            recruiter_id=test_recruiter.user_id,
        )
        created = await repo.create(match)

        await repo.delete(created.match_id)

        found = await repo.get_by_id(created.match_id)
        assert found is None