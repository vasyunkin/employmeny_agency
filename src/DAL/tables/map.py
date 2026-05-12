from src.DAL.tables.resumes import map_resumes_table
from src.DAL.tables.users import map_users_table
from src.DAL.tables.vacancies import map_vacancies_table


def map_tables() -> None:
    map_users_table()
    map_resumes_table()
    map_vacancies_table()