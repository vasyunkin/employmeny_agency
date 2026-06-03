from typing import Optional
from dishka import FromDishka

from src.dal.facade import DALFacade
from src.domain.resume import Resume
from .resume_dto import ResumeCreateIn, ResumeUpdateIn, ResumeOut
from .r_exceptions import ResumeAlreadyExists, ResumeNotFound, ForbiddenResumeAccess


class ResumeService:
    def __init__(self, dal: FromDishka[DALFacade]):
        self.dal = dal

    async def create(self, applicant_id: int, data: ResumeCreateIn) -> ResumeOut:
        """Создание нового резюме"""
        async with self.dal.uow as uow:
            if await uow.resume.exists_similar(applicant_id, data.desired_position):
                raise ResumeAlreadyExists(data.desired_position)

            resume = Resume(
                applicant_id=applicant_id,
                desired_position=data.desired_position,
                desired_salary=data.desired_salary,
                experience_years=data.experience_years,
                skills=data.skills,
                education=data.education,
            )

            created_resume = await uow.resume.create(resume)
            await uow.commit()

            return ResumeOut.model_validate(created_resume)

    async def get_by_id(self, resume_id: int, applicant_id: int) -> ResumeOut:
        """Получение резюме по ID с проверкой владельца"""
        async with self.dal.uow as uow:
            resume = await uow.resume.get_by_id(resume_id)

            if not resume:
                raise ResumeNotFound(resume_id)

            if resume.applicant_id != applicant_id:
                raise ForbiddenResumeAccess(resume_id, applicant_id)

            return ResumeOut.model_validate(resume)

    async def list_by_applicant(self, applicant_id: int) -> list[ResumeOut]:
        """Список всех резюме соискателя"""
        async with self.dal.uow as uow:
            resumes = await uow.resume.list_by_applicant(applicant_id)
            return [ResumeOut.model_validate(r) for r in resumes]

    async def deactivate(self, resume_id: int, applicant_id: int) -> None:
        """Деактивация резюме"""
        async with self.dal.uow as uow:
            resume = await uow.resume.get_by_id(resume_id)

            if not resume:
                raise ResumeNotFound(resume_id)

            if resume.applicant_id != applicant_id:
                raise ForbiddenResumeAccess(resume_id, applicant_id)

            await uow.resume.deactivate(resume_id)
            await uow.commit()

    async def search(
            self,
            desired_position: Optional[str] = None,
            min_experience: Optional[int] = None,
            is_active: bool = True,
            limit: int = 15,
            offset: int = 0
    ) -> list[ResumeOut]:
        async with self.dal.uow as uow:
            resumes = await uow.resume.search(
                desired_position=desired_position,
                min_experience=min_experience,
                is_active=is_active,
                limit=limit,
                offset=offset,
            )
            return [ResumeOut.model_validate(r) for r in resumes]