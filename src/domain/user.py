from dataclasses import dataclass
from enum import Enum


class UserRole(Enum):
    APPLICANT = "applicant"
    EMPLOYER = "employer"
    RECRUITER = "recruiter"


@dataclass
class User:
    user_id: int
    user_login: str
    password_hash: str
    first_name: str
    last_name: str
    user_role: UserRole = UserRole.APPLICANT
