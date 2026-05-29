"""
Тесты для SQLUserRepository.

Покрывает методы: create, get_by_id, get_by_login, exists_by_login.
"""

import pytest

from src.domain.user import User, UserRole


class TestUserRepositoryCreate:
    """Тесты метода create."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, facade):
        """Успешное создание пользователя."""
        repo = facade.uow.user

        user = User(
            user_login="john.doe",
            password_hash="hash123",
            first_name="John",
            last_name="Doe",
            user_role=UserRole.APPLICANT,
        )

        created_user = await repo.create(user)

        assert created_user.user_id is not None
        assert created_user.user_login == "john.doe"
        assert created_user.first_name == "John"
        assert created_user.last_name == "Doe"
        assert created_user.user_role == UserRole.APPLICANT
        assert isinstance(created_user, User)

    @pytest.mark.asyncio
    async def test_create_user_different_roles(self, facade):
        """Создание пользователей с разными ролями."""
        repo = facade.uow.user

        roles = [UserRole.APPLICANT, UserRole.EMPLOYER, UserRole.RECRUITER]

        for role in roles:
            user = User(
                user_login=f"test.{role.value}",
                password_hash="hash123",
                first_name="Test",
                last_name="User",
                user_role=role,
            )
            created = await repo.create(user)
            assert created.user_role == role
            assert created.user_id is not None


class TestUserRepositoryGetById:
    """Тесты метода get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, facade):
        """Успешное получение пользователя по ID."""
        repo = facade.uow.user

        user = User(
            user_login="maria.smith",
            password_hash="hash456",
            first_name="Maria",
            last_name="Smith",
            user_role=UserRole.EMPLOYER,
        )

        created_user = await repo.create(user)
        found_user = await repo.get_by_id(created_user.user_id)

        assert found_user is not None
        assert found_user.user_id == created_user.user_id
        assert found_user.user_login == "maria.smith"
        assert found_user.first_name == "Maria"
        assert found_user.last_name == "Smith"
        assert found_user.user_role == UserRole.EMPLOYER

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, facade):
        """Пользователь с несуществующим ID не найден."""
        repo = facade.uow.user
        result = await repo.get_by_id(999999)
        assert result is None


class TestUserRepositoryGetByLogin:
    """Тесты метода get_by_login."""

    @pytest.mark.asyncio
    async def test_get_by_login_success(self, facade):
        """Успешное получение пользователя по логину."""
        repo = facade.uow.user

        user = User(
            user_login="alex.brown",
            password_hash="hash789",
            first_name="Alex",
            last_name="Brown",
            user_role=UserRole.RECRUITER,
        )

        created_user = await repo.create(user)
        found_user = await repo.get_by_login("alex.brown")

        assert found_user is not None
        assert found_user.user_id == created_user.user_id
        assert found_user.user_login == "alex.brown"
        assert found_user.user_role == UserRole.RECRUITER

    @pytest.mark.asyncio
    async def test_get_by_login_not_found(self, facade):
        """Пользователь с несуществующим логином не найден."""
        repo = facade.uow.user
        result = await repo.get_by_login("non.existent")
        assert result is None


class TestUserRepositoryExistsByLogin:
    """Тесты метода exists_by_login."""

    @pytest.mark.asyncio
    async def test_exists_by_login_true(self, facade):
        """Проверка существования пользователя — возвращает True."""
        repo = facade.uow.user

        user = User(
            user_login="sam.taylor",
            password_hash="hash000",
            first_name="Sam",
            last_name="Taylor",
            user_role=UserRole.APPLICANT,
        )

        await repo.create(user)
        exists = await repo.exists_by_login("sam.taylor")

        assert exists is True

    @pytest.mark.asyncio
    async def test_exists_by_login_false(self, facade):
        """Проверка несуществующего логина — возвращает False."""
        repo = facade.uow.user
        exists = await repo.exists_by_login("ghost.user")
        assert exists is False