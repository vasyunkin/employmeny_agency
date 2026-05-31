from fastapi import APIRouter, HTTPException, status, Depends, Request

from src.service.auth.auth_service import AuthService
from src.service.auth.dto import RegisterIn, LoginIn, TokenOut
from src.service.auth.exceptions import UserAlreadyExists, InvalidCredentials

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


async def get_auth_service(request: Request) -> AuthService:
    container = request.state.dishka_container
    auth_service = container.get(AuthService)

    if hasattr(auth_service, "__await__"):
        return await auth_service

    return auth_service


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterIn,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        return await auth_service.register(data)
    except UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenOut)
async def login(
    data: LoginIn,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        return await auth_service.login(data)
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )