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
    is_active: bool = True
    resume_id: Optional[int] = None

    def __post_init__(self):
        if not self.desired_position:
            raise ValueError('Опа! Ошибка: desired_position не может быть пустой')