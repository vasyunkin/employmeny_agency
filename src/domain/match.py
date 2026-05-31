from dataclasses import dataclass
from enum import Enum
from typing import Optional

from src.domain.resume import Resume
from src.domain.vacancy import Vacancy


@dataclass
class Match:
    resume_id: Optional[int]
    vacancy_id: Optional[int]
    recruiter_id: int
    match_id: Optional[int] = None
    is_active: bool = True

    resume: Optional[Resume] = None
    vacancy: Optional[Vacancy] = None