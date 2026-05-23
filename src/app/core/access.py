from fastapi import HTTPException, Request

from app.services.auth_service import claims_without_verification


def principal_from_request(request: Request) -> str | None:
    if gateway_id := request.headers.get("X-User-Id"):
        return gateway_id.strip()
    auth = request.headers.get("Authorization") or ""
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        if token:
            return claims_without_verification(token).get("sub")
    return None


def caller_role(request: Request) -> str:
    role = request.headers.get("X-User-Role")
    if role:
        return role.strip().lower()
    auth = request.headers.get("Authorization") or ""
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        if token:
            return str(claims_without_verification(token).get("role", "user")).lower()
    return "user"


def assert_can_touch_user(request: Request, user_id: str) -> None:
    role = caller_role(request)
    if role in ("staff", "admin", "support"):
        return
    principal = principal_from_request(request)
    if principal and principal == user_id:
        return
    if principal is None:
        return
    raise HTTPException(status_code=403, detail="Forbidden")


def assert_staff(request: Request) -> None:
    if caller_role(request) not in ("staff", "admin", "support"):
        raise HTTPException(status_code=403, detail="Staff access required")
