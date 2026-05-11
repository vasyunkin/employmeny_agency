from dataclasses import dataclass
from decimal import Decimal
from typing import Optional



@dataclass
class Vacancy:
    employer_id: int
    title: str
    salary: Optional[Decimal] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    vacancy_status: bool = True
    vacancy_id: Optional[int] = None