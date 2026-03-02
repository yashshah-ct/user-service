from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import create_user, get_user_by_id, update_user
from app.messaging.rabbitmq import publish_user_created, get_connection, ensure_exchanges
router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse)
async def register_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    from app.services.user_service import get_user_by_email
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(db, data)
    await db.commit()
    conn = await get_connection()
    channel = await conn.channel()
    await ensure_exchanges(channel)
    await publish_user_created(channel, user.id, user.email, user.full_name)
    await channel.close()
    await conn.close()
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
        password_hash=user.password_hash,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
        password_hash=user.password_hash,
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def patch_user(
    user_id: str,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.full_name is not None:
        user = await update_user(db, user, full_name=data.full_name)
    await db.commit()
    await db.refresh(user)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
    )
