import pytest
import os
from dotenv import  load_dotenv
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from fastapi.testclient import TestClient

from src.dal.tables.base import metadata
from src.dal.tables.map import map_tables
from src.dal.facade import DALFacade
from src.main.app import create_app


load_dotenv()

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")

DB_PORT = "5437"
DB_NAME = f"{os.getenv('POSTGRES_DATABASE', 'employment_agency')}_test"

TEST_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


@pytest.fixture(scope="session")
def event_loop_policy():
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="session", autouse=True)
def setup_mapping():
    map_tables()


@pytest.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def session(engine):
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        try:
            await session.rollback()
        except Exception:
            pass


@pytest.fixture
async def facade(session):
    return DALFacade(session)


class MockCurrentUser:
    def __init__(self, user_id: int, user_role, user_login: str = "test_user"):
        self.user_id = user_id
        self.user_login = user_login
        self.user_role = user_role
        self.password_hash = "mock_hash"
        self.first_name = "Test"
        self.last_name = "User"
        self.is_active = True


@pytest.fixture
def app(session):
    app = create_app()

    from src.api.dependencies import get_current_user

    async def override_get_current_user():
        return MockCurrentUser(user_id=300, user_role="recruiter", user_login="recruiter")

    app.dependency_overrides[get_current_user] = override_get_current_user

    return app


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def recruiter_client(app):
    from src.api.dependencies import get_current_user

    async def override():
        return MockCurrentUser(user_id=300, user_role="recruiter", user_login="recruiter")

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def applicant_client(app):
    from src.api.dependencies import get_current_user

    async def override():
        return MockCurrentUser(user_id=100, user_role="applicant", user_login="applicant")

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def employer_client(app):
    from src.api.dependencies import get_current_user

    async def override():
        return MockCurrentUser(user_id=200, user_role="employer", user_login="employer")

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def other_recruiter_client(app):
    from src.api.dependencies import get_current_user

    async def override():
        return MockCurrentUser(user_id=999, user_role="recruiter", user_login="other_recruiter")

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
async def test_recruiter(facade):
    from src.domain.user import User, UserRole

    user = User(
        user_login="recruiter.test",
        password_hash="hash123",
        first_name="Test",
        last_name="Recruiter",
        user_role=UserRole.RECRUITER,
    )
    created_user = await facade.uow.user.create(user)
    await facade.uow.commit()
    return created_user


@pytest.fixture
async def test_applicant(facade):
    from src.domain.user import User, UserRole

    user = User(
        user_login="applicant.test",
        password_hash="hash123",
        first_name="Test",
        last_name="Applicant",
        user_role=UserRole.APPLICANT,
    )
    created_user = await facade.uow.user.create(user)
    await facade.uow.commit()
    return created_user


@pytest.fixture
async def test_employer(facade):
    from src.domain.user import User, UserRole

    user = User(
        user_login="employer.test",
        password_hash="hash123",
        first_name="Test",
        last_name="Employer",
        user_role=UserRole.EMPLOYER,
    )
    created_user = await facade.uow.user.create(user)
    await facade.uow.commit()
    return created_user


@pytest.fixture
async def test_resume(facade, test_applicant):
    from src.domain.resume import Resume

    resume = Resume(
        applicant_id=test_applicant.user_id,
        desired_position="Python Developer",
        desired_salary=5000.0,
        experience_years=3,
        skills="Python, SQL, FastAPI",
        education="Bachelor's Degree",
        is_active=True
    )
    created_resume = await facade.uow.resume.create(resume)
    await facade.uow.commit()
    return created_resume


@pytest.fixture
async def test_vacancy(facade, test_employer):
    from src.domain.vacancy import Vacancy

    vacancy = Vacancy(
        employer_id=test_employer.user_id,
        title="Senior Python Developer",
        salary=18000.0,
        requirements="Python, FastAPI, SQLAlchemy",
        responsibilities="Backend development",
        is_active=True
    )
    created_vacancy = await facade.uow.vacancy.create(vacancy)
    await facade.uow.commit()
    return created_vacancy


@pytest.fixture
async def test_match(facade, test_resume, test_vacancy, test_recruiter):
    from src.domain.match import Match

    match = Match(
        resume_id=test_resume.resume_id,
        vacancy_id=test_vacancy.vacancy_id,
        recruiter_id=test_recruiter.user_id,
        is_active=True,
        applicant_accepted=None,
        employer_accepted=None
    )
    created_match = await facade.uow.match.create(match)
    await facade.uow.commit()
    return created_match


@pytest.fixture
async def test_match_with_acceptance(facade, test_resume, test_vacancy, test_recruiter):
    from src.domain.match import Match

    match = Match(
        resume_id=test_resume.resume_id,
        vacancy_id=test_vacancy.vacancy_id,
        recruiter_id=test_recruiter.user_id,
        is_active=True,
        applicant_accepted=True,
        employer_accepted=None
    )
    created_match = await facade.uow.match.create(match)
    await facade.uow.commit()
    return created_match