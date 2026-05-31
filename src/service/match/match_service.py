from dishka import FromDishka

from src.dal.facade import DALFacade
from src.domain.match import Match, MatchStatus
from .match_dto import MatchCreateIn, MatchUpdateStatusIn, MatchOut, MatchDetailOut
from .m_exceptions import MatchAlreadyExists, MatchNotFound, ForbiddenMatchAccess


class MatchService:
    def __init__(self, dal: FromDishka[DALFacade]):
        self.dal = dal

    async def create(self, recruiter_id: int, data: MatchCreateIn) -> MatchOut:
        """Создать мэтч между резюме и вакансией"""
        async with self.dal.uow as uow:
            if await uow.match.exists(data.vacancy_id, data.resume_id):
                raise MatchAlreadyExists(data.resume_id, data.vacancy_id)

            match = Match(
                resume_id=data.resume_id,
                vacancy_id=data.vacancy_id,
                recruiter_id=recruiter_id,
            )

            created_match = await uow.match.create(match)
            await uow.commit()

            return MatchOut.model_validate(created_match)

    async def get_by_id(self, match_id: int, recruiter_id: int) -> MatchDetailOut:
        """Получить детальную информацию о мэтче"""
        async with self.dal.uow as uow:
            match = await uow.get_match_detail(match_id)

            if not match:
                raise MatchNotFound(match_id)

            if match.recruiter_id != recruiter_id:
                raise ForbiddenMatchAccess(match_id, recruiter_id)

            return MatchDetailOut.model_validate(match)

    async def list_by_recruiter(self, recruiter_id: int) -> list[MatchOut]:
        """Список всех мэтчей рекрутера"""
        async with self.dal.uow as uow:
            matches = await uow.match.list_by_recruiter(recruiter_id)
            return [MatchOut.model_validate(m) for m in matches]

    async def update_status(
        self,
        match_id: int,
        recruiter_id: int,
        data: MatchUpdateStatusIn
    ) -> MatchOut:
        """Обновить статус мэтча"""
        async with self.dal.uow as uow:
            match = await uow.match.get_by_id(match_id)

            if not match:
                raise MatchNotFound(match_id)

            if match.recruiter_id != recruiter_id:
                raise ForbiddenMatchAccess(match_id, recruiter_id)

            match.match_status = data.match_status

            await uow.match.update(match)
            await uow.commit()

            return MatchOut.model_validate(match)

    async def delete(self, match_id: int, recruiter_id: int) -> None:
        """Удалить мэтч (опционально)"""
        async with self.dal.uow as uow:
            match = await uow.match.get_by_id(match_id)

            if not match:
                raise MatchNotFound(match_id)

            if match.recruiter_id != recruiter_id:
                raise ForbiddenMatchAccess(match_id, recruiter_id)

            await uow.match.delete(match_id)
            await uow.commit()