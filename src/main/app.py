from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.presentation.api.routes.auth import router as auth_router
from src.presentation.api.routes.resumes import router as resumes_router
from src.presentation.api.routes.vacancy import router as vacancy_router
from src.presentation.api.routes.match import router as match_router
from src.presentation.api.routes.notification import router as notification_router
from src.main.ioc import setup_di

templates = Jinja2Templates(directory="src/presentation/templates")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Employment Agency",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.mount("/static", StaticFiles(directory="src/presentation/static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        template = templates.env.get_template("index.html")
        content = template.render({"request": request})
        return HTMLResponse(content)


    app.include_router(auth_router)
    app.include_router(resumes_router)
    app.include_router(vacancy_router)
    app.include_router(match_router)
    app.include_router(notification_router)

    setup_di(app)

    return app


app = create_app()