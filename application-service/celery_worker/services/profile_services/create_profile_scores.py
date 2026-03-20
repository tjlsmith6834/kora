import os
import logging
from sqlalchemy.orm import Session
from openai import OpenAI
from pydantic import BaseModel
import asyncio
from typing import List, Tuple
from uuid import UUID

from ..embedding_services.application_index import generate_application_faiss_index
from ..application_analysis_services.analyze_application import analyze_application
from ...utils.retrieve_rubrics import get_application_rubric_context
from ...utils.text_from_file_utils import extract_text_from_txt

from common.models_schemas.schemas.application_analysis import ApplicationAnalysisIn2
from common.models_schemas.schemas.profiles import ProfileCategoryScore, ProfileRubric, ProfileOverallScore
from common.models_schemas.schemas.rubric import Rubric
from common.models_schemas.schemas.application_analysis import ApplicationAnalysisCategory2
from common.models_schemas.schemas.rubric import RubricCategory

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

class CategoryScore(BaseModel):
    category_score: int
    category_score_reason: str

async def create_profile_scores(application_id: UUID, db_session: Session) -> Tuple[ProfileRubric, ProfileOverallScore]:
   """Get Metadata"""
   index, metadata = await generate_application_faiss_index(application_id, db_session)
   job_id, rubric, focus_embeddings, criteria_embeddings = await get_application_rubric_context(application_id, db_session)

   """analyze application"""
   application_analysis: ApplicationAnalysisIn2 = await analyze_application(index, metadata, application_id, db_session, rubric, focus_embeddings, criteria_embeddings)

   """score categories"""
   scored_categories = await run_all_category_scores(rubric, application_analysis)
   logging.info(f"Scored category: {scored_categories}")

   """score profile"""
   profile_rubric = ProfileRubric(
       category_scores=scored_categories
   )

   overall_score = await create_profile_overall_score(profile_rubric, rubric)

   return profile_rubric, overall_score

async def run_all_category_scores(
    rubric: Rubric,
    analysis: ApplicationAnalysisIn2
) -> List[ProfileCategoryScore]:
    analysis_by_category_id = {
        c.category_id: c for c in analysis.category_analyses
    }

    tasks = []

    for rubric_category in rubric.categories:
        candidate_data = analysis_by_category_id.get(rubric_category.category_id)
        if candidate_data is None:
            continue

        # Use create_profile_category_score to get the right return type
        tasks.append(
            create_profile_category_score(rubric_category, candidate_data)
        )

    return await asyncio.gather(*tasks)

async def calculate_category_score(category_data: RubricCategory, candidate_data: ApplicationAnalysisCategory2) -> CategoryScore:

    mental_model = extract_text_from_txt(
        os.path.join(PROJECT_ROOT, "prompts/grading_services/rubber_bands.txt")
    )

    category = category_data.category
    focus = category_data.focus
    criteria = category_data.criteria

    candidate_analysis = candidate_data.annotations_with_scores.model_dump()

    messages = [
        {
            "role": "system",
            "content": (
                f"###Objective:\n"
                f"You are a precise and judicious hiring manager. You will create an evidence-based ranking of how strong of a fit a candidate is for a given category of requirements for a job.\n\n"
                f"###Input:\n"
                f"Category Data: You will receive a category from a grading rubric along with a focus and criteria displaying what is needed from the candidate.\n"
                f"Candidate Analysis: You will receive an annotated list of strengths and gaps from a candidate's application for a role.\n\n"
                f"###Instructions:\n"
                f"1) Review the Category Data to determine what is needed of the candidate.\n"
                f"2) Review the Candidate Analysis to understand the capabilities and gaps of the candidate.\n"
                f"3) Using the high-level scoring rules, formulate a score 1-3 for how strong of a fit the candidate is for the role; 3 being the best fit and 1 being the worst.\n."
                f"3) Using the rubber bands and weights mental model below (below) adjust your 1-3 score to a scale of 1-10. Candidates score as a 3 should have a score 9-10, candidates with a score of 2 should have a score 6-8, and candidates with a score of 1 should have a score 0-5"
                f"4) Provide a brief explanation of the strengths and gaps influenced it.\n\n"
                f"##High Level Scoring Rules:\n"
                f"Consider any explicitly nice-to-have (ex: described as 'bonus' 'nice-to-have' 'preferred') only as items that can increase the score for a candidate\n"
                f"Consider any explicitly must-have criteria (ex: described as 'must have,' 'necessary,' 'required' etc) as hard blockers\n"
                f"Assign a score of 1 to the category if ANY explicitly must-have criteria are missing.\n"
                f"Assign a score of 1 to the category if <50% of criteria (excluding nice-to-have's) are met.\n"
                f"Assign a score of 1 to the category of 1 if the candidate overall does not seem capable of meeting the 'focus' question of the category.\n"
                f"Assign a score of 2 to the category if all explicitly must-have criteria are met, >50% of criteria (excluding nice-to-have's) are met, but you have any overarching doubts about the candidate's ability to fulfill the 'focus' question of the category.\n"
                f"Assign a score of 3 to the category if all explicitly must-have criteria are met, >50% of more of all criteria are met, and you believe the candidate is well suited to fulfill the 'focus of the category.\n"
                f"### Mental Model: Rubber Bands and Weights:\n"
                f"{mental_model}\n\n"
                "###Important Rules:\n"
                "1. **Use Only Explicit Evidence provided with the candidate data** - Do NOT assume gaps or strengths beyond what is explicitly stated.\n"
                "2. **Do not mention scores or mental model in explanation** - Only reference the candidate analysis and the category data.\n"
                "3. **Score must be an integer 1-10** - Your score must be an integer between 1 and 10.\n"
            )
        },
        {
            "role": "user",
            "content": (
                f"###Category Data:\n"
                f"Reminder: Score the candidate against these job requirements\n"
                f"Category: {category}\n"
                f"Focus: {focus}\n\n"
                f"Criteria:\n{', '.join(criteria)}\n\n"
                f"###Candidate Analysis:\n"
                f"Reminder: This is the list of strengths and gaps for the candidate you are scoring:\n"
                f"{candidate_analysis}\n\n"

            )
        }
    ]

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            response_format=CategoryScore,
            temperature=0.0,
        )

        category_score = response.choices[0].message.parsed

        logging.info(f"Scored category for {category}: {category}")

        return category_score

    except Exception as e:
        logging.error(f"❌ Error generating category score for {category}: {e}")
        category.category_score = 0
        category.category_score_reason = "Failed to generate score."

async def create_profile_category_score(category_data: RubricCategory, candidate_data: ApplicationAnalysisCategory2) -> ProfileCategoryScore:
    category_score = await calculate_category_score(category_data, candidate_data)
    profile_category_score = ProfileCategoryScore(
        category_id = category_data.category_id,
        category_score = category_score.category_score,
        category_score_reason = category_score.category_score_reason,
    )

    return profile_category_score

async def create_profile_overall_score(profile_category_scores: ProfileRubric, rubric: Rubric) -> ProfileOverallScore:

        weight_lookup = {cat.category_id: cat.weight for cat in rubric.categories}

        weighted_sum = 0.0
        total_weight = 0.0

        raw_scores = []

        for category_score in profile_category_scores.category_scores:
            score = category_score.category_score
            raw_scores.append(score)

            weight = weight_lookup.get(category_score.category_id, 0)
            weighted_sum += score * weight
            total_weight += weight

        if not raw_scores:
            normalized = 0  # No scores to average

        if total_weight > 0:
            normalized = (weighted_sum / (total_weight * 10)) * 100
        else:
            # Fallback to simple average rebased to 0–100
            normalized = (sum(raw_scores) / (len(raw_scores) * 10)) * 100

        score = round(normalized)

        headline = await create_profile_score_summary(profile_category_scores, score)

        overall_score = ProfileOverallScore(
            profile_score=score,
            headline=headline,
        )

        return overall_score

async def create_profile_score_summary(profile_rubric: ProfileRubric, applicant_score: int) -> str:
    profile_rubric_string = profile_rubric.model_dump()

    messages = [
        {
            "role": "system",
            "content": (
                f"###Objective:\n"
                f"You are an expert hiring evaluator. Your task is to generate a structured interpretation of an applicant's overall fit for a role based on their strengths, gaps, and the final score.\n\n"
                f"###Inputs:\n"
                f"Applicant Score: A number 0-100 defining how strong of a fit the candidate is for the role. Higher is better."
                f"Profile Rubric: A categorized summary of the strengths and weaknesses in the candidate's application for the role."
                f"###Instructions:\n"
                f"Review the applicant's overall score.\n"
                f"Write an ultra-concise headline to describe the candidate with respect to their fit for the role."
                f"If the score is 85 or above, describe what makes them stand out.\n"
                f"If the score is between 65 and 85, describe the tradeoff of the candidate.\n"
                f"If the score is 65 or below, describe why the candidate is not a good fit.\n\n"
                f"###Examples:\n"
                f"For a score 85+: Excellent fit. Shows particular acumen in systems architecture.\n"
                f"For a score 85+: Strong fit. Full alignment with all role needs.\n"
                f"For a score 66-84: Good fit. Strong managerial experience but has not worked in a startup environment.\n"
                f"For a score 66-84: Average fit. Strong experience in account management but has never worked in B2B software sales.\n"
                f"For a score 65-: Poor fit. Performant as an individual engineering contributor but has no managerial skill-set and has never worked on internet products.\n"
                f"For a score 65-: Poor fit. Some skills analogous to product design but no direct experience needed for role.\n"
                f"For a score 65+: Poor fit. No experiences which would directly enable candidate to succeed in role.\n"
                f"###Rules:\n"
                f"Summarize but do not embellish. Your headline should be directly supported by candidate data.\n"
                f"###Output Format:\n"
                f"Output a single string followed by a single period (.). Add no leading or additional trailing spaces or punctuation marks.\n"
            )
        },
        {
            "role": "user",
            "content": (
                f"### **Applicant Score:\n "
                f"Reminder: Use this to define the direction of your headline."
                f"{applicant_score}\n"
                f"###Profile Rubric:\n"
                f"Reminder: This is the categorized summary of the strengths and weaknesses in the candidate's application\n"
                f"{  profile_rubric_string}\n\n"
            )
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        headline = response.choices[0].message.content.strip()

        logging.info(f"Headline: {headline}")

        return headline

    except Exception as e:
        logging.error(f"❌ Error generating applicant score interpretation: {e}")
        return "Failed to generate interpretation."