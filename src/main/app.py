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
        template = templates.env.get_template("auth.html")
        content = template.render({"request": request})
        return HTMLResponse(content)


    @app.get("/resumes-page", response_class=HTMLResponse)
    async def resumes_page(request: Request):
        template = templates.env.get_template("items.html")
        return HTMLResponse(template.render({"request": request}))

    @app.get("/vacancies-page", response_class=HTMLResponse)
    async def vacancies_page(request: Request):
        template = templates.env.get_template("items.html")
        return HTMLResponse(template.render({"request": request}))

    @app.get("/matches-page", response_class=HTMLResponse)
    async def matches_page(request: Request):
        template = templates.env.get_template("items.html")
        return HTMLResponse(template.render({"request": request}))


    @app.get("/resumes/{resume_id}", response_class=HTMLResponse)
    async def resume_detail_page(request: Request):
        template = templates.env.get_template("entity_detail.html")
        return HTMLResponse(template.render({"request": request}))

    @app.get("/vacancies/{vacancy_id}", response_class=HTMLResponse)
    async def vacancy_detail_page(request: Request):
        template = templates.env.get_template("entity_detail.html")
        return HTMLResponse(template.render({"request": request}))

    @app.get("/matches/{match_id}", response_class=HTMLResponse)
    async def match_detail_page(request: Request):
        template = templates.env.get_template("entity_detail.html")
        return HTMLResponse(template.render({"request": request}))


    @app.get("/create/resume", response_class=HTMLResponse)
    async def create_resume_page(request: Request):
        template = templates.env.get_template("create_entity.html")
        return HTMLResponse(template.render({"request": request}))

    @app.get("/create/vacancy", response_class=HTMLResponse)
    async def create_vacancy_page(request: Request):
        template = templates.env.get_template("create_entity.html")
        return HTMLResponse(template.render({"request": request}))

    app.include_router(auth_router, prefix="/api")
    app.include_router(resumes_router, prefix="/api")
    app.include_router(vacancy_router, prefix="/api")
    app.include_router(match_router, prefix="/api")
    app.include_router(notification_router, prefix="/api")

    setup_di(app)

    return app


app = create_app()