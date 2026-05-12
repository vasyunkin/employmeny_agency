from sqlalchemy import Table, Column, Integer, Boolean, ForeignKey

from src.domain.interview import Interview
from src.DAL.tables.base import metadata, mapper_registry


interviews_table = Table(
    'interviews',
    metadata,
    Column(
        'interview_id',
        Integer,
        rimary_key=True
    ),
    Column(
        'match_id',
        Integer,
        ForeignKey('matches.match_id', ondelete='CASCADE'),
        nullable=False,
        unique=True
    ),
    Column(
        'slot_id',
        Integer,
        ForeignKey('interview_slots.slot_id', ondelete='CASCADE'),
        nullable=False,
        unique=True
    ),
    Column(
        'feedback_applicant',
        Boolean,
        server_default='false'
    ),
    Column(
        'feedback_employer',
        Boolean,
        server_default='false'
    ),
)


def map_interviews_table() -> None:
    mapper_registry.map_imperatively(Interview, interviews_table)