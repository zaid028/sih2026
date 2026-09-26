# FIREGUARD AI
### AI-Based Detection & Classification of Industrial Fires and Persistent Thermal Sources Using NASA FIRMS, OSM & Satellite Data
**Smart India Hackathon (SIH) | Problem Statement: SIH26162**

---

## 1. Executive Summary & Problem Overview

Industrial complexes, petrochemical refineries, chemical storage terminals, and steel mills handle vast quantities of combustible, volatile, and toxic hydrocarbons. When an industrial fire breaks out, the risks of catastrophic chain explosions, hazardous gas plumes, and community devastation are extreme.

While satellite thermal anomaly observations (such as **NASA FIRMS** MODIS and VIIRS) provide global coverage, raw satellite data presents a critical handicap to emergency authorities:
> **An uncontrolled 85 MW petrochemical refinery fire looks identical in raw coordinates to an authorized hydrocarbon flare stack, a routine blast furnace, or open agricultural stubble burning.**

**FIREGUARD AI** solves this problem. It is a government-grade tactical emergency command center that fuses:
1. **NASA FIRMS Real-Time Satellite Feeds** (MODIS Terra/Aqua, VIIRS S-NPP, NOAA-20, NOAA-21)
2. **OpenStreetMap (OSM) / Overpass Geospatial Facility Intelligence** (refineries, petrochemical units, chemical terminals, hazard polygons)
3. **8-Class AI Fire Classification Engine** (Machine learning model attributing features including FRP, brightness, temporal persistence, day/night flag, and facility proximity)
4. **Persistent Thermal Source Recurrence Clustering** (Isolating routine industrial heating from acute emergencies and detecting abnormal flare spikes exceeding $2.5\sigma$)
5. **Multi-Factor Explainable AI Risk Scoring (0–100)** (Categorized into LOW, MODERATE, HIGH, CRITICAL with plain-language causal reasoning)
6. **Dynamic Evacuation & Safety Route Engine** (Color-coded corridors avoiding active 500m blast and 1.5km toxic plume hazard zones to the nearest trauma center)
7. **Multi-Agency Simulated Emergency Dispatch** (Generating standardized alert payloads for NDRF, State Disaster Cells, and plant safety commanders)
8. **Dark Military/Aviation Command Center UI** (Pure modern Vanilla JS, Leaflet.js, Bootstrap 5, Chart.js — **strictly no React**).

---

## 2. Tactical Emergency Response Workflow

```
[ NASA FIRMS Satellites ] ──> [ Data Ingestion & Cleaning ]
                                        │
                                        ▼
[ OpenStreetMap Facilities ] ──> [ Geospatial Buffer & Spatial Join ]
                                        │
                                        ▼
                         [ Spatiotemporal Recurrence Engine ]
                                        │
                                        ▼
                         [ 8-Class AI Fire Classifier ]
                                        │
                                        ▼
                         [ Explainable Risk Engine (0-100) ]
                                        │
                                        ▼
                     [ Dynamic Safety Evacuation Router ]
                         (500m Blast Buffer Avoidance)
                                        │
                                        ▼
                   [ Multi-Agency Dispatch Simulation ]
                     (NDRF, Fire Services, SDMA, Plant)
                                        │
                                        ▼
                    [ Live Command Center Operations Room ]
```

**"Detect &rarr; Classify &rarr; Assess Risk &rarr; Locate Facility &rarr; Find Safe Route &rarr; Alert Responders &rarr; Manage Incident"**

---

## 3. Technology Stack

| Layer | Technology | Rationale & Specifications |
|:---|:---|:---|
| **Frontend** | HTML5, CSS3, Vanilla ES6+ JS | Zero compilation/bundling overhead; instant browser load; strictly NO React as requested. |
| **UI Framework** | Bootstrap 5.3 + Custom CSS | Responsive layout, dark aviation theme, glassmorphism cards, tactical red/orange indicators. |
| **Interactive Maps** | Leaflet.js 1.9.4 | Custom pulsing SVG markers, CartoDB DarkMatter & ESRI Satellite hybrid layers, hazard circles, evacuation polylines. |
| **Analytics** | Chart.js 4.4.1 | Doughnut, line, and bar visualizations for classification distribution, 24h trends, and regional clustering. |
| **Backend** | Python Flask (Werkzeug) | Robust, RESTful, lightweight, self-contained web server serving API endpoints and static frontend simultaneously. |
| **Database** | SQLite (Dev/Demo) + PostGIS (Prod) | Zero-setup local SQLite with custom spatial math functions; included production `schema_postgis.sql`. |
| **Machine Learning**| Scikit-learn + Geospatial Heuristics | 8-Class classifier with feature attribution, confidence scoring, and plain-language explainability. |
| **External APIs** | NASA FIRMS API + OSM Overpass | Pluggable connector with seamless fallback to high-fidelity tactical demo datasets. |

---

## 4. Key Architectural Modules

### 4.1 8-Class AI Fire Classification
The AI engine evaluates satellite radiometric observations alongside spatial and temporal features to assign one of 8 distinct operational classes:
1. **Industrial Fire (`IND_FIRE`)**: High-intensity thermal anomaly immediately adjacent to a petrochemical/chemical site with sudden onset.
2. **Persistent Industrial Thermal Source (`PERSIST_IND`)**: Documented routine heating (blast furnaces, smelters, cement kilns) with long recurrence history.
3. **Gas Flare (`GAS_FLARE`)**: Controlled refinery hydrocarbon flaring stack; tracked for baseline volume and flare spike anomalies.
4. **Forest / Vegetation Fire (`FOREST_FIRE`)**: Remote canopy/bush fire located $> 3\text{km}$ from registered industrial units.
5. **Agricultural / Bush Fire (`AGRI_FIRE`)**: Low-to-moderate daytime seasonal crop stubble burning in rural agricultural corridors.
6. **Waste-Burning Event (`WASTE_BURN`)**: Smoldering municipal solid waste at landfills or peri-urban dumping grounds.
7. **Possible False Positive (`FALSE_POS`)**: Sensor artifacts or solar reflection glint over high-albedo terrain (salt pans/reflective metal roofing).
8. **Unknown / Under Verification (`UNKNOWN`)**: Ambiguous spectral profile flagged for physical UAV or operator inspection.

### 4.2 Multi-Factor Explainable Risk Scoring (0–100)
Rather than producing an unexplainable black-box score, FIREGUARD AI computes transparent, weighted point contributions:
- **Facility Proximity & Hazard Tier (30 pts)**: $d \le 250\text{m}$ of high-hazard chemical/petrochemical unit.
- **Thermal Intensity / FRP (25 pts)**: Fire Radiative Power (MW) and brightness temperature.
- **NASA FIRMS Confidence (15 pts)**: Observation confidence percentage from VIIRS/MODIS.
- **Civilian Population Exposure (10 pts)**: Settlements within $1\text{--}3\text{km}$ downwind.
- **Critical Infrastructure Lifelines (10 pts)**: Proximity to gas pipelines, power substations, highways.
- **Persistence & Temporal Delta (10 pts)**: Sudden new outbreak vs documented routine flaring.

### 4.3 Dynamic Safety Route & Hazard Buffer Engine
When an active industrial fire is selected:
- **500m Red Blast/Thermal Zone**: Directly encompasses high-danger radiant heat. Roads inside are marked strictly impassable.
- **1500m Yellow Toxic Smoke Buffer**: Cautionary perimeter downwind of the combustion center.
- **Green Recommended Evacuation Corridor**: Automatically routes vehicles around the danger radius to the nearest emergency trauma hospital and Hazmat fire station.
- **Mobile Safety Mode**: Full-screen high-contrast display with large compass bearings, turn-by-turn safe egress instructions, and one-tap emergency calling.

---

## 5. Instant Installation & Quickstart

### Prerequisites
- Python 3.10+ (tested on Python 3.12/3.13)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### Option 1: One-Click Launch (Windows)
Double-click `run.bat` in the project root:
```bat
run.bat
```

### Option 2: Command Line Launch
```bash
# 1. Open project directory
cd c:\Users\mmoha\OneDrive\Desktop\SIH2026

# 2. Launch the application
python run.py
```

The script will automatically initialize the database, seed realistic industrial facilities and satellite hotspots, start the server at `http://127.0.0.1:5000/`, and open your default web browser!

---

## 6. Accessing the Application

| View | URL | Purpose |
|:---|:---|:---|
| **Public Presentation Portal** | `http://127.0.0.1:5000/` | Public landing page, SIH problem overview, pipeline diagram, evaluator guide. |
| **Tactical Command Center** | `http://127.0.0.1:5000/app` | Main operations dashboard, Leaflet tactical map, incident triage, safety routes, analytics. |
| **System Health API** | `http://127.0.0.1:5000/api/system/status` | Real-time system telemetry and NASA FIRMS connection status. |

---

## 7. Demo Personas & Evaluator Credentials

The command center top navigation bar features a **One-Click Role Switcher** so SIH evaluators can test different personas without logging in and out. Alternatively, log in via API with:

| Persona | Role | Username | Password | Operational Authority |
|:---|:---|:---|:---|:---|
| **Chief Controller Sharma** | `admin` | `admin` | `Admin@123` | Full system command, verify classifications, trigger multi-agency dispatches. |
| **Senior Operator Rao** | `operator` | `operator` | `Operator@123` | Triage live hotspots, update incident lifecycle, compute evacuation corridors. |
| **VP Health & Safety Patel** | `facility_manager`| `manager` | `Manager@123` | Monitor Jamnagar refinery boundary, review flare baselines, update plant contacts. |
| **Dr. Ananya Sen** | `analyst` | `analyst` | `Analyst@123` | Inspect recurrent thermal trends, Chart.js metrics, and XAI factor weights. |
| **Civilian Observer** | `public` | `citizen` | `Public@123` | View active regional hazard map, access safe evacuation routes & nearest hospitals. |

---

## 8. Connecting Live External APIs

### 8.1 Connecting Real NASA FIRMS API
By default, **Demo Mode** is enabled with high-fidelity realistic data for Jamnagar, Dahej, Vizag, Chembur, and Manali. To connect live NASA FIRMS feeds:
1. Register for a free API key at [NASA FIRMS MAP_KEY Portal](https://firms.modaps.eosdis.nasa.gov/api/map_key).
2. Open the **Settings** tab in the Command Center (`http://127.0.0.1:5000/app#settings`).
3. Paste your key into the **NASA FIRMS API KEY (MAP_KEY)** field and toggle **Demo Mode** to `OFF`.
4. Click **Save Settings** &rarr; **Trigger Immediate Satellite Ingestion**.
5. Alternatively, define `FIRMS_MAP_KEY=your_key_here` and `DEMO_MODE=false` in `.env`.

### 8.2 OpenStreetMap Overpass API
The system queries OSM for industrial polygons, refineries, fire stations, and hospitals:
- Configured in `backend/app/config.py` as `OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"`.
- Features built-in fallback caching so the application remains responsive even during public Overpass server throttling.

---

## 9. Running Automated Tests

Run the backend unit test suite covering AI classification, risk scoring, persistence clustering, routing, and REST endpoints:
```bash
python -m unittest discover -s backend/tests -p "test_*.py"
```

All tests execute and validate in $< 0.2$ seconds.

---

## 10. Production Deployment (PostgreSQL + PostGIS)

For enterprise high-availability deployment on a PostgreSQL server:
1. Install PostGIS:
   ```bash
   sudo apt-get install postgresql postgresql-contrib postgis
   ```
2. Create database and apply the provided schema:
   ```bash
   psql -U postgres -d fireguard_postgis -f backend/schema_postgis.sql
   ```
3. Set your environment variable:
   ```bash
   export DATABASE_URL="postgresql://postgres:password@localhost:5432/fireguard_postgis"
   ```
4. Start the server with Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

---

## 11. SIH 2026 Presentation Highlights

When demonstrating to the SIH evaluation jury:
1. **Show the Landing Page (`/`)**: Walk through the problem statement, why raw satellite points fail, and the 4-step pipeline.
2. **Open the Live Command Center (`/app`)**: Point out the dark military/tactical theme, UTC/IST clocks, active threats ticker, and Leaflet radar map.
3. **Inspect a Critical Hotspot**: Click the Jamnagar FCCU or Dahej Polymer Storage incident. Demonstrate the **AI Fire Classification** badge, **Feature Attribution Rationale**, and **Explainable Risk Score (85/100)**.
4. **Trigger Dynamic Evacuation Routing**: Click **Safety Route**. Show how the map renders the 500m Red blast zone and the Green safe evacuation path steering around it to the nearest trauma hospital.
5. **Demonstrate Incident Lifecycle & Simulated Dispatch**: Click **Dispatch Required** &rarr; **Dispatch Alert**. Show the pre-formatted multi-agency radio/SMS broadcast payload.
6. **Show Persistent Sources (`/app#persistent`)**: Explain how spatiotemporal clustering isolates routine refinery flaring from emergencies, and highlight the **Anomalous Flare Spike Alert (> 2.5 sigma)**.
7. **Switch Roles**: Use the top-bar dropdown to switch from Operator to Administrator or Facility Manager, demonstrating full role-based access control.

---
**FIREGUARD AI &bull; Smart India Hackathon 2026**
*Government of India &bull; National Disaster Management & Industrial Safety Directorate*
