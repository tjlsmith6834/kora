from fastapi import APIRouter, HTTPException, Query, Depends, Path, Body
from fastapi.responses import StreamingResponse
from typing import List
from uuid import UUID
import logging

from services.applications import fetch_application_summary_by_job_id, fetch_application_summary_by_application_id, fetch_application_analysis_rubric_by_application_id, fetch_application_form_question_answers_by_application_id, fetch_application_interview_question_answers_by_application_id, hide_application_by_application_id, fetch_resume_stream, submit_interview_question_answer
from services.profiles import fetch_profiles_by_job_id, fetch_profile_by_application_id
from services.auth import get_current_user_token
from schemas import ProfileRubric, ProfileSummary, QAResponse
from schemas.profiles import Profile
from schemas.auth import TokenPayload

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)

@router.get("/", response_model=List[ProfileSummary])
async def get_applications_by_query(
        token: TokenPayload = Depends(get_current_user_token),
        job_id: UUID = Query(...)
):
    try:
        logger.info(f"Router: Fetching applications for job: {job_id}")
        profile_list : List[ProfileSummary] = await fetch_application_summary_by_job_id(job_id)
        return profile_list
    except Exception:
        logger.exception("Error getting applications")
        raise HTTPException(status_code=500, detail="Error getting applications")

@router.get("/{application_id}/summary", response_model=ProfileSummary)
async def get_application_analysis_summary_by_application_id(
        token: TokenPayload = Depends(get_current_user_token),
        application_id: UUID = Path(...),
):
    try:
        profile: ProfileSummary = await fetch_application_summary_by_application_id(application_id)
        return profile
    except Exception:
        logger.exception("Error getting application summary")
        raise HTTPException(status_code=500, detail="Error getting application summary")

@router.get("/{application_id}/rubric", response_model=ProfileRubric)
async def get_application_analysis_rubric_by_application_id(
        token: TokenPayload = Depends(get_current_user_token),
        application_id: UUID = Path(...),
):
    try:
        profile_rubric: ProfileRubric = await fetch_application_analysis_rubric_by_application_id(application_id)
        logger.info(f"Router: Profile Rubric: {profile_rubric}")
        return profile_rubric
    except Exception:
        logger.exception("Error getting application rubric")
        raise HTTPException(status_code=500, detail="Error getting application summary")

@router.get("/{application_id}/form_question_answers", response_model=List[QAResponse])
async def get_form_question_answers_by_application_id(
        application_id: UUID = Path(...),
):
    try:
        qa_responses: List[QAResponse] = await fetch_application_form_question_answers_by_application_id(application_id)
        logger.info(f"Responses: {qa_responses}")
        return qa_responses
    except Exception:
        logger.exception("Error getting form question answers")
        raise HTTPException(status_code=500, detail="Error getting application summary")

@router.get("/{application_id}/interview_question_answers", response_model=List[QAResponse])
async def get_interview_question_answers(
        application_id: UUID = Path(...),
):
    try:
        qa_responses: List[QAResponse] = await fetch_application_interview_question_answers_by_application_id(application_id)
        logger.info(f"Responses: {qa_responses}")
        return qa_responses
    except Exception:
        logger.exception("Error fetching interview question answers")
        raise HTTPException(status_code=500, detail="Error fetchin interview question answers")

@router.post("/{application_id}/interview_question_answers")
async def submit_interview_question_answers(
        application_id: UUID = Path(..., description="The application ID for which the answer is being stored"),
        qa_response: QAResponse = Body(...)
):

    try:
        logger.info(
            f"Running save_answer_endpoint for application {application_id}\n"
            f"Question: {qa_response.question}, Answer: {qa_response.answer}"
        )

        qa_id = await submit_interview_question_answer(application_id, qa_response)

        return {
            "message": "Question answer stored successfully",
            "qa_id": qa_id,
        }
    except Exception:
        logger.exception("Error storing question answer")
        raise HTTPException(status_code=500, detail="Error storing question answer")

@router.put("/{application_id}/hide/", response_model=None)
async def hide_application(
        application_id: UUID = Path(...),
):
    try:
        await hide_application_by_application_id(application_id)
        return {"message": "Application hidden", "application_id": application_id}
    except Exception:
        logger.exception("Error hiding application")
        raise HTTPException(status_code=500, detail="Error fetchin interview question answers")


@router.get("/{application_id}/resume/", summary="Proxy resume stream to frontend")
async def get_application_resume(application_id: UUID) -> StreamingResponse:
    try:
        return await fetch_resume_stream(application_id)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error streaming resume")
        raise HTTPException(status_code=500, detail="Unexpected error")

@router.get("/profiles/", response_model=List[Profile])
async def get_profile_by_job_id(
        job_id: UUID = Query(...)
):
    try:
        logger.info(f"Router: Fetching profiles for job: {job_id}")
        profile_list : List[Profile] = await fetch_profiles_by_job_id(job_id)
        return profile_list
    except Exception:
        logger.exception("Error getting profiles")
        raise HTTPException(status_code=500, detail="Error getting profiles")

@router.get("/{application_id}/profile/", response_model=Profile)
async def get_profile_by_application_id(
        application_id: UUID = Path(...),
) -> Profile:
    try:
        return await fetch_profile_by_application_id(application_id)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error getting profile by application id")
        raise HTTPException(status_code=500, detail="Unexpected error")