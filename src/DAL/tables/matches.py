from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM

from src.domain.match import Match, MatchStatus
from src.DAL.tables.base import metadata, mapper_registry


match_statuses_enum = ENUM(
    MatchStatus,
    name='match_statuses',
    create_type=False,
    values_callable=lambda obj: [e.value for e in obj]
)


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
        'match_status',
        match_statuses_enum,
        nullable=False,
        server_default='created'
    ),
    UniqueConstraint('resume_id', 'vacancy_id'),
)


def map_matches_table() -> None:
    mapper_registry.map_imperatively(Match, matches_table)