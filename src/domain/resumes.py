from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Resume:
    applicant_id: int
    desired_position: str
    desired_salary: Optional[Decimal] = None
    experience_years: int = 0
    skills: Optional[str] = None
    education: Optional[str] = None
    resume_status: bool = True
    resume_id: Optional[int] = None