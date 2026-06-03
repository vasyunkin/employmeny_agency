from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from src.service.resume.resume_dto import ResumeOut
from src.service.vacancy.vacancy_dto import VacancyOut


class MatchCreateIn(BaseModel):
    resume_id: Optional[int] = Field(default=None, gt=0)
    vacancy_id: Optional[int] = Field(default=None, gt=0)


class MatchUpdateStatusIn(BaseModel):
    """Обновление статуса мэтча"""
    is_active: bool


class MatchUpdateAcceptanceIn(BaseModel):
    """Обновление статуса принятия мэтча и привязка недостающих компонентов"""
    applicant_accepted: Optional[bool] = None
    employer_accepted: Optional[bool] = None

    resume_id: Optional[int] = Field(default=None, gt=0)
    vacancy_id: Optional[int] = Field(default=None, gt=0)

class MatchOut(BaseModel):
    match_id: int
    resume_id: Optional[int]
    vacancy_id: Optional[int]
    recruiter_id: int
    is_active: bool
    applicant_accepted: Optional[bool] = None
    employer_accepted: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class MatchListOut(BaseModel):
    items: list[MatchOut]
    total: int = Field(default=0)


class MatchDetailOut(BaseModel):
    """Полная информация о мэтче для рекрутера"""
    match_id: int
    resume_id: Optional[int]
    vacancy_id: Optional[int]
    recruiter_id: int
    is_active: bool
    applicant_accepted: Optional[bool] = None
    employer_accepted: Optional[bool] = None

    resume: Optional[ResumeOut]
    vacancy: Optional[VacancyOut]

    model_config = ConfigDict(from_attributes=True)