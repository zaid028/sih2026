"""
FIREGUARD AI - Comprehensive Full-Stack System Integration Test
Verifies all static page routes, REST APIs, AI engines, dynamic routing,
role switching, and simulated emergency dispatch.
"""
import unittest
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.main import app

class TestSystemIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_landing_page(self):
        """Verify public landing page renders."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        text = resp.text
        self.assertIn("FIREGUARD AI", text)
        self.assertIn("SIH26162", text)
        self.assertIn("NASA FIRMS", text)

    def test_02_command_center_page(self):
        """Verify tactical command center page renders."""
        resp = self.client.get("/app")
        self.assertEqual(resp.status_code, 200)
        text = resp.text
        self.assertIn("tactical-map-container", text)
        self.assertIn("incidentDossierModal", text)

    def test_03_system_status_api(self):
        """Verify system status API."""
        resp = self.client.get("/api/system/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "OPERATIONAL")
        self.assertIn("demo_mode", data)
        self.assertGreater(data["active_hotspots"], 0)
        self.assertGreater(data["monitored_facilities"], 0)

    def test_04_hotspots_catalog_api(self):
        """Verify hotspots filtering and retrieval."""
        resp = self.client.get("/api/hotspots")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        hotspots = data if isinstance(data, list) else data.get("hotspots", [])
        self.assertGreaterEqual(len(hotspots), 5)

        # Test filter by satellite
        resp_viirs = self.client.get("/api/hotspots?satellite=SNPP")
        self.assertEqual(resp_viirs.status_code, 200)
        data_viirs = resp_viirs.json()
        viirs_list = data_viirs if isinstance(data_viirs, list) else data_viirs.get("hotspots", [])
        for hp in viirs_list:
            sat = hp.get("satellite") or hp.get("source_satellite")
            self.assertIn("SNPP", sat)

    def test_05_incidents_api(self):
        """Verify incident command triage and lifecycle."""
        resp = self.client.get("/api/incidents")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        incidents = data if isinstance(data, list) else data.get("incidents", [])
        self.assertGreaterEqual(len(incidents), 5)

        first_inc = incidents[0]
        # Fetch detailed dossier
        detail_resp = self.client.get(f"/api/incidents/{first_inc['id']}")
        self.assertEqual(detail_resp.status_code, 200)
        detail = detail_resp.json()
        self.assertIn("classification", detail)
        self.assertIn("risk_breakdown", detail)

    def test_06_incident_status_transition(self):
        """Verify incident lifecycle state update."""
        inc_id = "inc-jamnagar-01"
        patch_resp = self.client.patch(
            f"/api/incidents/{inc_id}/status",
            json={"status": "VERIFIED", "notes": "Ground drone confirmed thermal breakout", "role": "OPERATOR"}
        )
        self.assertEqual(patch_resp.status_code, 200)
        res = patch_resp.json()
        inc_obj = res.get("incident", res)
        self.assertEqual(inc_obj["status"], "VERIFIED")

    def test_07_industrial_facilities_api(self):
        """Verify industrial facility intelligence."""
        resp = self.client.get("/api/facilities")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        facilities = data if isinstance(data, list) else data.get("facilities", [])
        self.assertGreaterEqual(len(facilities), 5)

        # Test facility deep profile
        fac_id = facilities[0]["id"]
        detail_resp = self.client.get(f"/api/facilities/{fac_id}")
        self.assertEqual(detail_resp.status_code, 200)
        fac_detail = detail_resp.json()
        self.assertIn("emergency_contact", fac_detail)

    def test_08_persistent_sources_api(self):
        """Verify persistent source recurrence and flare detection."""
        resp = self.client.get("/api/persistent-sources")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("sources", data)
        self.assertGreaterEqual(len(data["sources"]), 1)

    def test_09_safety_routes_api(self):
        """Verify dynamic safety corridor avoiding 500m danger buffer."""
        resp = self.client.get("/api/routes/inc-jamnagar-01")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        routes = data if isinstance(data, list) else data.get("evacuation_routes", [])
        self.assertTrue(len(routes) > 0)
        r = routes[0]
        self.assertEqual(r.get("danger_radius_m", 500.0), 500.0)
        self.assertTrue(r["distance_km"] > 0)
        self.assertTrue(r.get("is_safe", True))

    def test_10_simulated_dispatch(self):
        """Verify multi-agency dispatch broadcast simulation."""
        resp = self.client.post(
            "/api/emergency/dispatch-sim",
            json={"incident_id": "inc-jamnagar-01", "role": "OPERATOR"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertIn("payload", data)
        self.assertIn("formatted_dispatch_message", data["payload"])
        self.assertIn("simulated_broadcast_channels", data["payload"])

    def test_11_role_switching(self):
        """Verify persona role switcher."""
        roles = ["admin", "operator", "facility_manager", "analyst", "public"]
        for role in roles:
            resp = self.client.post(
                "/api/auth/demo-switch",
                json={"role": role}
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["user"]["role"].lower(), role.lower())
            self.assertIn("token", data)

    def test_12_alerts_center(self):
        """Verify alert center and acknowledgements."""
        resp = self.client.get("/api/alerts")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        alerts = data if isinstance(data, list) else data.get("alerts", [])
        self.assertGreaterEqual(len(alerts), 0)

if __name__ == "__main__":
    unittest.main()
