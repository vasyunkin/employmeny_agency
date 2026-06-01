"""
Тесты для SqlInterviewSlotRepository.
"""

import pytest
from datetime import datetime, timedelta

from src.domain.interview_slot import InterviewSlot
from src.domain.user import User, UserRole


class TestInterviewSlotRepositoryCreate:
    """Тесты метода create."""

    @pytest.mark.asyncio
    async def test_create_slot_success(self, facade):
        """Успешное создание одного слота."""
        repo = facade.uow.interview_slot

        employer = await facade.uow.user.create(User(
            user_login="employer.slots",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        ))

        slot_datetime = datetime.now() + timedelta(days=1, hours=10)

        slot = InterviewSlot(
            employer_id=employer.user_id,
            slot_datetime=slot_datetime,
        )

        created_slot = await repo.create(slot)

        assert created_slot.slot_id is not None
        assert created_slot.employer_id == employer.user_id
        assert created_slot.slot_datetime == slot_datetime


    @pytest.mark.asyncio
    async def test_create_many_slots(self, facade):
        """Успешное создание нескольких слотов."""
        repo = facade.uow.interview_slot

        employer = await facade.uow.user.create(User(
            user_login="employer.many.slots",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        ))

        base_time = datetime.now() + timedelta(days=1)
        slots = [
            InterviewSlot(employer_id=employer.user_id, slot_datetime=base_time + timedelta(hours=i))
            for i in range(5)
        ]

        created_slots = await repo.create_many(slots)

        assert len(created_slots) == 5
        for slot in created_slots:
            assert slot.slot_id is not None
            assert slot.employer_id == employer.user_id


class TestInterviewSlotRepositoryListByEmployer:
    """Тесты метода list_by_employer."""

    @pytest.mark.asyncio
    async def test_list_by_employer_success(self, facade):
        """Получение всех слотов работодателя."""
        repo = facade.uow.interview_slot

        employer = await facade.uow.user.create(User(
            user_login="employer.list",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        ))

        base_time = datetime.now() + timedelta(days=1)
        for i in range(3):
            slot = InterviewSlot(
                employer_id=employer.user_id,
                slot_datetime=base_time + timedelta(hours=i)
            )
            await repo.create(slot)

        slots = await repo.list_by_employer(employer.user_id)

        assert len(slots) == 3
        for slot in slots:
            assert slot.employer_id == employer.user_id


    @pytest.mark.asyncio
    async def test_list_by_employer_empty(self, facade):
        """Работодатель без слотов."""
        repo = facade.uow.interview_slot

        employer = await facade.uow.user.create(User(
            user_login="employer.empty",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        ))

        slots = await repo.list_by_employer(employer.user_id)
        assert len(slots) == 0


class TestInterviewSlotRepositoryListByPeriod:
    """Тесты метода list_by_employer_and_period."""

    @pytest.mark.asyncio
    async def test_list_by_employer_and_period(self, facade):
        """Получение слотов в определённом временном диапазоне."""
        repo = facade.uow.interview_slot

        employer = await facade.uow.user.create(User(
            user_login="employer.period",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        ))

        base_time = datetime.now() + timedelta(days=1)

        # Создаём слоты в разное время
        await repo.create(InterviewSlot(employer_id=employer.user_id, slot_datetime=base_time))
        await repo.create(InterviewSlot(employer_id=employer.user_id, slot_datetime=base_time + timedelta(hours=2)))
        await repo.create(InterviewSlot(employer_id=employer.user_id, slot_datetime=base_time + timedelta(hours=5)))
        await repo.create(InterviewSlot(employer_id=employer.user_id, slot_datetime=base_time + timedelta(days=2)))  # вне диапазона

        start = base_time
        end = base_time + timedelta(hours=4)

        slots = await repo.list_by_employer_and_period(
            employer_id=employer.user_id,
            start_datetime=start,
            end_datetime=end
        )

        assert len(slots) == 2
        for slot in slots:
            assert start <= slot.slot_datetime < end
            assert slot.employer_id == employer.user_id

    @pytest.mark.asyncio
    async def test_list_by_period_no_slots(self, facade):
        """Нет слотов в указанном периоде."""
        repo = facade.uow.interview_slot

        employer = await facade.uow.user.create(User(
            user_login="employer.no.period",
            password_hash="hash123",
            first_name="Test",
            last_name="Employer",
            user_role=UserRole.EMPLOYER,
        ))

        slots = await repo.list_by_employer_and_period(
            employer_id=employer.user_id,
            start_datetime=datetime.now() + timedelta(days=10),
            end_datetime=datetime.now() + timedelta(days=11)
        )

        assert len(slots) == 0