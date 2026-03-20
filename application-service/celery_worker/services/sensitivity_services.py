import asyncio
from pydantic import BaseModel
from openai import OpenAI
import logging
import os
from typing import List, TypeVar, Generic

# Load OpenAI API key from env variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SensitivityFlag(BaseModel):
    flagged: bool

T = TypeVar("T")  # Generic type for input entries

async def filter_sensitive_entries(entries: List[T]) -> List[T]:
    """
    Filters out entries that contain sensitive information based on a single batched OpenAI request.

    Args:
        entries (List[T]): A list of entries of any type (str, dict, BaseModel, etc.)

    Returns:
        List[T]: The filtered list of entries that passed the sensitivity check.
    """
    if not entries:
        return []

    def format_entry(entry: T) -> str:
        if isinstance(entry, dict):
            return " | ".join([f"{key}: {value}" for key, value in entry.items()])
        elif isinstance(entry, BaseModel):
            return " | ".join([f"{key}: {value}" for key, value in entry.model_dump().items()])
        elif isinstance(entry, str):
            return entry
        else:
            logging.warning(f"Unexpected entry format: {entry}")
            return str(entry)

    check_texts = [format_entry(entry) for entry in entries]

    # Run sensitivity check in a single batch request
    flags = await check_sensitivity_list(check_texts)

    if len(flags) != len(entries):
        logging.error(f"Mismatch in sensitivity check results. Expected {len(entries)}, got {len(flags)}.")
        return []

    filtered_entries = [entry for entry, flagged in zip(entries, flags) if not flagged]

    logging.info(f"✅ {len(filtered_entries)} entries passed, 🚩 {len(entries) - len(filtered_entries)} flagged.")
    return filtered_entries


async def check_sensitivity_list(entries: List[str]) -> List[bool]:
    """
    Checks a list of text entries for sensitive content by dispatching them to check_sensitivity_item concurrently.

    Returns a list of booleans (True if the entry is flagged as sensitive).
    """
    try:
        # Use asyncio.gather with the splat (*) to concurrently run all checks.
        results = await asyncio.gather(*(check_sensitivity_item(entry) for entry in entries))
        return results  # Each result is already a boolean
    except Exception as e:
        logging.error(f"❌ Error checking sensitivity: {e}")
        # Fail-safe: Default to True (not flagged) for each entry if an error occurs.
        return [True] * len(entries)


async def check_sensitivity_item(entry: str) -> bool:
    messages = [
        {
            "role": "system",
            "content": (
                f"**TASK:** You are trying to find review references sensitive hiring categories in the text that you are reviewing.\n\n"
                f"**Sensitive hiring categories:**\n"     
                f"Check if the entry contains references to any of the following:\n\n"
                f"- Criminal history\n"
                f"- Age, Disability, Gender identity, Genetic information, National origin, Pregnancy, Race/color, Religion, Sex, Sexual orientation\n"
                f"- Salary history or compensation details\n"
                f"- Specific location requirements, commuting details, relocation willingness, or city/state mentions\n\n"
            )
        },
        {
            "role": "user",
            "content": (
                "**Text for review**\n"
                "Determine if this text contains references to sensitive hiring categories.\n"
                f"{entry}\n\n"
            )
        }
    ]
    response = client.beta.chat.completions.parse(
        model="gpt-4o",  # Ensure you're using the latest GPT-4o model
        messages=messages,
        response_format=SensitivityFlag
    )
    flag = response.choices[0].message.parsed
    return flag.flagged
