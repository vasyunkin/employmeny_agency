from dataclasses import dataclass
from enum import Enum


class UserRole(Enum):
    APPLICANT = "applicant"
    EMPLOYER = "employer"
    RECRUITER = "recruiter"


@dataclass
class User:
    id: int
    login: str
    pswd_hash: str
    first_name: str
    last_name: str
    user_role: UserRole = UserRole.APPLICANT
