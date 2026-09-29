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
    res = client.post("/api/emergency/dispatch-sim", json={"incident_id": "INC-2026-001", "role": "OPERATOR"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "payload" in data
    assert "dispatch_id" in data["payload"]
    assert "formatted_dispatch_message" in data["payload"]

def test_citizen_report_and_rbac():
    # 1. Citizen photo report submission via v1 API
    citizen_payload = {
        "title": "Visible Refinery Flame Plume",
        "latitude": 22.4707,
        "longitude": 70.0577,
        "description": "Dense black smoke rising from southwest tank farm",
        "photo_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
        "reporter_name": "Aarav Patel",
        "reporter_phone": "+91 98250 12345"
    }
    res = client.post("/api/v1/incidents/citizen-report", json=citizen_payload)
    assert res.status_code == 201
    cit_data = res.json()
    assert cit_data["success"] is True
    assert "tracking_number" in cit_data
    assert "incident" in cit_data

    # 2. Citizen photo report submission via legacy endpoint
    res_leg = client.post("/api/citizen-report", json=citizen_payload)
    assert res_leg.status_code == 200
    assert res_leg.json()["success"] is True

    # 3. Test RBAC: Public civilian cannot alter tactical incident status
    pub_login = client.post("/api/v1/auth/login", json={"username": "public_user", "password": "public123"})
    assert pub_login.status_code == 200
    pub_token = pub_login.json()["access_token"]

    # v1 PATCH incident with PUBLIC token -> 403 Forbidden
    patch_res = client.patch(
        "/api/v1/incidents/inc-jamnagar-01",
        json={"status": "RESOLVED"},
        headers={"Authorization": f"Bearer {pub_token}"}
    )
    assert patch_res.status_code == 403

    # Legacy PATCH status with PUBLIC token -> 403 Forbidden
    leg_patch_res = client.patch(
        "/api/incidents/inc-jamnagar-01/status",
        json={"status": "RESOLVED"},
        headers={"Authorization": f"Bearer {pub_token}"}
    )
    assert leg_patch_res.status_code == 403

    # Public user cannot trigger simulated multi-agency tactical broadcast
    pub_disp = client.post(
        "/api/emergency/dispatch-sim",
        json={"incident_id": "inc-jamnagar-01"},
        headers={"Authorization": f"Bearer {pub_token}"}
    )
    assert pub_disp.status_code == 403

