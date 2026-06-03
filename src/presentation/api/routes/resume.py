from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import List, Optional

from src.service.resume.resume_service import ResumeService
from src.service.resume.resume_dto import ResumeCreateIn, ResumeUpdateIn, ResumeOut
from src.service.resume.r_exceptions import ResumeAlreadyExists, ResumeNotFound, ForbiddenResumeAccess

from src.presentation.api.dependencies import get_current_user
from tests.unit.conftest import resume_service

router = APIRouter(
    prefix="/resumes",
    tags=["resumes"]
)


async def get_resume_service(request: Request) -> ResumeService:
    container = request.state.dishka_container
    service = container.get(ResumeService)

    if hasattr(service, "__await__"):
        return await service
    return service


@router.post("/", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
async def create_resume(
    data: ResumeCreateIn,
    resume_service: ResumeService = Depends(get_resume_service),
    current_user=Depends(get_current_user)
):
    if current_user.user_role.value != "applicant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only applicants can create resumes"
        )

    try:
        return await resume_service.create(
            applicant_id=current_user.user_id,
            data=data
        )
    except ResumeAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[ResumeOut])
async def list_my_resumes(
    resume_service: ResumeService = Depends(get_resume_service),
    current_user=Depends(get_current_user)
):
    if current_user.user_role.value != "applicant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only applicants can view their resumes"
        )

    return await resume_service.list_by_applicant(current_user.user_id)

@router.get("/search/", response_model=List[ResumeOut])
async def search_resumes(
        desired_position: Optional[str] = None,
        min_experience: Optional[int] = None,
        is_active: bool = True,
        limit: int = 15,
        offset: int = 0,
        resume_service=Depends(get_resume_service)
):
    return await resume_service.search(
            desired_position,
            min_experience,
            is_active,
            limit,
            offset,
        )


@router.get("/{resume_id}", response_model=ResumeOut)
async def get_resume(
    resume_id: int,
    resume_service: ResumeService = Depends(get_resume_service),
    current_user=Depends(get_current_user)
):
    try:
        return await resume_service.get_by_id(
            resume_id=resume_id,
            applicant_id=current_user.user_id
        )
    except ResumeNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenResumeAccess as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{resume_id}", response_model=ResumeOut)
async def update_resume(
    resume_id: int,
    data: ResumeUpdateIn,
    resume_service: ResumeService = Depends(get_resume_service),
    current_user=Depends(get_current_user)
):
    try:
        return await resume_service.update(
            resume_id=resume_id,
            applicant_id=current_user.user_id,
            data=data
        )
    except ResumeNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenResumeAccess as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{resume_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_resume(
    resume_id: int,
    resume_service: ResumeService = Depends(get_resume_service),
    current_user=Depends(get_current_user)
):
    try:
        await resume_service.deactivate(
            resume_id=resume_id,
            applicant_id=current_user.user_id
        )
    except ResumeNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenResumeAccess as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))