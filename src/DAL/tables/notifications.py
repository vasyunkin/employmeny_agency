from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey

from src.domain.notification import Notification
from src.DAL.tables.base import metadata, mapper_registry


notifications_table = Table(
    'notifications',
    metadata,
    Column('notification_id', Integer, primary_key=True),
    Column(
        'user_id',
        Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    ),
    Column('notification_type', String(50)),
    Column('message', String),
    Column('is_read', Booleannullable=False, server_default='False'),
)


def map_notifications_table() -> None:
    mapper_registry.map_imperatively(Notification, notifications_table)