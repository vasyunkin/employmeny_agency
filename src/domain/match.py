from dataclasses import dataclass
from enum import Enum
from typing import Optional

from src.domain.resume import Resume
from src.domain.vacancy import Vacancy


class MatchStatus(Enum):
    CREATED = 'created'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SCHEDULED = 'scheduled'
    COMPLETED = 'completed'


@dataclass
class Match:
    resume_id: Optional[int]
    vacancy_id: Optional[int]
    recruiter_id: int
    match_id: Optional[int] = None
    match_status: MatchStatus = MatchStatus.CREATED

    resume: Optional[Resume] = None
    vacancy: Optional[Vacancy] = None