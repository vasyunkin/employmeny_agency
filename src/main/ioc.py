from dishka import make_container, Provider, provide, Scope
from dishka.integrations.fastapi import setup_dishka

from src.dal.database import async_session_factory
from src.dal.facade import DALFacade
from src.service.providers import ServiceProvider


class DALProvider(Provider):
    """Провайдер для Data Access Layer"""

    @provide(scope=Scope.REQUEST)
    def dal_facade(self) -> DALFacade:
        return DALFacade(async_session_factory)


def get_container():
    """Создаёт и возвращает контейнер Dishka"""
    providers = [
        DALProvider(),
        ServiceProvider(),
        # Здесь позже будут добавляться другие провайдеры:
        # ConfigProvider(),
        # ExternalServicesProvider() и т.д.
    ]

    container = make_container(*providers)
    return container


def setup_di(app):
    """Настраивает DI в FastAPI приложении"""
    container = get_container()
    setup_dishka(container, app)