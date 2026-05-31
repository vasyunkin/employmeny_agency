"""replace_match_status_with_is_active

Revision ID: 162896d5f2cc
Revises: 3c113ef9606d
Create Date: 2026-06-01 03:27:48.522861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '162896d5f2cc'
down_revision: Union[str, Sequence[str], None] = '3c113ef9606d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Добавляем новое поле is_active с дефолтным значением
    op.add_column('matches', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

    # 2. Переносим данные из match_status в is_active
    #    Все статусы кроме 'rejected' становятся активными
    op.execute("""
        UPDATE matches 
        SET is_active = CASE 
            WHEN match_status = 'rejected' THEN false 
            ELSE true 
        END
    """)

    # 3. Убираем дефолт у match_status перед удалением колонки
    op.alter_column('matches', 'match_status', server_default=None)

    # 4. Удаляем старую колонку match_status
    op.drop_column('matches', 'match_status')

    # 5. Удаляем ENUM тип (только после того, как все ссылки удалены)
    op.execute("DROP TYPE match_statuses")


def downgrade() -> None:
    # Восстанавливаем ENUM тип
    op.execute("CREATE TYPE match_statuses AS ENUM ('created', 'approved', 'rejected', 'scheduled', 'completed')")

    # Добавляем колонку match_status
    op.add_column('matches', sa.Column('match_status', ENUM('created', 'approved', 'rejected', 'scheduled', 'completed',
                                                            name='match_statuses'), nullable=True))

    # Восстанавливаем данные из is_active
    op.execute("""
        UPDATE matches 
        SET match_status = CASE 
            WHEN is_active = true THEN 'created'
            ELSE 'rejected'
        END
    """)

    # Делаем колонку NOT NULL
    op.alter_column('matches', 'match_status', nullable=False, server_default='created')

    # Удаляем is_active
    op.drop_column('matches', 'is_active')
