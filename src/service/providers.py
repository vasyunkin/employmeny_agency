from dishka import Provider, provide, Scope

from src.dal.facade import DALFacade
from src.service.auth.auth_service import AuthService
from src.service.resume.resume_service import ResumeService
from src.service.vacancy.vacancy_service import VacancyService
from src.service.match.match_service import MatchService
from src.service.notification.notification_service import NotificationService


class ServiceProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def auth_service(self, dal: DALFacade) -> AuthService:
        return AuthService(dal)

    @provide(scope=Scope.REQUEST)
    def resume_service(self, dal: DALFacade) -> ResumeService:
        return ResumeService(dal)

    @provide(scope=Scope.REQUEST)
    def vacancy_service(self, dal: DALFacade) -> VacancyService:
        return VacancyService(dal)

    @provide(scope=Scope.REQUEST)
    def match_service(self, dal: DALFacade) -> MatchService:
        return MatchService(dal)

    @provide(scope=Scope.REQUEST)
    def match_service(self, dal: DALFacade) -> NotificationService:
        return NotificationService(dal)
