import os
import logging
from openai import OpenAI

from common.models_schemas.schemas import Rubric
from common.models_schemas.schemas.application_analysis import ApplicationAnalysisIn2
from common.models_schemas.schemas.survey import Survey

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def write_open_questions2(application_analysis: ApplicationAnalysisIn2, rubric: Rubric) -> Survey:

    application_string = application_analysis.model_dump_json(indent=2)
    rubric_string = rubric.model_dump_json(indent=2)

    messages = [
        {
            "role": "system",
            "content": (
                f"###Task\n"
                f"You are tasked with writing three interview questions that will most help a job candidate show that they are a fit for a role.\n\n"

                f"### Input\n"
                f"You will receive a structured input with:"
                f"`Job Context`: A structured rubric of categorized needs for a role. Each category will contain a focus area, criteria, an importance weight (higher is more important)."
                f"`Candidate Analysis`: A summary of evidence of strengths and gaps in a candidate's application for a role."
                
                f"###Instructions\n"
                f"1. Review the job context (categories, focuses, criteria, and relative weights). Make sure you fully understand the needs of the role.\n"
                f"2. Review the candidate analysis. In your own mind, create a list where the candidate has not shown sufficient evidence of fit for the role.\n"
                f"3. For each of the items in your list of missing areas, write a single interview question which, if answered well, would give you confidence that the candidate is a good fit for the role.\n"
                f"4. Organize the list of questions by most important to least important (the most important question should be that which if answered well would most affect the candidate's fit for the role).\n"
                f"5. Select only the three most important questions and return them.\n\n"
                
                f"###Question Guidelines\n"
                f"Your question should probe into the candidate's experience so that they can provide evidence that will fill in the gap in their application\n"
                f"Ensure your question entices the candidate to answer with an open response vs a one-word answer but do not make explicit requests for answer length.\n"
                f"Ensure your question asks for a specific example of the candidate’s past experience, focusing on outcomes, decisions, or actions taken.\n"
                f"Questions should prompt the candidate to share detailed stories or scenarios that illustrate their qualifications.\n"
                f"Questions should be short and concise, ideally limited to 1 sentence.\n\n"

                f"### **Output Format**:\n"
                f"Return a exactly three interview questions as a list of plain text strings without any quotes, code fences, or additional markers.\n\n"
            )
        },
        {
            "role": "user",
            "content": (
                f"###Job Context:\n"
                f"Reminder: A structured rubric of categorized needs for the role.\n"
                f"Category: {rubric_string}\n\n"
                f"###Candidate Analysis\n"
                f"Reminder:  A summary of evidence of strengths and gaps in a candidate's application."
                f"{application_string}\n\n"

            )
        }
    ]

    # ✅ Request structured response
    response = client.beta.chat.completions.parse(
        model="gpt-4o",  # Ensure you're using the latest GPT-4o model
        messages=messages,
        response_format=Survey,
        temperature=0.2,
    )

    survey = response.choices[0].message.parsed

    logging.info(survey.model_dump())

    return survey


async def write_open_questions3(application_text: str, rubric: Rubric) -> Survey:
    rubric_string = rubric.model_dump_json(indent=2)

    messages = [
        {
            "role": "system",
            "content": (
                f"###Task\n"
                f"You are tasked with writing three interview questions that will most help a job candidate show that they are a fit for a role.\n\n"

                f"### Input\n"
                f"You will receive a structured input with:"
                f"`Job Context`: A structured rubric of categorized needs for a role. Each category will contain a focus area, criteria, an importance weight (higher is more important)."
                f"`Candidate Application`: The candidate's application for the role."

                f"###Instructions\n"
                f"1. Review the job context (categories, focuses, criteria, and relative weights). Make sure you fully understand the needs of the role.\n"
                f"2. Review the candidate application. In your own mind, create a list where the candidate has not shown sufficient evidence of fit for the role.\n"
                f"3. For each of the items in your list of missing areas, write a single interview question which, if answered well, would give you confidence that the candidate is a good fit for the role.\n"
                f"4. Organize the list of questions by most important to least important (the most important question should be that which if answered well would most affect the candidate's fit for the role).\n"
                f"5. Select only the three most important questions and return them.\n\n"

                f"###Question Guidelines\n"
                f"Your question should probe into the candidate's experience so that they can provide evidence that will fill in the gap in their application\n"
                f"Ensure your question entices the candidate to answer with an open response vs a one-word answer but do not make explicit requests for answer length.\n"
                f"Ensure your question asks for a specific example of the candidate’s past experience, focusing on outcomes, decisions, or actions taken.\n"
                f"Questions should prompt the candidate to share detailed stories or scenarios that illustrate their qualifications.\n"
                f"Questions should be short and concise, ideally limited to 1 sentence.\n\n"

                f"### **Output Format**:\n"
                f"Return a exactly three interview questions as a list of plain text strings without any quotes, code fences, or additional markers.\n\n"
            )
        },
        {
            "role": "user",
            "content": (
                f"###Job Context:\n"
                f"Reminder: A structured rubric of categorized needs for the role.\n"
                f"Category: {rubric_string}\n\n"
                f"###Candidate Application\n"
                f"Reminder:  This is the candidate's application."
                f"{application_text}\n\n"

            )
        }
    ]

    # ✅ Request structured response
    response = client.beta.chat.completions.parse(
        model="gpt-4o",  # Ensure you're using the latest GPT-4o model
        messages=messages,
        response_format=Survey,
        temperature=0.2,
    )

    survey = response.choices[0].message.parsed

    logging.info(survey.model_dump())

    return survey
