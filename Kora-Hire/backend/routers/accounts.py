import os
from fastapi import APIRouter, HTTPException, status, Path, Body, Depends
from uuid import UUID
import logging
from pydantic import BaseModel

from services.accounts import create_user, get_user, validate_organization_id, get_public_key_for_organization_id
from services.auth import get_current_user_token
from schemas.auth import TokenPayload

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)

class CreateUserPayload(BaseModel):
    firebase_uid: str
@router.post("/{organization_id}/user")
async def post_new_user(
        organization_id: UUID = Path(...),
        firebase_uid_payload: CreateUserPayload = Body(...)
):
    try:
        logger.info(f"Creating user for organization: {organization_id}")
        stored_user = await create_user(organization_id=organization_id, firebase_uid=firebase_uid_payload.firebase_uid)
        logger.info(f"Created user: {stored_user}")
        return stored_user
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error creating user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{organization_id}/validate")
async def get_organization_id_validate(
    organization_id: str = Path(..., description="Organization ID (UUID)")
):
    try:
        try:
            org_uuid = UUID(organization_id)
        except ValueError:
            return {
                "valid": False,
                "error": "Organization ID must be a valid UUID."
            }

        logger.info(f"Validating organization: {org_uuid}")

        valid = await validate_organization_id(organization_id=org_uuid)

        return {"valid": bool(valid)}

    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error validating organization id")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/public_key")
async def get_public_key(
        token: TokenPayload = Depends(get_current_user_token)
):
    try:
        if token.uid == "demo-user":
            return "no_key"
        user = await get_user(token.uid)
        logger.info(f"Getting public key for organization: {user.org_id}")
        key = await get_public_key_for_organization_id(organization_id=user.org_id)
        logger.info("Public key retrieved for organization")
        return key
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error getting public key")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )