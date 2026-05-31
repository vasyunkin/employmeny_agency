from pydantic import BaseModel, Field, ConfigDict


class NotificationCreateIn(BaseModel):
    """Создание уведомления (внутреннее, не из API)"""
    user_id: int = Field(gt=0)
    notification_type: str = Field(min_length=1, max_length=50)
    message: str = Field(min_length=1)


class NotificationOut(BaseModel):
    notification_id: int
    user_id: int
    notification_type: str
    message: str
    is_read: bool

    model_config = ConfigDict(from_attributes=True)


class NotificationListOut(BaseModel):
    items: list[NotificationOut]
    total: int = 0