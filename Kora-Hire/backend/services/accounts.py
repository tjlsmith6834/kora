import os
import logging
logger = logging.getLogger(__name__)
import json
import asyncio
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential
from uuid import UUID
import boto3
from botocore.exceptions import BotoCoreError, ClientError
lambda_client = boto3.client("lambda", region_name=os.getenv("AWS_REGION", "us-east-2"))
_user_cache = {}

from schemas.accounts import User

def wrap_event(payload: dict) -> dict:
    return {
        "body": json.dumps(payload)
    }

async def _invoke_lambda_with_retry(
    function_name: str,
    wrapped_payload: dict,
    attempts: int = 3,
    timeout_seconds: float = 8.0,
) -> dict:
    """Invoke Lambda with timeout and bounded retries for transient slowness/errors."""
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            logger.info("Invoking Lambda (attempt %s/%s): %s", attempt, attempts, function_name)
            return await asyncio.wait_for(
                asyncio.to_thread(
                    lambda_client.invoke,
                    FunctionName=function_name,
                    InvocationType="RequestResponse",
                    Payload=json.dumps(wrapped_payload),
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


async def invoke_lambda(function_name: str, payload: dict) -> dict:
    wrapped_payload = wrap_event(payload)
    logger.info("Preparing Lambda invoke: %s payload_keys=%s", function_name, list(payload.keys()))

    try:
        response = await _invoke_lambda_with_retry(function_name, wrapped_payload)

        raw_payload = response.get("Payload")
        if raw_payload is None:
            raise HTTPException(status_code=500, detail="Missing payload in Lambda response")

        response_payload = json.load(raw_payload)
        logger.debug(f"Raw Lambda response: {response_payload}")

        if "FunctionError" in response:
            logger.error(f"Lambda {function_name} returned FunctionError: {response_payload}")
            raise HTTPException(status_code=500, detail="Lambda function error")

        if "body" in response_payload:
            try:
                return json.loads(response_payload["body"])
            except json.JSONDecodeError:
                logger.error(f"Failed to parse body JSON from Lambda: {response_payload['body']}")
                raise HTTPException(status_code=500, detail="Malformed JSON in Lambda body")

        return response_payload

    except Exception as e:
        logger.exception(f"Exception while invoking Lambda {function_name}")
        raise HTTPException(status_code=500, detail="Lambda invocation failed")

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
async def validate_organization_id(organization_id: UUID) -> bool:
    function_name = "validate-organization-id-function"
    result = await invoke_lambda(function_name, {"organization_id": str(organization_id)})
    valid = result.get("valid", False)
    if not valid:
        logger.warning(f"Organization ID validation failed: {organization_id}")
    return valid

async def create_user(organization_id: UUID, firebase_uid: str) -> dict:
    if not await validate_organization_id(organization_id):
        logger.warning(f"Invalid organization ID: {organization_id}")
        raise HTTPException(status_code=400, detail="Invalid organization ID")

    function_name = "create-user-function"
    result = await invoke_lambda(
        function_name,
        {
            "organization_id": str(organization_id),
            "firebase_uid": str(firebase_uid)
        }
    )

    if not result:
        logger.error("Empty response from create-user Lambda")
        raise HTTPException(status_code=500, detail="Empty response from create-user Lambda")

    if "error" in result:
        logger.error(f"Lambda returned error: {result}")
        raise HTTPException(status_code=500, detail=f"Lambda error: {result['error']}")

    if "user_id" not in result:
        logger.error(f"Missing user_id in Lambda response: {result}")
        raise HTTPException(status_code=500, detail="User creation failed — missing user_id")

    return result

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
async def get_user(firebase_uid: str) -> User:
    if firebase_uid in _user_cache:
        logger.info(f"Cache hit for firebase_uid: {firebase_uid}")
        return _user_cache[firebase_uid]

    function_name = "get-user-function"
    result = await invoke_lambda(function_name, {"firebase_uid": firebase_uid})

    try:
        user_data = result["user"]
        user = User(
            user_id=user_data["user_id"],
            org_id=user_data["organization_id"],
            role=user_data["role"],
        )
        _user_cache[firebase_uid] = user
        return user

    except (KeyError, TypeError) as e:
        logger.error(f"Malformed user data from Lambda: {result}")
        raise HTTPException(status_code=500, detail=f"Malformed Lambda response: {e}")

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
async def get_public_key_for_organization_id(organization_id: UUID) -> str:
    function_name = "get-public-key-function"
    result = await invoke_lambda(function_name, {"organization_id": str(organization_id)})

    public_key = result.get("public_key")
    if not public_key:
        logger.error(f"Missing public key in Lambda response: {result}")
        raise HTTPException(status_code=500, detail="Public key not found in Lambda response")

    return public_key