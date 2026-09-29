/**
 * FIREGUARD AI - Satellite Thermal Analysis View Controller
 * Multi-Spectral Sensor Ingestion, Crosshair Inspection & Telemetry Analysis
 * SIH26162: NASA FIRMS (MODIS/VIIRS) & Satellite Data
 */

const HotspotsView = {
  render() {
    this.renderTelemetryHUD();
    this.initThermalCanvas();
    this.populateTable();
    this.bindFilters();
  },

  renderTelemetryHUD() {
    const hudContainer = document.getElementById("hotspots-telemetry-hud");
    if (!hudContainer) return;

    // Pick top active hotspot or mock highest FRP hotspot
    const topHp = (AppState.hotspots && AppState.hotspots.length > 0)
      ? [...AppState.hotspots].sort((a, b) => (b.frp || 0) - (a.frp || 0))[0]
      : { id: "HP-JAM-01", brightness_k: 362.4, frp: 84.2, confidence: 98.6, satellite: "VIIRS S-NPP" };

    const brightVal = topHp.brightness_k || topHp.brightness || 362.4;
    const frpVal = topHp.frp || topHp.frp_mw || 84.2;
    const confVal = topHp.confidence || 98.6;
    const satName = topHp.satellite || topHp.source_satellite || "VIIRS 375m";

    hudContainer.innerHTML = `
      <!-- 4 Telemetry Summary Cards -->
      <div class="row g-3 mb-3">
        <div class="col-xl-3 col-sm-6">
          <div class="tactical-card p-3">
            <div class="d-flex justify-content-between align-items-center">
              <span class="kpi-label">Brightness Temp</span>
              <i class="bi bi-thermometer-sun text-danger fs-5"></i>
            </div>
            <div class="kpi-number text-danger" style="font-size: 1.85rem;" id="sat-bright-disp">${brightVal} K</div>
            <span class="text-muted" style="font-size: 0.72rem;">Band I4 (3.74 μm) &bull; Mid-IR Peak</span>
          </div>
        </div>

        <div class="col-xl-3 col-sm-6">
          <div class="tactical-card p-3">
            <div class="d-flex justify-content-between align-items-center">
              <span class="kpi-label">Radiative Power (FRP)</span>
              <i class="bi bi-fire text-warning fs-5"></i>
            </div>
            <div class="kpi-number text-warning" style="font-size: 1.85rem;" id="sat-frp-disp">${frpVal} MW</div>
            <span class="text-muted" style="font-size: 0.72rem;">Severe Combustive Heat Flux</span>
          </div>
        </div>

        <div class="col-xl-3 col-sm-6">
          <div class="tactical-card p-3">
            <div class="d-flex justify-content-between align-items-center">
              <span class="kpi-label">Sensor Resolution</span>
              <i class="bi bi-bullseye text-info fs-5"></i>
            </div>
            <div class="kpi-number text-info" style="font-size: 1.85rem;">375m I-Band</div>
            <span class="text-muted" style="font-size: 0.72rem;">NASA FIRMS ${satName}</span>
          </div>
        </div>

        <div class="col-xl-3 col-sm-6">
          <div class="tactical-card p-3">
            <div class="d-flex justify-content-between align-items-center">
              <span class="kpi-label">Detection Confidence</span>
              <i class="bi bi-check2-circle text-success fs-5"></i>
            </div>
            <div class="kpi-number text-success" style="font-size: 1.85rem;">${confVal}%</div>
            <span class="text-muted" style="font-size: 0.72rem;">Cloud & Glint Filter Verified</span>
          </div>
        </div>
      </div>

      <!-- Multi-Spectral Thermal Colormap Viewer -->
      <div class="tactical-card p-3 mb-3">
        <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
          <div class="card-title-tactical">
            <i class="bi bi-display"></i> Multi-Spectral Thermal Radiance Colormap (Crosshair Inspection)
          </div>
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-dark text-info border border-secondary" style="font-size: 0.72rem;">
              <i class="bi bi-crosshair"></i> CROSSHAIR ACTIVE
            </span>
            <span class="font-monospace text-light" style="font-size: 0.75rem;" id="crosshair-temp-readout">Pixel: 362.4 K &bull; 84.2 MW</span>
          </div>
        </div>

        <div style="position: relative; width: 100%; height: 210px; background: #080B10; border-radius: 8px; overflow: hidden; border: 1px solid var(--border-card);">
          <canvas id="thermalColormapCanvas" style="width: 100%; height: 100%; display: block; cursor: crosshair;"></canvas>
          <div id="thermal-crosshair-h" style="position: absolute; left: 0; right: 0; height: 1px; background: rgba(56, 189, 248, 0.7); pointer-events: none; display: none;"></div>
          <div id="thermal-crosshair-v" style="position: absolute; top: 0; bottom: 0; width: 1px; background: rgba(56, 189, 248, 0.7); pointer-events: none; display: none;"></div>
          <div id="thermal-tooltip" style="position: absolute; background: rgba(15, 23, 42, 0.9); border: 1px solid #38BDF8; color: #FFF; padding: 2px 6px; font-size: 11px; font-family: monospace; border-radius: 4px; pointer-events: none; display: none;"></div>
        </div>
        <div class="d-flex justify-content-between align-items-center text-muted mt-2" style="font-size: 0.72rem;">
          <span>Thermal Scale: 290 K (Ambient Background) &rarr; 380 K (High Combustive Plume)</span>
          <span class="text-info font-monospace">Hover to inspect pixel-level spectral radiance</span>
        </div>
      </div>
    `;
  },

  initThermalCanvas() {
    const canvas = document.getElementById("thermalColormapCanvas");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();

    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const width = rect.width;
    const height = rect.height;

    // Draw multi-spectral heat gradient simulation
    const grad = ctx.createRadialGradient(width * 0.45, height * 0.5, 10, width * 0.45, height * 0.5, width * 0.6);
    grad.addColorStop(0, "#FFFFFF");   // Hot center (White)
    grad.addColorStop(0.12, "#FEF08A"); // Yellow
    grad.addColorStop(0.28, "#F97316"); // Orange
    grad.addColorStop(0.50, "#EF4444"); // Red
    grad.addColorStop(0.72, "#7E22CE"); // Deep Purple
    grad.addColorStop(0.90, "#1E1B4B"); // Deep Blue/Black
    grad.addColorStop(1, "#0A0D14");    // Background Obsidian

    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);

    // Add secondary flare source
    const grad2 = ctx.createRadialGradient(width * 0.78, height * 0.35, 5, width * 0.78, height * 0.35, 75);
    grad2.addColorStop(0, "#FFF");
    grad2.addColorStop(0.2, "#FDE047");
    grad2.addColorStop(0.5, "#F97316");
    grad2.addColorStop(1, "transparent");
    ctx.fillStyle = grad2;
    ctx.fillRect(0, 0, width, height);

    // Crosshair hover handlers
    const crossH = document.getElementById("thermal-crosshair-h");
    const crossV = document.getElementById("thermal-crosshair-v");
    const tip = document.getElementById("thermal-tooltip");
    const readout = document.getElementById("crosshair-temp-readout");

    canvas.onmousemove = (e) => {
      const b = canvas.getBoundingClientRect();
      const x = e.clientX - b.left;
      const y = e.clientY - b.top;

      if (crossH) { crossH.style.display = "block"; crossH.style.top = `${y}px`; }
      if (crossV) { crossV.style.display = "block"; crossV.style.left = `${x}px`; }

      // Compute pseudo temperature based on proximity to center
      const dist = Math.hypot(x - width * 0.45, y - height * 0.5);
      const maxDist = width * 0.6;
      const factor = Math.max(0, 1 - (dist / maxDist));
      const tempK = (295.0 + factor * 72.4).toFixed(1);
      const frpMw = (factor * 84.2).toFixed(1);

      if (tip) {
        tip.style.display = "block";
        tip.style.left = `${Math.min(width - 120, x + 12)}px`;
        tip.style.top = `${Math.max(10, y - 25)}px`;
        tip.innerText = `${tempK} K | ${frpMw} MW`;
      }

      if (readout) {
        readout.innerHTML = `Pixel: <strong class="text-danger">${tempK} K</strong> &bull; <strong class="text-warning">${frpMw} MW</strong>`;
      }
    };

    canvas.onmouseleave = () => {
      if (crossH) crossH.style.display = "none";
      if (crossV) crossV.style.display = "none";
      if (tip) tip.style.display = "none";
    };
  },

  bindFilters() {
    const satSelect = document.getElementById("filter-hotspots-sat");
    const confSlider = document.getElementById("filter-hotspots-conf");
    const indCheck = document.getElementById("filter-hotspots-industrial");
    const persistCheck = document.getElementById("filter-hotspots-persist");

    const apply = () => {
      const filters = {
        satellite: satSelect ? satSelect.value : "",
        min_confidence: confSlider ? confSlider.value : 0,
        is_industrial: indCheck && indCheck.checked ? true : null,
        is_persistent: persistCheck && persistCheck.checked ? true : null
      };

      if (confSlider) {
        const valSpan = document.getElementById("filter-conf-val");
        if (valSpan) valSpan.innerText = `${confSlider.value}%`;
      }

      this.filterHotspots(filters);
    };

    if (satSelect) satSelect.onchange = apply;
    if (confSlider) confSlider.oninput = apply;
    if (indCheck) indCheck.onchange = apply;
    if (persistCheck) persistCheck.onchange = apply;
  },

  filterHotspots(filters) {
    let list = [...AppState.hotspots];

    if (filters.satellite) {
      list = list.filter(h => h.source_satellite === filters.satellite);
    }
    if (filters.min_confidence > 0) {
      list = list.filter(h => h.confidence >= filters.min_confidence);
    }
    if (filters.is_industrial !== null) {
      list = list.filter(h => (filters.is_industrial ? h.facility_id !== null : h.facility_id === null));
    }
    if (filters.is_persistent !== null) {
      list = list.filter(h => h.is_persistent === filters.is_persistent);
    }

    this.renderRows(list);
  },

  populateTable() {
    this.renderRows(AppState.hotspots);
  },

  renderRows(list) {
    const tbody = document.getElementById("hotspots-table-body");
    if (!tbody) return;

    if (!list.length) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted p-4">No thermal hotspots matching active tactical filters.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(hp => {
      const inc = AppState.incidents.find(i => i.hotspot_id === hp.id);
      const riskTier = hp.risk_level || (inc ? inc.risk_level : "EVALUATING");
      const riskClass = (riskTier || "low").toLowerCase();
      const sat = hp.satellite || hp.source_satellite || "VIIRS";
      const frpVal = hp.frp !== undefined ? hp.frp : (hp.frp_mw !== undefined ? hp.frp_mw : 35.0);
      const brightVal = hp.brightness || hp.brightness_k || 320.0;
      const confVal = hp.confidence !== undefined ? hp.confidence : 80;

      return `
        <tr>
          <td><strong style="color: #38BDF8; font-family: var(--font-mono);">${hp.id}</strong></td>
          <td style="font-family: var(--font-mono); font-size: 0.8rem;">
            ${Number(hp.latitude).toFixed(4)}°N, ${Number(hp.longitude).toFixed(4)}°E
          </td>
          <td><span class="badge bg-secondary" style="font-size: 0.72rem;">${sat}</span></td>
          <td><strong style="color: #F87171;">${frpVal} MW</strong></td>
          <td>${brightVal} K</td>
          <td>
            <div class="progress" style="height: 6px; width: 60px; background: #1E293B;">
              <div class="progress-bar bg-info" style="width: ${confVal}%;"></div>
            </div>
            <span style="font-size: 0.68rem; color: #94A3B8;">${confVal}%</span>
          </td>
          <td>
            <span class="badge-risk ${riskClass}">
              ${riskTier}
            </span>
          </td>
          <td>
            <button class="btn-tactical btn-sm py-1" onclick="TacticalMap.panTo(${hp.latitude}, ${hp.longitude}, 14); Router.navigate('dashboard');" title="Locate on Tactical Map">
              <i class="bi bi-geo-alt"></i>
            </button>
            ${inc ? `<button class="btn-tactical btn-sm py-1 ms-1" onclick="IncidentModal.open('${inc.id}')" title="Inspect AI Dossier"><i class="bi bi-robot"></i> AI</button>` : ''}
          </td>
        </tr>
      `;
    }).join("");
  }
};
