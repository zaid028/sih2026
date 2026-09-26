"""
FIREGUARD AI - Automated Unit & System Test Suite
Tests AI classification, risk scoring, persistence detection, dynamic routing, and API responses.
"""
import unittest
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.services.classifier import FireClassifier
from app.services.risk_scorer import RiskScorer
from app.services.persistent_detector import PersistentSourceDetector
from app.services.routing_engine import RoutingEngine

class TestFireGuardCore(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_ai_classifier_industrial_fire(self):
        """Test AI classification accurately identifies high-risk industrial fires."""
        hotspot = {"frp_mw": 85.0, "brightness_k": 385.0, "confidence": 95, "daynight": "N"}
        facility = {"name": "Jamnagar Refining Complex", "facility_type": "refinery"}
        result = FireClassifier.classify_hotspot(hotspot, facility, distance_m=180.0)

        self.assertEqual(result["class_code"], "INDUSTRIAL_FIRE")
        self.assertGreater(result["confidence_pct"], 80.0)
        self.assertTrue(len(result["top_factors"]) > 0)
        self.assertIn("Jamnagar", result["explanation_text"])

    def test_ai_classifier_false_positive(self):
        """Test AI classifier filters low-confidence solar reflections."""
        hotspot = {"frp_mw": 5.0, "brightness_k": 310.0, "confidence": 30, "daynight": "D"}
        result = FireClassifier.classify_hotspot(hotspot, None, distance_m=4000.0)

        self.assertEqual(result["class_code"], "FALSE_POS")

    def test_risk_scorer_critical(self):
        """Test risk score reaches CRITICAL tier for close proximity high-FRP fires."""
        hotspot = {"frp_mw": 95.0, "brightness_k": 390.0, "confidence": 95}
        facility = {"name": "Dahej Petrochemical", "hazard_category": "HAZMAT_TIER_1"}
        risk = RiskScorer.calculate_risk(
            hotspot, facility, distance_to_facility_m=120.0,
            classification_code="INDUSTRIAL_FIRE", near_population_km=0.8, near_critical_infra=True
        )

        self.assertEqual(risk["risk_tier"], "CRITICAL")
        self.assertGreaterEqual(risk["total_score"], 80.0)
        self.assertIn("factor_breakdown", risk)
        self.assertTrue(len(risk["bullet_reasons"]) >= 4)

    def test_persistent_source_clustering(self):
        """Test spatiotemporal clustering detects recurring thermal sources."""
        hotspots = [
            {"latitude": 22.3920, "longitude": 69.8650, "frp_mw": 25.0, "acquisition_date": "2026-09-20"},
            {"latitude": 22.3922, "longitude": 69.8652, "frp_mw": 28.0, "acquisition_date": "2026-09-22"},
            {"latitude": 22.3921, "longitude": 69.8651, "frp_mw": 26.5, "acquisition_date": "2026-09-25"}
        ]
        facilities = [{"name": "Jamnagar Refinery", "facility_type": "refinery", "latitude": 22.390, "longitude": 69.860}]
        sources = PersistentSourceDetector.analyze_persistent_sources(hotspots, facilities)

        self.assertGreaterEqual(len(sources), 1)
        self.assertEqual(sources[0]["status"], "NORMAL_OPERATIONAL")

    def test_routing_engine_hazard_buffer(self):
        """Test routing engine computes 500m danger buffer and safe bypass."""
        emerg = [
            {"name": "Civil Hospital", "facility_type": "hospital", "latitude": 22.468, "longitude": 70.065, "phone": "108"}
        ]
        plan = RoutingEngine.generate_evacuation_plan(22.385, 69.871, emerg)

        self.assertIn("danger_buffers", plan)
        self.assertEqual(plan["danger_buffers"]["blast_zone_red"]["radius_m"], 500.0)
        self.assertTrue(len(plan["evacuation_routes"]) > 0)
        route = plan["evacuation_routes"][0]
        self.assertTrue(len(route["safe_route_green"]) > 0)

    def test_api_system_status(self):
        """Test GET /api/system/status endpoint."""
        resp = self.app.get("/api/system/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OPERATIONAL")
        self.assertTrue(data["active_hotspots"] > 0)

    def test_api_incidents(self):
        """Test GET /api/incidents endpoint."""
        resp = self.app.get("/api/incidents")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("incidents", data)
        self.assertTrue(len(data["incidents"]) > 0)

    def test_api_analytics_charts(self):
        """Test GET /api/analytics/charts endpoint."""
        resp = self.app.get("/api/analytics/charts")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("classification_distribution", data)
        self.assertIn("temporal_trend", data)

if __name__ == "__main__":
    unittest.main()
