from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database import crud
from packages.shared.schemas import AppConfig
from services.api.dependencies import get_api_runtime, get_db_session
from services.api.runtime import ApiRuntime
from services.api.schemas import ApiKeyUpdateRequest, MessageResponse, SettingsResponse, SettingsUpdateRequest


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
async def get_settings(runtime: ApiRuntime = Depends(get_api_runtime)) -> SettingsResponse:
    values = runtime.bootstrap.config.as_dict()
    return SettingsResponse(values=values)


@router.put("", response_model=SettingsResponse)
async def update_settings(
    payload: SettingsUpdateRequest,
    runtime: ApiRuntime = Depends(get_api_runtime),
    session: AsyncSession = Depends(get_db_session),
) -> SettingsResponse:
    if not payload.values:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No settings provided")

    valid_keys = set(AppConfig.__dataclass_fields__.keys())  # type: ignore[attr-defined]
    invalid = [key for key in payload.values.keys() if key not in valid_keys]
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported settings keys: {', '.join(sorted(invalid))}",
        )

    runtime.bootstrap.config.set_many(payload.values)

    for key, value in payload.values.items():
        await crud.upsert_setting(session, key=key, value=json.dumps(value, ensure_ascii=True))

    return SettingsResponse(values=runtime.bootstrap.config.as_dict())


@router.post("/api-key", response_model=MessageResponse)
async def set_api_key(
    payload: ApiKeyUpdateRequest,
    runtime: ApiRuntime = Depends(get_api_runtime),
    session: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    runtime.bootstrap.config.save_encrypted_key(payload.provider, payload.api_key)
    encrypted_key_name = f"ENCRYPTED_{payload.provider.upper()}"
    encrypted_value = runtime.bootstrap.config.as_dict().get(encrypted_key_name, "")
    await crud.upsert_setting(session, key=encrypted_key_name, value=encrypted_value)
    return MessageResponse(message=f"{payload.provider} API key updated")
