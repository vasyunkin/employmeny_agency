from pydantic import BaseModel, Field, ConfigDict

from src.domain.match import MatchStatus
from src.service.resume.resume_dto import ResumeOut
from src.service.vacancy.vacancy_dto import VacancyOut


class MatchCreateIn(BaseModel):
    resume_id: int = Field(gt=0)
    vacancy_id: int = Field(gt=0)


class MatchUpdateStatusIn(BaseModel):
    """Обновление статуса мэтча"""
    match_status: MatchStatus


class MatchOut(BaseModel):
    match_id: int
    resume_id: int
    vacancy_id: int
    recruiter_id: int
    match_status: MatchStatus

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
    match_status: MatchStatus

    resume: ResumeOut
    vacancy: VacancyOut

    model_config = ConfigDict(from_attributes=True)