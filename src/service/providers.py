from dishka import Provider, provide, Scope

from src.dal.facade import DALFacade
from src.service.auth.auth_service import AuthService
from src.service.resume.resume_service import ResumeService
from src.service.vacancy.vacancy_service import VacancyService
from src.service.match.match_service import MatchService
from src.service.notification.notification_service import NotificationService
from src.service.notification.notification_creator import NotificationCreator


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
    def match_service(self, dal: DALFacade, notification_creator: NotificationCreator) -> MatchService:
        return MatchService(dal, notification_creator)

    @provide(scope=Scope.REQUEST)
    def notification_service(self, dal: DALFacade) -> NotificationService:
        return NotificationService(dal)

    @provide(scope=Scope.REQUEST)
    def notification_creator(self, dal: DALFacade) -> NotificationCreator:
        return NotificationCreator(dal)
