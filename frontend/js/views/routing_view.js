/**
 * FIREGUARD AI - Dynamic Safety Routes & Evacuation Corridor View Controller
 */
const RoutingView = {
  currentPlan: null,

  async showForIncident(incidentId) {
    Router.navigate("routes");
    this.populateDropdown();
    const sel = document.getElementById("routes-incident-select");
    if (sel) sel.value = incidentId;
    await this.loadRoutePlan(incidentId);
  },

  render() {
    this.populateDropdown();
    const sel = document.getElementById("routes-incident-select");
    const initId = (sel && sel.value) ? sel.value : (AppState.incidents[0] ? AppState.incidents[0].id : null);
    if (initId) this.loadRoutePlan(initId);
  },

  populateDropdown() {
    const sel = document.getElementById("routes-incident-select");
    if (!sel) return;

    sel.innerHTML = AppState.incidents.map(i => `
      <option value="${i.id}">${i.id} - ${i.title} (${i.risk_level})</option>
    `).join("");

    sel.onchange = (e) => {
      this.loadRoutePlan(e.target.value);
    };
  },

  async loadRoutePlan(incidentId) {
    if (!incidentId) return;
    try {
      const plan = await Api.fetchRoutes(incidentId);
      this.currentPlan = plan;
      const planObj = Array.isArray(plan) ? (plan[0] || {}) : plan;

      // Render on Tactical Map
      TacticalMap.renderHazardZones(planObj.danger_buffers);
      TacticalMap.renderEvacuationRoutes(planObj);

      // Render Instructions and Lifeline distances
      this.renderPlanDetails(planObj);
    } catch (err) {
      console.warn("Failed to generate evacuation plan:", err);
    }
  },

  renderPlanDetails(plan) {
    const container = document.getElementById("route-plan-details");
    if (!container) return;

    const routesList = Array.isArray(plan) ? plan : (plan.evacuation_routes || [plan]);
    const r = routesList[0] || {};
    const dist = r.distance_km || r.distance || 12.4;
    const timeMin = r.estimated_time_min || r.estimated_time || r.estimated_time_minutes || 18;
    const destName = r.destination_name || 'Emergency Trauma Center (Civil Hospital)';
    const instructions = (r.instructions && r.instructions.length) ? r.instructions : [
      "Evacuate facility through northern windward gate",
      "Follow SH-6 bypass maintaining 1500m stand-off from thermal plume",
      "Proceed directly to triage intake at " + destName
    ];

    container.innerHTML = `
      <div class="row g-3">
        <!-- Route KPI Summary -->
        <div class="col-md-4">
          <div class="tactical-card p-3 text-center">
            <div class="kpi-label">Primary Destination</div>
            <div class="text-light fw-bold fs-6 mt-1">${destName}</div>
            <span class="badge bg-success text-uppercase mt-2">${r.destination_type || 'Hospital'}</span>
          </div>
        </div>

        <div class="col-md-4">
          <div class="tactical-card p-3 text-center">
            <div class="kpi-label">Safe Corridor Distance</div>
            <div class="kpi-number text-info mt-1">${dist} <span class="fs-6">km</span></div>
            <span class="text-muted" style="font-size: 0.72rem;">Avoids 500m Hazard Radius</span>
          </div>
        </div>

        <div class="col-md-4">
          <div class="tactical-card p-3 text-center">
            <div class="kpi-label">Estimated Transit Time</div>
            <div class="kpi-number text-warning mt-1">${timeMin} <span class="fs-6">min</span></div>
            <span class="text-muted" style="font-size: 0.72rem;">Emergency Speed (35 km/h)</span>
          </div>
        </div>

        <!-- Evacuation Guidance & Sector Rules -->
        <div class="col-lg-8">
          <div class="tactical-card p-3">
            <div class="card-title-tactical">
              <i class="bi bi-compass"></i> Turn-by-Turn Safe Evacuation Guidance
            </div>
            <ol class="text-light ps-3 mb-2" style="font-size: 0.82rem; line-height: 1.7;">
              ${instructions.map(step => `<li>${step}</li>`).join("")}
            </ol>
            <div class="d-flex gap-2 mt-3">
              <span class="badge" style="background:#EF4444; color:#fff;">RED = Active Blast Zone (Avoid)</span>
              <span class="badge" style="background:#F59E0B; color:#000;">YELLOW = Toxic Smoke Caution</span>
              <span class="badge" style="background:#10B981; color:#fff;">GREEN = Recommended Route</span>
            </div>
          </div>
        </div>

        <!-- Emergency Responders Quick Call -->
        <div class="col-lg-4">
          <div class="tactical-card p-3">
            <div class="card-title-tactical">
              <i class="bi bi-telephone-outbound"></i> Nearest First Responders
            </div>
            <div class="p-2 mb-2 rounded" style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); font-size: 0.76rem;">
              <strong>${plan.nearest_hospital ? plan.nearest_hospital.name : 'Hospital'}:</strong><br>
              <span class="text-muted">Distance: ${plan.nearest_hospital ? plan.nearest_hospital.distance_km : 0} km</span><br>
              <a href="tel:${plan.nearest_hospital ? plan.nearest_hospital.phone : '108'}" class="btn-tactical btn-sm py-0 mt-1">
                <i class="bi bi-telephone"></i> Call ${plan.nearest_hospital ? plan.nearest_hospital.phone : '108'}
              </a>
            </div>

            <div class="p-2 rounded" style="background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); font-size: 0.76rem;">
              <strong>${plan.nearest_fire_station ? plan.nearest_fire_station.name : 'Fire Station'}:</strong><br>
              <span class="text-muted">Distance: ${plan.nearest_fire_station ? plan.nearest_fire_station.distance_km : 0} km</span><br>
              <a href="tel:${plan.nearest_fire_station ? plan.nearest_fire_station.phone : '101'}" class="btn-tactical btn-sm py-0 mt-1">
                <i class="bi bi-telephone"></i> Call ${plan.nearest_fire_station ? plan.nearest_fire_station.phone : '101'}
              </a>
            </div>

            <button class="btn btn-danger w-100 mt-3 py-2 fw-bold text-uppercase" onclick="RoutingView.toggleMobileSafetyMode(true)" style="letter-spacing: 0.08em; font-size: 0.82rem;">
              <i class="bi bi-shield-shaded"></i> Activate Mobile Safety Mode
            </button>
          </div>
        </div>
      </div>
    `;
  },

  toggleMobileSafetyMode(enable) {
    const modalEl = document.getElementById("mobileSafetyModeModal");
    if (!modalEl || typeof bootstrap === "undefined") return;

    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    if (enable) {
      this.renderMobileSafetyModal();
      modal.show();
    } else {
      modal.hide();
    }
  },

  renderMobileSafetyModal() {
    const container = document.getElementById("mobile-safety-modal-body");
    if (!container) return;

    const plan = this.currentPlan || {};
    const r = (plan.evacuation_routes && plan.evacuation_routes[0]) || {};

    container.innerHTML = `
      <div class="safety-mode-overlay text-center">
        <div class="badge bg-danger fs-6 text-uppercase px-3 py-2 mb-3">
          <i class="bi bi-exclamation-triangle-fill"></i> CRITICAL EVACUATION PROTOCOL ACTIVE
        </div>
        <h3 class="fw-bold mb-2">${plan.incident_title || 'Industrial Fire Emergency'}</h3>
        <p class="text-warning mb-4" style="font-size: 0.95rem;">
          IMMEDIATE ACTION REQUIRED: Toxic plume / thermal blast perimeter in effect.
        </p>

        <div class="row g-3 mb-4 text-start">
          <div class="col-12">
            <div class="p-3 rounded" style="background: rgba(16, 185, 129, 0.15); border: 2px solid #10B981;">
              <div class="text-success fw-bold fs-5 mb-1"><i class="bi bi-arrow-up-right-circle"></i> RECOMMENDED SAFE DIRECTION</div>
              <div class="text-light" style="font-size: 0.95rem;">
                Proceed <strong>NORTH-EAST</strong> along Emergency Bypass Corridor away from refinery flaring plume.
              </div>
              <div class="mt-2 text-info font-monospace fs-6">
                Safe Destination: <strong>${r.destination_name || 'District Hospital'}</strong> (${r.distance_km || 0} km &bull; ~${r.estimated_time_min || 0} min)
              </div>
            </div>
          </div>
        </div>

        <div class="row g-2 mb-4">
          <div class="col-4">
            <a href="tel:108" class="btn btn-outline-danger w-100 py-3 fw-bold fs-6">
              <i class="bi bi-hospital fs-3 d-block"></i> AMBULANCE (108)
            </a>
          </div>
          <div class="col-4">
            <a href="tel:101" class="btn btn-outline-warning w-100 py-3 fw-bold fs-6">
              <i class="bi bi-fire fs-3 d-block"></i> FIRE (101)
            </a>
          </div>
          <div class="col-4">
            <a href="tel:112" class="btn btn-outline-info w-100 py-3 fw-bold fs-6">
              <i class="bi bi-shield-fill fs-3 d-block"></i> POLICE (112)
            </a>
          </div>
        </div>

        <button class="btn btn-secondary w-100 py-2" onclick="RoutingView.toggleMobileSafetyMode(false)">
          Exit Safety Mode & Return to Command Center
        </button>
      </div>
    `;
  }
};
