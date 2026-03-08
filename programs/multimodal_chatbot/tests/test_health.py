"""
Tests for the /health endpoint.
"""

import pytest


@pytest.mark.asyncio
async def test_health_ok(test_client):
    """Health endpoint returns 200 with status 'ok' when Redis is connected."""
    response = await test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["redis"] == "connected"
