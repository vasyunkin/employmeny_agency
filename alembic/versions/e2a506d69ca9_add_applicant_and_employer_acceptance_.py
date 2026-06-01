"""add_applicant_and_employer_acceptance_to_matches

Revision ID: e2a506d69ca9
Revises: 162896d5f2cc
Create Date: 2026-06-01 12:18:37.428017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2a506d69ca9'
down_revision: Union[str, Sequence[str], None] = '162896d5f2cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем новые колонки
    op.add_column('matches', sa.Column(
        'applicant_accepted',
        sa.Boolean(),
        nullable=True,
        server_default=None
    ))

    op.add_column('matches', sa.Column(
        'employer_accepted',
        sa.Boolean(),
        nullable=True,
        server_default=None
    ))


def downgrade() -> None:
    # Удаляем колонки при откате
    op.drop_column('matches', 'applicant_accepted')
    op.drop_column('matches', 'employer_accepted')
