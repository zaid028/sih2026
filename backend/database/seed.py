"""
FIREGUARD AI - Database Initializer & Rich Seed Data
Populates users, industrial facilities across India, emergency facilities, contacts, persistent sources, and active incidents.
"""
from datetime import datetime
import json
import uuid
from sqlalchemy.orm import Session
from backend.models.entities import (
    User, IndustrialFacility, ThermalHotspot, Incident, IncidentEvent,
    AIPrediction, RiskAssessment, PersistentSource, EmergencyService,
    EmergencyContact, Alert, Route
)
from backend.utils.security import hash_password

def seed_database_if_empty(db: Session):
    """Seed database with realistic operational data if empty."""
    if db.query(User).first():
        return  # Already seeded

    print("[FIREGUARD DB] Seeding initial database...")

    # 1. Users with RBAC roles
    users = [
        User(
            id=str(uuid.uuid4()),
            username="admin",
            email="admin@fireguard.gov.in",
            hashed_password=hash_password("admin123"),
            role="ADMIN",
            full_name="National Director S. K. Varma",
            agency="National Disaster Management Authority (NDMA)",
            phone="+91 11 2670 1700"
        ),
        User(
            id=str(uuid.uuid4()),
            username="operator",
            email="operator@fireguard.gov.in",
            hashed_password=hash_password("operator123"),
            role="OPERATOR",
            full_name="Commander Rajesh Sharma",
            agency="State Emergency Operation Center (SEOC) Gujarat",
            phone="+91 79 2325 1900"
        ),
        User(
            id=str(uuid.uuid4()),
            username="analyst",
            email="analyst@fireguard.gov.in",
            hashed_password=hash_password("analyst123"),
            role="ANALYST",
            full_name="Dr. Ananya Sen",
            agency="ISRO / NRSC Earth Observation Division",
            phone="+91 40 2388 4000"
        ),
        User(
            id=str(uuid.uuid4()),
            username="facility_mgr",
            email="safety@reliance.com",
            hashed_password=hash_password("facility123"),
            role="FACILITY_MANAGER",
            full_name="Vikramaditya Mehta",
            agency="Reliance Jamnagar HSE Directorate",
            phone="+91 288 661 1000"
        ),
        User(
            id=str(uuid.uuid4()),
            username="public_user",
            email="public@citizen.in",
            hashed_password=hash_password("public123"),
            role="PUBLIC",
            full_name="Citizen Watch Desk",
            agency="Public Domain Access",
            phone="+91 99999 88888"
        )
    ]
    db.add_all(users)
    db.flush()

    # 2. Major Industrial Facilities in India
    facilities = [
        IndustrialFacility(
            id="fac-jamnagar-01",
            name="Reliance Industries Jamnagar Refinery & Petrochemical Complex",
            facility_type="Refinery & Petrochemical",
            industry_sector="Oil & Gas",
            latitude=22.4707,
            longitude=70.0577,
            address="Motikhavdi, Jamnagar, Gujarat 361140",
            state="Gujarat",
            district="Jamnagar",
            hazmat_level="LEVEL-4",
            active_units=42,
            flaring_authorized=True,
            normal_flaring_frp_mw=30.0,
            emergency_contact="Chief Safety Officer Jamnagar",
            emergency_phone="+91 288 661 2000"
        ),
        IndustrialFacility(
            id="fac-vadinar-02",
            name="Nayara Energy Vadinar Refinery Complex",
            facility_type="Refinery",
            industry_sector="Oil & Gas",
            latitude=22.3789,
            longitude=69.8512,
            address="Vadinar, Khambhalia, Devbhumi Dwarka, Gujarat 361010",
            state="Gujarat",
            district="Devbhumi Dwarka",
            hazmat_level="LEVEL-4",
            active_units=24,
            flaring_authorized=True,
            normal_flaring_frp_mw=25.0,
            emergency_contact="Vadinar Terminal Fire Station",
            emergency_phone="+91 2833 661 400"
        ),
        IndustrialFacility(
            id="fac-dahej-03",
            name="ONGC Petro additions Limited (OPaL) Dahej Complex",
            facility_type="Petrochemical Cracker",
            industry_sector="Chemical & Petrochemical",
            latitude=21.6881,
            longitude=72.5847,
            address="PCPIR Zone, Dahej Industrial Estate, Bharuch, Gujarat 392130",
            state="Gujarat",
            district="Bharuch",
            hazmat_level="LEVEL-4",
            active_units=18,
            flaring_authorized=True,
            normal_flaring_frp_mw=28.0,
            emergency_contact="OPaL Crisis Management Center",
            emergency_phone="+91 2641 282 000"
        ),
        IndustrialFacility(
            id="fac-vizag-04",
            name="HPCL Visakhapatnam Refinery Complex",
            facility_type="Refinery",
            industry_sector="Oil & Gas",
            latitude=17.6868,
            longitude=83.2185,
            address="Malkapuram, Visakhapatnam, Andhra Pradesh 530011",
            state="Andhra Pradesh",
            district="Visakhapatnam",
            hazmat_level="LEVEL-3",
            active_units=16,
            flaring_authorized=True,
            normal_flaring_frp_mw=20.0,
            emergency_contact="HPCL Disaster Response Cell",
            emergency_phone="+91 891 289 4000"
        ),
        IndustrialFacility(
            id="fac-rinl-05",
            name="Rashtriya Ispat Nigam Ltd (RINL) Vizag Steel Plant",
            facility_type="Steel Plant & Blast Furnace",
            industry_sector="Heavy Metallurgy",
            latitude=17.6254,
            longitude=83.1782,
            address="Kurmannapalem, Visakhapatnam, Andhra Pradesh 530031",
            state="Andhra Pradesh",
            district="Visakhapatnam",
            hazmat_level="LEVEL-3",
            active_units=28,
            flaring_authorized=False,
            normal_flaring_frp_mw=50.0,
            emergency_contact="Vizag Steel Fire Safety Control",
            emergency_phone="+91 891 251 8200"
        ),
        IndustrialFacility(
            id="fac-mumbai-06",
            name="BPCL Mumbai Refinery Chembur",
            facility_type="Refinery",
            industry_sector="Oil & Gas",
            latitude=19.0068,
            longitude=72.8981,
            address="Mahul Road, Chembur, Mumbai, Maharashtra 400074",
            state="Maharashtra",
            district="Mumbai Suburban",
            hazmat_level="LEVEL-4",
            active_units=20,
            flaring_authorized=True,
            normal_flaring_frp_mw=22.0,
            emergency_contact="BPCL Chembur Emergency Station",
            emergency_phone="+91 22 2553 3000"
        ),
        IndustrialFacility(
            id="fac-trombay-07",
            name="Rashtriya Chemicals & Fertilizers (RCF) Trombay Unit",
            facility_type="Fertilizer & Chemical Complex",
            industry_sector="Chemical",
            latitude=19.0345,
            longitude=72.9056,
            address="Administrative Building, Chembur, Mumbai, Maharashtra 400074",
            state="Maharashtra",
            district="Mumbai Suburban",
            hazmat_level="LEVEL-3",
            active_units=14,
            flaring_authorized=False,
            normal_flaring_frp_mw=15.0,
            emergency_contact="RCF Safety & Environment Cell",
            emergency_phone="+91 22 2552 2000"
        ),
        IndustrialFacility(
            id="fac-chennai-08",
            name="Chennai Petroleum Corporation Ltd (CPCL) Manali",
            facility_type="Refinery",
            industry_sector="Oil & Gas",
            latitude=13.1672,
            longitude=80.2641,
            address="Manali Industrial Area, Chennai, Tamil Nadu 600068",
            state="Tamil Nadu",
            district="Chennai",
            hazmat_level="LEVEL-3",
            active_units=18,
            flaring_authorized=True,
            normal_flaring_frp_mw=24.0,
            emergency_contact="CPCL Disaster Management Desk",
            emergency_phone="+91 44 2594 4000"
        )
    ]
    db.add_all(facilities)
    db.flush()

    # 3. Emergency Services (Hospitals, Fire, Police)
    emergency_services = [
        EmergencyService(
            id="es-hosp-01",
            name="Jamnagar Civil Hospital (GG Govt Hospital)",
            service_type="hospital",
            latitude=22.4680,
            longitude=70.0650,
            address="P.N. Marg, Indira Marg, Jamnagar, Gujarat",
            phone="+91 288 255 0204",
            capacity="1250 beds, Dedicated Burn ICU",
            operating_status="24x7 Operational",
            source="OpenStreetMap Overpass"
        ),
        EmergencyService(
            id="es-fire-02",
            name="Jamnagar Municipal Corporation Fire Station",
            service_type="fire_station",
            latitude=22.4715,
            longitude=70.0710,
            address="Station Road, Jamnagar, Gujarat",
            phone="+91 288 255 0101",
            capacity="8 Foam Tenders, 2 Hazmat Rescue Trucks",
            operating_status="24x7 Operational",
            source="OpenStreetMap Overpass"
        ),
        EmergencyService(
            id="es-pol-03",
            name="Meghpar Police Station (Refinery Zone Jurisdiction)",
            service_type="police",
            latitude=22.4550,
            longitude=70.0410,
            address="SH-6, Meghpar, Jamnagar, Gujarat",
            phone="+91 288 234 5100",
            capacity="Quick Reaction Tactical Force",
            operating_status="24x7 Operational",
            source="OpenStreetMap Overpass"
        ),
        EmergencyService(
            id="es-fire-04",
            name="Dahej PCPIR Mutual Aid Fire & Rescue Center",
            service_type="fire_station",
            latitude=21.6910,
            longitude=72.5790,
            address="PCPIR Central Corridor, Dahej, Gujarat",
            phone="+91 2641 256 101",
            capacity="Industrial Chemical Foam Units",
            operating_status="24x7 Operational",
            source="OpenStreetMap Overpass"
        ),
        EmergencyService(
            id="es-hosp-05",
            name="Bharuch Civil Hospital Trauma Center",
            service_type="hospital",
            latitude=21.7051,
            longitude=72.9959,
            address="Station Road, Bharuch, Gujarat",
            phone="+91 2642 242 100",
            capacity="450 beds",
            operating_status="24x7 Operational",
            source="OpenStreetMap Overpass"
        ),
        EmergencyService(
            id="es-fire-06",
            name="Mumbai Chembur Fire Station (Zone 5)",
            service_type="fire_station",
            latitude=19.0520,
            longitude=72.8990,
            address="Sion-Trombay Road, Chembur, Mumbai",
            phone="+91 22 2522 1010",
            capacity="Advanced Hazmat Snorkel Unit",
            operating_status="24x7 Operational",
            source="OpenStreetMap Overpass"
        ),
        EmergencyService(
            id="es-hosp-07",
            name="Shatabdi Municipal General Hospital Chembur",
            service_type="hospital",
            latitude=19.0580,
            longitude=72.9010,
            address="Govandi Station Road, Chembur, Mumbai",
            phone="+91 22 2556 4000",
            capacity="350 beds",
            operating_status="24x7 Operational",
            source="OpenStreetMap Overpass"
        ),
        EmergencyService(
            id="es-fire-08",
            name="Vizag Port & Industrial Fire Brigade",
            service_type="fire_station",
            latitude=17.6950,
            longitude=83.2750,
            address="Port Area, Visakhapatnam, Andhra Pradesh",
            phone="+91 891 256 4801",
            capacity="Heavy Foam Crash Tenders",
            operating_status="24x7 Operational",
            source="OpenStreetMap Overpass"
        ),
        EmergencyService(
            id="es-hosp-09",
            name="King George Hospital (KGH) Visakhapatnam",
            service_type="hospital",
            latitude=17.7080,
            longitude=83.3050,
            address="Collector Office Road, Maharanipeta, Visakhapatnam",
            phone="+91 891 256 4891",
            capacity="1500 beds, Regional Burns Specialty",
            operating_status="24x7 Operational",
            source="OpenStreetMap Overpass"
        ),
        EmergencyService(
            id="es-shelter-10",
            name="Jamnagar District Cyclone & Disaster Multi-Purpose Shelter",
            service_type="shelter",
            latitude=22.4820,
            longitude=70.0820,
            address="Bedeshwar Road, Jamnagar, Gujarat",
            phone="+91 288 266 1234",
            capacity="2500 civilians",
            operating_status="Ready on Alert",
            source="National Disaster Management Authority"
        )
    ]
    db.add_all(emergency_services)
    db.flush()

    # 4. Emergency Contacts (Requirement 14)
    contacts = [
        EmergencyContact(
            id=str(uuid.uuid4()),
            category="Fire Department",
            name="Chief Fire Officer K. N. Patel",
            agency="Gujarat State Fire Service (Jamnagar Zone)",
            designation="Chief Fire Officer",
            phone="+91 288 255 0101",
            email="cfo.jamnagar@gujarat.gov.in",
            state="Gujarat",
            district="Jamnagar",
            is_primary=True
        ),
        EmergencyContact(
            id=str(uuid.uuid4()),
            category="Police",
            name="Superintendent of Police",
            agency="Gujarat Police (Jamnagar District HQ)",
            designation="Superintendent of Police",
            phone="+91 288 255 0200",
            email="sp-jam@gujarat.gov.in",
            state="Gujarat",
            district="Jamnagar",
            is_primary=True
        ),
        EmergencyContact(
            id=str(uuid.uuid4()),
            category="Ambulance",
            name="108 GVK EMRI Regional Emergency Response",
            agency="Gujarat 108 Emergency Ambulance Service",
            designation="Central Dispatcher",
            phone="108",
            email="dispatch@gvkemri.org",
            state="Gujarat",
            district="Statewide",
            is_primary=True
        ),
        EmergencyContact(
            id=str(uuid.uuid4()),
            category="Disaster Management",
            name="District Collector & Magistrate Jamnagar",
            agency="District Disaster Management Authority (DDMA)",
            designation="Chairman DDMA",
            phone="+91 288 255 0100",
            email="collector-jam@gujarat.gov.in",
            state="Gujarat",
            district="Jamnagar",
            is_primary=True
        ),
        EmergencyContact(
            id=str(uuid.uuid4()),
            category="Facility Emergency Manager",
            name="Dr. Alok Verma",
            agency="Reliance Jamnagar HSE Directorate",
            designation="Head of Crisis Response",
            phone="+91 288 661 2222",
            email="alok.verma@ril.com",
            state="Gujarat",
            district="Jamnagar",
            is_primary=True
        ),
        EmergencyContact(
            id=str(uuid.uuid4()),
            category="Personal Emergency Contact",
            name="State Control Room Duty Officer",
            agency="Gujarat State Disaster Management Authority (GSDMA)",
            designation="Duty Officer",
            phone="+91 79 2325 9275",
            email="controlroom@gsdma.org",
            state="Gujarat",
            district="Gandhinagar",
            is_primary=False
        )
    ]
    db.add_all(contacts)
    db.flush()

    # 5. Persistent Thermal Sources (Requirement 7)
    persistent_sources = [
        PersistentSource(
            id="ps-jamnagar-flare",
            facility_id="fac-jamnagar-01",
            name="Reliance Jamnagar Elevated Flare Header #4",
            latitude=22.4712,
            longitude=70.0582,
            detection_count=28,
            detection_frequency=0.92,
            first_detected="2026-08-01",
            latest_detected="2026-09-26",
            avg_frp=28.5,
            avg_brightness=332.0,
            persistence_score=94.0,
            is_anomalous_spike=False,
            anomaly_z_score=0.45,
            status="MONITORED"
        ),
        PersistentSource(
            id="ps-dahej-cracker",
            facility_id="fac-dahej-03",
            name="OPaL Dahej Dual-Feed Cracker Unit Ground Flare",
            latitude=21.6885,
            longitude=72.5851,
            detection_count=22,
            detection_frequency=0.85,
            first_detected="2026-08-10",
            latest_detected="2026-09-26",
            avg_frp=34.2,
            avg_brightness=341.0,
            persistence_score=89.0,
            is_anomalous_spike=False,
            anomaly_z_score=0.82,
            status="MONITORED"
        ),
        PersistentSource(
            id="ps-vizag-furnace",
            facility_id="fac-rinl-05",
            name="RINL Vizag Blast Furnace #2 'Krishna' Tapping Point",
            latitude=17.6258,
            longitude=83.1786,
            detection_count=35,
            detection_frequency=0.98,
            first_detected="2026-07-15",
            latest_detected="2026-09-26",
            avg_frp=58.0,
            avg_brightness=358.0,
            persistence_score=98.0,
            is_anomalous_spike=True,
            anomaly_z_score=2.85,
            status="ANOMALOUS_SPIKE"
        ),
        PersistentSource(
            id="ps-chembur-flare",
            facility_id="fac-mumbai-06",
            name="BPCL Mumbai Refinery FCCU Flare Stack",
            latitude=19.0072,
            longitude=72.8985,
            detection_count=19,
            detection_frequency=0.78,
            first_detected="2026-08-20",
            latest_detected="2026-09-26",
            avg_frp=24.1,
            avg_brightness=328.0,
            persistence_score=82.0,
            is_anomalous_spike=False,
            anomaly_z_score=0.31,
            status="MONITORED"
        )
    ]
    db.add_all(persistent_sources)
    db.flush()

    # 6. Active Hotspots & Incidents
    # Incident 1: Jamnagar Refinery Fire (CRITICAL)
    hs1 = ThermalHotspot(
        id="hs-jamnagar-01",
        latitude=22.4707,
        longitude=70.0577,
        brightness=368.4,
        scan=0.38,
        track=0.36,
        acq_date=datetime.utcnow().strftime("%Y-%m-%d"),
        acq_time="1045",
        timestamp=f"{datetime.utcnow().strftime('%Y-%m-%d')} 10:45:00 UTC",
        satellite="SNPP",
        instrument="VIIRS",
        confidence=94.0,
        version="2.0NRT",
        bright_t31=301.2,
        frp=68.4,
        daynight="D",
        source="NASA FIRMS",
        nearest_facility_id="fac-jamnagar-01",
        distance_to_facility_km=0.25,
        classification="Industrial Fire",
        risk_score=88.0,
        risk_level="CRITICAL",
        status="ACTIVE"
    )
    db.add(hs1)

    inc1 = Incident(
        id="inc-jamnagar-01",
        incident_number="INC-2026-0926-001",
        hotspot_id=hs1.id,
        facility_id="fac-jamnagar-01",
        title="Thermal Anomaly Excursion - Reliance Jamnagar Polypropylene Area",
        status="VERIFIED",
        risk_level="CRITICAL",
        risk_score=88.0,
        classification="Industrial Fire",
        confidence=0.94,
        latitude=22.4707,
        longitude=70.0577,
        operator_notes="Verified via aerial drone feed. Foam cooling perimeter established at North Tank Farm. Ready for dispatch confirmation.",
        verified_by="Commander Sharma",
        dispatch_status="READY",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(inc1)

    # Route for inc1
    r1 = Route(
        id="route-jamnagar-01",
        incident_id=inc1.id,
        name="North Gate to Jamnagar Civil Hospital Evacuation Route",
        route_type="EVACUATION",
        distance_km=14.2,
        estimated_time_minutes=20,
        danger_radius_m=500,
        is_safe=True,
        waypoints_json=json.dumps([
            [22.4707, 70.0577],
            [22.4810, 70.0620],
            [22.4750, 70.0710],
            [22.4680, 70.0650]
        ]),
        hazards_json=json.dumps([
            {"type": "THERMAL_EXCLUSION_ZONE", "radius": 500, "coords": [22.4707, 70.0577]}
        ]),
        avoided_zones_json=json.dumps([
            {"zone": "500m Blast & Toxic Vapor Radius", "status": "BYPASS_CLEARED"}
        ]),
        destination_name="Jamnagar Civil Hospital"
    )
    db.add(r1)

    # Alert for inc1
    a1 = Alert(
        id="alert-jamnagar-01",
        incident_id=inc1.id,
        severity="CRITICAL",
        alert_type="INDUSTRIAL_FIRE",
        title="CRITICAL INDUSTRIAL FIRE: Reliance Jamnagar Complex",
        message="Satellite VIIRS detected 68.4 MW thermal hotspot within 250m of Level-4 Hazmat storage. Emergency services alerted.",
        channels_json=json.dumps(["DASHBOARD", "SMS", "EMAIL"]),
        read_status=False,
        acknowledged=False
    )
    db.add(a1)

    # Incident 2: RINL Blast Furnace Spike (HIGH)
    hs2 = ThermalHotspot(
        id="hs-vizag-02",
        latitude=17.6254,
        longitude=83.1782,
        brightness=395.0,
        scan=0.36,
        track=0.35,
        acq_date=datetime.utcnow().strftime("%Y-%m-%d"),
        acq_time="1015",
        timestamp=f"{datetime.utcnow().strftime('%Y-%m-%d')} 10:15:00 UTC",
        satellite="SNPP",
        instrument="VIIRS",
        confidence=98.0,
        version="2.0NRT",
        bright_t31=308.2,
        frp=128.5,
        daynight="D",
        source="NASA FIRMS",
        nearest_facility_id="fac-rinl-05",
        distance_to_facility_km=0.12,
        classification="Persistent Industrial Thermal Source",
        risk_score=78.0,
        risk_level="CRITICAL",
        status="ACTIVE"
    )
    db.add(hs2)

    inc2 = Incident(
        id="inc-vizag-02",
        incident_number="INC-2026-0926-002",
        hotspot_id=hs2.id,
        facility_id="fac-rinl-05",
        title="2.5-Sigma Thermal Anomaly Spike - RINL Vizag Blast Furnace #2",
        status="UNDER_REVIEW",
        risk_level="HIGH",
        risk_score=78.0,
        classification="Persistent Industrial Thermal Source",
        confidence=0.98,
        latitude=17.6254,
        longitude=83.1782,
        operator_notes="Thermal power reached 128.5 MW (z-score: 2.85). Plant telemetry indicates molten slag tapping sequence.",
        verified_by="",
        dispatch_status="STANDBY",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(inc2)

    db.commit()
    print("[FIREGUARD DB] Database seeding completed successfully.")
