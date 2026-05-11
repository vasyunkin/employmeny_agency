from sqlalchemy import Table, Column, String, Integer

from src.domain.resumes import Resume
from src.DAL.tables.base import metadata, mapper_registry


resumes_table = Table(
    'resumes',
    metadata,
    Column('resume_id', Integer, primary_key=True),
    Column(''),
    Column(),
)