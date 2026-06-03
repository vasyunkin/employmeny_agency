from dishka import FromDishka
from src.dal.facade import DALFacade
from src.domain.match import Match
from src.service.notification.notification_creator import NotificationCreator
from .match_dto import (
    MatchCreateIn,
    MatchUpdateStatusIn,
    MatchOut,
    MatchDetailOut,
    MatchUpdateAcceptanceIn
)
from .m_exceptions import (
    MatchAlreadyExists,
    MatchNotFound,
    ForbiddenMatchAccess
)


class MatchService:
    def __init__(
        self,
        dal: FromDishka[DALFacade],
        notification_creator: FromDishka[NotificationCreator]
    ):
        self.dal = dal
        self.notification_creator = notification_creator

    async def create(self, recruiter_id: int, data: MatchCreateIn) -> MatchOut:
        async with self.dal.uow as uow:
            if data.vacancy_id is not None and data.resume_id is not None:
                if await uow.match.exists(data.vacancy_id, data.resume_id):
                    raise MatchAlreadyExists(data.resume_id, data.vacancy_id)

            match = Match(
                resume_id=data.resume_id,
                vacancy_id=data.vacancy_id,
                recruiter_id=recruiter_id,
                is_active=True,
                applicant_accepted=None,
                employer_accepted=None
            )

            created_match = await uow.match.create(match)

            await uow.commit()
            return MatchOut.model_validate(created_match)

    async def notify(self, match_id: int, recruiter_id: int):
        async with self.dal.uow as uow:
            match = await uow.get_match_detail(match_id)

            if not match:
                raise MatchNotFound(match_id)

            if match.recruiter_id != recruiter_id:
                raise ForbiddenMatchAccess(match_id, recruiter_id)

            if match.resume_id is None or match.vacancy_id is None:
                raise ValueError("Match is incomplete")

            await self.notification_creator.on_match_created(uow, match)
            await uow.commit()

    async def get_by_id(self, match_id: int, recruiter_id: int = None) -> MatchDetailOut:
        async with self.dal.uow as uow:
            match = await uow.get_match_detail(match_id)

            if not match:
                raise MatchNotFound(match_id)

            return MatchDetailOut.model_validate(match)

    async def list_by_recruiter(self, recruiter_id: int) -> list[MatchOut]:
        async with self.dal.uow as uow:
            matches = await uow.match.list_by_recruiter(recruiter_id)
            return [MatchOut.model_validate(m) for m in matches]

    async def update_status(
        self,
        match_id: int,
        recruiter_id: int,
        data: MatchUpdateStatusIn
    ) -> MatchOut:
        async with self.dal.uow as uow:
            match = await uow.match.get_by_id(match_id)
            if not match:
                raise MatchNotFound(match_id)
            if match.recruiter_id != recruiter_id:
                raise ForbiddenMatchAccess(match_id, recruiter_id)

            match.is_active = data.is_active
            await uow.match.update(match)
            await uow.commit()
            return MatchOut.model_validate(match)

    async def update_acceptance(
            self,
            match_id: int,
            recruiter_id: int,
            data: MatchUpdateAcceptanceIn
    ) -> MatchOut:
        async with self.dal.uow as uow:
            match = await uow.get_match_detail(match_id)
            if not match:
                raise MatchNotFound(match_id)

            if data.resume_id is not None:
                match.resume_id = data.resume_id
            if data.vacancy_id is not None:
                match.vacancy_id = data.vacancy_id

            if data.applicant_accepted is not None:
                match.applicant_accepted = data.applicant_accepted
            if data.employer_accepted is not None:
                match.employer_accepted = data.employer_accepted

            if match.applicant_accepted is False or match.employer_accepted is False:
                match.is_active = False
            elif match.applicant_accepted is True and match.employer_accepted is True:
                match.is_active = False

            await uow.match.update(match)

            await uow._session.flush()

            if match.resume_id is not None and match.vacancy_id is not None:
                refreshed_match = await uow.get_match_detail(match_id)
                await self.notification_creator.on_acceptance_changed(uow, refreshed_match)

            await uow.commit()
            return MatchOut.model_validate(match)

    async def delete(self, match_id: int, recruiter_id: int) -> None:
        async with self.dal.uow as uow:
            match = await uow.match.get_by_id(match_id)
            if not match:
                raise MatchNotFound(match_id)
            if match.recruiter_id != recruiter_id:
                raise ForbiddenMatchAccess(match_id, recruiter_id)

            await uow.match.delete(match_id)
            await uow.commit()