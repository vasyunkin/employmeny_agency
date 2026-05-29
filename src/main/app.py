from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka

from src.api.v1.auth import router as auth_router
# позже добавишь другие роутеры

def create_app() -> FastAPI:
    app = FastAPI(
        title="Employment Agency API",
        version="0.1.0"
    )

    # Подключаем роутеры
    app.include_router(auth_router)

    # Настройка DI (dishka)
    from src.main.ioc import get_container  # или где у тебя контейнер
    setup_dishka(get_container(), app)

    return app