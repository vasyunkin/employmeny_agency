from dataclasses import dataclass
from typing import Optional


@dataclass
class Notification:
    user_id: int
    notification_type: Optional[str] = None
    message: Optional[str] = None
    is_read: bool = False
    notification_id: Optional[int] = None