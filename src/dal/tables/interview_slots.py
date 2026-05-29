from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime

from src.domain.interview_slot import InterviewSlot
from src.dal.tables.base import metadata, mapper_registry


interview_slots_table = Table(
    'interview_slots',
    metadata,
    Column(
        'slot_id',
        Integer,
        primary_key=True
    ),
    Column(
        'employer_id',
        Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    ),
    Column(
        'slot_datetime',
        DateTime,
        nullable=False
    ),
)


def map_interview_slots_table() -> None:
    mapper_registry.map_imperatively(InterviewSlot, interview_slots_table)