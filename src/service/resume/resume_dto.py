from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ResumeCreateIn(BaseModel):
    desired_position: str = Field(min_length=3, max_length=255)
    desired_salary: Optional[float] = Field(None, ge=0)
    experience_years: int = Field(default=0, ge=0)
    skills: Optional[str] = Field(None, max_length=5000)
    education: Optional[str] = Field(None, max_length=5000)


class ResumeUpdateIn(BaseModel):
    desired_position: Optional[str] = Field(None, min_length=5, max_length=255)
    desired_salary: Optional[float] = Field(None, ge=0)
    experience_years: Optional[int] = Field(None, ge=0)
    skills: Optional[str] = None
    education: Optional[str] = None


class ResumeOut(BaseModel):
    resume_id: int
    applicant_id: int
    desired_position: str
    desired_salary: Optional[float]
    experience_years: int
    skills: Optional[str]
    education: Optional[str]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ResumeListOut(BaseModel):
    items: list[ResumeOut]
    total: int = Field(default=0)