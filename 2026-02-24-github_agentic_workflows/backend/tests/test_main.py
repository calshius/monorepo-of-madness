import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app, items


@pytest.fixture(autouse=True)
def reset_items():
    """Clear the in-memory store before each test."""
    items.clear()
    yield
    items.clear()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_list_items_empty(client: AsyncClient):
    resp = await client.get("/items")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_item(client: AsyncClient):
    resp = await client.post("/items", json={"name": "Widget", "description": "A fine widget"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == 1
    assert data["name"] == "Widget"
    assert data["description"] == "A fine widget"


@pytest.mark.asyncio
async def test_create_and_list_items(client: AsyncClient):
    await client.post("/items", json={"name": "A"})
    await client.post("/items", json={"name": "B"})
    resp = await client.get("/items")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_get_item(client: AsyncClient):
    await client.post("/items", json={"name": "Gadget", "description": "Handy"})
    resp = await client.get("/items/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Gadget"


@pytest.mark.asyncio
async def test_get_item_not_found(client: AsyncClient):
    resp = await client.get("/items/999")
    assert resp.status_code == 404
