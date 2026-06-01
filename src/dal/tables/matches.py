from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint, Boolean
from src.domain.match import Match
from src.dal.tables.base import metadata, mapper_registry


matches_table = Table(
    'matches',
    metadata,
    Column('match_id', Integer, primary_key=True),
    Column(
        'resume_id',
        Integer,
        ForeignKey('resumes.resume_id', ondelete='CASCADE')
    ),
    Column(
        'vacancy_id',
        Integer,
        ForeignKey('vacancies.vacancy_id', ondelete='CASCADE')
    ),
    Column(
        'recruiter_id',
        Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    ),
    Column(
        'is_active',
        Boolean,
        nullable=False,
        server_default='true'
    ),
    Column(
        'applicant_accepted',
        Boolean,
        nullable=True,
        server_default=None
    ),
    Column(
        'employer_accepted',
        Boolean,
        nullable=True,
        server_default=None
    ),
    UniqueConstraint('resume_id', 'vacancy_id'),
)


def map_matches_table() -> None:
    mapper_registry.map_imperatively(Match, matches_table)