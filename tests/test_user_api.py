import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/users",
        json={
            "email": "test@example.com",
            "password": "securepass123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post(
        "/users",
        json={
            "email": "login@example.com",
            "password": "pass123",
            "full_name": "Login User",
        },
    )
    response = await client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "pass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_user(client: AsyncClient):
    create_resp = await client.post(
        "/users",
        json={
            "email": "get@example.com",
            "password": "pass123",
            "full_name": "Get User",
        },
    )
    user_id = create_resp.json()["id"]
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "get@example.com"


@pytest.mark.asyncio
async def test_jwks(client: AsyncClient):
    response = await client.get("/auth/jwks")
    assert response.status_code == 200
    data = response.json()
    assert "keys" in data
    assert len(data["keys"]) >= 1


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
