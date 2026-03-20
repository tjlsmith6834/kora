import os
import logging
import json
import asyncio
from uuid import UUID
from fastapi import HTTPException
import httpx
import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)
lambda_client = boto3.client("lambda", region_name=os.getenv("AWS_REGION", "us-east-2"))


async def _invoke_lambda_with_retry(
    function_name: str,
    payload: dict,
    attempts: int = 3,
    timeout_seconds: float = 8.0,
) -> dict:
    """Invoke Lambda with timeout and bounded retries for transient slowness/errors."""
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            logger.info("Invoking Lambda (attempt %s/%s)...", attempt, attempts)
            return await asyncio.wait_for(
                asyncio.to_thread(
                    lambda_client.invoke,
                    FunctionName=function_name,
                    InvocationType="RequestResponse",
                    Payload=json.dumps(payload),
                ),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError as e:
            last_error = e
            logger.warning("Lambda invoke timed out (attempt %s/%s)", attempt, attempts)
        except (BotoCoreError, ClientError) as e:
            last_error = e
            logger.warning("Lambda invoke failed (attempt %s/%s): %s", attempt, attempts, e)

        if attempt < attempts:
            await asyncio.sleep(min(2 ** (attempt - 1), 4))

    logger.exception("Lambda invocation exhausted retries", exc_info=last_error)
    raise HTTPException(status_code=500, detail="Lambda invocation failed after retries")


async def authenticate_job_id_and_public_key(job_id: UUID, public_key: bytes) -> bool:
    if not os.getenv("AWS_ACCESS_KEY_ID"):
        logger.warning("AWS_ACCESS_KEY_ID not set")
    jobs_base_url = os.getenv("JOBS_SERVICE_BASE_URL")
    lambda_function_name = "validate-public-key-function"

    if not jobs_base_url:
        raise ValueError("JOBS_SERVICE_BASE_URL not set")

    if not lambda_function_name:
        raise ValueError("lambda_function_name not set")

    jobs_url = f"{jobs_base_url}/{job_id}"

    # Step 1: Fetch job info via HTTP
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(jobs_url)
            response.raise_for_status()
            data = response.json()
    except httpx.RequestError as e:
        logger.exception("Error fetching job for public key validation")
        raise HTTPException(
            status_code=500,
            detail="Error fetching job"
        )
    except Exception as e:
        logger.exception("Unexpected error fetching job for public key validation")
        raise HTTPException(
            status_code=500,
            detail="Unexpected error fetching job"
        )

    org_id = data.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=500, detail="Job missing organization_id")

    # Step 2: Call Lambda to validate public key
    payload = {
        "organization_id": str(org_id),
        "public_key": public_key.decode() if isinstance(public_key, bytes) else str(public_key)
    }

    logger.info("Calling Lambda for public key validation")

    try:
        response = await _invoke_lambda_with_retry(lambda_function_name, payload)

        if response.get("FunctionError"):
            logger.error("Lambda function error: FunctionError returned")
            raise HTTPException(status_code=500, detail="Lambda execution failed")

        payload_stream = response.get("Payload")
        if not payload_stream:
            raise HTTPException(status_code=500, detail="Missing payload in Lambda response")

        result = json.load(payload_stream)

        if "body" in result:
            parsed_body = json.loads(result["body"])
        else:
            parsed_body = result

        logger.info("Lambda validation completed")

        is_valid = parsed_body.get("valid", False)
        if not is_valid:
            raise HTTPException(status_code=403, detail="Invalid public key")

        return is_valid

    except (BotoCoreError, ClientError) as e:
        logger.exception("AWS error during Lambda invocation")
        raise HTTPException(
            status_code=500,
            detail="AWS error during Lambda invocation"
        )
    except (KeyError, json.JSONDecodeError) as e:
        logger.exception("Malformed response from Lambda")
        raise HTTPException(
            status_code=500,
            detail="Malformed response from Lambda"
        )
    except Exception as e:
        logger.exception("Unexpected error during Lambda validation")
        raise HTTPException(
            status_code=500,
            detail="Unexpected error during Lambda validation"
        )