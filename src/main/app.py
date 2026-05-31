from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.api.v1.auth import router as auth_router
from src.api.v1.resumes import router as resumes_router
from src.main.ioc import setup_di

templates = Jinja2Templates(directory="src/presentation")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Employment Agency",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.mount("/static", StaticFiles(directory="src/static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        template = templates.env.get_template("index.html")
        content = template.render({"request": request})
        return HTMLResponse(content)

    app.include_router(auth_router)
    app.include_router(resumes_router)


    setup_di(app)

    return app


app = create_app()