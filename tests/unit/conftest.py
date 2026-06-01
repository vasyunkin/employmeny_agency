import pytest
from unittest.mock import AsyncMock, MagicMock

from src.service.resume.resume_service import ResumeService
from src.service.vacancy.vacancy_dto import VacancyCreateIn
from src.domain.resume import Resume
from src.domain.vacancy import Vacancy
from src.domain.match import Match
from src.domain.notification import Notification


@pytest.fixture
def mock_uow():
    """Мок UnitOfWork со всеми репозиториями"""
    uow_mock = AsyncMock()
    uow_mock.resume = AsyncMock()
    uow_mock.vacancy = AsyncMock()
    uow_mock.match = AsyncMock()
    uow_mock.notification = AsyncMock()
    uow_mock.commit = AsyncMock()
    uow_mock.rollback = AsyncMock()
    uow_mock.__aenter__ = AsyncMock(return_value=uow_mock)
    uow_mock.__aexit__ = AsyncMock(return_value=None)

    # Добавляем метод get_match_detail
    uow_mock.get_match_detail = AsyncMock()

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
def mock_notification_creator():
    """Мок NotificationCreator"""
    notification_mock = AsyncMock()
    notification_mock.on_match_created = AsyncMock()
    notification_mock.on_acceptance_changed = AsyncMock()
    return notification_mock


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


# ========== ФИКСТУРЫ ДЛЯ MATCH_SERVICE ==========

@pytest.fixture
def match_service(mock_dal, mock_notification_creator):
    """Экземпляр MatchService с замоканными зависимостями"""
    from src.service.match.match_service import MatchService
    return MatchService(
        dal=mock_dal,
        notification_creator=mock_notification_creator
    )


@pytest.fixture
def sample_match():
    """Пример мэтча из domain"""
    return Match(
        match_id=1,
        resume_id=1,
        vacancy_id=1,
        recruiter_id=300,
        is_active=True,
        applicant_accepted=None,
        employer_accepted=None
    )


@pytest.fixture
def sample_match_with_accepted():
    """Пример мэтча с подтверждениями"""
    return Match(
        match_id=2,
        resume_id=1,
        vacancy_id=1,
        recruiter_id=300,
        is_active=True,
        applicant_accepted=True,
        employer_accepted=True
    )


@pytest.fixture
def sample_match_detail(sample_match, sample_resume, sample_vacancy):
    """Пример детального мэтча с резюме и вакансией"""
    match = sample_match
    match.resume = sample_resume
    match.vacancy = sample_vacancy
    return match


@pytest.fixture
def create_match_data():
    """Данные для создания мэтча"""
    from src.service.match.match_dto import MatchCreateIn
    return MatchCreateIn(
        resume_id=1,
        vacancy_id=1
    )


@pytest.fixture
def update_match_status_data():
    """Данные для обновления статуса мэтча"""
    from src.service.match.match_dto import MatchUpdateStatusIn
    return MatchUpdateStatusIn(is_active=False)


@pytest.fixture
def update_match_acceptance_applicant_data():
    """Данные для обновления принятия мэтча (соискатель)"""
    from src.service.match.match_dto import MatchUpdateAcceptanceIn
    return MatchUpdateAcceptanceIn(applicant_accepted=True)


@pytest.fixture
def update_match_acceptance_employer_data():
    """Данные для обновления принятия мэтча (работодатель)"""
    from src.service.match.match_dto import MatchUpdateAcceptanceIn
    return MatchUpdateAcceptanceIn(employer_accepted=True)


@pytest.fixture
def update_match_acceptance_both_data():
    """Данные для обновления принятия мэтча (оба)"""
    from src.service.match.match_dto import MatchUpdateAcceptanceIn
    return MatchUpdateAcceptanceIn(applicant_accepted=True, employer_accepted=True)


# ========== ФИКСТУРЫ ДЛЯ NOTIFICATION_SERVICE ==========

@pytest.fixture
def notification_service(mock_dal):
    """Экземпляр NotificationService с замоканным DAL"""
    from src.service.notification.notification_service import NotificationService
    return NotificationService(dal=mock_dal)


@pytest.fixture
def notification_creator(mock_dal):
    """Экземпляр NotificationCreator с замоканным DAL"""
    from src.service.notification.notification_creator import NotificationCreator
    return NotificationCreator(dal=mock_dal)


@pytest.fixture
def sample_notification():
    """Пример уведомления из domain"""
    return Notification(
        notification_id=1,
        user_id=100,
        notification_type="match_created",
        message="Ваше резюме откликнуто на вакансию 'Python Developer'.",
        is_read=False
    )


@pytest.fixture
def sample_read_notification():
    """Пример прочитанного уведомления"""
    return Notification(
        notification_id=2,
        user_id=100,
        notification_type="match_success",
        message="Обе стороны согласились. Сделка успешно завершена!",
        is_read=True
    )


@pytest.fixture
def create_notification_data():
    """Данные для создания уведомления"""
    from src.service.notification.notification_dto import NotificationCreateIn
    return NotificationCreateIn(
        user_id=100,
        notification_type="match_created",
        message="Ваше резюме откликнуто на вакансию 'Python Developer'."
    )


@pytest.fixture
def sample_match_for_notification(sample_match_detail):
    """Мэтч для тестов уведомлений (с заполненными resume и vacancy)"""
    return sample_match_detail