from abc import abstractmethod
from typing import Protocol, Optional

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
    async def deactivate(self, vacancy_id: int) -> None:
        ...

    async def search(
            self,
            title: Optional[str] = None,
            min_salary: Optional[float] = None,
            is_active: Optional[bool] = True,
            limit: int = 50,
            offset: int = 0
    ) -> list[Vacancy]:
        ...