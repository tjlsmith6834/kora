from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

from common.models_schemas.models import Application
from common.models_schemas.models.profile import (
    CandidateProfile,
    CandidateProfileCategoryScore,
    CandidateProfileSummaryBullet,
    CareerPath,
    RecentRole as RecentRoleModel
)
from common.models_schemas.schemas.profiles import (
    Profile2,
    ProfileOverallScore,
    ProfileRubric,
    ProfileCategoryScore,
    ProfileSummaryBullet,
    ProfileBullets,
    ProfileCareerPath,
    RoleSummary,
    RecentRole as RecentRoleSchema
)

def get_profiles2_by_job_id(job_id: UUID, db: Session) -> list[Profile2]:
    try:
        # Step 1: Fetch joined data for all analyzed applications under job_id
        stmt = (
            select(
                CandidateProfile,
                Application,
                CareerPath,
                CandidateProfileSummaryBullet.detail,
                CandidateProfileSummaryBullet.position,
                CandidateProfileSummaryBullet.type,
                RecentRoleModel
            )
            .join(Application, CandidateProfile.application_id == Application.application_id)
            .join(CareerPath, CandidateProfile.profile_id == CareerPath.profile_id)
            .join(CandidateProfileSummaryBullet, CandidateProfile.profile_id == CandidateProfileSummaryBullet.profile_id)
            .outerjoin(RecentRoleModel, RecentRoleModel.application_id == Application.application_id)
            .where(Application.job_id == job_id)
            .where(Application.application_status == "analyzed")
        )

        rows = db.execute(stmt).all()
        logger.info("Found %s rows for job_id=%s", len(rows), job_id)
        if not rows:
            return []

        # Step 2: Group rows by (profile_id, application_id) to aggregate bullets
        grouped = {}
        for row in rows:
            profile = row.CandidateProfile
            application = row.Application
            career = row.CareerPath

            key = (profile.profile_id, application.application_id)
            if key not in grouped:
                grouped[key] = {
                    "profile": profile,
                    "application": application,
                    "career": career,
                    "bullets_roles": []
                }

            grouped[key]["bullets_roles"].append(row)

        # Step 3: Build Profile2 objects
        profiles = []

        for (profile_id, application_id), group in grouped.items():
            profile = group["profile"]
            application = group["application"]
            career = group["career"]
            bullets_roles_rows = group["bullets_roles"]

            overall = assemble_profile_score(profile)
            career_path = assemble_career_path(career)
            bullets = assemble_profile_bullets(bullets_roles_rows)
            recent_roles = assemble_recent_roles(bullets_roles_rows)

            # Separate query per profile for rubric scores
            rubric_stmt = (
                select(CandidateProfileCategoryScore)
                .where(CandidateProfileCategoryScore.profile_id == profile.profile_id)
            )
            rubric_models = db.execute(rubric_stmt).scalars().all()
            rubric = assemble_rubric_scores(rubric_models)

            profile2 = Profile2(
                profile_id=profile.profile_id,
                application_id=application.application_id,
                applicant_name=f"{application.candidate_first_name} {application.candidate_last_name}",
                applicant_email=application.candidate_email,
                linkedin_url=application.linkedin,
                portfolio_url=application.portfolio,
                github_url=application.github,
                applicant_career=career_path,
                profile_score=overall,
                profile_bullets=bullets,
                profile_rubric=rubric,
                recent_roles=recent_roles
            )

            logger.debug("Built Profile2 profile_id=%s application_id=%s", profile2.profile_id, profile2.application_id)
            profiles.append(profile2)

        return profiles

    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to get Profile2 list for job_id %s", job_id)
        raise HTTPException(status_code=500, detail="Internal server error")

def get_profile2_by_application_id(application_id: UUID, db: Session) -> Profile2:
    try:
        # Get main profile, app, bullets, and career path in one query
        stmt = (
            select(
                CandidateProfile,
                Application,
                CareerPath,
                CandidateProfileSummaryBullet.detail,
                CandidateProfileSummaryBullet.position,
                CandidateProfileSummaryBullet.type,
                RecentRoleModel
            )
            .join(Application, CandidateProfile.application_id == Application.application_id)
            .join(CareerPath, CandidateProfile.profile_id == CareerPath.profile_id)
            .join(CandidateProfileSummaryBullet, CandidateProfile.profile_id == CandidateProfileSummaryBullet.profile_id)
            .outerjoin(RecentRoleModel, RecentRoleModel.application_id == Application.application_id)
            .where(Application.application_id == application_id)
        )

        rows = db.execute(stmt).all()

        if not rows:
            raise HTTPException(status_code=404, detail="No profile found")

        first_row = rows[0]
        profile = first_row.CandidateProfile
        application = first_row.Application
        career = first_row.CareerPath

        # Use helpers to build components
        bullets = assemble_profile_bullets(rows)
        overall = assemble_profile_score(profile)
        career_path = assemble_career_path(career)
        recent_roles = assemble_recent_roles(rows)

        # Fetch rubric scores separately
        rubric_stmt = (
            select(CandidateProfileCategoryScore)
            .where(CandidateProfileCategoryScore.profile_id == profile.profile_id)
        )
        rubric_rows = db.execute(rubric_stmt).scalars().all()
        rubric = assemble_rubric_scores(rubric_rows)

        return_profile = Profile2(
            profile_id=profile.profile_id,
            application_id=application.application_id,
            applicant_name=f"{application.candidate_first_name} {application.candidate_last_name}",
            applicant_email=application.candidate_email,
            linkedin_url=application.linkedin,
            portfolio_url=application.portfolio,
            github_url=application.github,
            applicant_career=career_path,
            profile_score=overall,
            profile_bullets=bullets,
            profile_rubric=rubric,
            recent_roles=recent_roles
        )

        logger.info(
            "Profile found profile_id=%s application_id=%s",
            return_profile.profile_id,
            return_profile.application_id,
        )

        return return_profile

    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to get Profile2 for application_id %s", application_id)
        raise HTTPException(status_code=500, detail="Internal server error")

def assemble_profile_bullets(rows) -> ProfileBullets:
    liked = []
    disliked = []
    seen = set()  # (type, position, detail)

    for row in rows:
        key = (row.type, row.position, row.detail)
        if key in seen:
            continue
        seen.add(key)

        bullet = ProfileSummaryBullet(order=row.position, detail=row.detail)

        if row.type == "strength":
            liked.append(bullet)
        elif row.type == "weakness":
            disliked.append(bullet)

    return ProfileBullets(liked_bullets=liked, disliked_bullets=disliked)

def assemble_profile_score(row) -> ProfileOverallScore:
    return ProfileOverallScore(
        profile_score=row.overall_score,
        headline=row.summary
    )

def assemble_career_path(row) -> ProfileCareerPath:
    return ProfileCareerPath(
        years_of_experience=row.years_of_experience,
        average_tenure=row.average_tenure,
        number_promotions=row.number_promotions,
        most_recent_role=RoleSummary(
            title=row.most_recent_title,
            company=row.most_recent_company,
            tenure=row.most_recent_tenure
        ),
        longest_tenured_role=RoleSummary(
            title=row.longest_title,
            company=row.longest_company,
            tenure=row.longest_tenure
        ),
    )


def assemble_recent_roles(rows) -> List[RecentRoleSchema]:
    roles: List[RecentRoleSchema] = []
    seen_ids = set()  # avoid duplicates from joins

    for row in rows:

        orm_role = row.RecentRole # NOTE: this must match the ORM class name, not your alias

        if orm_role is None:
            continue

        if orm_role.id in seen_ids:
            continue
        seen_ids.add(orm_role.id)

        role = RecentRoleSchema(
            id=orm_role.id,
            application_id=orm_role.application_id,
            title=orm_role.title,
            organization=orm_role.organization,
            recency=orm_role.recency,
            end_date=orm_role.end_date,
            start_date=orm_role.start_date,
        )
        roles.append(role)

    roles.sort(key=lambda r: r.recency)
    return roles

def assemble_rubric_scores(rows) -> ProfileRubric:
    return ProfileRubric(category_scores=[
        ProfileCategoryScore(
            category_id=row.category_id,
            category_score=row.score,
            category_score_reason=row.reasoning
        ) for row in rows
    ])