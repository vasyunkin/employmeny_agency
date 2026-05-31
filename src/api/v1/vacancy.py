from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import List

from src.service.vacancy.vacancy_service import VacancyService
from src.service.vacancy.vacancy_dto import VacancyCreateIn, VacancyOut
from src.service.vacancy.v_exceptions import VacancyNotFound, ForbiddenVacancyAccess

from src.api.dependencies import get_current_user


router = APIRouter(
    prefix="/vacancies",
    tags=["vacancies"]
)


async def get_vacancy_service(request: Request) -> VacancyService:
    container = request.state.dishka_container
    service = container.get(VacancyService)

    if hasattr(service, "__await__"):
        return await service
    return service


@router.post("/", response_model=VacancyOut, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    data: VacancyCreateIn,
    vacancy_service: VacancyService = Depends(get_vacancy_service),
    current_user=Depends(get_current_user)
):
    if current_user.user_role.value != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can create vacancies"
        )

    return await vacancy_service.create(
        employer_id=current_user.user_id,
        data=data
    )


@router.get("/", response_model=List[VacancyOut])
async def list_my_vacancies(
    vacancy_service: VacancyService = Depends(get_vacancy_service),
    current_user=Depends(get_current_user)
):
    if current_user.user_role.value != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can view their vacancies"
        )

    return await vacancy_service.list_by_employer(current_user.user_id)


@router.get("/{vacancy_id}", response_model=VacancyOut)
async def get_vacancy(
    vacancy_id: int,
    vacancy_service: VacancyService = Depends(get_vacancy_service),
    current_user=Depends(get_current_user)
):
    try:
        return await vacancy_service.get_by_id(
            vacancy_id=vacancy_id,
            employer_id=current_user.user_id
        )
    except VacancyNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenVacancyAccess as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{vacancy_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_vacancy(
    vacancy_id: int,
    vacancy_service: VacancyService = Depends(get_vacancy_service),
    current_user=Depends(get_current_user)
):
    try:
        await vacancy_service.deactivate(
            vacancy_id=vacancy_id,
            employer_id=current_user.user_id
        )
    except VacancyNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenVacancyAccess as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))