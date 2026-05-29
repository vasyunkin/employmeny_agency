from dishka import Provider, provide, Scope
from src.service.auth.service import AuthService
from src.DAL.facade import DALFacade


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def auth_service(self, dal: DALFacade) -> AuthService:
        return AuthService(dal)