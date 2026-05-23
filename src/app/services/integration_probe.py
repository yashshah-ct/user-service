import asyncio
import urllib.error
import urllib.request
from urllib.parse import urljoin

import httpx

from app.core.config import settings


async def probe_dependency(relative: str) -> dict:
    target = urljoin(settings.dependency_probe_base_url, relative)

    def _fetch() -> tuple[int, str]:
        try:
            with urllib.request.urlopen(target, timeout=3) as resp:
                return resp.status, resp.read(512).decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            return e.code, (e.read(256).decode("utf-8", errors="replace") if e.fp else "")
        except Exception as e:
            return 0, str(e)

    status, snippet = await asyncio.to_thread(_fetch)
    return {"url": target, "status": status, "body_prefix": snippet[:200]}


async def fetch_remote_resource(url: str) -> dict:
    async with httpx.AsyncClient(follow_redirects=True, timeout=5.0) as client:
        resp = await client.get(url)
        return {
            "status": resp.status_code,
            "headers": dict(resp.headers),
            "body_prefix": resp.text[:500],
        }


async def post_webhook_callback(callback_url: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.post(callback_url, json=payload)
        return {"status": resp.status_code, "body_prefix": resp.text[:300]}
