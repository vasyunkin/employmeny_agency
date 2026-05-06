import pytest
from sqlalchemy.exc import IntegrityError

from src.DAL.repositories.sql_user_repository import SQLUserRepository
from src.DAL.uow import SQLAlchemyUnitOfWork, unit_of_work
from src.domain.user import User, UserRole


# ====================== Тесты через прямой репозиторий ======================

@pytest.mark.asyncio
async def test_create_user_success(db_session):
    repo = SQLUserRepository(db_session)

    user = User(
        user_id=None,                    # важно: None при создании
        user_login="unique_user123",
        password_hash="secure_hash_123",
        first_name="Тест",
        last_name="Пользователь",
        user_role=UserRole.APPLICANT,
    )

    created = await repo.create(user)

    assert created.user_id is not None
    assert created.user_id > 0
    assert created.user_login == "unique_user123"
    assert created.user_role == UserRole.APPLICANT
    assert created.first_name == "Тест"

    # Проверяем, что можно получить по id
    fetched = await repo.get_by_id(created.user_id)
    assert fetched is not None
    assert fetched.user_login == created.user_login


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    repo = SQLUserRepository(db_session)
    result = await repo.get_by_id(999999)
    assert result is None


@pytest.mark.asyncio
async def test_create_user_duplicate_login_raises(db_session):
    repo = SQLUserRepository(db_session)

    user1 = User(
        user_id=None,
        user_login="duplicate_test",
        password_hash="hash1",
        first_name="Алексей",
        last_name="Иванов",
        user_role=UserRole.APPLICANT,
    )

    user2 = User(
        user_id=None,
        user_login="duplicate_test",      # дубликат
        password_hash="hash2",
        first_name="Мария",
        last_name="Петрова",
        user_role=UserRole.APPLICANT,
    )

    await repo.create(user1)

    with pytest.raises(IntegrityError):
        await repo.create(user2)


# ====================== Тесты через Unit of Work ======================

@pytest.mark.asyncio
async def test_uow_create_user(db_session, async_session_maker):
    """Тест создания пользователя через UnitOfWork"""
    async with unit_of_work(async_session_maker) as uow:
        user = User(
            user_id=None,
            user_login="uow_test_user",
            password_hash="uow_hash",
            first_name="Unit",
            last_name="OfWork",
            user_role=UserRole.APPLICANT,
        )

        created = await uow.user.create(user)

        assert created.user_id is not None
        assert created.user_login == "uow_test_user"

        # Проверяем внутри той же транзакции
        fetched = await uow.user.get_by_id(created.user_id)
        assert fetched is not None


@pytest.mark.asyncio
async def test_uow_rollback_on_error(async_session_maker):
    """Проверяем, что при ошибке происходит rollback"""
    login = "rollback_test_user"

    try:
        async with unit_of_work(async_session_maker) as uow:
            user = User(
                user_id=None,
                user_login=login,
                password_hash="hash",
                first_name="Test",
                last_name="Rollback",
                user_role=UserRole.APPLICANT,
            )
            await uow.user.create(user)
            raise ValueError("Simulated error")  # имитируем ошибку
    except ValueError:
        pass

    # Проверяем, что пользователь НЕ сохранился после rollback
    async with unit_of_work(async_session_maker) as uow:
        found = await uow.user.get_by_login(login)
        assert found is None