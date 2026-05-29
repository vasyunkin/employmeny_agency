from src.dal.tables.interview_slots import map_interview_slots_table
from src.dal.tables.interviews import map_interviews_table
from src.dal.tables.matches import map_matches_table
from src.dal.tables.notifications import map_notifications_table
from src.dal.tables.resumes import map_resumes_table
from src.dal.tables.users import map_users_table
from src.dal.tables.vacancies import map_vacancies_table


def map_tables() -> None:
    map_users_table()
    map_resumes_table()
    map_vacancies_table()
    map_matches_table()
    map_interview_slots_table()
    map_interviews_table()
    map_notifications_table()
