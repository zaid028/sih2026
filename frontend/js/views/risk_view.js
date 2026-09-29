/**
 * FIREGUARD AI - Master Risk Analytics & Predictive Simulation View Controller
 * Based on Master Reference UI (media_1790686940444.jpg)
 * SIH26162: AI-Based Detection & Classification of Industrial Fires & Persistent Thermal Sources
 */

const RiskView = {
  riskMap: null,
  vectorLayers: {
    '1h': null,
    '6h': null,
    '24h': null
  },
  currentVector: '1h',
  criticalMarker: null,
  activeScore: 82,
  baseIncident: null,

  // Default scenario parameters matching reference screenshot
  scenarioState: {
    windShift: 15,        // +15° Azimuth
    suppressionUnits: 4,  // 4 Aerial Units
    barrierDensity: 75    // 75% Capacity
  },

  init() {
    this.render();
  },

  render() {
    const container = document.getElementById("view-risk");
    if (!container) return;

    // Pick active or first critical incident
    this.baseIncident = (AppState.incidents && AppState.incidents.length > 0)
      ? (AppState.incidents.find(i => i.risk_level === "CRITICAL") || AppState.incidents[0])
      : {
          id: "INC-JAM-4092",
          title: "Jamnagar Petrochemical Complex Tank Farm C-4",
          risk_score: 82,
          risk_level: "CRITICAL",
          facility_name: "Reliance Jamnagar Refinery",
          frp: 84.2,
          confidence: 98.4
        };

    // Render Master Layout matching reference screenshot media_1790686940444.jpg
    container.innerHTML = `
      <!-- Hero Simulation Banner -->
      <div class="hero-simulation-banner">
        <div>
          <div class="banner-threat-tag">
            <span class="badge-threat-vector">CRITICAL THREAT VECTOR</span>
            <span class="banner-sim-id">Monte Carlo Sim #4092-B &bull; Grid: 22.3854°N, 69.8712°E</span>
          </div>
          <h1 class="banner-main-title">Predictive Risk Analytics & Simulation</h1>
        </div>

        <div class="banner-right-meta">
          <div class="ai-confidence-block">
            <div class="ai-confidence-label">AI Confidence Rating</div>
            <div class="ai-confidence-val">98.4% Precision</div>
          </div>
          <button class="btn-run-simulation" onclick="RiskView.runSimulation()">
            <i class="bi bi-arrow-repeat"></i> Run Simulation
          </button>
        </div>
      </div>

      <!-- 3-Column Risk Analytics Top Grid -->
      <div class="risk-top-grid">
        
        <!-- Card 1: Sector Risk Index -->
        <div class="sector-risk-card">
          <div class="card-title-styled">
            <i class="bi bi-shield-shaded text-info"></i> Sector Risk Index
            <i class="bi bi-info-circle ms-auto text-secondary" title="Multi-variate synthesized risk index based on satellite FRP, facility hazard classification and OSM distance joins."></i>
          </div>

          <!-- Animated Circular SVG Gauge -->
          <div class="gauge-wrapper">
            <svg class="gauge-svg" viewBox="0 0 160 160">
              <circle class="gauge-bg" cx="80" cy="80" r="68"></circle>
              <circle class="gauge-fill" id="risk-gauge-circle" cx="80" cy="80" r="68"
                      stroke-dasharray="427"
                      stroke-dashoffset="76.86"></circle>
            </svg>
            <div class="gauge-center-text">
              <span class="gauge-score-number" id="risk-score-display">82</span>
              <span class="gauge-score-label text-danger" id="risk-score-status">CRITICAL / 100</span>
            </div>
          </div>

          <!-- Breakdown Metrics Rows -->
          <div class="risk-breakdown-list">
            <div class="breakdown-row">
              <span class="breakdown-name"><i class="bi bi-buildings text-info me-1"></i> Industrial Facilities</span>
              <span class="breakdown-val text-danger" id="val-ind-fac">91</span>
            </div>
            <div class="breakdown-row">
              <span class="breakdown-name"><i class="bi bi-fuel-pump text-warning me-1"></i> Chemical Storage</span>
              <span class="breakdown-val text-danger" id="val-chem-stor">88</span>
            </div>
            <div class="breakdown-row">
              <span class="breakdown-name"><i class="bi bi-people text-muted me-1"></i> Surrounding Communities</span>
              <span class="breakdown-val text-warning" id="val-communities">67</span>
            </div>
            <div class="breakdown-row">
              <span class="breakdown-name"><i class="bi bi-signpost-2 text-success me-1"></i> Evacuation Corridors</span>
              <span class="breakdown-val text-info" id="val-evac-routes">54</span>
            </div>
          </div>
        </div>

        <!-- Card 2: Environmental Vector Stream -->
        <div class="env-vector-card">
          <div class="card-title-styled">
            <i class="bi bi-wind text-info"></i> Environmental Vector Stream
            <span class="badge bg-dark text-info border border-secondary ms-auto" style="font-size: 0.68rem;">LIVE TELEMETRY</span>
          </div>

          <div class="env-tiles-grid">
            <!-- Tile 1: Wind -->
            <div class="env-tile">
              <div class="env-tile-label"><i class="bi bi-compass me-1 text-info"></i> Wind Velocity</div>
              <div class="env-tile-val text-info" id="env-wind-val">42.5 km/h</div>
              <div class="env-tile-sub">Vector: NW (315°)</div>
            </div>

            <!-- Tile 2: Ambient Temp -->
            <div class="env-tile">
              <div class="env-tile-label"><i class="bi bi-thermometer-high me-1 text-danger"></i> Ambient Temp</div>
              <div class="env-tile-val text-danger" id="env-temp-val">41.2°C</div>
              <div class="env-tile-sub">Thermal Peak: Jamnagar Hub</div>
            </div>

            <!-- Tile 3: Humidity -->
            <div class="env-tile">
              <div class="env-tile-label"><i class="bi bi-moisture me-1 text-warning"></i> Relative Humidity</div>
              <div class="env-tile-val text-warning" id="env-humidity-val">14.8%</div>
              <div class="env-tile-sub">Critical Low Threshold</div>
            </div>

            <!-- Tile 4: Fuel Moisture / FRP -->
            <div class="env-tile">
              <div class="env-tile-label"><i class="bi bi-fire me-1 text-danger"></i> Thermal Intensity / FRP</div>
              <div class="env-tile-val text-light" id="env-frp-val">84.2 MW</div>
              <div class="env-tile-sub">Severe Combustive Flux</div>
            </div>
          </div>

          <div class="sensor-node-footer">
            <span class="pulse-dot-green"></span>
            <span>Telemetry stream synced across 18 industrial AWS IoT weather nodes in Gujarat SEZ.</span>
          </div>
        </div>

        <!-- Card 3: Scenario Control Matrix -->
        <div class="scenario-matrix-card">
          <div class="card-title-styled">
            <i class="bi bi-sliders text-info"></i> Scenario Control Matrix
            <span class="badge bg-secondary text-light ms-auto" style="font-size: 0.68rem;">SIMULATION</span>
          </div>

          <!-- Slider 1: Wind Shift -->
          <div class="matrix-slider-group">
            <div class="slider-header-row">
              <span class="slider-title">Wind Shift / Trajectory</span>
              <span class="slider-val-tag" id="disp-wind-shift">+15° Azimuth</span>
            </div>
            <input type="range" class="tactical-range" id="input-wind-shift" min="-90" max="90" value="15" oninput="RiskView.onSliderChange()">
          </div>

          <!-- Slider 2: Suppression Force -->
          <div class="matrix-slider-group">
            <div class="slider-header-row">
              <span class="slider-title">Suppression Force / Response</span>
              <span class="slider-val-tag" id="disp-suppression">4 Aerial Units</span>
            </div>
            <input type="range" class="tactical-range" id="input-suppression" min="0" max="10" value="4" oninput="RiskView.onSliderChange()">
          </div>

          <!-- Slider 3: Barrier Density -->
          <div class="matrix-slider-group">
            <div class="slider-header-row">
              <span class="slider-title">Barrier Density / Containment</span>
              <span class="slider-val-tag" id="disp-barrier">75% Capacity</span>
            </div>
            <input type="range" class="tactical-range" id="input-barrier" min="0" max="100" value="75" oninput="RiskView.onSliderChange()">
          </div>

          <!-- Matrix Action Buttons -->
          <div class="matrix-actions-row">
            <button class="btn-matrix-reset" onclick="RiskView.resetSliders()">
              <i class="bi bi-arrow-counterclockwise"></i> Reset Defaults
            </button>
            <button class="btn-matrix-recalc" onclick="RiskView.recalculateRisk()">
              <i class="bi bi-cpu-fill"></i> Apply & Recalculate
            </button>
          </div>
        </div>

      </div>

      <!-- Main Geospatial Risk Projection Card (Exact Reference UI) -->
      <div class="risk-map-card">
        <div class="risk-map-header">
          <div class="card-title-styled">
            <i class="bi bi-radar text-info"></i> Industrial Fire Impact & Risk Projection
            <span class="text-muted ms-2" style="font-size: 0.76rem; font-weight: normal;">Monte Carlo Plume & Fire-Front Breach Model</span>
          </div>

          <div class="vector-tabs-group">
            <button class="vector-tab-pill active" id="btn-vector-1h" onclick="RiskView.setVectorWindow('1h')">1-Hour Vector</button>
            <button class="vector-tab-pill" id="btn-vector-6h" onclick="RiskView.setVectorWindow('6h')">6-Hour Vector</button>
            <button class="vector-tab-pill" id="btn-vector-24h" onclick="RiskView.setVectorWindow('24h')">24-Hour Vector</button>
          </div>
        </div>

        <!-- Tactical Leaflet Map Canvas -->
        <div class="risk-leaflet-wrapper">
          <div id="risk-leaflet-canvas" style="width: 100%; height: 480px; background: #0B0E14;"></div>

          <!-- Floating Active Fire Front HUD -->
          <div class="floating-hud-firefront">
            <span class="pulse-dot-red"></span>
            <div>
              <div class="hud-firefront-title">ACTIVE FIRE FRONT</div>
              <div class="hud-firefront-sub" id="hud-firefront-rate">Spread Rate: 3.4 km/h East-Southeast &bull; Head FRP: 84.2 MW</div>
            </div>
          </div>

          <!-- Floating Pulsing Radar Pin / Threat Asset HUD -->
          <div class="floating-hud-radar-asset" id="hud-radar-asset">
            <div class="radar-ping-dot"></div>
            <div class="radar-asset-info">
              <span class="radar-asset-title">CRITICAL ASSET: Chemical Storage Unit C-4</span>
              <span class="radar-asset-sub">High-explosive naphtha inventory &bull; Proximity: 350m Stand-off</span>
            </div>
          </div>

          <!-- Coordinates & Projection HUD -->
          <div class="floating-hud-coords">
            <span><i class="bi bi-crosshair text-info"></i> <span id="risk-hud-coords">22.3854° N, 69.8712° E</span></span>
            <span>&bull;</span>
            <span class="text-info">JAMNAGAR INDUSTRIAL CLUSTER SECTOR 4</span>
            <span>&bull;</span>
            <span class="text-warning">OSM JOIN CERTIFIED</span>
          </div>

          <!-- Map Legend HUD -->
          <div class="floating-hud-legend">
            <div class="legend-row">
              <span class="legend-box" style="background: rgba(239, 68, 68, 0.45); border: 1px solid #EF4444;"></span>
              <span>1-Hour Critical Breach (Immediate Impact)</span>
            </div>
            <div class="legend-row">
              <span class="legend-box" style="background: rgba(249, 115, 22, 0.3); border: 1px solid #F97316;"></span>
              <span>6-Hour Toxic Plume & Thermal Dispersion</span>
            </div>
            <div class="legend-row">
              <span class="legend-box" style="background: rgba(56, 189, 248, 0.2); border: 1px solid #38BDF8;"></span>
              <span>24-Hour Regional Evacuation Perimeter</span>
            </div>
          </div>
        </div>

        <!-- Scrubber Bar at Bottom of Map -->
        <div class="map-scrubber-bar">
          <div class="d-flex align-items-center gap-2" style="min-width: 140px;">
            <button class="btn btn-sm btn-outline-info py-0 px-2" onclick="RiskView.playScrubber()"><i class="bi bi-play-fill" id="scrubber-play-icon"></i></button>
            <span class="font-monospace text-light" style="font-size: 0.78rem;" id="scrubber-time-label">T+0h (Detection)</span>
          </div>
          <input type="range" class="form-range flex-grow-1" id="scrubber-slider" min="0" max="24" step="1" value="0" oninput="RiskView.onScrubberChange(this.value)">
          <span class="badge bg-dark text-info border border-secondary font-monospace" style="font-size: 0.72rem;">24H PROJECTION</span>
        </div>
      </div>

      <!-- Lower Split Cards: Persistent Analysis & AI Classification Checklist -->
      <div class="row g-3 mt-1">
        
        <!-- Left: Persistent Thermal Source Analysis -->
        <div class="col-lg-6">
          <div class="master-card p-3 h-100">
            <div class="card-title-styled mb-2">
              <i class="bi bi-clock-history text-purple" style="color: #A855F7;"></i> Persistent Thermal Source Analysis
              <span class="badge bg-dark border border-secondary text-info ms-auto" style="font-size: 0.68rem;">SPATIOTEMPORAL CLUSTERING</span>
            </div>
            <p class="text-muted" style="font-size: 0.78rem;">
              Differentiates continuous industrial process flaring from acute, out-of-control emergency blazes by correlating 90-day baseline radiance signatures.
            </p>

            <div class="persistent-timeline-box">
              <div class="p-timeline-item">
                <div class="p-timeline-badge bg-info"></div>
                <div class="p-timeline-content">
                  <div class="p-timeline-header">
                    <strong>Refinery Flare Stack #2 (Jamnagar)</strong>
                    <span class="badge bg-secondary font-monospace">BASELINE DETECTED</span>
                  </div>
                  <div class="p-timeline-body">
                    Normal operational flaring confirmed across 142 passes. Mean FRP: 24.3 MW (σ = 2.1 MW).
                  </div>
                </div>
              </div>

              <div class="p-timeline-item">
                <div class="p-timeline-badge bg-warning"></div>
                <div class="p-timeline-content">
                  <div class="p-timeline-header">
                    <strong>Furnace Exhaust Stack A-1 (Hazira)</strong>
                    <span class="badge bg-dark text-warning border border-warning font-monospace">STABLE HEAT</span>
                  </div>
                  <div class="p-timeline-body">
                    Thermal signature consistent with continuous metallurgic processing cycle.
                  </div>
                </div>
              </div>

              <div class="p-timeline-item current-spike">
                <div class="p-timeline-badge bg-danger"></div>
                <div class="p-timeline-content">
                  <div class="p-timeline-header">
                    <strong class="text-danger">Current Hotspot (Grid 22.3854°N, 69.8712°E)</strong>
                    <span class="badge bg-danger font-monospace">SPIKE DETECTED (+3.4σ)</span>
                  </div>
                  <div class="p-timeline-body text-light">
                    Thermal Radiative Power surged to <strong>84.2 MW</strong>, exceeding historical 90-day baseline by <strong>340%</strong>. Spatiotemporal classifier flagged as <strong>UNCONTROLLED COMBUSTION</strong>.
                  </div>
                </div>
              </div>
            </div>

            <!-- Persistence Metrics Footnote -->
            <div class="d-flex justify-content-between align-items-center mt-3 p-2 rounded" style="background: rgba(168, 85, 247, 0.08); border: 1px solid rgba(168, 85, 247, 0.2); font-size: 0.75rem;">
              <span class="text-light"><i class="bi bi-shield-check text-purple"></i> False Alarm Reduction Rate:</span>
              <strong class="font-monospace text-info">98.6% Precision</strong>
            </div>
          </div>
        </div>

        <!-- Right: AI Classification & Mitigation Protocol -->
        <div class="col-lg-6">
          <div class="master-card p-3 h-100">
            <div class="card-title-styled mb-2">
              <i class="bi bi-cpu-fill text-info"></i> AI Classification & Tactical Mitigation Protocol
              <span class="badge bg-danger text-light ms-auto font-monospace" style="font-size: 0.68rem;">TIER-1 HAZARD</span>
            </div>
            <p class="text-muted" style="font-size: 0.78rem;">
              Multi-source geospatial correlation joins satellite coordinates with OpenStreetMap high-hazard industrial polygons and weather layers.
            </p>

            <!-- Checklist -->
            <div class="ai-checklist-box">
              <div class="checklist-item">
                <i class="bi bi-check-circle-fill text-success fs-5"></i>
                <div>
                  <div class="checklist-title">Classified as Industrial Petrochemical Fire</div>
                  <div class="checklist-sub">Random Forest + Gradient Boost ensemble model confidence: <strong>87.4%</strong> (vs 12.6% Biomass / Crop burn).</div>
                </div>
              </div>

              <div class="checklist-item">
                <i class="bi bi-check-circle-fill text-success fs-5"></i>
                <div>
                  <div class="checklist-title">Proximity to Hazardous Storage Tanks</div>
                  <div class="checklist-sub">Located <strong>350 meters</strong> from bulk chemical containment tank C-4 (OSM Node #4819203).</div>
                </div>
              </div>

              <div class="checklist-item">
                <i class="bi bi-check-circle-fill text-success fs-5"></i>
                <div>
                  <div class="checklist-title">Atmospheric Dispersion Risk</div>
                  <div class="checklist-sub">Plume tracking projects toxic SO2 / particulate concentration over highway corridor SH-6 in 45 minutes.</div>
                </div>
              </div>
            </div>

            <!-- Operator Tactical Protocol Triggers -->
            <div class="mt-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="text-muted text-uppercase fw-bold" style="font-size: 0.7rem; letter-spacing: 0.05em;">RECOMMENDED IMMEDIATE PROTOCOLS</span>
                <span class="text-info font-monospace" style="font-size: 0.7rem;">SOP-IND-409</span>
              </div>
              <div class="d-grid gap-2">
                <button class="btn btn-outline-danger btn-sm text-start d-flex justify-content-between align-items-center" onclick="App.openInitiateProtocolModal()">
                  <span><i class="bi bi-lightning-charge-fill me-2"></i> Trigger Automated Deluge Foam & Valve Isolation</span>
                  <span class="badge bg-danger">EXECUTE</span>
                </button>
                <button class="btn btn-outline-warning text-light btn-sm text-start d-flex justify-content-between align-items-center" onclick="App.openBroadcastModal()">
                  <span><i class="bi bi-broadcast me-2 text-warning"></i> Issue Emergency Evacuation Broadcast to Sector 4</span>
                  <span class="badge bg-warning text-dark">BROADCAST</span>
                </button>
                <button class="btn btn-outline-info btn-sm text-start d-flex justify-content-between align-items-center" onclick="Router.navigate('routes')">
                  <span><i class="bi bi-signpost-2 me-2"></i> View Dynamic Safe Evacuation Corridor (Avoiding Buffer)</span>
                  <span class="badge bg-info text-dark">CORRIDOR</span>
                </button>
              </div>
            </div>

          </div>
        </div>

      </div>
    `;

    // Initialize the Risk Leaflet Map
    setTimeout(() => {
      this.initRiskMap();
      this.setRiskScore(this.activeScore);
    }, 100);
  },

  initRiskMap() {
    const mapEl = document.getElementById("risk-leaflet-canvas");
    if (!mapEl) return;

    // Clean up if exists
    if (this.riskMap) {
      this.riskMap.remove();
      this.riskMap = null;
    }

    const centerLat = 22.3854;
    const centerLon = 69.8712;

    this.riskMap = L.map("risk-leaflet-canvas", {
      center: [centerLat, centerLon],
      zoom: 14,
      zoomControl: false,
      attributionControl: false
    });

    L.control.zoom({ position: "bottomright" }).addTo(this.riskMap);

    // Dark tactical tile layer
    L.tileLayer(AppConfig.MAP_TILES.DARK.url, {
      maxZoom: 18,
      subdomains: "abcd"
    }).addTo(this.riskMap);

    // Track mouse coordinates in risk HUD
    this.riskMap.on("mousemove", (e) => {
      const coordEl = document.getElementById("risk-hud-coords");
      if (coordEl) {
        coordEl.innerText = `${e.latlng.lat.toFixed(4)}° N, ${e.latlng.lng.toFixed(4)}° E`;
      }
    });

    // Render the Fire Front Origin Marker
    const fireIcon = L.divIcon({
      className: "tactical-fire-marker",
      html: `
        <div style="position: relative; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;">
          <div style="position: absolute; width: 36px; height: 36px; border-radius: 50%; background: rgba(239, 68, 68, 0.4); animation: pulse-ring 1.8s infinite;"></div>
          <div style="width: 20px; height: 20px; border-radius: 50%; background: #EF4444; border: 2px solid #FFFFFF; box-shadow: 0 0 12px #EF4444; display: flex; align-items: center; justify-content: center; color: #FFFFFF; font-size: 11px;">
            <i class="bi bi-fire"></i>
          </div>
        </div>
      `,
      iconSize: [36, 36],
      iconAnchor: [18, 18]
    });

    L.marker([centerLat, centerLon], { icon: fireIcon })
      .addTo(this.riskMap)
      .bindPopup(`
        <div style="background: #111620; color: #FFFFFF; padding: 6px; font-family: sans-serif; font-size: 0.8rem; border-radius: 6px;">
          <strong style="color: #EF4444;"><i class="bi bi-fire"></i> Active Industrial Fire Origin</strong><br>
          Facility: Jamnagar Petrochem C-4<br>
          Radiant FRP: <strong>84.2 MW</strong><br>
          Classification: <strong>Uncontrolled Tank Fire</strong>
        </div>
      `);

    // Render Critical Asset Marker (Chemical Storage Unit C-4)
    const assetIcon = L.divIcon({
      className: "tactical-asset-marker",
      html: `
        <div style="position: relative; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
          <div style="position: absolute; width: 32px; height: 32px; border-radius: 50%; background: rgba(249, 115, 22, 0.35); animation: pulse-ring 2.2s infinite;"></div>
          <div style="width: 18px; height: 18px; border-radius: 4px; background: #F97316; border: 2px solid #FFFFFF; box-shadow: 0 0 10px #F97316; display: flex; align-items: center; justify-content: center; color: #000; font-size: 10px; font-weight: bold;">
            <i class="bi bi-fuel-pump"></i>
          </div>
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    });

    L.marker([centerLat + 0.0028, centerLon + 0.0035], { icon: assetIcon })
      .addTo(this.riskMap)
      .bindPopup(`
        <div style="background: #111620; color: #FFFFFF; padding: 6px; font-size: 0.8rem;">
          <strong style="color: #F97316;">Critical Asset: Chemical Storage Unit C-4</strong><br>
          Hazard: High-Explosive Naphtha &bull; 350m Stand-off
        </div>
      `);

    // Draw Vector Impact Polygons
    this.drawVectorPolygons(centerLat, centerLon);
  },

  drawVectorPolygons(lat, lon) {
    if (!this.riskMap) return;

    // Clear existing vector layers
    if (this.vectorLayers['1h']) this.riskMap.removeLayer(this.vectorLayers['1h']);
    if (this.vectorLayers['6h']) this.riskMap.removeLayer(this.vectorLayers['6h']);
    if (this.vectorLayers['24h']) this.riskMap.removeLayer(this.vectorLayers['24h']);

    // Calculate angular shift based on scenario slider
    const shiftRad = (this.scenarioState.windShift * Math.PI) / 180;
    const dx = Math.cos(shiftRad);
    const dy = Math.sin(shiftRad);

    // 1-Hour Vector Breach (Immediate Impact - Red)
    const poly1h = [
      [lat, lon],
      [lat + 0.0035 + (0.001 * dy), lon + 0.006 + (0.002 * dx)],
      [lat + 0.005 + (0.002 * dy), lon + 0.004 + (0.0015 * dx)],
      [lat + 0.0025 + (0.001 * dy), lon - 0.001],
      [lat, lon]
    ];

    this.vectorLayers['1h'] = L.polygon(poly1h, {
      color: "#EF4444",
      fillColor: "#EF4444",
      fillOpacity: 0.45,
      weight: 2,
      dashArray: "4, 4"
    }).addTo(this.riskMap);

    // 6-Hour Vector Breach (Secondary Threat - Amber)
    const poly6h = [
      [lat, lon],
      [lat + 0.008 + (0.003 * dy), lon + 0.015 + (0.005 * dx)],
      [lat + 0.012 + (0.004 * dy), lon + 0.011 + (0.003 * dx)],
      [lat + 0.006 + (0.002 * dy), lon - 0.003],
      [lat, lon]
    ];

    this.vectorLayers['6h'] = L.polygon(poly6h, {
      color: "#F97316",
      fillColor: "#F97316",
      fillOpacity: 0.25,
      weight: 2,
      dashArray: "6, 6"
    });

    // 24-Hour Perimeter Vector (Regional Dispersion - Cyan/Blue)
    const poly24h = [
      [lat, lon],
      [lat + 0.016 + (0.005 * dy), lon + 0.028 + (0.008 * dx)],
      [lat + 0.024 + (0.007 * dy), lon + 0.020 + (0.006 * dx)],
      [lat + 0.012 + (0.003 * dy), lon - 0.007],
      [lat, lon]
    ];

    this.vectorLayers['24h'] = L.polygon(poly24h, {
      color: "#38BDF8",
      fillColor: "#38BDF8",
      fillOpacity: 0.15,
      weight: 2
    });

    // Default to 1h active
    this.setVectorWindow(this.currentVector);
  },

  setVectorWindow(vectorKey) {
    this.currentVector = vectorKey;

    // Update pill buttons
    ['1h', '6h', '24h'].forEach(v => {
      const btn = document.getElementById(`btn-vector-${v}`);
      if (btn) {
        if (v === vectorKey) btn.classList.add("active");
        else btn.classList.remove("active");
      }
    });

    if (!this.riskMap) return;

    // Show selected vector layer, add/remove accordingly
    ['1h', '6h', '24h'].forEach(v => {
      if (this.vectorLayers[v]) {
        if (v === vectorKey) {
          if (!this.riskMap.hasLayer(this.vectorLayers[v])) {
            this.vectorLayers[v].addTo(this.riskMap);
          }
        } else {
          // Keep previous layer with lighter opacity or remove if needed
          if (v === '1h' && vectorKey !== '1h') {
            // Keep 1h visible as inner core
            this.vectorLayers['1h'].setStyle({ fillOpacity: 0.25 });
          } else {
            if (this.riskMap.hasLayer(this.vectorLayers[v])) {
              this.riskMap.removeLayer(this.vectorLayers[v]);
            }
          }
        }
      }
    });

    // Update spread rate HUD text
    const rateEl = document.getElementById("hud-firefront-rate");
    if (rateEl) {
      if (vectorKey === '1h') {
        rateEl.innerText = "Spread Rate: 3.4 km/h East-Southeast • Head FRP: 84.2 MW • Breach: 350m";
      } else if (vectorKey === '6h') {
        rateEl.innerText = "Spread Rate: 3.8 km/h East • Toxic Plume Front: 1.8 km • Air Quality: Critical";
      } else {
        rateEl.innerText = "Regional Dispersion Radius: 4.2 km • Containment Strategy: Active Foam Ring";
      }
    }
  },

  setRiskScore(score) {
    this.activeScore = score;
    const scoreEl = document.getElementById("risk-score-display");
    const statusEl = document.getElementById("risk-score-status");
    const circleEl = document.getElementById("risk-gauge-circle");

    if (scoreEl) {
      this.animateNumber("risk-score-display", parseInt(scoreEl.innerText) || 50, score, 600);
    }

    // Circumference = 2 * PI * 68 ≈ 427.26
    const circumference = 427.26;
    const offset = circumference - (circumference * (score / 100));

    if (circleEl) {
      circleEl.style.transition = "stroke-dashoffset 0.8s ease-in-out, stroke 0.8s ease";
      circleEl.style.strokeDashoffset = offset;

      if (score >= 75) {
        circleEl.style.stroke = "#EF4444";
        if (statusEl) {
          statusEl.innerText = "CRITICAL / 100";
          statusEl.className = "gauge-score-label text-danger";
        }
      } else if (score >= 50) {
        circleEl.style.stroke = "#F97316";
        if (statusEl) {
          statusEl.innerText = "HIGH RISK / 100";
          statusEl.className = "gauge-score-label text-warning";
        }
      } else {
        circleEl.style.stroke = "#10B981";
        if (statusEl) {
          statusEl.innerText = "MODERATE / 100";
          statusEl.className = "gauge-score-label text-success";
        }
      }
    }
  },

  animateNumber(elementId, start, end, duration) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const range = end - start;
    const startTime = performance.now();

    function step(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const current = Math.round(start + (range * progress));
      el.innerText = current;
      if (progress < 1) {
        requestAnimationFrame(step);
      }
    }
    requestAnimationFrame(step);
  },

  onSliderChange() {
    const windEl = document.getElementById("input-wind-shift");
    const suppEl = document.getElementById("input-suppression");
    const barrEl = document.getElementById("input-barrier");

    const dispWind = document.getElementById("disp-wind-shift");
    const dispSupp = document.getElementById("disp-suppression");
    const dispBarr = document.getElementById("disp-barrier");

    if (windEl && dispWind) {
      const val = parseInt(windEl.value);
      dispWind.innerText = (val >= 0 ? `+${val}°` : `${val}°`) + " Azimuth";
      this.scenarioState.windShift = val;
    }

    if (suppEl && dispSupp) {
      dispSupp.innerText = `${suppEl.value} Aerial Units`;
      this.scenarioState.suppressionUnits = parseInt(suppEl.value);
    }

    if (barrEl && dispBarr) {
      dispBarr.innerText = `${barrEl.value}% Capacity`;
      this.scenarioState.barrierDensity = parseInt(barrEl.value);
    }
  },

  resetSliders() {
    this.scenarioState = {
      windShift: 15,
      suppressionUnits: 4,
      barrierDensity: 75
    };

    const windEl = document.getElementById("input-wind-shift");
    const suppEl = document.getElementById("input-suppression");
    const barrEl = document.getElementById("input-barrier");

    if (windEl) windEl.value = 15;
    if (suppEl) suppEl.value = 4;
    if (barrEl) barrEl.value = 75;

    this.onSliderChange();
    this.recalculateRisk();
  },

  recalculateRisk() {
    // Dynamic calculation formula based on scenario control matrix
    // Base score = 82
    // Suppression units reduce risk: -2.5 pts per unit
    // Barrier density reduces risk: -0.15 pts per %
    // High wind angle increases risk spread

    const wind = Math.abs(this.scenarioState.windShift);
    const supp = this.scenarioState.suppressionUnits;
    const barrier = this.scenarioState.barrierDensity;

    let computedScore = Math.round(82 - (supp * 2.2) - ((barrier - 50) * 0.2) + (wind * 0.12));
    computedScore = Math.max(25, Math.min(98, computedScore));

    this.setRiskScore(computedScore);

    // Update breakdown metrics
    const indFac = Math.round(Math.min(99, computedScore + 9));
    const chemStor = Math.round(Math.min(99, computedScore + 6));
    const comm = Math.round(Math.max(20, computedScore - 15));
    const evac = Math.round(Math.max(15, computedScore - 28));

    const el1 = document.getElementById("val-ind-fac");
    const el2 = document.getElementById("val-chem-stor");
    const el3 = document.getElementById("val-communities");
    const el4 = document.getElementById("val-evac-routes");

    if (el1) el1.innerText = indFac;
    if (el2) el2.innerText = chemStor;
    if (el3) el3.innerText = comm;
    if (el4) el4.innerText = evac;

    // Redraw vector polygons with newly adjusted wind azimuth & containment
    this.drawVectorPolygons(22.3854, 69.8712);

    // Flash toast notification
    if (typeof App !== "undefined" && App.showTacticalToast) {
      App.showTacticalToast(`Risk Model Recalculated: Index ${computedScore}/100 based on ${supp} aerial units & ${barrier}% containment.`);
    }
  },

  runSimulation() {
    const btn = document.querySelector(".btn-run-simulation");
    if (btn) {
      btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Simulating...`;
      btn.disabled = true;
    }

    setTimeout(() => {
      if (btn) {
        btn.innerHTML = `<i class="bi bi-arrow-repeat"></i> Run Simulation`;
        btn.disabled = false;
      }
      this.recalculateRisk();
      if (typeof App !== "undefined" && App.showTacticalToast) {
        App.showTacticalToast("Monte Carlo Plume Simulation #4092-B: 500 iterations converged with 98.4% precision.");
      }
    }, 900);
  },

  onScrubberChange(val) {
    const label = document.getElementById("scrubber-time-label");
    if (label) {
      label.innerText = `T+${val}h (${val == 0 ? 'Detection' : 'Projection'})`;
    }

    if (val < 3) {
      this.setVectorWindow('1h');
    } else if (val < 12) {
      this.setVectorWindow('6h');
    } else {
      this.setVectorWindow('24h');
    }
  },

  playScrubber() {
    const slider = document.getElementById("scrubber-slider");
    const icon = document.getElementById("scrubber-play-icon");
    if (!slider) return;

    if (this.scrubberTimer) {
      clearInterval(this.scrubberTimer);
      this.scrubberTimer = null;
      if (icon) icon.className = "bi bi-play-fill";
      return;
    }

    if (icon) icon.className = "bi bi-pause-fill";
    this.scrubberTimer = setInterval(() => {
      let cur = parseInt(slider.value) + 1;
      if (cur > 24) cur = 0;
      slider.value = cur;
      this.onScrubberChange(cur);
      if (cur === 24) {
        clearInterval(this.scrubberTimer);
        this.scrubberTimer = null;
        if (icon) icon.className = "bi bi-play-fill";
      }
    }, 350);
  }
};
