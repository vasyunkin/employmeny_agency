from fastapi import APIRouter, HTTPException, status
from dishka.integrations.fastapi import FromDishka, inject

from src.service.auth.auth_service import AuthService
from src.service.auth.dto import RegisterIn, LoginIn, TokenOut
from src.service.auth.exceptions import UserAlreadyExists, InvalidCredentials

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
@inject
async def register(
    data: RegisterIn,
    auth_service: FromDishka[AuthService]
):
    try:
        return await auth_service.register(data)
    except UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenOut)
@inject
async def login(
    data: LoginIn,
    auth_service: FromDishka[AuthService]
):
    try:
        return await auth_service.login(data)
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )