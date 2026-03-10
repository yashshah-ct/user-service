from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import check_rate_limit_auth
from app.db.session import get_db
from app.schemas.user import UserLogin, TokenResponse
from app.services.user_service import get_user_by_email
from app.services.auth_service import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


async def _rate_limit_auth(request: Request) -> None:
    check_rate_limit_auth(request)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_rate_limit_auth),
):
    user = await get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token)


@router.get("/jwks")
async def jwks():
    from app.services.jwks_service import get_jwks
    return get_jwks()
