from dataclasses import dataclass
from typing import Optional


@dataclass
class Notification:
    user_id: int
    notification_type: Optional[str] = None
    message: Optional[str] = None
    notification_status: bool = False
    notification_id: Optional[int] = None