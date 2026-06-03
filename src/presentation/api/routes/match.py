from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import List

from src.service.match.match_service import MatchService
from src.service.match.match_dto import (
    MatchCreateIn,
    MatchUpdateStatusIn,
    MatchUpdateAcceptanceIn,
    MatchOut,
    MatchDetailOut
)
from src.service.match.m_exceptions import (
    MatchAlreadyExists,
    MatchNotFound,
    ForbiddenMatchAccess
)

from src.presentation.api.dependencies import get_current_user

router = APIRouter(
    prefix="/matches",
    tags=["matches"]
)


async def get_match_service(request: Request) -> MatchService:
    container = request.state.dishka_container
    service = container.get(MatchService)

    if hasattr(service, "__await__"):
        return await service
    return service


@router.post("/", response_model=MatchOut, status_code=status.HTTP_201_CREATED)
async def create_match(
    data: MatchCreateIn,
    match_service: MatchService = Depends(get_match_service),
    current_user=Depends(get_current_user)
):
    if current_user.user_role.value != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can create matches"
        )

    try:
        return await match_service.create(
            recruiter_id=current_user.user_id,
            data=data
        )
    except MatchAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[MatchOut])
async def list_my_matches(
    match_service: MatchService = Depends(get_match_service),
    current_user=Depends(get_current_user)
):
    if current_user.user_role.value != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view their matches"
        )

    return await match_service.list_by_recruiter(current_user.user_id)


@router.get("/{match_id}", response_model=MatchDetailOut)
async def get_match_detail(
    match_id: int,
    match_service: MatchService = Depends(get_match_service),
    current_user=Depends(get_current_user)
):
    try:
        return await match_service.get_by_id(
            match_id=match_id,
            recruiter_id=current_user.user_id
        )
    except MatchNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenMatchAccess as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{match_id}/notify")
async def notify_match(
    match_id: int,
    match_service: MatchService = Depends(get_match_service),
    current_user=Depends(get_current_user)
):
    await match_service.notify(match_id, current_user.user_id)
    return {"status": "ok"}


@router.patch("/{match_id}/status", response_model=MatchOut)
async def update_match_status(
    match_id: int,
    data: MatchUpdateStatusIn,
    match_service: MatchService = Depends(get_match_service),
    current_user=Depends(get_current_user)
):
    try:
        return await match_service.update_status(
            match_id=match_id,
            recruiter_id=current_user.user_id,
            data=data
        )
    except MatchNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenMatchAccess as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch("/{match_id}/acceptance", response_model=MatchOut)
async def update_match_acceptance(
    match_id: int,
    data: MatchUpdateAcceptanceIn,
    match_service: MatchService = Depends(get_match_service),
    current_user=Depends(get_current_user)
):
    """
    Обновление статуса принятия мэтча.
    Здесь автоматически триггерятся уведомления через service layer.
    """
    try:
        return await match_service.update_acceptance(
            match_id=match_id,
            recruiter_id=current_user.user_id,
            data=data
        )
    except MatchNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenMatchAccess as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(
    match_id: int,
    match_service: MatchService = Depends(get_match_service),
    current_user=Depends(get_current_user)
):
    try:
        await match_service.delete(
            match_id=match_id,
            recruiter_id=current_user.user_id
        )
    except MatchNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenMatchAccess as e:
        raise HTTPException(status_code=403, detail=str(e))