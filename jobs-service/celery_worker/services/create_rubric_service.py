import os
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict
import logging

from .sensitivity_service import filter_sensitive_entries

from common.models_schemas.schemas import RubricCategoryIn, RubricIn

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RubricCriteriaGPT(BaseModel):
    criteria: List[str]
    failure_reason: Optional[str] = None

class RubricCategoryGPT(BaseModel):
    category: str
    focus: str
    criteria: List[str]

class RubricCategoryListGPT(BaseModel):
    categories: List[RubricCategoryGPT]
    failure_reason: Optional[str] = None

class RubricCategoryWeightGPT(BaseModel):
    category: str
    weight: int

class RubricCategoryWeightsListGPT(BaseModel):
    categories: List[RubricCategoryWeightGPT]


#Main Functions
async def create_rubric(job_description: str, hiring_manager_voiceover: Optional[str] = None) -> RubricIn:
    try:
        criteria = await extract_criteria(job_description, hiring_manager_voiceover)
        categorized_criteria = await categorize_criteria(criteria)
        weights = await assign_weights(job_description, categorized_criteria, hiring_manager_voiceover)
        rubric = await rebase_combine_weights_and_categories(weights, categorized_criteria)
        return rubric

    except Exception as e:
        raise ValueError(f"Error creating rubric: {e}")

#Helper Functions
async def extract_criteria(job_description: str, hiring_manager_voiceover: Optional[str] = None) -> RubricCriteriaGPT:

        messages = [
            {
                "role": "system",
                "content": (
                    f"###Task\n"
                    f"Objective: You are tasked with finding all necessary criteria for evaluating a job applicant.\n\n"
                    
                    f"###Instructions for extracting criteria:\n"
                    f"You will be provided with context describing a job and the requirements for a candidate applying to the job (ex: job description, hiring manager voiceover, etc.).\n"
                    f"Review all job context fist.\n"
                    f"List all criteria you believe a candidate should meet in order to be successful at the job.\n\n"

                    f"###Criteria Guidelines\n"
                    f"Provide a comprehensive list of criteria.\n"
                    f"Include technical skills, qualifications, experience, mindset, situational requirements, and cultural fit.\n"
                    f"Go beyond explicitly stated requirements by identifying implicit traits or abilities that are likely to be valuable for success in the role.\n"
                    f"Where possible be concrete in the requirements needed for the candidate.\n"
                    f"Be granular. When possible, break topics into multiple criteria highlighting different aspects of the job's needs.\n\n"
                    
                    f"### Output format instructions:\n"
                    f"Return a Pydantic object strictly adhering to the predefined schema. If no critera can be extracted, include a 'failure_reason' field explaining why."
                )
            },
            {
                "role": "user",
                "content": (
                    f"###Job Context:\n"
                    f"Reminder: Extract criteria for evaluating a job applicant from the items below.\n"
                    f"Job Description: {job_description}\n"
                    f"Hiring Manager Voiceover:\n{hiring_manager_voiceover or '<none>'}\n\n"
                )
            }
        ]

        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=messages,
                response_format=RubricCriteriaGPT,
            )

            extracted_criteria: RubricCriteriaGPT = response.choices[0].message.parsed
            extracted_criteria.criteria = await filter_sensitive_entries(extracted_criteria.criteria)

            logging.info(f"Extracted criteria: {extracted_criteria}")

            return extracted_criteria

        except ValidationError as ve:
            logging.error("Schema validation failed: %s", ve)
            raise ValidationError("Schema validation failed") from ve

        except Exception as e:
            logging.error(f"Error extracting criteria: {e}")
            raise RuntimeError("Could not extract rubric criteria") from e

# Helper Functions
async def categorize_criteria(rubric_criteria: RubricCriteriaGPT) -> RubricCategoryListGPT:

    messages = [
        {
            "role": "system",
            "content": (
                f"###Task\n"
                f"Objective: You are tasked with organizing the job criteria into **3-7 distinct, competency-focused categories and describing the focus of that category.\n\n"

                f"###Instructions for categorizing criteria:\n"
                f"You will be provided with a list of criteria for evaluating a job candidate.\n"
                f"Review all criteria first.\n"
                f"Organize criteria into 3-7 distinct distinct categories that represent the overarching themes that the criteria represent.\n"
                f"Assign a focus to each category; a short sentence describing what the category and criteria are looking for "
                

                f"###Category Guidelines\n"
                f"Each category must represent a unique competency or skill area (e.g., Strategic Thinking, Collaboration, Adaptability, Leadership, Technical Skills).\n"
                f"Group multiple related criteria into each category. Summarize the criteria as part of the category description."
                f"Avoiding creating categories with only one criterion.  Do not create separate categories for individual criteria unless absolutely necessary.\n"
                f"Categories should focus on broader competencies and behaviors, such as problem-solving, leadership, collaboration, or industry knowledge.\n"
                f"Avoid categories that are generalizations vs competency/skill areas (ex: DO NOT use 'education,' 'experience,' 'skills,' etc as categories)\n"
                f"Ensure all provided criteria are included in the categories.\n\n"
                
                f"###Focus Guidelines\n"
                f"The focus should combine and synthesize all the criteria under the category into a single high-level idea.\n"
                f"Do not repeat or explicitly restate the criteria. Instead, distill the common themes into a broader purpose or evaluation goal."
                f"Make the focus actionable, describing **what to look for** when evaluating a job candidate against the criteria."
                
                f'###Example\n'
                f"- Criteria (Input): 'Strong analytical skills', 'Ability to use data for strategic decision-making', 'Experience with financial modeling'\n"
                f"- Category (Output: 'Analytics'\n"
                f"- Focus (Output): 'Evaluate the candidate's ability to leverage analytical skills and data-driven insights for effective decision-making.\n\n"

                f"### Output format instructions:\n"
                f"Return a Pydantic object strictly adhering to the predefined schema. If no categories or focuses can be extracted, include a 'failure_reason' field explaining why."
            )
        },
        {
            "role": "user",
            "content": (
                f"###Criteria:\n"
                f"Reminder: You are categorizing these criteria and describing their focus\n"
                f"Criteria: {rubric_criteria.criteria}\n"
            )
        }
    ]

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            response_format=RubricCategoryListGPT,
        )

        extracted_categories: RubricCategoryListGPT = response.choices[0].message.parsed

        matched_categories = await match_criteria_to_categories(rubric_criteria, extracted_categories)

        logging.info(f"Categorized criteria: {matched_categories}")

        return matched_categories

    except ValidationError as ve:
        logging.error("Schema validation failed: %s", ve)
        raise ValidationError("Schema validation failed") from ve

    except Exception as e:
        logging.error(f"Error extracting criteria: {e}")
        raise RuntimeError("Could not extract rubric criteria") from e



async def match_criteria_to_categories(master_criteria: RubricCriteriaGPT, master_categories: RubricCategoryListGPT) -> RubricCategoryListGPT:
    """
    Remove from each RubricCategoryGPT any criterion not present
    in master.criteria. Returns a fresh RubricCategoryListGPT.
    """
    allowed = set(master_criteria.criteria)
    matched = []
    for cat in master_categories.categories:
        kept = [c for c in cat.criteria if c in allowed]
        matched.append(
            RubricCategoryGPT(
                category=cat.category,
                focus=cat.focus,
                criteria=kept
            )
        )

    return RubricCategoryListGPT(
        categories=matched,
        failure_reason=master_categories.failure_reason
    )


async def assign_weights(
        job_description: str,
        rubric_categories: RubricCategoryListGPT,
        hiring_manager_voiceover: Optional[str] = None
) -> RubricCategoryWeightsListGPT:

    messages = [
        {
            "role": "system",
            "content": (
                f"###Task\n"
                f"Objective: You are tasked with assigning importance weights (zero to one) to categories and criteria used for evaluating a job applicant.\n\n"
                
                f"###Instructions for weighting categories:\n"
                f"You will be provided with context describing a job and the requirements for a candidate applying to the job (ex: job description, hiring manager voiceover, etc.).\n"
                f"You will also be provided with the categorized criteria used for evaluating a job applicant."
                f"Review all context first.\n"
                f"Assign a weight 1-5, as a whole number to each category describing how important that category (and the underlying criteria) are to the role.\n\n"
                
                f"### Output format instructions:\n"
                f"Return a Pydantic object strictly adhering to the predefined schema."
                f"Each weight should be an integer between 1 and 5 inclusive."
            )
        },
        {
            "role": "user",
            "content": (
                f"###Job Context:\n"
                f"Reminder: Evaluate the importance of the categories against this context.\n"
                f"Job Description: {job_description}\n"
                f"Hiring Manager Voiceover:\n{hiring_manager_voiceover or '<none>'}\n\n"
                f"###Categories and criteria:\n"
                f"Reminder: Assign a weight to each category describing how important it and the underlying criteria are to the role above.\n"
                f"{rubric_categories}\n"
            )
        }
    ]

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            response_format=RubricCategoryWeightsListGPT,
        )

        extracted_weights: RubricCategoryWeightsListGPT = response.choices[0].message.parsed

        logging.info(f"Extracted weights: {extracted_weights}")

        return extracted_weights

    except ValidationError as ve:
        logging.error("Schema validation failed: %s", ve)
        raise ValidationError("Schema validation failed") from ve

    except Exception as e:
        logging.error(f"Error weighting categories: {e}")
        raise RuntimeError("Could not assign weights to categories") from e


async def rebase_combine_weights_and_categories(
    master_weights: RubricCategoryWeightsListGPT,
    master_categories: RubricCategoryListGPT
) -> RubricIn:
    """
    For each category in master_categories, builds a RubricCategoryIn where:
      - category & criteria come straight from master_categories
      - focus comes from master_categories (if present) or is set to ""
      - weight is looked up in master_weights (defaults to 0.0)
    """
    # 1) build a lookup from category name → weight
    weight_map: Dict[str, int] = {
        w.category: w.weight for w in master_weights.categories
    }

    combined: list[RubricCategoryIn] = []
    for cat in master_categories.categories:
        # grab matching weight or default to 0.0
        w = weight_map.get(cat.category, 0.00)

        # if your master_categories items have a `focus` attribute, use it;
        # otherwise default to the empty string
        focus = getattr(cat, "focus", "")

        combined.append(
            RubricCategoryIn(
                category=cat.category,
                criteria=cat.criteria,
                weight=w,
                focus=focus,
            )
        )

    combined_rubric =  RubricIn(categories=combined)

    logging.info(f"Combined rubric: {combined_rubric}")

    return combined_rubric