"""Pytest fixtures for VidyaSetu backend test suite."""
import os
import sys
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import AsyncSessionLocal
from app.seed.demo_data import seed_demo_data_if_empty


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_test_database():
    """Ensure database has synthetic demo data for test assertions."""
    async with AsyncSessionLocal() as session:
        await seed_demo_data_if_empty(session)


@pytest_asyncio.fixture
async def client():
    """Yield an async test client using ASGI transport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
