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
from app.modules.auth.security import create_access_token
from app.models import ProgrammeApproval, Institution
import uuid
from sqlalchemy import select


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_test_database():
    """Ensure database has synthetic demo data for test assertions."""
    async with AsyncSessionLocal() as session:
        await seed_demo_data_if_empty(session)


@pytest_asyncio.fixture
async def create_isolated_programme():
    """Factory fixture returning a helper to register an isolated ProgrammeApproval for test scenarios."""
    async def _create(programme_name: str, sanctioned_intake: int = 50, academic_year: str = "2025-26"):
        async with AsyncSessionLocal() as session:
            inst = (await session.execute(select(Institution).limit(1))).scalar_one()
            prog = ProgrammeApproval(
                id=str(uuid.uuid4()),
                institution_id=inst.id,
                programme_name=programme_name,
                degree_level="Undergraduate",
                academic_year=academic_year,
                sanctioned_intake=sanctioned_intake,
                approved_quota_details=f"State Quota 100% ({sanctioned_intake} seats)",
            )
            session.add(prog)
            await session.commit()
            return prog

    return _create


@pytest_asyncio.fixture
async def client():
    """Yield an authenticated async test client with Council Regulator clearance."""
    regulator_token = create_access_token(
        user_id="usr_reg_01",
        email="compliance.officer@aicte-gov.in",
        role="REGULATOR_AICTE",
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {regulator_token}"},
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def unauthenticated_client():
    """Yield an unauthenticated async test client with no Authorization header."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
