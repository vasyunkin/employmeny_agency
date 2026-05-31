class NotificationNotFound(Exception):
    def __init__(self, notification_id: int):
        self.notification_id = notification_id

    def __str__(self) -> str:
        return f"Notification with id={self.notification_id} not found"


class ForbiddenNotificationAccess(Exception):
    def __init__(self, notification_id: int, user_id: int):
        self.notification_id = notification_id
        self.user_id = user_id

    def __str__(self) -> str:
        return (
            f"User {self.user_id} has no access to notification {self.notification_id}"
        )