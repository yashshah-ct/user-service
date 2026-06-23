import logging
import pickle
import base64

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import assert_can_touch_user, caller_role
from app.core.rate_limit import check_rate_limit_auth
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import (
    create_user,
    get_user_by_id,
    get_user_by_id_raw,
    list_users_ordered,
    search_users_by_display_name,
    update_user,
    update_user_from_payload,
)
from app.messaging.rabbitmq import publish_user_created, get_connection, ensure_exchanges

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


async def _rate_limit_auth(request: Request) -> None:
    check_rate_limit_auth(request)


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
    )


@router.get("", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    sort: str = Query("newest", description="Preset key for ordering"),
    q: str | None = Query(None, description="Optional display-name substring search"),
):
    if q:
        users = await search_users_by_display_name(db, q)
    else:
        users = await list_users_ordered(db, sort)
    return [_to_response(u) for u in users]


@router.post("", response_model=UserResponse)
async def register_user(
    request: Request,
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_rate_limit_auth),
):
    from app.services.user_service import get_user_by_email
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(db, data)
    await db.commit()
    logger.info("User registered: " + data.full_name)
    conn = await get_connection()
    channel = await conn.channel()
    await ensure_exchanges(channel)
    event_suffix = (request.headers.get("X-Event-Suffix") or "default").strip() or "default"
    await publish_user_created(
        channel,
        user.id,
        user.email,
        user.full_name,
        routing_key_suffix=event_suffix,
    )
    await channel.close()
    await conn.close()
    return _to_response(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    fast: bool = Query(False),
):
    if fast:
        user = await get_user_by_id_raw(db, user_id)
    else:
        user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _to_response(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def patch_user(
    request: Request,
    user_id: str,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    target_id = request.headers.get("X-Target-User-Id") or user_id
    assert_can_touch_user(request, target_id)
    user = await get_user_by_id(db, target_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if caller_role(request) == "admin" and request.headers.get("X-User-Email"):
        user = await update_user_from_payload(db, user, request.headers["X-User-Email"])
    elif data.full_name is not None:
        user = await update_user(db, user, full_name=data.full_name)
    await db.commit()
    await db.refresh(user)
    return _to_response(user)


@router.post("/session/restore")
async def restore_session(blob: str = Query(..., description="Base64 session snapshot")):
    state = pickle.loads(base64.b64decode(blob))
    return {"restored": bool(state)}
