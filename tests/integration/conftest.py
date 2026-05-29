import pytest
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from datetime import datetime, timedelta


from src.domain.user import User, UserRole
from src.domain.resume import Resume
from src.domain.vacancy import Vacancy
from src.domain.match import Match
from src.domain.interview_slot import InterviewSlot
from src.domain.interview import Interview

from src.DAL.tables.base import metadata
from src.DAL import tables
from src.DAL.tables.map import map_tables
from src.DAL.facade import DALFacade


TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5437/employment_test_db"
)


@pytest.fixture(scope="session")
def event_loop_policy():
    """Использовать единый event loop policy."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture
async def engine():
    """Создаёт движок для тестовой БД."""
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
    """Создаёт сессию для каждого теста с автоматическим откатом."""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        try:
            await session.rollback()
        except Exception:
            pass


@pytest.fixture(scope="session", autouse=True)
def setup_mapping():
    """Маппинг выполняется только один раз за всю сессию тестов"""
    map_tables()


@pytest.fixture
async def facade(session):
    return DALFacade(session)


@pytest.fixture
async def test_user(facade):
    user = User(
        user_login="john.doe",
        password_hash="hash123",
        first_name="John",
        last_name="Doe",
        user_role=UserRole.APPLICANT,
    )
    created_user = await facade.uow.user.create(user)
    return created_user


# ====================== ТЕСТОВЫЕ ДАННЫЕ ДЛЯ MATCH ======================

@pytest.fixture
async def test_recruiter(facade):
    """Тестовый рекрутер"""
    user = User(
        user_login="recruiter.test",
        password_hash="hash123",
        first_name="Test",
        last_name="Recruiter",
        user_role=UserRole.RECRUITER,
    )
    return await facade.uow.user.create(user)


@pytest.fixture
async def test_applicant(facade):
    """Тестовый соискатель"""
    user = User(
        user_login="applicant.test",
        password_hash="hash123",
        first_name="Test",
        last_name="Applicant",
        user_role=UserRole.APPLICANT,
    )
    return await facade.uow.user.create(user)


@pytest.fixture
async def test_employer(facade):
    """Тестовый работодатель"""
    user = User(
        user_login="employer.test",
        password_hash="hash123",
        first_name="Test",
        last_name="Employer",
        user_role=UserRole.EMPLOYER,
    )
    return await facade.uow.user.create(user)


@pytest.fixture
async def test_resume(facade, test_applicant):
    """Тестовое резюме"""
    resume = Resume(
        applicant_id=test_applicant.user_id,
        desired_position="Python Developer",
        experience_years=3,
    )
    return await facade.uow.resume.create(resume)


@pytest.fixture
async def test_vacancy(facade, test_employer):
    """Тестовая вакансия"""
    vacancy = Vacancy(
        employer_id=test_employer.user_id,
        title="Senior Python Developer",
        salary=250000,
    )
    return await facade.uow.vacancy.create(vacancy)


@pytest.fixture
async def test_interview_setup(facade):
    """
    Создаёт полный набор данных для тестирования Interview:
    applicant -> resume -> employer -> vacancy -> recruiter -> match -> slot -> interview
    """
    # 1. Пользователи
    applicant = await facade.uow.user.create(User(
        user_login="applicant.setup",
        password_hash="hash123",
        first_name="Test",
        last_name="Applicant",
        user_role=UserRole.APPLICANT,
    ))

    employer = await facade.uow.user.create(User(
        user_login="employer.setup",
        password_hash="hash123",
        first_name="Test",
        last_name="Employer",
        user_role=UserRole.EMPLOYER,
    ))

    recruiter = await facade.uow.user.create(User(
        user_login="recruiter.setup",
        password_hash="hash123",
        first_name="Test",
        last_name="Recruiter",
        user_role=UserRole.RECRUITER,
    ))

    # 2. Резюме
    resume = await facade.uow.resume.create(Resume(
        applicant_id=applicant.user_id,
        desired_position="Python Developer",
        experience_years=3,
    ))

    # 3. Вакансия
    vacancy = await facade.uow.vacancy.create(Vacancy(
        employer_id=employer.user_id,
        title="Senior Python Developer",
        salary=250000,
    ))

    # 4. Match
    match = await facade.uow.match.create(Match(
        resume_id=resume.resume_id,
        vacancy_id=vacancy.vacancy_id,
        recruiter_id=recruiter.user_id,
    ))

    # 5. Interview Slot
    slot = await facade.uow.interview_slot.create(InterviewSlot(
        employer_id=employer.user_id,
        slot_datetime=datetime.now() + timedelta(days=1, hours=10),
    ))

    # 6. Interview
    interview = await facade.uow.interview.create(Interview(
        match_id=match.match_id,
        slot_id=slot.slot_id,
    ))

    return {
        "applicant": applicant,
        "employer": employer,
        "recruiter": recruiter,
        "resume": resume,
        "vacancy": vacancy,
        "match": match,
        "slot": slot,
        "interview": interview,
    }