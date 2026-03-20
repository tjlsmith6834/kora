import os
import asyncio
from openai import OpenAI
import numpy as np
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Literal
from uuid import UUID
import logging

from ..db_services.get_recent_roles_block import get_recent_roles_block

from common.models_schemas.models import Application
from common.models_schemas.schemas import Rubric, RubricCategory
from common.models_schemas.schemas.application_analysis import ApplicationAnalysisCategory2, ApplicationAnalysisIn2, ScoredApplicationAnnotationList

# Initialize the LLM client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Main Functions
async def analyze_application(
    application_faiss_index,
    application_metadata,
    application_id: UUID,
    db_session: Session,
    rubric: Rubric,
    focus_embeddings: List[np.ndarray],
    criteria_embeddings: List[np.ndarray]
) -> ApplicationAnalysisIn2:

    try:
        application = db_session.query(Application).get(application_id)

        career_path = get_recent_roles_block(application_id, db_session)

        tasks = [
            analyze_application_categories(
                rubric_category,
                application_faiss_index,
                application_metadata,
                focus_embeddings[i],
                criteria_embeddings[i],
                career_path
            )
            for i, rubric_category in enumerate(rubric.categories)
        ]

        analysis_results = await asyncio.gather(*tasks, return_exceptions=True)

        category_analysis_results = [
            result for result in analysis_results
            if isinstance(result, ApplicationAnalysisCategory2)
        ]

        application.application_status = "analyzed"
        db_session.add(application)
        db_session.commit()

        application_analysis = ApplicationAnalysisIn2(
            application_id=application_id,
            category_analyses=category_analysis_results,
        )

        logging.info(f"Application analysis: {application_analysis}")

        return application_analysis

    except Exception as e:
        logging.error(f"❌ Error in analyze_application2: {e}")
        raise

async def analyze_application_categories(
    category_data: RubricCategory,
    application_faiss_index,
    application_metadata,
    focus_embedding,
    criteria_embedding,
    career_path
) -> ApplicationAnalysisCategory2:

    try:
        # Step 1: Retrieve relevant application data from FAISS index
        distances_focus, indices_focus = application_faiss_index.search(focus_embedding.reshape(1, -1), 10)
        distances_criteria, indices_criteria = application_faiss_index.search(criteria_embedding.reshape(1, -1), 10)

        # Step 2: Merge unique indices
        all_indices = list(indices_focus[0]) + list(indices_criteria[0])
        unique_indices = list(set(all_indices))

        candidate_data = "\n".join([application_metadata[idx] for idx in unique_indices])


        # Step 3: Run async tasks for gap and strength analysis
        result = await annotate_category(category_data, candidate_data, career_path)

        logging.info(f"Category result: {result}")

        category_analysis = ApplicationAnalysisCategory2(
            category_id=category_data.category_id,
            category=category_data.category,
            annotations_with_scores=result
        )

        logging.info(f"Category analysis: {category_analysis}")

        return category_analysis

    except Exception as e:
        raise e


async def annotate_category(category_data: RubricCategory, candidate_data: str, career_path: str) -> ScoredApplicationAnnotationList:
    logging.info(f"Annotating category: {category_data.category}")

    category = category_data.category
    focus = category_data.focus
    criteria = category_data.criteria

    messages = [
        {
            "role": "system",
            "content": (
                f"###Objective:\n"
                f"Conduct an evidence-based assessment of a job candidate's strengths and weaknesses with respect to an assessment category for the job.\n"
                f"\n"

                f"###Instructions:\n"
                f"1. Review the job requirements (category, focus, criteria); understand the needs of the role with respect to the focus area and criteria.\n"
                f"2. Review the candidate data. For yourself, summarize the dataset into explicit actions the candidate has taken and hard/soft skills that they possess. Remove mentions of outcomes.\n"
                f"3. Consider only the actions and skills of the candidate (ignoring outcomes). List skills and actions (or lack thereof) that are relevant to the job requirements. Aim for thoroughness here.\n"
                f"4. Categorize your skills and actions into higher-level strengths and list them out.\n"
                f"5. Review where the candidate's strengths do not meet the needs of the role (either partially or entirely missed) and list those as weaknesses. Ensure that any criteria or potential need of the job that is lacking proper evidence has been listed as a weakness.\n"
                f"6. Assign alignment levels to the strengths and weaknesses. Back these up with a reason.\n"
                f"7. Check you work. Make sure your strengths and weaknesses are not contradictory (ideally they should be complementary). Also make sure your strengths and weaknesses are well aligned to all the information in the candidate data and the the role needs.\n"
                f"\n"

                f"### Evidence Guidelines:\n"
                f"- **Do not assume** modality, skill, or behavior based on generic terms (e.g., 'communicated', 'managed', 'oversaw'). These are only valid if paired with clear details.\n"
                f"- **Do not infer** experience or capability from job titles or seniority.\n"
                f"- **Only count actions explicitly stated** in the candidate data. If a skill or behavior is not directly evidenced in a bullet or sentence, do not credit it.\n"
                f"- Do no embellish at all.\n"
                f"\n"

                f"### Career Path Guidelines:"
                f"- You will be given a 'Career Path' section summarizing the candidate's roles with dates and tenure."
                f"- You MAY use the career path as EVIDENCE for: recency, tenure length, progression (e.g., promotions), stability vs. frequent moves, gaps, and domain continuity."
                f"- You MUST NOT infer skills from titles alone. Treat the career path as timeline evidence, not a source of unstated skills or outcomes."
                f"- Use the career path to calibrate alignment levels (e.g., recent and sustained experience in a matching domain may raise alignment; long gaps or only distant experience may lower it)."
                f"- When you reference it, cite the specific line(s) from the 'Career Path' section in your Evidence."

                f"###Skill Guidelines:\n"
                f"-When assessing skills, pay attention to the role the client was in. Ex: If a candidate increased sales of a product while working as an engineer, this is not evidence of sales experience; rather that they improved a product which indirectly increased sales.\n"
                f"-Generalize but be concrete. Ex: If a candidate show years of experience with Javascript and Python you could write 'Full-stack software development.'\n"
                f"-Aim for a atomicity to support a broader area. Ex: If you believe a candidate is is strong in 'leadership' understand and write if this was achieved through 'team building,' 'growing culture,' 'persuasive speaking' etc.\n"
                f"-Do not list more than one skill in a single strength. Ex: Do not write 'Uses statistical testing and user interviews to deliver outcomes.' Instead, break these into 'Quantitative data analysis' and 'Customer research.'\n"
                f"-Write skills such that they are completely exclusive of each other.\n"
                f"-Try to be as concise as possible. Ex: Instead of 'Leadership in team development' write as 'team development' or 'mentorship'"
                f"\n"

                f"###How to think about strengths:\n"
                f"Only list a strength if the candidate's actions or skills **explicitly** demonstrate a match to a job requirement.\n"
                f"For any given strength (as a categorized set of evidence) you should think about alignment level as follows:\n"
                f"Only consider the alignment of the strength to the needs of the role. Do not consider the importance of the need itself.\n"
                f"A strong fit (high alignment level) is one where the candidate's experience or skills align exactly with the needs of the role.\n"
                f"A medium fit (medium alignment level) is one where the actions in the candidate's application are aligned with the needs of the role but the specific skill-set is not perfectly aligned with the needs of the role.\n"
                f"A low fit (low alignment level) is one where the actions or skills of the candidate's application could be translated to the needs of the role but aren't directly aligned.\n"
                f"Example Strong Fit: [Role Need] Hire and develop high impact salespeople capable of meeting/exceeding sales quota | [Applicant Experience] Hired and managed a team of 6 sales associates which which met sales quotas for furniture vertical in three consecutive years.\n"
                f"Example Strong Fit: [Role Need] Excellent working knowledge of UI/UX design principles and software namely; Figma, Photoshop, Illustrator & wider Adobe Suite. | [Applicant Experience] Owned end-to-end design lifecycle for mobile app. Leveraged Figma and Illustrator to create prototypes and high-fidelity mocks.\n"
                f"Example Medium Fit: [Role Need] Project manage apartment turnovers, gut renovations, unit combinations, lobby, and corridor upgrades. | [Applicant Experience] Managed renovations of multiple office spaces including two full lobby guts renovations.\n"
                f"Example Medium Fit: [Role Need] Leverage Salesforce to maintain client relationships and develop new leads. | [Applicant Experience] Managed relationships with four clients using Zendesk.\n"
                f"Example Low Fit: [Role Need] Proficiency with the full web stack development inclusive of React and Ruby. | [Applicant Experience] Developed a complete mobile application for iOS using Swift programming language.\n"
                f"Example Low Fit: [Role Need] Experience with marketing analytics tools (Google Analytics, etc.). | [Applicant Experience] As a data analyst, Leveraged Looker and Tableau to create dashboards for a product team.\n"
                f"- **Do not inflate alignment level** based on how critical a skill is to the role. Alignment level measures alignment, not necessity.\n"
                f"\n"

                f"###How to think about weaknesses:\n"
                f"List a weakness if the candidate's skill set either partially or entirely **fails to meet** a job requirement.\n"
                f"Weaknesses should be considered in the sense of 'how far off' the candidate skills are from the requirements of the job.\n"
                f"Weaknesses should be complementary to strengths such that a reader of both strengths and weaknesses will fully understand the fit of a candidate to the role\n"
                f"When thinking about weakness *do* infer how well a candidate's experiences might translate to the role's needs even if the needs are not explicitly met"
                f"A strong weakness (high alignment level) is one where the candidate's experience or skills do not translate at all to the needs of the role.\n"
                f"A medium weakness (medium alignment level) is one where strengths of the candidate's application could be generally aligned to the needs of the role but aren't directly translatable.\n"
                f"A low weakness (low alignment level) is one where the actions or skills of the candidate's application could be translated to the needs of the role (ex: the candidate is missing a specific hard skill needed for the role but has high experience with a similar hard skill).\n"
                f"Example Strong Weakness: [Role Need] Experience in creating digital assets for social media posts and ad campaigns. | [Applicant Experience] Has no experiences in design whatsoever. Has not worked with digital assets either.\n"
                f"Example Strong Weakness: [Role Need] Ability to lead product research and design cycles with a high bar for UX and usability. | [Applicant Experience] Has never worked in the research for new products, only in implementation of existing plans. Has never done user or marketplace research. Does not show any evidence of implementing user experience concepts\n"
                f"Example Medium Weakness: [Role Need] Strong documentation skills with the ability to  translate technical solutions into customer-facing narratives. | [Applicant Experience] Has trained customers on how to use technical products but has not prepared documentation for those purposes. Uncertain technical writing ability.\n"
                f"Example Medium Weakness: [Role Need] Experience managing multi-year subscription renewals in long-term commercial relationships. | [Applicant Experience] Has maintained long-term relationships with customers in purchase-order based relationships where the customers would make regular purchases of good. Has not worked with a subscription-based model.\n"
                f"Example Low Weakness: [Role Need] Ability to use LinkedIn Recruiter, job boards, and Boolean searches to identify top candidates. | [Applicant Experience] Managed a successful recruiting pipeline for a startup. Has never used LinkedIn recruiter specifically but has used other talent acquisition tools and, in a previous role, has used client prospecting tools.\n"
                f"Example Low Weakness: [Role Need] Experience define the short, medium, and long term product roadmaps. | [Applicant Experience] Previously ran a startup showing ability to think strategically. Worked as a product manager for 10 years with multiple launches shown in experience so likely owned product roadmaps.\n"
                f"\n"

                f"###Output Format:\n"
                f"Return a list of structured annotations."
                f"For each item in your final list you should have:\n"
                f"Type: List whether you are about to describe a strength or weakness.\n"
                f"Comment: The high-level strength or weaknesses.\n"
                f"Evidence: List all evidence from the candidate data that support the strength or weakness.\n"
                f"Alignment Level: Define how aligned the strength or weaknesses is to the job requirements as 'high,' 'medium,' or 'low.' Consider the alignment of the evidence NOT the importance of the needs themselves."
                f"Alignment Reason: Why you think the strength or weakness alignment should receive the score you gave it."
                f"\n"
            )
        },
        {
            "role": "user",
            "content": (
                    f"###Candidate Data*\n"
                    f"Reminder: This is data from the candidate's application that you should search for strengths."
                    f"{candidate_data}\n"
                    f"\n"

                    f"### Career Path (most recent first)"
                    f"{career_path}\n"

            f"###Job Requirements:\n"
    f"Reminder: This is the focus area and associated criteria you are assessing the candidate against\n"
    f"Category: {category}\n"
    f"Focus Area: {focus}\n"
    f"Job Criteria:{criteria}"
    )
    }
    ]

    response = await asyncio.to_thread(
        client.beta.chat.completions.parse,
        model="gpt-4o",
        messages=messages,
        response_format=ScoredApplicationAnnotationList,
        temperature=0,
    )

    annotations = response.choices[0].message.parsed

    logging.info(annotations.model_dump())

    return annotations

