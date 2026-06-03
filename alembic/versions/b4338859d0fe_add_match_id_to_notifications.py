"""add_match_id_to_notifications

Revision ID: b4338859d0fe
Revises: e2a506d69ca9
Create Date: 2026-06-04 02:33:05.012340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4338859d0fe'
down_revision: Union[str, Sequence[str], None] = 'e2a506d69ca9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонку match_id
    op.add_column('notifications',
                  sa.Column('match_id', sa.Integer(), nullable=True)
                  )

    # Добавляем внешний ключ
    op.create_foreign_key(
        'fk_notifications_match_id',
        'notifications', 'matches',
        ['match_id'], ['match_id'],
        ondelete='SET NULL'
    )

    # Создаем индекс для ускорения запросов
    op.create_index('idx_notifications_match_id', 'notifications', ['match_id'])


def downgrade() -> None:
    # Удаляем индекс
    op.drop_index('idx_notifications_match_id', table_name='notifications')

    # Удаляем внешний ключ
    op.drop_constraint('fk_notifications_match_id', 'notifications', type_='foreignkey')

    # Удаляем колонку
    op.drop_column('notifications', 'match_id')
