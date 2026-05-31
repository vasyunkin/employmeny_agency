from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from typing import Annotated

from src.main.config import auth_config
from src.dal.facade import DALFacade
from src.domain.user import User


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

oauth2_scheme = HTTPBearer()


async def get_dal_facade(request: Request) -> DALFacade:
    """Получение DALFacade через Dishka"""
    container = request.state.dishka_container
    dal = container.get(DALFacade)

    if hasattr(dal, "__await__"):
        return await dal
    return dal


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
    dal: DALFacade = Depends(get_dal_facade)
) -> User:
    """Получение текущего пользователя по JWT токену"""
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            auth_config.get_secret_key(),
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with dal.uow as uow:
        user = await uow.user.get_by_id(int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user