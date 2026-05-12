from sqlalchemy import Table, Column, Integer, String, Text, Numeric, Boolean, ForeignKey

from src.domain.vacancy import Vacancy
from src.DAL.tables.base import metadata, mapper_registry


vacancies_table = Table(
    'vacancies',
    metadata,
    Column('vacancy_id', Integer, primary_key=True),
    Column(
        'employer_id',
        Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    ),
    Column('title', String(100), nullable=False),
    Column('salary', Numeric(10, 2)),
    Column('requirements', Text),
    Column('responsibilities', Text),
    Column('is_active', Boolean, nullable=False, server_default='True'),
)


def map_vacancies_table() -> None:
    mapper_registry.map_imperatively(Vacancy, vacancies_table)