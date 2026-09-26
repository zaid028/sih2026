"""
FIREGUARD AI - Authentication, User Profile, and View API Tests
Verifies Login, JWT verification, /me endpoint, KPI data structures,
and compatibility layer for 100% frontend operational readiness.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_login_success():
    res = client.post("/api/v1/auth/login", json={
        "username": "operator",
        "password": "operator123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "OPERATOR"
    assert data["username"] == "operator"

def test_auth_me_endpoint():
    # Login first
    login_res = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_res.json()["access_token"]

    # Call /me
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    profile = me_res.json()
    assert profile["username"] == "admin"
    assert profile["role"] == "ADMIN"
    assert "agency" in profile
    assert "email" in profile

def test_legacy_kpis_contract():
    res = client.get("/api/analytics/kpis")
    assert res.status_code == 200
    kpis = res.json()
    assert "total_hotspots" in kpis
    assert "industrial_fires" in kpis
    assert "high_risk_incidents" in kpis
    assert "persistent_sources" in kpis
    assert "avg_response_time_min" in kpis

def test_persistent_sources_contract():
    res = client.get("/api/persistent-sources")
    assert res.status_code == 200
    data = res.json()
    assert "sources" in data
    assert len(data["sources"]) > 0

def test_emergency_contacts_contract():
    res = client.get("/api/emergency/contacts")
    assert res.status_code == 200
    data = res.json()
    assert "contacts" in data
    assert len(data["contacts"]) > 0

def test_dispatch_simulation_contract():
    res = client.post("/api/emergency/dispatch-sim", json={"incident_id": "INC-2026-001"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "payload" in data
    assert "dispatch_id" in data["payload"]
    assert "formatted_dispatch_message" in data["payload"]
