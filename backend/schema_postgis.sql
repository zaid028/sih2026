-- ==============================================================================
-- FIREGUARD AI - Production PostgreSQL + PostGIS Database Schema
-- SIH Problem Statement SIH26162
-- ==============================================================================

-- Enable PostGIS spatial extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- 1. Users & RBAC
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    role VARCHAR(32) DEFAULT 'analyst',
    organization VARCHAR(120) DEFAULT 'Disaster Management Authority',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Industrial Facilities (with PostGIS Geometry Polygons)
CREATE TABLE IF NOT EXISTS industrial_facilities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(160) NOT NULL,
    facility_type VARCHAR(64) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom GEOMETRY(Point, 4326),
    polygon_geom GEOMETRY(Polygon, 4326),
    hazard_category VARCHAR(32) DEFAULT 'HAZMAT_TIER_1',
    address VARCHAR(255),
    district VARCHAR(80),
    state VARCHAR(80),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_facilities_geom ON industrial_facilities USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_facilities_poly ON industrial_facilities USING GIST(polygon_geom);

-- 3. NASA FIRMS Thermal Hotspots
CREATE TABLE IF NOT EXISTS thermal_hotspots (
    id SERIAL PRIMARY KEY,
    source_satellite VARCHAR(32) DEFAULT 'VIIRS_SNPP',
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom GEOMETRY(Point, 4326),
    brightness_k DOUBLE PRECISION NOT NULL,
    frp_mw DOUBLE PRECISION NOT NULL,
    confidence INTEGER DEFAULT 80,
    acquisition_date VARCHAR(10) NOT NULL,
    acquisition_time VARCHAR(10),
    daynight VARCHAR(1) DEFAULT 'D',
    facility_id INTEGER REFERENCES industrial_facilities(id) ON DELETE SET NULL,
    distance_to_facility_m DOUBLE PRECISION,
    is_persistent BOOLEAN DEFAULT FALSE,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hotspots_geom ON thermal_hotspots USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_hotspots_date ON thermal_hotspots(acquisition_date);

-- 4. Emergency Incidents
CREATE TABLE IF NOT EXISTS incidents (
    id VARCHAR(32) PRIMARY KEY,
    hotspot_id INTEGER REFERENCES thermal_hotspots(id) ON DELETE SET NULL,
    facility_id INTEGER REFERENCES industrial_facilities(id) ON DELETE SET NULL,
    title VARCHAR(180) NOT NULL,
    fire_class VARCHAR(40) DEFAULT 'UNKNOWN',
    risk_score DOUBLE PRECISION DEFAULT 50.0,
    risk_level VARCHAR(20) DEFAULT 'MODERATE',
    status VARCHAR(30) DEFAULT 'REPORTED',
    reported_by VARCHAR(64) DEFAULT 'AI_FIRMS_DETECTOR',
    response_notes TEXT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_risk ON incidents(risk_score DESC);

-- 5. AI Classifications (Explainable Output)
CREATE TABLE IF NOT EXISTS ai_classifications (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(32) REFERENCES incidents(id) ON DELETE CASCADE,
    primary_class VARCHAR(40) NOT NULL,
    confidence_pct DOUBLE PRECISION NOT NULL,
    top_factors JSONB DEFAULT '[]'::jsonb,
    explanation_text TEXT,
    recommended_response TEXT,
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Explainable Risk Scores
CREATE TABLE IF NOT EXISTS risk_scores (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(32) REFERENCES incidents(id) ON DELETE CASCADE,
    total_score DOUBLE PRECISION NOT NULL,
    risk_tier VARCHAR(20) NOT NULL,
    factor_breakdown JSONB DEFAULT '{}'::jsonb,
    why_explanation TEXT,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Emergency Lifelines & Infrastructure
CREATE TABLE IF NOT EXISTS emergency_facilities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    facility_type VARCHAR(40) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom GEOMETRY(Point, 4326),
    phone VARCHAR(50),
    address VARCHAR(255),
    bed_capacity INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_emergency_geom ON emergency_facilities USING GIST(geom);

-- 8. Emergency Contacts & Agency Directory
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id SERIAL PRIMARY KEY,
    agency_name VARCHAR(120) NOT NULL,
    contact_type VARCHAR(50) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    district VARCHAR(80),
    state VARCHAR(80),
    is_primary BOOLEAN DEFAULT FALSE
);

-- 9. Real-Time Alerts
CREATE TABLE IF NOT EXISTS alerts (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(32) REFERENCES incidents(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'HIGH',
    message TEXT NOT NULL,
    is_acknowledged BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Evacuation Routes & Corridors
CREATE TABLE IF NOT EXISTS routes (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(32) REFERENCES incidents(id) ON DELETE CASCADE,
    target_facility_id INTEGER REFERENCES emergency_facilities(id),
    route_type VARCHAR(30) DEFAULT 'SAFE_EVACUATION',
    distance_km DOUBLE PRECISION NOT NULL,
    estimated_time_min INTEGER NOT NULL,
    route_geom GEOMETRY(LineString, 4326),
    avoids_hazard_zone BOOLEAN DEFAULT TRUE
);

-- Spatial Query Example: Find all thermal hotspots within 1km of chemical or petrochemical plants:
-- SELECT h.id, h.frp_mw, f.name AS facility_name, ST_Distance(h.geom::geography, f.geom::geography) AS dist_meters
-- FROM thermal_hotspots h
-- JOIN industrial_facilities f ON ST_DWithin(h.geom::geography, f.geom::geography, 1000.0)
-- WHERE f.facility_type IN ('refinery', 'chemical_plant') AND h.frp_mw > 30.0;
