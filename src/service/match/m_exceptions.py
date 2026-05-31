class MatchError(Exception):
    pass


class MatchAlreadyExists(MatchError):
    """Мэтч между этим резюме и вакансией уже существует"""
    def __init__(self, resume_id: int, vacancy_id: int):
        self.resume_id = resume_id
        self.vacancy_id = vacancy_id
        super().__init__(
            f"Match between resume {resume_id} and vacancy {vacancy_id} already exists"
        )


class MatchNotFound(MatchError):
    """Мэтч не найден"""
    def __init__(self, match_id: int):
        self.match_id = match_id
        super().__init__(f"Match with id {match_id} not found")


class ForbiddenMatchAccess(MatchError):
    """Попытка доступа к чужому мэтчу"""
    def __init__(self, match_id: int, recruiter_id: int):
        self.match_id = match_id
        self.recruiter_id = recruiter_id
        super().__init__(
            f"Access denied to match {match_id} for recruiter {recruiter_id}"
        )