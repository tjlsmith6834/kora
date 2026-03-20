import os
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from datetime import date
from uuid import UUID
from sqlalchemy.orm import Session
import logging

from ...utils.text_from_file_utils import extract_text_from_file

from common.storage_retrieval_services.retrieve_docs import retrieve_primary_resume
from common.models_schemas.schemas.profiles import RecentRole

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GptRoles(BaseModel):
    roles: List[RecentRole]

async def find_extract_recent_roles(application_id: UUID, db_session: Session) -> List[RecentRole]:
    """Get resume"""
    resume_file = await retrieve_primary_resume(application_id, db_session)
    """Get resume text"""
    resume_text = extract_text_from_file(resume_file)
    """Extract career path"""
    career_path = await extract_recent_roles(resume_text)
    """Store career path"""
    return career_path


async def extract_recent_roles(resume_text: str) -> List[RecentRole]:
    def five_years_ago_month_start(today: date | None = None) -> date:
        if today is None:
            today = date.today()
        # Same month, same day (or set to 1), minus 5 years
        return date(today.year - 5, today.month, 1)

    cutoff_date = five_years_ago_month_start()  # e.g. 2020-11-01 right now
    cutoff_label = cutoff_date.strftime("%B %Y")

    messages = [
        {
            "role": "system",
            "content": (
                f"Objective: You are a detail oriented document-reader who will extract professional roles that occurred before {cutoff_label} from a candidate's resume perfectly accurately.\n\n"

                f"###Input:\n"
                f"You will receive the full text of the applicant's resume as a single string from which you can extract all necessary information."

                f"###Instructions:\n"
                f"Read the applicant's resume and extract the following data points for the five most recent years of professional roles. Ignore any role that ended before {cutoff_label}. Do not include education or non-professional roles (if there are fewer than five years of professional roles in the application, capture all the professional roles they have worked in):\n"
                f"title: The job title the candidate carried.\n"
                f"organization: The company the candidate was working at.\n"
                f"recency: The stack rank order that this role is in terms of recency. Use 0 for the most recent role then ascend.\n"
                f"end_date: The date that the role ended. If the role is still ongoing ('present' end date) mark this null. If month and year but no end day is provided assume the first of the month.\n"
                f"start_date: The date that the role started. If month and year but no start day is provided assume the first of the month.\n\n"
                f"Check your work. Discard any roles with an end date before {cutoff_label}. Use precision to the current month."

                f"###Output format:\n"
                f"Strictly provide a GptRoles object.\n"
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
            response_format=GptRoles,
            temperature=0.0,
        )

        career_path = response.choices[0].message.parsed

        logging.info(f"Career Path: {career_path}")

        return career_path.roles

    except Exception as e:
        raise

