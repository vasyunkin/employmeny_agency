from dishka import Provider, provide, Scope
from src.service.auth.auth_service import AuthService
from src.dal.facade import DALFacade


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def auth_service(self, dal: DALFacade) -> AuthService:
        return AuthService(dal)