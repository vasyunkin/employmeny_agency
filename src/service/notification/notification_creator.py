from dishka import FromDishka

from src.dal.facade import DALFacade
from src.domain.notification import Notification


class NotificationCreator:
    def __init__(self, dal: FromDishka[DALFacade]):
        self.dal = dal

    async def _create(self, uow, user_id: int, n_type: str, message: str):
        notification = Notification(
            user_id=user_id,
            notification_type=n_type,
            message=message
        )
        await uow.notification.create(notification)

    async def on_match_created(self, uow, match) -> None:
        resume = match.resume
        vacancy = match.vacancy

        applicant_id = resume.applicant_id
        employer_id = vacancy.employer_id

        await self._create(
            uow,
            applicant_id,
            "match_created",
            f"Подходящая вакансия для вас! -> '{vacancy.title}'."
        )

        await self._create(
            uow,
            employer_id,
            "match_created",
            f"Для вакансии '{vacancy.title}' найден кандидат."
        )

    async def on_acceptance_changed(self, uow, match) -> None:
        resume = match.resume
        vacancy = match.vacancy

        applicant_id = resume.applicant_id
        employer_id = vacancy.employer_id
        recruiter_id = match.recruiter_id

        a = match.applicant_accepted
        e = match.employer_accepted

        # FAIL
        if a is False or e is False:
            for user_id in [applicant_id, employer_id, recruiter_id]:
                await self._create(
                    uow,
                    user_id,
                    "match_failed",
                    "Сделка не состоялась"
                )
            return

        # SUCCESS
        if a is True and e is True:
            for user_id in [applicant_id, employer_id, recruiter_id]:
                await self._create(
                    uow,
                    user_id,
                    "match_success",
                    "Обе стороны согласились. Сделка успешно завершена!"
                )
            return

        # PARTIAL
        if a is True or e is True:
            for user_id in [applicant_id, employer_id, recruiter_id]:
                await self._create(
                    uow,
                    user_id,
                    "match_partial",
                    "Одна из сторон приняла предложение"
                )