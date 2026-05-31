from dishka import FromDishka

from src.dal.facade import DALFacade
from src.domain.vacancy import Vacancy
from .vacancy_dto import VacancyCreateIn, VacancyOut
from .v_exceptions import VacancyNotFound, ForbiddenVacancyAccess


class VacancyService:
    def __init__(self, dal: FromDishka[DALFacade]):
        self.dal = dal

    async def create(self, employer_id: int, data: VacancyCreateIn) -> VacancyOut:
        async with self.dal.uow as uow:
            vacancy = Vacancy(
                employer_id=employer_id,
                title=data.title,
                salary=data.salary,
                requirements=data.requirements,
                responsibilities=data.responsibilities,
            )

            created_vacancy = await uow.vacancy.create(vacancy)
            await uow.commit()

            return VacancyOut.model_validate(created_vacancy)

    async def get_by_id(self, vacancy_id: int, employer_id: int) -> VacancyOut:
        async with self.dal.uow as uow:
            vacancy = await uow.vacancy.get_by_id(vacancy_id)

            if not vacancy:
                raise VacancyNotFound(vacancy_id)

            if vacancy.employer_id != employer_id:
                raise ForbiddenVacancyAccess(vacancy_id, employer_id)

            return VacancyOut.model_validate(vacancy)

    async def list_by_employer(self, employer_id: int) -> list[VacancyOut]:
        async with self.dal.uow as uow:
            vacancies = await uow.vacancy.list_by_employer(employer_id)
            return [VacancyOut.model_validate(v) for v in vacancies]

    async def deactivate(self, vacancy_id: int, employer_id: int) -> None:
        async with self.dal.uow as uow:
            vacancy = await uow.vacancy.get_by_id(vacancy_id)

            if not vacancy:
                raise VacancyNotFound(vacancy_id)

            if vacancy.employer_id != employer_id:
                raise ForbiddenVacancyAccess(vacancy_id, employer_id)

            await uow.vacancy.deactivate(vacancy_id)
            await uow.commit()