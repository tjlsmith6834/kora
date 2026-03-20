import os
from openai import OpenAI
from pydantic import BaseModel
from uuid import UUID
from sqlalchemy.orm import Session
import logging

from ...utils.text_from_file_utils import extract_text_from_file

from common.storage_retrieval_services.retrieve_docs import retrieve_primary_resume
from common.models_schemas.schemas.profiles import ProfileCareerPath

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def extract_and_store_career_path(application_id: UUID, db_session: Session) -> ProfileCareerPath:
    """Get resume"""
    resume_file = await retrieve_primary_resume(application_id, db_session)
    """Get resume text"""
    resume_text = extract_text_from_file(resume_file)
    """Extract career path"""
    career_path = await extract_career_path(resume_text)
    """Store career path"""
    return career_path

async def extract_career_path(resume_text: str)->ProfileCareerPath:
    messages = [
        {
            "role": "system",
            "content": (
                f"Objective: You are a detail oriented document-reader who will extract data points on a candidate's career path from their resume perfectly accurately.\n\n"

                f"###Input:\n"
                f"You will receive the full text of the applicant's resume as a single string from which you can extract all necessary information."
                
                f"###Instructions:\n"
                f"Read the applicant's resume and extract the following data points:\n"
                "years_of_experience: Rounded to the nearest integer, number of years of professional experience. Do not include education. Do not double-count concurrent experiences.\n"
                "most_recent_role: The most recent professional role for the candidate. For this role include: [Job Title] [Company name they worked for] [Years the candidate spent at the company for this role rounded to nearest integer].\n"
                "longest_tenured_role: The professional role where the candidate has spent the most time. For this role include: [Job Title] [Company name they worked for] [Years the candidate spent at the company for this role rounded to nearest integer].\n"
                "average_tenure: The average tenure in years across all professional roles rounded to the nearest integer\n"
                "number_promotions: The count of all promotions in the candidate's resume. Include cases where the candidate stayed at the same company and looks like their position increased in value.\n\n"

                f"###Output format:\n"
                f"Strictly adhere to the object model for ProfileCareerPath. Do no include beginning or trailing spaces or punctuation.\n"
            )
        },
        {
            "role": "user",
            "content": (
                f"###Resume:\n"
                f"{resume_text}"
            )
        }
    ]

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            response_format=ProfileCareerPath,
            temperature=0.0,
        )

        career_path = response.choices[0].message.parsed

        logging.info(f"Career Path: {career_path}")

        return career_path
    except Exception as e:
        raise

