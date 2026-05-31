class ResumeError(Exception):
    pass


class ResumeAlreadyExists(ResumeError):
    """Пользователь уже имеет активное резюме с такой желаемой должностью"""
    def __init__(self, desired_position: str):
        self.desired_position = desired_position
        super().__init__(f"Resume with desired position '{desired_position}' already exists")


class ResumeNotFound(ResumeError):
    """Резюме не найдено"""
    def __init__(self, resume_id: int):
        self.resume_id = resume_id
        super().__init__(f"Resume with id {resume_id} not found")


class ForbiddenResumeAccess(ResumeError):
    """Попытка доступа к чужому резюме"""
    def __init__(self, resume_id: int, user_id: int):
        self.resume_id = resume_id
        self.user_id = user_id
        super().__init__(f"Access denied to resume {resume_id} for user {user_id}")