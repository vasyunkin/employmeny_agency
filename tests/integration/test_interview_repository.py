"""
Тесты для SqlInterviewRepository.
"""

import pytest


class TestInterviewRepositoryCreate:
    """Тесты метода create."""

    @pytest.mark.asyncio
    async def test_create_interview_success(self, facade, test_interview_setup):
        """Успешное создание интервью."""
        repo = facade.uow.interview
        setup = test_interview_setup

        assert setup["interview"].interview_id is not None
        assert setup["interview"].match_id == setup["match"].match_id
        assert setup["interview"].slot_id == setup["slot"].slot_id


class TestInterviewRepositoryGetById:
    """Тесты метода get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, facade, test_interview_setup):
        repo = facade.uow.interview
        setup = test_interview_setup

        found = await repo.get_by_id(setup["interview"].interview_id)

        assert found is not None
        assert found.interview_id == setup["interview"].interview_id
        assert found.match_id == setup["match"].match_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, facade):
        repo = facade.uow.interview
        result = await repo.get_by_id(999999)
        assert result is None


class TestInterviewRepositoryGetByMatchId:
    """Тесты метода get_by_match_id."""

    @pytest.mark.asyncio
    async def test_get_by_match_id_success(self, facade, test_interview_setup):
        repo = facade.uow.interview
        setup = test_interview_setup

        found = await repo.get_by_match_id(setup["match"].match_id)

        assert found is not None
        assert found.match_id == setup["match"].match_id


class TestInterviewRepositoryExistsBySlot:
    """Тесты метода exists_by_slot."""

    @pytest.mark.asyncio
    async def test_exists_by_slot_true(self, facade, test_interview_setup):
        repo = facade.uow.interview
        setup = test_interview_setup

        exists = await repo.exists_by_slot(setup["slot"].slot_id)
        assert exists is True

    @pytest.mark.asyncio
    async def test_exists_by_slot_false(self, facade):
        repo = facade.uow.interview
        exists = await repo.exists_by_slot(999999)
        assert exists is False


class TestInterviewRepositoryUpdateFeedback:
    """Тесты обновления фидбека."""

    @pytest.mark.asyncio
    async def test_update_applicant_feedback(self, facade, test_interview_setup):
        repo = facade.uow.interview
        setup = test_interview_setup

        await repo.update_applicant_feedback(setup["interview"].interview_id, True)

        updated = await repo.get_by_id(setup["interview"].interview_id)
        assert updated.feedback_applicant is True

    @pytest.mark.asyncio
    async def test_update_employer_feedback(self, facade, test_interview_setup):
        repo = facade.uow.interview
        setup = test_interview_setup

        await repo.update_employer_feedback(setup["interview"].interview_id, True)

        updated = await repo.get_by_id(setup["interview"].interview_id)
        assert updated.feedback_employer is True