import pytest

from src.domain.user import User, UserRole


@pytest.mark.asyncio
async def test_create_user_success(facade):
    user = User(
        user_login="john.doe",
        password_hash="hash123",
        first_name="John",
        last_name="Doe",
        user_role=UserRole.APPLICANT,
    )

    created_user = await facade.uow.user.create(user)

    assert created_user.user_id is not None
    assert created_user.user_login == "john.doe"
    assert created_user.first_name == "John"
    assert created_user.last_name == "Doe"
    assert created_user.user_role == UserRole.APPLICANT


@pytest.mark.asyncio
async def test_get_user_by_id_success(facade):
    user = User(
        user_login="maria.smith",
        password_hash="hash456",
        first_name="Maria",
        last_name="Smith",
        user_role=UserRole.EMPLOYER,
    )

    created_user = await facade.uow.user.create(user)
    found_user = await facade.uow.user.get_by_id(created_user.user_id)

    assert found_user is not None
    assert found_user.user_id == created_user.user_id
    assert found_user.user_login == "maria.smith"
    assert found_user.first_name == "Maria"
    assert found_user.last_name == "Smith"
    assert found_user.user_role == UserRole.EMPLOYER


@pytest.mark.asyncio
async def test_get_user_by_login_success(facade):
    user = User(
        user_login="alex.brown",
        password_hash="hash789",
        first_name="Alex",
        last_name="Brown",
        user_role=UserRole.RECRUITER,
    )

    created_user = await facade.uow.user.create(user)
    found_user = await facade.uow.user.get_by_login("alex.brown")

    assert found_user is not None
    assert found_user.user_id == created_user.user_id
    assert found_user.user_login == "alex.brown"
    assert found_user.user_role == UserRole.RECRUITER


@pytest.mark.asyncio
async def test_exists_by_login_returns_true(facade):
    user = User(
        user_login="sam.taylor",
        password_hash="hash000",
        first_name="Sam",
        last_name="Taylor",
    )

    await facade.uow.user.create(user)

    assert await facade.uow.user.exists_by_login("sam.taylor") is True


@pytest.mark.asyncio
async def test_get_user_not_found_returns_none(facade):
    result = await facade.uow.user.get_by_id(999999)

    assert result is None


