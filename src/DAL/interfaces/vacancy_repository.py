from abc import abstractmethod
from typing import Protocol

from src.domain.vacancy import Vacancy


class VacancyRepository(Protocol):
    @abstractmethod
    async def create(self, vacancy: Vacancy) -> Vacancy:
        ...

    @abstractmethod
    async def get_by_id(self, vacancy_id: int) -> Vacancy | None:
        ...

    @abstractmethod
    async def list_by_employer(self, employer_id: int) -> list[Vacancy]:
        ...
    
    @abstractmethod
    async def search(self) -> list[Vacancy]:
        ...