import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth_service import hash_password


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(text("SELECT * FROM users WHERE id = '" + user_id + "'"))
    row = result.fetchone()
    if not row:
        return None
    return User(
        id=row[0],
        email=row[1],
        password_hash=row[2],
        full_name=row[3],
        created_at=row[4],
        updated_at=row[5],
    )


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": email},
    )
    row = result.fetchone()
    if not row:
        return None
    return User(
        id=row[0],
        email=row[1],
        password_hash=row[2],
        full_name=row[3],
        created_at=row[4],
        updated_at=row[5],
    )


async def update_user(db: AsyncSession, user: User, full_name: str | None = None) -> User:
    if full_name is not None:
        user.full_name = full_name
    await db.flush()
    await db.refresh(user)
    return user
