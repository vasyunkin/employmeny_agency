from pydantic import BaseModel, Field
from src.domain.user import UserRole


class RegisterIn(BaseModel):
    user_login: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    user_role: UserRole = UserRole.APPLICANT


class LoginIn(BaseModel):
    user_login: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"