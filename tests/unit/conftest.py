import pytest
from unittest.mock import AsyncMock, MagicMock

from src.service.resume.resume_service import ResumeService
from src.service.vacancy.vacancy_dto import VacancyCreateIn
from src.domain.resume import Resume
from src.domain.vacancy import Vacancy


@pytest.fixture
def mock_uow():
    """Мок UnitOfWork со всеми репозиториями"""
    uow_mock = AsyncMock()
    uow_mock.resume = AsyncMock()
    uow_mock.commit = AsyncMock()
    uow_mock.rollback = AsyncMock()
    uow_mock.__aenter__ = AsyncMock(return_value=uow_mock)
    uow_mock.__aexit__ = AsyncMock(return_value=None)

    uow_mock.session = AsyncMock()
    uow_mock.session.refresh = AsyncMock()

    return uow_mock


@pytest.fixture
def mock_dal(mock_uow):
    """Мок DALFacade"""
    dal_mock = MagicMock()
    dal_mock.uow = mock_uow
    return dal_mock


@pytest.fixture
def resume_service(mock_dal):
    """Экземпляр сервиса с замоканным DAL"""
    return ResumeService(dal=mock_dal)


@pytest.fixture
def sample_resume():
    """Пример резюме из domain"""
    return Resume(
        resume_id=1,
        applicant_id=100,
        desired_position="Python Developer",
        desired_salary=5000.0,
        experience_years=3,
        skills="Python, SQL",
        education="Bachelor",
        is_active=True
    )


@pytest.fixture
def sample_resume_out_data():
    """Данные для ResumeOut (для проверки валидации)"""
    return {
        "resume_id": 1,
        "applicant_id": 100,
        "desired_position": "Python Developer",
        "desired_salary": 5000.0,
        "experience_years": 3,
        "skills": "Python, SQL",
        "education": "Bachelor",
        "is_active": True
    }


@pytest.fixture
def create_resume_data():
    """Данные для создания резюме"""
    from src.service.resume.resume_dto import ResumeCreateIn
    return ResumeCreateIn(
        desired_position="Python Developer",
        desired_salary=5000.0,
        experience_years=3,
        skills="Python, SQL",
        education="Bachelor"
    )


@pytest.fixture
def update_resume_data():
    """Данные для обновления резюме"""
    from src.service.resume.resume_dto import ResumeUpdateIn
    return ResumeUpdateIn(
        desired_salary=6000.0,
        experience_years=4
    )


@pytest.fixture
def partial_update_resume_data():
    """Данные для частичного обновления резюме"""
    from src.service.resume.resume_dto import ResumeUpdateIn
    return ResumeUpdateIn(skills="Python, SQL, Docker")


@pytest.fixture
def vacancy_service(mock_dal):
    from src.service.vacancy.vacancy_service import VacancyService
    return VacancyService(dal=mock_dal)


@pytest.fixture
def sample_vacancy():
    return Vacancy(
        vacancy_id=1,
        employer_id=200,
        title="Senior Python Developer",
        salary=18000.0,
        requirements="Python, FastAPI, SQLAlchemy",
        responsibilities="Backend development",
        is_active=True
    )


@pytest.fixture
def create_vacancy_data():
    return VacancyCreateIn(
        title="Senior Python Developer",
        salary=200000,
        requirements="Experience with FastAPI",
        responsibilities="API development"
    )