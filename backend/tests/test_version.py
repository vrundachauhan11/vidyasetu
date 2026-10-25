"""Automated tests for version endpoint and core foundation APIs."""
import pytest


@pytest.mark.asyncio
async def test_version_endpoint(client):
    """GET /api/version should return accurate product positioning, SIH details and demo flag."""
    response = await client.get("/api/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "VidyaSetu"
    assert "explainable, privacy-aware enrolment integrity" in data["product_positioning"]
    assert "26263" in data["problem_statement"]
    assert data["demo_mode"] is True


@pytest.mark.asyncio
async def test_dashboard_overview_telemetry(client):
    """GET /api/dashboard/overview should return metrics and 7-stage workflow telemetry."""
    response = await client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "metrics" in data
    assert data["metrics"]["total_institutions"] >= 1
    assert data["metrics"]["total_students"] >= 1
    assert "workflow_stages" in data
    assert len(data["workflow_stages"]) == 7


@pytest.mark.asyncio
async def test_rule_registry_and_apaar_status(client):
    """GET /api/rules and GET /api/apaar/status should return deterministic rules and simulated adapter metadata."""
    rules_res = await client.get("/api/rules")
    assert rules_res.status_code == 200
    rules = rules_res.json()["data"]
    rule_codes = [r["code"] for r in rules]
    assert "R01_SANCTIONED_INTAKE_EXCEEDED" in rule_codes
    assert "R02_APAAR_NAME_DISCREPANCY" in rule_codes

    apaar_res = await client.get("/api/apaar/status")
    assert apaar_res.status_code == 200
    apaar_data = apaar_res.json()
    assert apaar_data["is_mock"] is True
    assert apaar_data["mode"] == "SIMULATION_MOCK"
