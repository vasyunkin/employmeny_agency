import pytest
from sqlalchemy.exc import IntegrityError

from src.DAL.repositories.sql_user_repository import SQLUserRepository
from src.domain.user import User, UserRole


@pytest.mark.asyncio
async def test_create_user_success(db_session):
    repo = SQLUserRepository(db_session)

    user = User(
        user_id=0,
        user_login="unique_user123",
        password_hash="secure_hash_123",
        first_name="Тест",
        last_name="Пользователь",
        user_role=UserRole.APPLICANT
    )

    created = await repo.create(user)

    assert created.user_id is not None and created.user_id > 0
    assert created.user_login == "unique_user123"
    assert created.user_role == UserRole.APPLICANT

    fetched = await repo.get_by_id(created.user_id)
    assert fetched is not None
    assert fetched.user_login == created.user_login


@pytest.mark.asyncio
async def test_create_user_duplicate_login_raises(db_session):
    repo = SQLUserRepository(db_session)

    user1 = User(
        id=0, login="duplicate_test", pswd_hash="hash1",
        first_name="A", last_name="B", user_role=UserRole.APPLICANT
    )
    user2 = User(
        id=0, login="duplicate_test", pswd_hash="hash2",
        first_name="C", last_name="D", user_role=UserRole.APPLICANT
    )

    await repo.create(user1)

    with pytest.raises(IntegrityError):
        await repo.create(user2)


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    repo = SQLUserRepository(db_session)
    result = await repo.get_by_id(999999)
    assert result is None