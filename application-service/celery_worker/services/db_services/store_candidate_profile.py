from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4, UUID
import logging

from common.models_schemas.models.profile import CandidateProfile, CandidateProfileCategoryScore, CandidateProfileSummaryBullet, CareerPath
from common.models_schemas.schemas.profiles import ProfileOverallScore, ProfileRubric, ProfileBullets, ProfileCareerPath

async def store_candidate_profile(
        application_id: UUID,
        overall_score: ProfileOverallScore,
        profile_rubric: ProfileRubric,
        profile_bullets: ProfileBullets,
        career_path: ProfileCareerPath,
        db_session: Session):
    try:
        logging.info(f"Storing profile for application_id: {application_id}")

        # Get the profile(s) being deleted
        profile_ids = db_session.query(CandidateProfile.profile_id).filter(
            CandidateProfile.application_id == application_id
        ).all()

        # Flatten list of tuples to list of UUIDs
        profile_ids = [pid for (pid,) in profile_ids]

        # Delete dependent category scores
        db_session.query(CandidateProfileCategoryScore).filter(
            CandidateProfileCategoryScore.profile_id.in_(profile_ids)
        ).delete(synchronize_session=False)

        db_session.query(CandidateProfileSummaryBullet).filter(
            CandidateProfileSummaryBullet.profile_id.in_(profile_ids)
        ).delete(synchronize_session=False)

        db_session.query(CareerPath).filter(
            CareerPath.profile_id.in_(profile_ids)
        ).delete(synchronize_session=False)

        # Now delete the profiles
        db_session.query(CandidateProfile).filter(
            CandidateProfile.application_id == application_id
        ).delete(synchronize_session=False)

        # Step 1: Create and insert CandidateProfile record
        candidate_profile = CandidateProfile(
            profile_id=uuid4(),
            application_id=application_id,
            overall_score=overall_score.profile_score,
            summary=overall_score.headline
        )
        db_session.add(candidate_profile)
        db_session.flush()

        # Step 2: Insert CandidateProfileCategoryScore records
        category_scores = []
        for profile_score in profile_rubric.category_scores:
            category_score = CandidateProfileCategoryScore(
                category_score_id=uuid4(),
                profile_id=candidate_profile.profile_id,
                category_id=profile_score.category_id,
                score=profile_score.category_score,
                reasoning=profile_score.category_score_reason
            )
            category_scores.append(category_score)

        db_session.add_all(category_scores)

        # Step 3: Insert CandidateProfileSummaryBullet records
        summary_bullets = []

        for bullet_type, bullets in [("strength", profile_bullets.liked_bullets), ("weakness", profile_bullets.disliked_bullets)]:
            for bullet in bullets:
                summary_bullets.append(CandidateProfileSummaryBullet(
                    bullet_id=uuid4(),
                    profile_id=candidate_profile.profile_id,
                    type=bullet_type,
                    position=bullet.order,
                    detail=bullet.detail,
                ))

        db_session.add_all(summary_bullets)

        career_path_record = CareerPath(
            id=uuid4(),
            profile_id=candidate_profile.profile_id,
            years_of_experience=career_path.years_of_experience,
            average_tenure=career_path.average_tenure,
            number_promotions=career_path.number_promotions,
            most_recent_title=career_path.most_recent_role.title,
            most_recent_company=career_path.most_recent_role.company,
            most_recent_tenure=career_path.most_recent_role.tenure,
            longest_title=career_path.longest_tenured_role.title,
            longest_company=career_path.longest_tenured_role.company,
            longest_tenure=career_path.longest_tenured_role.tenure
        )
        db_session.add(career_path_record)
        db_session.flush()

        # Step 3: Commit the transaction
        db_session.commit()
        logging.info(f"✅ Successfully stored candidate profile for application_id: {application_id}")

    except SQLAlchemyError as e:
        db_session.rollback()
        logging.error(f"❌ Database error while storing analysis results: {str(e)}")
        raise

    except Exception as e:
        db_session.rollback()
        logging.error(f"❌ Unexpected error: {str(e)}")
        raise