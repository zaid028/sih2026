/**
 * FIREGUARD AI - Industrial Facilities View Controller
 */
const FacilitiesView = {
  render() {
    this.renderCards();
  },

  renderCards() {
    const container = document.getElementById("facilities-grid-container");
    if (!container) return;

    if (!AppState.facilities.length) {
      container.innerHTML = `<div class="col-12 text-center text-muted p-4">Loading industrial facility database...</div>`;
      return;
    }

    container.innerHTML = AppState.facilities.map(fac => {
      const hasActive = (fac.active_incidents_count || 0) > 0;
      const cardBorder = hasActive ? "border-danger" : "border-info";
      const hazCategory = fac.hazard_category || fac.hazmat_level || "HAZMAT_TIER_1";
      const hazardColor = hazCategory.includes("TIER_1") || hazCategory.includes("LEVEL-4") ? "danger" : "warning";
      const facType = (fac.facility_type || "Industrial Complex").toUpperCase();
      const contactName = fac.emergency_contact_name || fac.emergency_contact || "Safety Officer";
      const contactPhone = fac.emergency_contact_phone || fac.emergency_phone || "+91 101";

      return `
        <div class="col-lg-4 col-md-6">
          <div class="tactical-card h-100 p-3 ${cardBorder}">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <span class="badge bg-${hazardColor} text-uppercase" style="font-size: 0.68rem;">
                ${hazCategory.replace(/_/g, ' ')}
              </span>
              ${hasActive ? `<span class="badge bg-danger pulse-dot critical"></span>` : '<span class="badge bg-success">NOMINAL</span>'}
            </div>
            <h5 class="text-light fw-bold mb-1" style="font-size: 1rem;">${fac.name}</h5>
            <div class="text-info mb-2" style="font-size: 0.78rem;">
              <i class="bi bi-tag"></i> ${facType} &bull; ${fac.district || ''}, ${fac.state || ''}
            </div>
            <p class="text-muted mb-3" style="font-size: 0.76rem; min-height: 34px;">
              ${fac.address || 'Industrial Special Economic Zone Corridor'}
            </p>

            <div class="p-2 rounded mb-3" style="background: rgba(15, 23, 42, 0.8); font-size: 0.76rem;">
              <div class="d-flex justify-content-between mb-1">
                <span class="text-muted">Safety Commander:</span>
                <span class="text-light">${contactName}</span>
              </div>
              <div class="d-flex justify-content-between">
                <span class="text-muted">Emergency Hotline:</span>
                <span class="text-warning font-monospace">${contactPhone}</span>
              </div>
            </div>

            <div class="d-flex gap-2 mt-auto">
              <button class="btn-tactical btn-sm flex-grow-1" onclick="FacilitiesView.openProfile('${fac.id}')">
                <i class="bi bi-building"></i> Deep Profile
              </button>
              <button class="btn-tactical btn-sm" onclick="TacticalMap.panTo(${fac.latitude}, ${fac.longitude}, 14); Router.navigate('dashboard');" title="Center on Map">
                <i class="bi bi-geo-alt"></i>
              </button>
            </div>
          </div>
        </div>
      `;
    }).join("");
  },

  async openProfile(facilityId) {
    try {
      const fac = await Api.fetchFacilityDetail(facilityId);
      const titleEl = document.getElementById("facility-modal-title");
      const bodyEl = document.getElementById("facility-modal-body");

      if (titleEl) titleEl.innerText = fac.name;
      if (bodyEl) {
        bodyEl.innerHTML = `
          <div class="row g-3">
            <div class="col-md-6">
              <div class="p-3 rounded" style="background: rgba(15, 23, 42, 0.8); border: 1px solid var(--border-subtle);">
                <h6 class="text-info text-uppercase mb-2" style="font-size: 0.78rem;">Plant Specification & Hazard Tier</h6>
                <table class="table table-sm table-borderless text-light mb-0" style="font-size: 0.8rem;">
                  <tr><td class="text-muted">Facility Type:</td><td>${(fac.facility_type || 'Industrial').toUpperCase()}</td></tr>
                  <tr><td class="text-muted">Hazard Classification:</td><td class="text-danger fw-bold">${fac.hazard_category || fac.hazmat_level || 'LEVEL-3'}</td></tr>
                  <tr><td class="text-muted">Coordinates:</td><td class="font-monospace">${Number(fac.latitude || 0).toFixed(5)}°N, ${Number(fac.longitude || 0).toFixed(5)}°E</td></tr>
                  <tr><td class="text-muted">District / State:</td><td>${fac.district || ''}, ${fac.state || ''}</td></tr>
                  <tr><td class="text-muted">Address:</td><td>${fac.address || 'Industrial SEZ Area'}</td></tr>
                </table>
              </div>
            </div>

            <div class="col-md-6">
              <div class="p-3 rounded" style="background: rgba(15, 23, 42, 0.8); border: 1px solid var(--border-subtle);">
                <h6 class="text-info text-uppercase mb-2" style="font-size: 0.78rem;">Nearby Emergency Infrastructure (Within 25km)</h6>
                <div style="max-height: 180px; overflow-y: auto;">
                  ${(fac.emergency_resources || []).map(r => `
                    <div class="d-flex justify-content-between align-items-center p-1 border-bottom border-secondary" style="font-size: 0.78rem;">
                      <div>
                        <strong>${r.name}</strong>
                        <div class="text-muted" style="font-size: 0.7rem;">${(r.facility_type || 'Station').toUpperCase()} &bull; Phone: ${r.phone || '101'}</div>
                      </div>
                      <span class="badge bg-secondary font-monospace">${r.distance_km || 0} km</span>
                    </div>
                  `).join("") || '<div class="text-muted">No emergency stations registered within radius.</div>'}
                </div>
              </div>
            </div>

            <div class="col-12">
              <div class="p-3 rounded" style="background: rgba(15, 23, 42, 0.8); border: 1px solid var(--border-subtle);">
                <h6 class="text-info text-uppercase mb-2" style="font-size: 0.78rem;">Historical Thermal Hotspots & Incidents Log</h6>
                <div class="table-responsive">
                  <table class="table table-sm text-light mb-0" style="font-size: 0.78rem;">
                    <thead>
                      <tr class="text-muted">
                        <th>ID / Time</th><th>Type</th><th>FRP</th><th>Brightness</th><th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${(fac.incidents || []).map(inc => `
                        <tr>
                          <td class="font-monospace text-info">${inc.id}</td>
                          <td>${(inc.classification || inc.fire_class || 'Thermal Source').replace(/_/g, ' ')}</td>
                          <td class="text-danger">${inc.hotspot ? inc.hotspot.frp_mw + ' MW' : 'N/A'}</td>
                          <td>${inc.hotspot ? inc.hotspot.brightness_k + ' K' : 'N/A'}</td>
                          <td><span class="badge bg-primary">${inc.status || 'DETECTED'}</span></td>
                        </tr>
                      `).join("") || '<tr><td colspan="5" class="text-muted">No prior thermal anomalies recorded.</td></tr>'}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        `;
      }

      const modalEl = document.getElementById("facilityDetailModal");
      if (modalEl && typeof bootstrap !== "undefined") {
        bootstrap.Modal.getOrCreateInstance(modalEl).show();
      }
    } catch (err) {
      console.error("Facility detail fetch failed:", err);
    }
  }
};
