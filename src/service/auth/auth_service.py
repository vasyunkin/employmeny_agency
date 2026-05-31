from datetime import datetime, timedelta
import hashlib

from dishka import FromDishka
from jose import jwt
from passlib.context import CryptContext

from src.dal.facade import DALFacade
from src.domain.user import User
from .auth_dto import RegisterIn, LoginIn, TokenOut
from .a_exceptions import UserAlreadyExists, InvalidCredentials
from src.main.config import auth_config


pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=100000
)


class AuthService:
    def __init__(self, dal: FromDishka[DALFacade]):
        self.dal = dal

    async def register(self, data: RegisterIn) -> TokenOut:
        async with self.dal.uow as uow:
            if await uow.user.exists_by_login(data.user_login):
                raise UserAlreadyExists(f"User with login {data.user_login} already exists")

            hashed_password = pwd_context.hash(data.password)

            user = User(
                user_login=data.user_login,
                password_hash=hashed_password,
                first_name=data.first_name,
                last_name=data.last_name,
                user_role=data.user_role,
            )

            await uow.user.create(user)
            await uow.commit()

            return self._create_access_token(user)

    async def login(self, data: LoginIn) -> TokenOut:
        async with self.dal.uow as uow:
            user = await uow.user.get_by_login(data.user_login)

            if not user or not pwd_context.verify(data.password, user.password_hash):
                raise InvalidCredentials()

            return self._create_access_token(user)

    def _create_access_token(self, user: User) -> TokenOut:
        expire = datetime.utcnow() + timedelta(days=7)

        to_encode = {
            "sub": str(user.user_id),
            "login": user.user_login,
            "role": user.user_role.value,
            "exp": expire
        }

        encoded_jwt = jwt.encode(
            to_encode,
            auth_config.get_secret_key(),
            algorithm="HS256"
        )

        return TokenOut(access_token=encoded_jwt)