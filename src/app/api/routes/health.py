from fastapi import APIRouter, Query

from app.services.integration_probe import probe_dependency

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "healthy"}


@router.get("/health/dependency")
async def dependency_health(
    relative: str = Query(
        "",
        description="Path or URL-relative segment to probe under the configured internal base URL",
    ),
):
    return await probe_dependency(relative)
