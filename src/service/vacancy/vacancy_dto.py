from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal


class VacancyCreateIn(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    salary: Optional[Decimal] = Field(None, ge=0)
    requirements: Optional[str] = Field(None, max_length=5000)
    responsibilities: Optional[str] = Field(None, max_length=5000)


class VacancyOut(BaseModel):
    vacancy_id: Optional[int]
    employer_id: int
    title: str
    salary: Optional[float]
    requirements: Optional[str]
    responsibilities: Optional[str]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class VacancyListOut(BaseModel):
    items: list[VacancyOut]
    total: int = Field(default=0)