from sqlalchemy import Table, Column, String, Integer, Boolean, Numeric, ForeignKey, Text

from src.domain.resume import Resume
from src.DAL.tables.base import metadata, mapper_registry


resumes_table = Table(
    'resumes',
    metadata,
    Column('resume_id', Integer, primary_key=True),
    Column(
        'applicant_id',
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    ),
    Column('desired_position', String(255), nullable=False),
    Column('desired_salary', Numeric(10, 2)),
    Column('experience_years', Integer, server_default="0"),
    Column('skills', Text),
    Column('education', Text),
    Column('is_active', Boolean, nullable=False, server_default="True"),
)


def map_resumes_table() -> None:
    mapper_registry.map_imperatively(Resume, resumes_table)