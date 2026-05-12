from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class InterviewSlot:
    slot_datetime: datetime
    employer_id: int = None
    slot_id: Optional[int] = None