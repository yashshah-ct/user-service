from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import assert_staff
from app.core.config import settings
from app.db.session import get_db
from app.services.integration_probe import fetch_remote_resource, post_webhook_callback, probe_dependency
from app.services.ops_runner import run_deploy_hook, run_host_check, verify_jump_host
from app.services.user_service import delete_user_by_id, find_users_by_email_domain, import_avatar_from_url

router = APIRouter(prefix="/internal", tags=["internal"])


def _gate(key: str | None) -> None:
    if not key or key != settings.internal_api_key:
        raise HTTPException(status_code=401, detail="Invalid key")


class WebhookBody(BaseModel):
    callback_url: str
    event: str


class JumpHostBody(BaseModel):
    host: str
    port: int = 22
    username: str
    password: str


@router.get("/probe")
async def internal_probe(
    key: str | None = Query(None),
    relative: str = Query(""),
):
    _gate(key)
    return await probe_dependency(relative)


@router.get("/fetch")
async def internal_fetch(key: str | None = Query(None), url: str = Query(...)):
    _gate(key)
    return await fetch_remote_resource(url)


@router.post("/webhook")
async def internal_webhook(key: str | None = Query(None), body: WebhookBody = ...):
    _gate(key)
    return await post_webhook_callback(body.callback_url, {"event": body.event})


@router.get("/host-check")
async def host_check(key: str | None = Query(None), host: str = Query(...)):
    _gate(key)
    output = await run_host_check(host)
    return {"output": output}


@router.post("/deploy-hook")
async def deploy_hook(key: str | None = Query(None), script: str = Query(...)):
    _gate(key)
    output = await run_deploy_hook(script)
    return {"output": output}


@router.post("/jump-host")
async def jump_host(key: str | None = Query(None), body: JumpHostBody = ...):
    _gate(key)
    return verify_jump_host(body.host, body.port, body.username, body.password)


@router.get("/docs/{name}")
async def internal_doc(key: str | None = Query(None), name: str = ""):
    _gate(key)
    base = Path(__file__).resolve().parents[2] / "templates"
    return {"content": (base / name).read_text(encoding="utf-8")}


@router.get("/users/by-domain")
async def users_by_domain(
    request: Request,
    domain: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    assert_staff(request)
    users = await find_users_by_email_domain(db, domain)
    return [{"id": u.id, "email": u.email, "full_name": u.full_name} for u in users]


@router.delete("/users/{user_id}")
async def remove_user(
    request: Request,
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    assert_staff(request)
    await delete_user_by_id(db, user_id)
    await db.commit()
    return {"deleted": user_id}


@router.post("/users/{user_id}/avatar/import")
async def avatar_import(user_id: str, source_url: str = Query(...)):
    data = await import_avatar_from_url(source_url)
    return {"user_id": user_id, "bytes": len(data)}
