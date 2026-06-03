from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List

from src.service.notification.notification_service import NotificationService
from src.service.notification.notification_creator import NotificationCreator

from src.service.notification.notification_dto import (
    NotificationOut,
)
from src.service.notification.n_exceptions import (
    NotificationNotFound,
    ForbiddenNotificationAccess
)

from src.presentation.api.dependencies import get_current_user


router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


# =========================
# DEPENDENCIES
# =========================

async def get_notification_service(request: Request) -> NotificationService:
    container = request.state.dishka_container
    service = container.get(NotificationService)

    if hasattr(service, "__await__"):
        return await service
    return service


async def get_notification_creator(request: Request) -> NotificationCreator:
    container = request.state.dishka_container
    creator = container.get(NotificationCreator)

    if hasattr(creator, "__await__"):
        return await creator
    return creator


# =========================
# CRUD
# =========================

@router.get("/", response_model=List[NotificationOut])
async def list_notifications(
    notification_service: NotificationService = Depends(get_notification_service),
    current_user=Depends(get_current_user)
):
    return await notification_service.list_by_user(current_user.user_id)


@router.get("/unread", response_model=List[NotificationOut])
async def list_unread_notifications(
    notification_service: NotificationService = Depends(get_notification_service),
    current_user=Depends(get_current_user)
):
    return await notification_service.list_unread(current_user.user_id)


@router.get("/{notification_id}", response_model=NotificationOut)
async def get_notification(
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user=Depends(get_current_user)
):
    try:
        return await notification_service.get_by_id(
            notification_id=notification_id,
            user_id=current_user.user_id
        )
    except NotificationNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenNotificationAccess as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_as_read(
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user=Depends(get_current_user)
):
    try:
        await notification_service.mark_as_read(
            notification_id=notification_id,
            user_id=current_user.user_id
        )
    except NotificationNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenNotificationAccess as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_as_read(
    notification_service: NotificationService = Depends(get_notification_service),
    current_user=Depends(get_current_user)
):
    await notification_service.mark_all_as_read(current_user.user_id)