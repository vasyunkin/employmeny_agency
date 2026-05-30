from fastapi import FastAPI

from src.api.v1.auth import router as auth_router
from src.main.ioc import setup_di


def create_app() -> FastAPI:
    app = FastAPI(
        title="Employment Agency",
        docs_url="/docs",  # Swagger UI
        redoc_url="/redoc"
    )

    app.include_router(auth_router)
    setup_di(app)

    return app


app = create_app()