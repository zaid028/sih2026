"""
FIREGUARD AI - Comprehensive Initial Data Seeding
Seeds realistic facilities, hotspots, incidents, emergency infrastructure, contacts,
and demo credentials for instant out-of-the-box demonstration.
"""
from datetime import datetime, timedelta
import json
import logging
from app.database import SessionLocal, Base, engine
from app.models import (
    User, IndustrialFacility, ThermalHotspot, Incident,
    AIClassification, RiskScore, EmergencyFacility, EmergencyContact,
    Alert, Route, AuditLog
)
from app.services.auth_service import AuthService
from app.services.classifier import FireClassifier
from app.services.risk_scorer import RiskScorer
from app.services.routing_engine import RoutingEngine

logger = logging.getLogger(__name__)

def seed_database():
    """Initializes tables and seeds high-fidelity initial data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Avoid duplicate seeding if users exist
    if db.query(User).first():
        db.close()
        return

    logger.info("Seeding FIREGUARD AI database with tactical operational data...")

    # 1. Users
    users_data = [
        {"username": "admin", "email": "admin@fireguard.gov.in", "role": "admin", "full_name": "Chief Controller Sharma", "org": "National Disaster Management Authority (NDMA)"},
        {"username": "operator", "email": "operator@fireguard.gov.in", "role": "operator", "full_name": "Senior Operator Rao", "org": "Emergency Operations Center (EOC)"},
        {"username": "manager", "email": "manager@jamnagar.refinery.in", "role": "facility_manager", "full_name": "K. Patel (VP Health & Safety)", "org": "Jamnagar Refining & Petrochemical Complex"},
        {"username": "analyst", "email": "analyst@fireguard.gov.in", "role": "analyst", "full_name": "Dr. Ananya Sen", "org": "Geospatial Satellite Analytics Directorate"},
        {"username": "citizen", "email": "citizen@public.org", "role": "public", "full_name": "Public Observer", "org": "Civilian Emergency Awareness"}
    ]

    for u in users_data:
        user = User(
            username=u["username"],
            email=u["email"],
            password_hash=AuthService.hash_password("Admin@123" if u["role"] == "admin" else f"{u['username'].capitalize()}@123"),
            full_name=u["full_name"],
            role=u["role"],
            organization=u["org"]
        )
        db.add(user)
    db.commit()

    # 2. Industrial Facilities across India's Key Industrial Hubs
    facilities_data = [
        {
            "name": "Reliance Jamnagar Refining Complex",
            "type": "refinery",
            "lat": 22.3840, "lon": 69.8680,
            "hazard": "HAZMAT_TIER_1",
            "address": "Motikhavdi, Jamnagar, Gujarat 361140",
            "district": "Jamnagar", "state": "Gujarat",
            "contact_name": "Col. V. Mehta (Head of Plant Security)", "contact_phone": "+91 288 400 1200",
            "poly": [[22.378, 69.860], [22.392, 69.862], [22.391, 69.878], [22.376, 69.875], [22.378, 69.860]]
        },
        {
            "name": "Nayara Energy Vadinar Refinery",
            "type": "refinery",
            "lat": 22.4210, "lon": 69.7340,
            "hazard": "HAZMAT_TIER_1",
            "address": "Vadinar, Devbhumi Dwarka, Gujarat 361010",
            "district": "Devbhumi Dwarka", "state": "Gujarat",
            "contact_name": "R. K. Verma (Safety Commander)", "contact_phone": "+91 283 366 1111",
            "poly": [[22.415, 69.725], [22.428, 69.728], [22.426, 69.742], [22.412, 69.740], [22.415, 69.725]]
        },
        {
            "name": "ONGC Petro additions Ltd (OPaL) Dahej",
            "type": "chemical_plant",
            "lat": 21.7110, "lon": 72.5450,
            "hazard": "HAZMAT_TIER_1",
            "address": "Dahej PCPIR, Vagra, Bharuch, Gujarat 392130",
            "district": "Bharuch", "state": "Gujarat",
            "contact_name": "S. Majumdar (Emergency Response Lead)", "contact_phone": "+91 264 126 5000",
            "poly": [[21.705, 72.538], [21.718, 72.540], [21.716, 72.555], [21.702, 72.552], [21.705, 72.538]]
        },
        {
            "name": "HPCL Visakh Refinery",
            "type": "refinery",
            "lat": 17.6880, "lon": 83.2490,
            "hazard": "HAZMAT_TIER_1",
            "address": "Malkapuram, Visakhapatnam, Andhra Pradesh 530011",
            "district": "Visakhapatnam", "state": "Andhra Pradesh",
            "contact_name": "P. Ramana (Refinery Safety GM)", "contact_phone": "+91 891 289 4000",
            "poly": [[17.682, 83.242], [17.694, 83.244], [17.692, 83.258], [17.680, 83.255], [17.682, 83.242]]
        },
        {
            "name": "Rashtriya Ispat Nigam Ltd (RINL) Vizag Steel",
            "type": "steel_mill",
            "lat": 17.6230, "lon": 83.1810,
            "hazard": "TIER_2",
            "address": "Visakhapatnam Steel Plant, Vizag, Andhra Pradesh 530031",
            "district": "Visakhapatnam", "state": "Andhra Pradesh",
            "contact_name": "M. Sanyal (Blast Furnace Safety Controller)", "contact_phone": "+91 891 251 8888",
            "poly": [[17.615, 83.172], [17.632, 83.175], [17.630, 83.192], [17.612, 83.189], [17.615, 83.172]]
        },
        {
            "name": "BPCL Mumbai Refinery Chembur",
            "type": "refinery",
            "lat": 19.0120, "lon": 72.9010,
            "hazard": "HAZMAT_TIER_1",
            "address": "Mahul Road, Chembur, Mumbai, Maharashtra 400074",
            "district": "Mumbai Suburban", "state": "Maharashtra",
            "contact_name": "D. Kulkarni (Chief Fire Officer BPCL)", "contact_phone": "+91 22 2553 3000",
            "poly": [[19.006, 72.895], [19.018, 72.898], [19.016, 72.910], [19.004, 72.906], [19.006, 72.895]]
        },
        {
            "name": "Rashtriya Chemicals & Fertilizers (RCF) Trombay",
            "type": "chemical_plant",
            "lat": 19.0050, "lon": 72.8910,
            "hazard": "HAZMAT_TIER_1",
            "address": "Administrative Bldg, Chembur, Mumbai 400074",
            "district": "Mumbai Suburban", "state": "Maharashtra",
            "contact_name": "A. Deshmukh (Hazmat Safety Lead)", "contact_phone": "+91 22 2552 2000",
            "poly": [[18.999, 72.885], [19.010, 72.887], [19.008, 72.898], [18.997, 72.895], [18.999, 72.885]]
        },
        {
            "name": "Chennai Petroleum Corporation (CPCL) Manali",
            "type": "refinery",
            "lat": 13.1650, "lon": 80.2620,
            "hazard": "HAZMAT_TIER_1",
            "address": "Manali, Chennai, Tamil Nadu 600068",
            "district": "Chennai", "state": "Tamil Nadu",
            "contact_name": "T. Sundaram (General Manager EHS)", "contact_phone": "+91 44 2594 4000",
            "poly": [[13.158, 80.255], [13.172, 80.258], [13.170, 80.270], [13.156, 80.267], [13.158, 80.255]]
        }
    ]

    saved_facilities = []
    for f in facilities_data:
        fac = IndustrialFacility(
            name=f["name"],
            facility_type=f["type"],
            latitude=f["lat"],
            longitude=f["lon"],
            hazard_category=f["hazard"],
            address=f["address"],
            district=f["district"],
            state=f["state"],
            emergency_contact_name=f["contact_name"],
            emergency_contact_phone=f["contact_phone"],
            polygon_coords=json.dumps(f["poly"])
        )
        db.add(fac)
        saved_facilities.append(fac)
    db.commit()

    # 3. Emergency Infrastructure (Hospitals, Fire Stations, Police, Shelters)
    emergency_facilities_data = [
        # Jamnagar
        {"name": "GG Government Hospital & Trauma Centre", "type": "hospital", "lat": 22.4680, "lon": 70.0650, "phone": "+91 288 255 0200", "address": "Indira Marg, Jamnagar", "beds": 450},
        {"name": "Jamnagar Industrial Area Fire & Rescue HQ", "type": "fire_station", "lat": 22.4010, "lon": 69.8920, "phone": "+91 288 271 0101", "address": "GIDC Phase-2, Jamnagar", "beds": 0},
        {"name": "District Cyclone & Emergency Shelter Jamnagar", "type": "shelter", "lat": 22.4350, "lon": 69.9500, "phone": "+91 288 267 1077", "address": "Civil Lines, Jamnagar", "beds": 600},

        # Dahej / Bharuch
        {"name": "Dahej GIDC Hazmat Fire Station", "type": "fire_station", "lat": 21.7220, "lon": 72.5620, "phone": "+91 264 125 0101", "address": "PCPIR Central, Dahej", "beds": 0},
        {"name": "Bharuch Civil Hospital & Emergency Trauma Unit", "type": "hospital", "lat": 21.7080, "lon": 72.9980, "phone": "+91 264 224 0100", "address": "Station Road, Bharuch", "beds": 350},
        {"name": "GIDC Evacuation Assembly Center Dahej", "type": "shelter", "lat": 21.7350, "lon": 72.5800, "phone": "+91 264 125 0222", "address": "Sector 4, Dahej", "beds": 800},

        # Visakhapatnam
        {"name": "King George Hospital (KGH) Super Speciality Trauma Centre", "type": "hospital", "lat": 17.7080, "lon": 83.3050, "phone": "+91 891 256 4891", "address": "Maharanipeta, Visakhapatnam", "beds": 1200},
        {"name": "Visakhapatnam Industrial Corridor Fire Station", "type": "fire_station", "lat": 17.6740, "lon": 83.2210, "phone": "+91 891 251 0101", "address": "Gajuwaka Industrial Belt, Vizag", "beds": 0},
        {"name": "Visakhapatnam Port Disaster Shelter", "type": "shelter", "lat": 17.6950, "lon": 83.2850, "phone": "+91 891 287 3111", "address": "Port Area, Vizag", "beds": 500},

        # Mumbai Chembur
        {"name": "BARC Hospital & Chemical Burn Treatment Center", "type": "hospital", "lat": 19.0430, "lon": 72.9280, "phone": "+91 22 2559 8000", "address": "Anushaktinagar, Chembur, Mumbai", "beds": 390},
        {"name": "Chembur Industrial Fire Command Station", "type": "fire_station", "lat": 19.0280, "lon": 72.8980, "phone": "+91 22 2522 0101", "address": "SVT Road, Chembur, Mumbai", "beds": 0},

        # Chennai Manali
        {"name": "Government Peripheral Hospital Manali", "type": "hospital", "lat": 13.1780, "lon": 80.2480, "phone": "+91 44 2594 1200", "address": "Nedunchezhian Salai, Manali, Chennai", "beds": 200},
        {"name": "Manali Petrochemical Fire Station", "type": "fire_station", "lat": 13.1690, "lon": 80.2710, "phone": "+91 44 2594 0101", "address": "CPCL Approach Road, Manali", "beds": 0}
    ]

    saved_emergency = []
    for ef in emergency_facilities_data:
        fac = EmergencyFacility(
            name=ef["name"],
            facility_type=ef["type"],
            latitude=ef["lat"],
            longitude=ef["lon"],
            phone=ef["phone"],
            address=ef["address"],
            bed_capacity=ef["beds"]
        )
        db.add(fac)
        saved_emergency.append(fac)
    db.commit()

    # 4. Emergency Contacts
    contacts_data = [
        {"agency": "National Disaster Response Force (NDRF) 6th Bn", "type": "NDRF", "phone": "+91 11 2436 3260", "email": "hq.ndrf@nic.in", "district": "National", "state": "All-India", "primary": True},
        {"agency": "Gujarat State Emergency Operation Centre (SEOC)", "type": "SDMA", "phone": "+91 79 2325 1900", "email": "seoc.guj@nic.in", "district": "Gandhinagar", "state": "Gujarat", "primary": True},
        {"agency": "Andhra Pradesh State Disaster Management Authority", "type": "SDMA", "phone": "+91 863 237 7103", "email": "apsdma@ap.gov.in", "district": "Tadepalli", "state": "Andhra Pradesh", "primary": True},
        {"agency": "Maharashtra State Disaster Management Cell", "type": "SDMA", "phone": "+91 22 2202 7990", "email": "controlroom@maharashtra.gov.in", "district": "Mumbai", "state": "Maharashtra", "primary": True},
        {"agency": "Tamil Nadu State Disaster Management Agency", "type": "SDMA", "phone": "+91 44 2859 3990", "email": "tnsdma@tn.gov.in", "district": "Chennai", "state": "Tamil Nadu", "primary": True},
        {"agency": "Central Fire Control & Hazmat Dispatch", "type": "FIRE_DEPARTMENT", "phone": "101", "email": "fire.emergency@gov.in", "district": "National", "state": "All-India", "primary": True},
        {"agency": "National Emergency Ambulance Response", "type": "AMBULANCE", "phone": "108", "email": "ambulance.dispatch@emri.in", "district": "National", "state": "All-India", "primary": True},
        {"agency": "Petroleum & Explosives Safety Organisation (PESO)", "type": "FACILITY_MGR", "phone": "+91 712 251 0248", "email": "explosives@explosives.gov.in", "district": "Nagpur HQ", "state": "All-India", "primary": False}
    ]

    for c in contacts_data:
        contact = EmergencyContact(
            agency_name=c["agency"],
            contact_type=c["type"],
            phone=c["phone"],
            email=c["email"],
            district=c["district"],
            state=c["state"],
            is_primary=c["primary"]
        )
        db.add(contact)
    db.commit()

    # 5. Hotspots & Incidents
    now = datetime.utcnow()
    hotspot_scenarios = [
        # SCENARIO 1: CRITICAL RUNAWAY INDUSTRIAL FIRE (Jamnagar FCCU)
        {
            "inc_id": "INC-2026-0812",
            "title": "Jamnagar FCCU Unit-4 High-Thermal Conflagration",
            "sat": "VIIRS_SNPP",
            "lat": 22.3854, "lon": 69.8712,
            "bright": 388.4, "frp": 84.5, "conf": 94, "daynight": "N",
            "fac_idx": 0, "preset_class": "INDUSTRIAL_FIRE", "status": "DISPATCH_REQUIRED",
            "pop_dist": 0.9, "infra": True
        },
        # SCENARIO 2: CRITICAL INDUSTRIAL FIRE (Dahej Polymer Storage)
        {
            "inc_id": "INC-2026-0813",
            "title": "Dahej Petrochemical Polymer Storage Facility Blaze",
            "sat": "VIIRS_SNPP",
            "lat": 21.7124, "lon": 72.5488,
            "bright": 395.1, "frp": 96.2, "conf": 96, "daynight": "D",
            "fac_idx": 2, "preset_class": "INDUSTRIAL_FIRE", "status": "REPORTED",
            "pop_dist": 1.2, "infra": True
        },
        # SCENARIO 3: HIGH RISK INDUSTRIAL INCIDENT (Chembur BPCL Hydrocracker)
        {
            "inc_id": "INC-2026-0814",
            "title": "Chembur BPCL Hydrocracker Thermal Anomaly",
            "sat": "VIIRS_SNPP",
            "lat": 19.0145, "lon": 72.9023,
            "bright": 376.8, "frp": 64.3, "conf": 89, "daynight": "N",
            "fac_idx": 5, "preset_class": "INDUSTRIAL_FIRE", "status": "VERIFIED",
            "pop_dist": 0.6, "infra": True
        },
        # SCENARIO 4: ROUTINE PERSISTENT GAS FLARE (Jamnagar Flare Stack)
        {
            "inc_id": "INC-2026-0815",
            "title": "Jamnagar Hydrocarbon Refinery Routine Flare Stack",
            "sat": "VIIRS_NOAA20",
            "lat": 22.3921, "lon": 69.8650,
            "bright": 348.2, "frp": 26.8, "conf": 88, "daynight": "N",
            "fac_idx": 0, "preset_class": "GAS_FLARE", "status": "VERIFIED",
            "pop_dist": 2.5, "infra": False
        },
        # SCENARIO 5: PERSISTENT INDUSTRIAL SOURCE (RINL Vizag Blast Furnace)
        {
            "inc_id": "INC-2026-0816",
            "title": "RINL Vizag Steel Continuous Blast Furnace Tapping",
            "sat": "VIIRS_NOAA20",
            "lat": 17.6250, "lon": 83.1840,
            "bright": 361.5, "frp": 48.0, "conf": 85, "daynight": "D",
            "fac_idx": 4, "preset_class": "PERSISTENT_IND", "status": "RESOLVED",
            "pop_dist": 2.8, "infra": True
        },
        # SCENARIO 6: HIGH-RISK THERMAL BREAKOUT (Vizag HPCL Refinery Tank Farm)
        {
            "inc_id": "INC-2026-0817",
            "title": "Vizag HPCL Refinery Fuel Storage Perimeter Thermal Spike",
            "sat": "VIIRS_SNPP",
            "lat": 17.6892, "lon": 83.2514,
            "bright": 382.6, "frp": 72.0, "conf": 91, "daynight": "N",
            "fac_idx": 3, "preset_class": "INDUSTRIAL_FIRE", "status": "IN_PROGRESS",
            "pop_dist": 1.1, "infra": True
        },
        # SCENARIO 7: MUNICIPAL WASTE BURNING (Vizag City Outer)
        {
            "inc_id": "INC-2026-0818",
            "title": "Vizag Suburban Open Landfill Waste Smolder",
            "sat": "MODIS_Aqua",
            "lat": 17.7510, "lon": 83.3100,
            "bright": 324.0, "frp": 9.5, "conf": 62, "daynight": "D",
            "fac_idx": None, "preset_class": "WASTE_BURN", "status": "RESOLVED",
            "pop_dist": 1.5, "infra": False
        },
        # SCENARIO 8: FALSE POSITIVE (Dahej Coastal Salt Pan Glint)
        {
            "inc_id": "INC-2026-0819",
            "title": "Dahej Coastal High-Albedo Solar Reflection",
            "sat": "MODIS_Terra",
            "lat": 21.6840, "lon": 72.5890,
            "bright": 312.4, "frp": 6.8, "conf": 38, "daynight": "D",
            "fac_idx": 2, "preset_class": "FALSE_POS", "status": "FALSE_ALARM",
            "pop_dist": 4.0, "infra": False
        },
        # SCENARIO 9: FOREST FIRE IN FOOTHILLS
        {
            "inc_id": "INC-2026-0820",
            "title": "Narmada River Foothill Forest Fire",
            "sat": "MODIS_Aqua",
            "lat": 21.8450, "lon": 73.2100,
            "bright": 341.2, "frp": 29.5, "conf": 82, "daynight": "D",
            "fac_idx": None, "preset_class": "FOREST_FIRE", "status": "VERIFIED",
            "pop_dist": 5.2, "infra": False
        }
    ]

    for s in hotspot_scenarios:
        fac = saved_facilities[s["fac_idx"]] if s["fac_idx"] is not None else None
        
        # Calculate distance to facility
        dist_m = None
        if fac:
            dist_m = RoutingEngine.DANGER_RADIUS_M * 0.7 if "FIRE" in s["preset_class"] else 420.0

        det_time = now - timedelta(minutes=int(s["inc_id"][-2:]) * 7)

        hp = ThermalHotspot(
            source_satellite=s["sat"],
            latitude=s["lat"],
            longitude=s["lon"],
            brightness_k=s["bright"],
            frp_mw=s["frp"],
            confidence=s["conf"],
            acquisition_date=det_time.strftime("%Y-%m-%d"),
            acquisition_time=det_time.strftime("%H%M"),
            daynight=s["daynight"],
            facility_id=fac.id if fac else None,
            distance_to_facility_m=dist_m,
            is_persistent=s["preset_class"] in ["PERSISTENT_IND", "GAS_FLARE"],
            detected_at=det_time
        )
        db.add(hp)
        db.flush()

        # Run AI Classification
        ai_result = FireClassifier.classify_hotspot(
            hotspot={"frp_mw": s["frp"], "brightness_k": s["bright"], "confidence": s["conf"], "daynight": s["daynight"], "preset_type": s["preset_class"]},
            facility=fac.to_dict() if fac else None,
            distance_m=dist_m,
            historical_recurrence=6 if s["preset_class"] in ["PERSISTENT_IND", "GAS_FLARE"] else 1
        )

        # Run Risk Scoring
        risk_result = RiskScorer.calculate_risk(
            hotspot={"frp_mw": s["frp"], "brightness_k": s["bright"], "confidence": s["conf"]},
            facility=fac.to_dict() if fac else None,
            distance_to_facility_m=dist_m,
            classification_code=s["preset_class"],
            is_persistent=s["preset_class"] in ["PERSISTENT_IND", "GAS_FLARE"],
            near_population_km=s["pop_dist"],
            near_critical_infra=s["infra"]
        )

        # Create Incident
        inc = Incident(
            id=s["inc_id"],
            hotspot_id=hp.id,
            facility_id=fac.id if fac else None,
            title=s["title"],
            fire_class=s["preset_class"],
            risk_score=risk_result["total_score"],
            risk_level=risk_result["risk_tier"],
            status=s["status"],
            reported_by="AI_SATELLITE_PIPELINE",
            response_notes=ai_result["recommended_response"],
            detected_at=det_time
        )
        db.add(inc)
        db.flush()

        # Create AIClassification record
        ai_rec = AIClassification(
            incident_id=inc.id,
            primary_class=ai_result["class_name"],
            confidence_pct=ai_result["confidence_pct"],
            top_factors=json.dumps(ai_result["top_factors"]),
            explanation_text=ai_result["explanation_text"],
            recommended_response=ai_result["recommended_response"]
        )
        db.add(ai_rec)

        # Create RiskScore record
        risk_rec = RiskScore(
            incident_id=inc.id,
            total_score=risk_result["total_score"],
            risk_tier=risk_result["risk_tier"],
            factor_breakdown=json.dumps(risk_result["factor_breakdown"]),
            why_explanation=risk_result["why_explanation"]
        )
        db.add(risk_rec)

        # Create Alert if Risk is High or Critical
        if risk_result["risk_tier"] in ["CRITICAL", "HIGH"]:
            alert = Alert(
                id=f"ALT-{s['inc_id'][-4:]}",
                incident_id=inc.id,
                alert_type="INDUSTRIAL_FIRE_EMERGENCY" if s["preset_class"] == "INDUSTRIAL_FIRE" else "HIGH_THERMAL_ANOMALY",
                severity=risk_result["risk_tier"],
                message=f"CRITICAL: {s['title']} detected near {fac.name if fac else 'coordinates'}. FRP: {s['frp']} MW. Immediate hazard response required.",
                is_acknowledged=s["status"] == "RESOLVED",
                sent_at=det_time
            )
            db.add(alert)

        # Pre-generate Evacuation Route for Industrial Fire incidents
        if s["preset_class"] == "INDUSTRIAL_FIRE":
            evac_plan = RoutingEngine.generate_evacuation_plan(
                s["lat"], s["lon"], [ef.to_dict() for ef in saved_emergency]
            )
            if evac_plan["evacuation_routes"]:
                r_info = evac_plan["evacuation_routes"][0]
                target_ef = next((ef for ef in saved_emergency if ef.name == r_info["destination_name"]), saved_emergency[0])
                route_rec = Route(
                    id=f"RTE-{s['inc_id'][-4:]}",
                    incident_id=inc.id,
                    target_facility_id=target_ef.id,
                    route_type="SAFE_EVACUATION",
                    distance_km=r_info["distance_km"],
                    estimated_time_min=r_info["estimated_time_min"],
                    waypoints_json=json.dumps(r_info["safe_route_green"]),
                    avoids_hazard_zone=True
                )
                db.add(route_rec)

    db.commit()

    # 6. Audit Log initial entry
    audit = AuditLog(
        user_id=1,
        action="SYSTEM_INITIALIZATION",
        target_type="DATABASE",
        target_id="ALL",
        details="FIREGUARD AI tactical system booted with NASA FIRMS, OSM facilities, and AI classification models."
    )
    db.add(audit)
    db.commit()
    db.close()
    logger.info("Database seeding successfully completed!")
