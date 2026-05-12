from dataclasses import dataclass
from typing import Optional


@dataclass
class Interview:
    match_id: int
    slot_id: int
    feedback_applicant: Optional[bool] = False
    feedback_employer: Optional[bool] = False
    interview_id: Optional[int] = None