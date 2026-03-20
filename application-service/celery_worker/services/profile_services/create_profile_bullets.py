import os
from openai import OpenAI
from pydantic import BaseModel
import logging
from typing import List

from celery_worker.services.sensitivity_services import filter_sensitive_entries

from common.models_schemas.schemas.profiles import ProfileRubric, ProfileBullets

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ScoreBulletGPT(BaseModel):
    order: int
    detail: str

class BulletListGPT(BaseModel):
    bullets: List[ScoreBulletGPT]

async def generate_profile_bullets(profile_rubric: ProfileRubric) -> ProfileBullets:

    messages = [
        {
            "role": "system",
            "content": (
                f"Objective:\n"
                f"You are tasked with listing the most important strengths and weaknesses for a candidate for a role.\n\n"
                
                f"###Instructions:\n"
                f"From the context provided, extract the 3 most important strengths and the 3 most important weaknesses for the candidate. \n"
                f"List the strengths and the weaknesses separately as ordered bullets (most important to least important)\n"
                
                f"###Output Guidelines:\n"
                f"Provide a list of bullets representing the most 3 most important strengths and the 3 most important weaknesses for the candidate.\n"
                f"For each bullet provide:"
                f"order: The ordering of the bullet in your list bullets in terms of importance (1 being most important).\n"
                f"detail: The attribute of the candidate you are trying to highlight.\n\n"
                
                "###Important Rules:**\n"
                f"- Each bullet should be limited to 1-2 sentences.\n"
                f"- Your bullet should be clearly supported by the context provided.\n"
                f"- Write in generalization that summarize the the candidate's attributes. Do not list specific items from the context."
                f"- You may combine strengths or weaknesses from the context to create an overarching bullet to highlight but do not make up new information.\n"
                f"- You may simplify verbiage from the context for brevity.\n"
                f"- Be as concise as possible. Avoid adverbs, terms with similar meaning, and trailing sentences/phrases.\n"
                f"- All bullets should be completely exclusive of each other.\n"
                f"- Focus on candidate attributes, not the evidence behind it. Ex: Instead of 'Strong strategic thinking and data analysis skills, demonstrated through the ability to develop insights and translate them into effective business strategies.' just write 'Strong strategic thinking and data analysis skills'"
                f"- Focus on candidate attributes, not outcomes. Ex: Instead of 'Ability to align stakeholders and implement go-to-market strategies, driving significant sales growth.' just write 'Ability to align stakeholders and implement go-to-market strategies'"
                f"- Do not reference the job requirements directly. Ex: Instead of 'Missing specific experience in recruiting, onboarding, and developing a sales team, which is critical for the role.' just write 'Missing specific experience in recruiting, onboarding, and developing a sales team'"
                f"- Do not reference the applicant either indirectly or via their name. Ex: Instead of 'The application does not mention experience in monitoring sales activities' just write 'No experience in monitoring sales activities.'"
                f"- Do not embellish at all.\n"
            )
        },
        {
            "role": "user",
            "content": (
                f"### Context:\n"
                f"Reminder: This is the full analysis of a candidate from which you should extract important bullets\n"
                f"{profile_rubric}\n"
            )
        }
    ]

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            response_format=ProfileBullets,
        )

        bullet_data: ProfileBullets = response.choices[0].message.parsed

        # Update category object in place
        bullet_data.liked_bullets = await filter_sensitive_entries(bullet_data.liked_bullets)
        bullet_data.disliked_bullets = await filter_sensitive_entries(bullet_data.disliked_bullets)

    except Exception as e:
        logging.error(f"❌ Error generating bullets: {e}")
        raise e

    logging.info(f"Created bullets: {bullet_data}")

    return bullet_data