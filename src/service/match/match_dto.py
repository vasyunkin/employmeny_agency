from pydantic import BaseModel, Field, ConfigDict

from src.service.resume.resume_dto import ResumeOut
from src.service.vacancy.vacancy_dto import VacancyOut


class MatchCreateIn(BaseModel):
    resume_id: int = Field(gt=0)
    vacancy_id: int = Field(gt=0)


class MatchUpdateStatusIn(BaseModel):
    """Обновление статуса мэтча"""
    is_active: bool  # вместо match_status


class MatchOut(BaseModel):
    match_id: int
    resume_id: int
    vacancy_id: int
    recruiter_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class MatchListOut(BaseModel):
    items: list[MatchOut]
    total: int = Field(default=0)


class MatchDetailOut(BaseModel):
    """Полная информация о мэтче для рекрутера"""
    match_id: int
    resume_id: int
    vacancy_id: int
    recruiter_id: int
    is_active: bool

    resume: ResumeOut
    vacancy: VacancyOut

    model_config = ConfigDict(from_attributes=True)