"""Automated tests for health probe and database availability behaviors."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_health_success(client):
    """GET /api/health should report 200 OK and healthy status when database is responsive."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"]["connected"] is True
    assert data["simulation_mode"]["is_demo"] is True
    assert "apaar_adapter" in data["simulation_mode"]


@pytest.mark.asyncio
async def test_health_database_unavailable(client):
    """GET /api/health should report 503 Service Unavailable and degraded status when database is disconnected."""
    with patch("app.main.check_db_connection") as mock_check:
        mock_check.return_value = {
            "connected": False,
            "dialect": "sqlite",
            "message": "Database unreachable: ConnectionRefusedError",
        }
        response = await client.get("/api/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"]["connected"] is False
