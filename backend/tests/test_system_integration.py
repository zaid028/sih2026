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

from app.main import app

class TestSystemIntegration(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_01_landing_page(self):
        """Verify public landing page renders."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        text = resp.get_data(as_text=True)
        self.assertIn("FIREGUARD AI", text)
        self.assertIn("SIH26162", text)
        self.assertIn("NASA FIRMS", text)

    def test_02_command_center_page(self):
        """Verify tactical command center page renders."""
        resp = self.client.get("/app")
        self.assertEqual(resp.status_code, 200)
        text = resp.get_data(as_text=True)
        self.assertIn("tactical-map-container", text)
        self.assertIn("incidentDossierModal", text)
        self.assertIn("mobileSafetyModeModal", text)

    def test_03_system_status_api(self):
        """Verify system status API."""
        resp = self.client.get("/api/system/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OPERATIONAL")
        self.assertIn("demo_mode", data)
        self.assertGreater(data["active_hotspots"], 0)
        self.assertGreater(data["monitored_facilities"], 0)

    def test_04_hotspots_catalog_api(self):
        """Verify hotspots filtering and retrieval."""
        resp = self.client.get("/api/hotspots")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("hotspots", data)
        self.assertGreaterEqual(len(data["hotspots"]), 5)

        # Test filter by satellite
        resp_viirs = self.client.get("/api/hotspots?satellite=VIIRS_SNPP")
        self.assertEqual(resp_viirs.status_code, 200)
        data_viirs = resp_viirs.get_json()
        for hp in data_viirs["hotspots"]:
            self.assertEqual(hp["source_satellite"], "VIIRS_SNPP")

    def test_05_incidents_api(self):
        """Verify incident command triage and lifecycle."""
        resp = self.client.get("/api/incidents")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertGreaterEqual(len(data["incidents"]), 5)

        first_inc = data["incidents"][0]
        # Fetch detailed dossier
        detail_resp = self.client.get(f"/api/incidents/{first_inc['id']}")
        self.assertEqual(detail_resp.status_code, 200)
        detail = detail_resp.get_json()
        self.assertIn("ai_classification", detail)
        self.assertIn("risk_breakdown", detail)

    def test_06_incident_status_transition(self):
        """Verify incident lifecycle state update."""
        inc_id = "INC-2026-0812"
        patch_resp = self.client.patch(
            f"/api/incidents/{inc_id}/status",
            data=json.dumps({"status": "VERIFIED", "notes": "Ground drone confirmed thermal breakout"}),
            content_type="application/json"
        )
        self.assertEqual(patch_resp.status_code, 200)
        res = patch_resp.get_json()
        self.assertEqual(res["incident"]["status"], "VERIFIED")

    def test_07_industrial_facilities_api(self):
        """Verify industrial facility intelligence."""
        resp = self.client.get("/api/facilities")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertGreaterEqual(len(data["facilities"]), 5)

        # Test facility deep profile
        fac_id = data["facilities"][0]["id"]
        detail_resp = self.client.get(f"/api/facilities/{fac_id}")
        self.assertEqual(detail_resp.status_code, 200)
        fac_detail = detail_resp.get_json()
        self.assertIn("emergency_resources", fac_detail)

    def test_08_persistent_sources_api(self):
        """Verify persistent source recurrence and flare detection."""
        resp = self.client.get("/api/persistent-sources")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("sources", data)
        self.assertGreaterEqual(len(data["sources"]), 1)

    def test_09_safety_routes_api(self):
        """Verify dynamic safety corridor avoiding 500m danger buffer."""
        resp = self.client.get("/api/routes/INC-2026-0812")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("danger_buffers", data)
        self.assertIn("blast_zone_red", data["danger_buffers"])
        self.assertEqual(data["danger_buffers"]["blast_zone_red"]["radius_m"], 500.0)
        self.assertIn("evacuation_routes", data)
        self.assertTrue(len(data["evacuation_routes"]) > 0)
        r = data["evacuation_routes"][0]
        self.assertTrue(r["distance_km"] > 0)
        self.assertTrue(len(r["safe_route_green"]) >= 2)

    def test_10_simulated_dispatch(self):
        """Verify multi-agency dispatch broadcast simulation."""
        resp = self.client.post(
            "/api/emergency/dispatch-sim",
            data=json.dumps({"incident_id": "INC-2026-0812"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
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
                data=json.dumps({"role": role}),
                content_type="application/json"
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data["user"]["role"], role)
            self.assertIn("token", data)

    def test_12_alerts_center(self):
        """Verify alert center and acknowledgements."""
        resp = self.client.get("/api/alerts")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("alerts", data)
        if len(data["alerts"]) > 0:
            alt_id = data["alerts"][0]["id"]
            ack_resp = self.client.patch(f"/api/alerts/{alt_id}/ack")
            self.assertEqual(ack_resp.status_code, 200)
            self.assertTrue(ack_resp.get_json()["alert"]["is_acknowledged"])

if __name__ == "__main__":
    unittest.main()
