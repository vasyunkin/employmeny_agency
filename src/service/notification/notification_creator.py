from dishka import FromDishka

from src.dal.facade import DALFacade
from src.domain.notification import Notification


class NotificationCreator:
    def __init__(self, dal: FromDishka[DALFacade]):
        self.dal = dal

    async def _create(self, uow, user_id: int, n_type: str, message: str, match_id: int = None):
        notification = Notification(
            user_id=user_id,
            notification_type=n_type,
            message=message,
            match_id=match_id  # Добавлен match_id
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
            f"Подходящая вакансия для вас! -> '{vacancy.title}'.",
            match_id=match.match_id  # Передаем match_id
        )

        await self._create(
            uow,
            employer_id,
            "match_created",
            f"Для вакансии '{vacancy.title}' найден кандидат.",
            match_id=match.match_id  # Передаем match_id
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
                    "Сделка не состоялась",
                    match_id=match.match_id  # Передаем match_id
                )
            return

        # SUCCESS
        if a is True and e is True:
            for user_id in [applicant_id, employer_id, recruiter_id]:
                await self._create(
                    uow,
                    user_id,
                    "match_success",
                    "Обе стороны согласились. Сделка успешно завершена!",
                    match_id=match.match_id  # Передаем match_id
                )
            return

        # PARTIAL
        if a is True or e is True:
            for user_id in [applicant_id, employer_id, recruiter_id]:
                await self._create(
                    uow,
                    user_id,
                    "match_partial",
                    "Одна из сторон приняла предложение",
                    match_id=match.match_id  # Передаем match_id
                )