import pytest
from fastapi import status


class TestCreateMatchAPI:

    @pytest.mark.asyncio
    async def test_create_match_success(
            self,
            recruiter_client,
            facade,
            test_resume,
            test_vacancy,
            test_recruiter
    ):
        data = {
            "resume_id": test_resume.resume_id,
            "vacancy_id": test_vacancy.vacancy_id
        }

        response = recruiter_client.post("/matches", json=data)

        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()
        assert result["resume_id"] == test_resume.resume_id
        assert result["vacancy_id"] == test_vacancy.vacancy_id
        assert result["recruiter_id"] == test_recruiter.user_id
        assert result["is_active"] is True

        from src.domain.match import Match
        from sqlalchemy import select

        async with facade.uow._session as session:
            query = select(Match).where(
                Match.resume_id == test_resume.resume_id,
                Match.vacancy_id == test_vacancy.vacancy_id
            )
            result_db = await session.execute(query)
            match = result_db.scalar_one()
            assert match is not None
            assert match.recruiter_id == test_recruiter.user_id

    def test_create_match_not_recruiter(self, applicant_client, test_resume, test_vacancy):
        data = {
            "resume_id": test_resume.resume_id,
            "vacancy_id": test_vacancy.vacancy_id
        }

        response = applicant_client.post("/matches", json=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_create_match_duplicate(
            self,
            recruiter_client,
            test_resume,
            test_vacancy,
            test_match
    ):
        data = {
            "resume_id": test_resume.resume_id,
            "vacancy_id": test_vacancy.vacancy_id
        }

        response = recruiter_client.post("/matches", json=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.text

    def test_create_match_invalid_data(self, recruiter_client):
        response = recruiter_client.post("/matches", json={"resume_id": -1})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestListMatchesAPI:

    @pytest.mark.asyncio
    async def test_list_my_matches_success(self, recruiter_client, test_match, test_recruiter):
        response = recruiter_client.get("/matches")

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

        first_match = result[0]
        assert "match_id" in first_match
        assert "recruiter_id" in first_match
        assert first_match["recruiter_id"] == test_recruiter.user_id

    def test_list_my_matches_not_recruiter(self, applicant_client):
        response = applicant_client.get("/matches")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetMatchDetailAPI:

    @pytest.mark.asyncio
    async def test_get_match_detail_success(self, recruiter_client, test_match):
        response = recruiter_client.get(f"/matches/{test_match.match_id}")

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["match_id"] == test_match.match_id
        assert "resume" in result
        assert "vacancy" in result
        assert "desired_position" in result["resume"]
        assert "title" in result["vacancy"]

    @pytest.mark.asyncio
    async def test_get_match_detail_not_found(self, recruiter_client):
        response = recruiter_client.get("/matches/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_match_detail_forbidden(self, other_recruiter_client, test_match):
        response = other_recruiter_client.get(f"/matches/{test_match.match_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateMatchStatusAPI:

    @pytest.mark.asyncio
    async def test_update_status_success(self, recruiter_client, test_match):
        data = {"is_active": False}

        response = recruiter_client.patch(
            f"/matches/{test_match.match_id}/status",
            json=data
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["is_active"] is False
        assert result["match_id"] == test_match.match_id

    @pytest.mark.asyncio
    async def test_update_status_not_found(self, recruiter_client):
        response = recruiter_client.patch(
            "/matches/99999/status",
            json={"is_active": False}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_status_forbidden(self, other_recruiter_client, test_match):
        response = other_recruiter_client.patch(
            f"/matches/{test_match.match_id}/status",
            json={"is_active": False}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateMatchAcceptanceAPI:

    @pytest.mark.asyncio
    async def test_update_acceptance_applicant_success(self, recruiter_client, test_match):
        data = {"applicant_accepted": True}

        response = recruiter_client.patch(
            f"/matches/{test_match.match_id}/acceptance",
            json=data
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["applicant_accepted"] is True
        assert result["employer_accepted"] is None
        assert result["is_active"] is True

    @pytest.mark.asyncio
    async def test_update_acceptance_both_true(self, recruiter_client, test_match_with_acceptance):
        data = {"employer_accepted": True}

        response = recruiter_client.patch(
            f"/matches/{test_match_with_acceptance.match_id}/acceptance",
            json=data
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["applicant_accepted"] is True
        assert result["employer_accepted"] is True
        assert result["is_active"] is False

    @pytest.mark.asyncio
    async def test_update_acceptance_reject(self, recruiter_client, test_match):
        data = {"applicant_accepted": False}

        response = recruiter_client.patch(
            f"/matches/{test_match.match_id}/acceptance",
            json=data
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["applicant_accepted"] is False
        assert result["is_active"] is False

    @pytest.mark.asyncio
    async def test_update_acceptance_not_found(self, recruiter_client):
        response = recruiter_client.patch(
            "/matches/99999/acceptance",
            json={"applicant_accepted": True}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_acceptance_forbidden(self, other_recruiter_client, test_match):
        response = other_recruiter_client.patch(
            f"/matches/{test_match.match_id}/acceptance",
            json={"applicant_accepted": True}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteMatchAPI:

    @pytest.mark.asyncio
    async def test_delete_match_success(self, recruiter_client, facade, test_match):
        response = recruiter_client.delete(f"/matches/{test_match.match_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        from src.domain.match import Match
        from sqlalchemy import select

        async with facade.uow._session as session:
            query = select(Match).where(Match.match_id == test_match.match_id)
            result = await session.execute(query)
            assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_delete_match_not_found(self, recruiter_client):
        response = recruiter_client.delete("/matches/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_match_forbidden(self, other_recruiter_client, test_match):
        response = other_recruiter_client.delete(f"/matches/{test_match.match_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestMatchBusinessLogic:

    @pytest.mark.asyncio
    async def test_full_match_workflow(self, recruiter_client, test_resume, test_vacancy):
        create_response = recruiter_client.post("/matches", json={
            "resume_id": test_resume.resume_id,
            "vacancy_id": test_vacancy.vacancy_id
        })
        assert create_response.status_code == status.HTTP_201_CREATED
        match_id = create_response.json()["match_id"]

        accept_applicant = recruiter_client.patch(
            f"/matches/{match_id}/acceptance",
            json={"applicant_accepted": True}
        )
        assert accept_applicant.status_code == status.HTTP_200_OK
        assert accept_applicant.json()["is_active"] is True

        accept_employer = recruiter_client.patch(
            f"/matches/{match_id}/acceptance",
            json={"employer_accepted": True}
        )
        assert accept_employer.status_code == status.HTTP_200_OK

        final_match = accept_employer.json()
        assert final_match["is_active"] is False
        assert final_match["applicant_accepted"] is True
        assert final_match["employer_accepted"] is True

    @pytest.mark.asyncio
    async def test_match_rejection_workflow(self, recruiter_client, test_resume, test_vacancy):
        create_response = recruiter_client.post("/matches", json={
            "resume_id": test_resume.resume_id,
            "vacancy_id": test_vacancy.vacancy_id
        })
        assert create_response.status_code == status.HTTP_201_CREATED
        match_id = create_response.json()["match_id"]

        recruiter_client.patch(
            f"/matches/{match_id}/acceptance",
            json={"applicant_accepted": True}
        )

        reject_response = recruiter_client.patch(
            f"/matches/{match_id}/acceptance",
            json={"employer_accepted": False}
        )

        assert reject_response.status_code == status.HTTP_200_OK
        final_match = reject_response.json()
        assert final_match["is_active"] is False
        assert final_match["applicant_accepted"] is True
        assert final_match["employer_accepted"] is False