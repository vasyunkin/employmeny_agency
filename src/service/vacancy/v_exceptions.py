class VacancyError(Exception):
    pass


class VacancyNotFound(VacancyError):
    def __init__(self, vacancy_id: int):
        self.vacancy_id = vacancy_id
        super().__init__(f"Vacancy with id {vacancy_id} not found")


class ForbiddenVacancyAccess(VacancyError):
    def __init__(self, vacancy_id: int, user_id: int):
        self.vacancy_id = vacancy_id
        self.user_id = user_id
        super().__init__(f"Access denied to vacancy {vacancy_id} for user {user_id}")