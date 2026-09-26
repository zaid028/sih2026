"""
FIREGUARD AI - Complete End-to-End API Test Suite (Requirement 27)
Verifies:
NASA FIRMS ingestion -> hotspot database -> OSM correlation -> AI classification ->
risk calculation -> incident creation -> emergency facility lookup -> route generation ->
alert creation -> frontend API response
"""
import unittest
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os
os.environ["DATABASE_URL"] = "sqlite:///backend/data/test_fireguard_e2e.db"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database.session import Base, get_db
from backend.database.seed import seed_database_if_empty
from backend.models.entities import User

test_db_file = PROJECT_ROOT / "backend" / "data" / "test_fireguard_e2e.db"
test_engine = create_engine(f"sqlite:///{test_db_file}", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestFireGuardEndToEndAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if test_db_file.exists():
            test_db_file.unlink()
        Base.metadata.create_all(bind=test_engine)
        db = TestingSessionLocal()
        try:
            seed_database_if_empty(db)
        finally:
            db.close()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        if test_db_file.exists():
            try:
                test_db_file.unlink()
            except Exception:
                pass

    def test_01_health_monitor(self):
        """Requirement 26: Health monitor must return operational status of all micro-components."""
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("components", data)
        self.assertIn("backend", data["components"])
        self.assertIn("database", data["components"])
        self.assertIn("nasa_firms", data["components"])
        self.assertIn("osm", data["components"])
        self.assertIn("ai_engine", data["components"])
        self.assertIn("routing", data["components"])
        self.assertIn("notification_service", data["components"])
        self.assertEqual(data["components"]["backend"], "ONLINE")
        self.assertEqual(data["components"]["database"], "ONLINE")

    def test_02_nasa_firms_ingestion(self):
        """Requirement 2 & 3: NASA FIRMS ingestion into hotspot database."""
        resp = self.client.post("/api/v1/hotspots/ingest?country=IND&day_range=1")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["ingested_count"], 0)
        self.assertIn("source", data)

    def test_03_hotspot_database_query(self):
        """Requirement 2: Fetch hotspots with filters."""
        resp = self.client.get("/api/v1/hotspots?confidence=70")
        self.assertEqual(resp.status_code, 200)
        hotspots = resp.json()
        self.assertIsInstance(hotspots, list)
        self.assertGreater(len(hotspots), 0)
        first = hotspots[0]
        self.assertIn("id", first)
        self.assertIn("latitude", first)
        self.assertIn("longitude", first)
        self.assertIn("brightness", first)
        self.assertIn("confidence", first)

    def test_04_osm_correlation_and_location_analysis(self):
        """Requirement 4 & 5: Geospatial correlation around Jamnagar coordinates."""
        payload = {"latitude": 22.4707, "longitude": 70.0577, "radius_km": 25.0}
        resp = self.client.post("/api/v1/analyze/location", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("nearest_facility", data)
        self.assertIn("distance_to_facility", data)
        self.assertIn("nearby_hospitals", data)
        self.assertIn("nearby_fire_stations", data)
        self.assertIn("nearby_roads", data)
        self.assertLess(data["distance_to_facility"], 5.0)

    def test_05_ai_classification(self):
        """Requirement 6: 8-Class AI fire classifier with XAI attribution."""
        payload = {
            "features": {
                "frp": 68.4,
                "brightness": 368.5,
                "distance_to_facility_km": 0.25,
                "facility_type": "Refinery",
                "recurrence_count": 18,
                "confidence": 94.0,
                "is_spike": True
            }
        }
        resp = self.client.post("/api/v1/ai/classify", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["classification"], "Industrial Fire")
        self.assertGreaterEqual(data["confidence"], 0.80)
        self.assertIsInstance(data["factors"], list)
        self.assertGreater(len(data["factors"]), 0)

    def test_06_risk_calculation(self):
        """Requirement 8: ISO31000 Explainable Risk Assessment (0-100)."""
        payload = {
            "classification": "Industrial Fire",
            "confidence": 0.94,
            "features": {
                "frp": 68.4,
                "brightness": 368.5,
                "distance_to_facility_km": 0.25,
                "hazmat_level": "LEVEL-4",
                "recurrence_count": 15,
                "population_exposure": 3500
            }
        }
        resp = self.client.post("/api/v1/risk/calculate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("risk_score", data)
        self.assertIn("risk_level", data)
        self.assertIn("factors", data)
        self.assertIn("explanation", data)
        self.assertGreaterEqual(data["risk_score"], 76.0)
        self.assertEqual(data["risk_level"], "CRITICAL")

    def test_07_incident_crud_and_operator_verification(self):
        """Requirement 9 & 10: Incident management and status transition."""
        # 1. Create incident
        create_payload = {
            "title": "Automated End-to-End Test Incident",
            "latitude": 22.4707,
            "longitude": 70.0577,
            "risk_score": 88.0,
            "risk_level": "CRITICAL",
            "classification": "Industrial Fire",
            "confidence": 0.92,
            "operator_notes": "Awaiting field officer review"
        }
        resp = self.client.post("/api/v1/incidents", json=create_payload)
        self.assertEqual(resp.status_code, 201)
        inc_data = resp.json()
        inc_id = inc_data["id"]
        self.assertEqual(inc_data["status"], "DETECTED")

        # 2. Get incident by ID
        resp = self.client.get(f"/api/v1/incidents/{inc_id}")
        self.assertEqual(resp.status_code, 200)

        # 3. Update status (operator verification)
        patch_payload = {
            "status": "VERIFIED",
            "operator_notes": "Confirmed on high-resolution CCTV sensor. Authorizing mutual aid staging.",
            "verified_by": "Senior Officer Varma"
        }
        resp = self.client.patch(f"/api/v1/incidents/{inc_id}", json=patch_payload)
        self.assertEqual(resp.status_code, 200)
        updated = resp.json()
        self.assertEqual(updated["status"], "VERIFIED")
        self.assertEqual(updated["verified_by"], "Senior Officer Varma")

    def test_08_emergency_services_lookup(self):
        """Requirement 11: Emergency services query."""
        resp = self.client.get("/api/v1/emergency-services?service_type=hospital")
        self.assertEqual(resp.status_code, 200)
        hospitals = resp.json()
        self.assertIsInstance(hospitals, list)
        self.assertGreater(len(hospitals), 0)

        # Nearest hospital
        resp = self.client.get("/api/v1/emergency-services/nearest?latitude=22.4707&longitude=70.0577&service_type=hospital")
        self.assertEqual(resp.status_code, 200)
        nearest = resp.json()
        self.assertIn("name", nearest)
        self.assertEqual(nearest["service_type"], "hospital")

    def test_09_safety_routing(self):
        """Requirement 12: Safe evacuation routing avoiding danger buffer zone."""
        payload = {
            "origin": {"latitude": 22.4707, "longitude": 70.0577},
            "destination": {"latitude": 22.4680, "longitude": 70.0650},
            "avoid_radius_m": 1500
        }
        resp = self.client.post("/api/v1/routes/safe", json=payload)
        self.assertEqual(resp.status_code, 200)
        route_data = resp.json()
        self.assertIn("recommended_route", route_data)
        self.assertIn("distance", route_data)
        self.assertIn("estimated_time", route_data)
        self.assertIn("hazards", route_data)
        self.assertIn("disclaimer", route_data)

    def test_10_alerts_creation_and_ack(self):
        """Requirement 15: Alert generation and acknowledgment."""
        payload = {
            "severity": "CRITICAL",
            "alert_type": "INDUSTRIAL_FIRE",
            "title": "Automated Hazard Warning",
            "message": "Radiation perimeter 500m active.",
            "channels": ["DASHBOARD", "SMS"]
        }
        resp = self.client.post("/api/v1/alerts", json=payload)
        self.assertEqual(resp.status_code, 201)
        alert = resp.json()
        alert_id = alert["id"]
        self.assertFalse(alert["read_status"])

        # Mark read
        resp = self.client.patch(f"/api/v1/alerts/{alert_id}/read")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["read_status"])

    def test_11_persistent_sources(self):
        """Requirement 7: Persistent thermal sources."""
        resp = self.client.get("/api/v1/persistent-sources")
        self.assertEqual(resp.status_code, 200)
        sources = resp.json()
        self.assertIsInstance(sources, list)
        self.assertGreater(len(sources), 0)

    def test_12_authentication_jwt(self):
        """Requirement 19: JWT Auth login and /me verification."""
        resp = self.client.post("/api/v1/auth/login", json={"username": "operator", "password": "operator123"})
        self.assertEqual(resp.status_code, 200)
        token_data = resp.json()
        self.assertIn("access_token", token_data)
        self.assertEqual(token_data["role"], "OPERATOR")

        # Test authenticated /me
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        resp = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(resp.status_code, 200)
        user_info = resp.json()
        self.assertEqual(user_info["username"], "operator")

    def test_13_complete_sih_demo_pipeline(self):
        """Requirement 25: POST /api/v1/demo/run executing all 12 pipeline steps."""
        resp = self.client.post("/api/v1/demo/run")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "COMPLETE")
        self.assertEqual(data["pipeline_step_count"], 12)
        self.assertIn("incident", data)
        self.assertIn("classification", data)
        self.assertIn("risk", data)
        self.assertIn("facility", data)
        self.assertIn("emergency_services", data)
        self.assertIn("routes", data)
        self.assertIn("alerts", data)

    def test_14_consistent_error_handling(self):
        """Requirement 22: Error contracts must return { success: false, error: { code, message } }."""
        resp = self.client.get("/api/v1/incidents/non-existent-id-999")
        self.assertEqual(resp.status_code, 404)
        err_data = resp.json()
        self.assertFalse(err_data["success"])
        self.assertIn("error", err_data)
        self.assertIn("code", err_data["error"])
        self.assertIn("message", err_data["error"])

if __name__ == "__main__":
    unittest.main()
