/**
 * FIREGUARD AI - Incident Command Dossier Modal & Offcanvas Controller
 * Provides in-depth satellite telemetry, AI classification explainability,
 * risk factor attributions, emergency actions, and simulated dispatch payloads.
 */
const IncidentModal = {
  currentIncident: null,

  async open(incidentId) {
    try {
      const data = await Api.fetchIncidentDetail(incidentId);
      this.currentIncident = data;
      AppState.activeIncident = data;
      this.renderModalContent(data);

      const modalEl = document.getElementById("incidentDossierModal");
      if (modalEl && typeof bootstrap !== "undefined") {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
      }
    } catch (err) {
      console.error("Failed to load incident detail:", err);
      alert("Unable to load incident dossier.");
    }
  },

  renderModalContent(inc) {
    const titleEl = document.getElementById("dossier-title");
    const idEl = document.getElementById("dossier-id");
    const riskBadgeEl = document.getElementById("dossier-risk-badge");
    const statusBadgeEl = document.getElementById("dossier-status-badge");
    const contentEl = document.getElementById("dossier-body-content");

    if (titleEl) titleEl.innerText = inc.title;
    if (idEl) idEl.innerText = inc.id;

    if (riskBadgeEl) {
      riskBadgeEl.className = `badge-risk ${inc.risk_level.toLowerCase()}`;
      riskBadgeEl.innerHTML = `<i class="bi bi-exclamation-triangle-fill"></i> ${inc.risk_level} (${inc.risk_score}/100)`;
    }

    if (statusBadgeEl) {
      statusBadgeEl.innerText = (inc.status || "DETECTED").replace(/_/g, ' ');
    }

    // Role-Based Access Control on Dossier Actions
    const userRole = (AppState.currentUser?.role || "OPERATOR").toUpperCase();
    const opActions = document.getElementById("dossier-operator-actions");
    const pubActions = document.getElementById("dossier-public-actions");
    const dispBtn = document.getElementById("btn-dossier-dispatch");

    if (userRole === "PUBLIC") {
      if (opActions) opActions.style.display = "none";
      if (pubActions) pubActions.style.display = "flex";
      if (dispBtn) dispBtn.style.display = "none";
    } else if (userRole === "ANALYST") {
      if (opActions) opActions.style.display = "none";
      if (pubActions) pubActions.style.display = "none";
      if (dispBtn) dispBtn.style.display = "none";
    } else {
      if (opActions) opActions.style.display = "flex";
      if (pubActions) pubActions.style.display = "none";
      if (dispBtn) dispBtn.style.display = "inline-flex";
    }

    if (!contentEl) return;

    const hp = inc.hotspot || {};
    const ai = inc.ai_classification || {};
    const risk = inc.risk_breakdown || {};
    const fac = inc.facility || {};
    const evac = inc.evacuation_plan || {};

    const factors = ai.top_factors || [];

    contentEl.innerHTML = `
      <div class="row g-3">
        <!-- 1. Satellite Observation Telemetry -->
        <div class="col-lg-6">
          <div class="tactical-card h-100 p-3">
            <div class="card-title-tactical">
              <i class="bi bi-broadcast-pin"></i> NASA FIRMS Satellite Telemetry
            </div>
            <table class="table table-sm table-borderless text-light mb-0" style="font-size: 0.8rem;">
              <tr>
                <td class="text-muted">Satellite Sensor:</td>
                <td><strong class="text-info">${hp.source_satellite || 'VIIRS_SNPP'}</strong></td>
              </tr>
              <tr>
                <td class="text-muted">Coordinates:</td>
                <td class="font-monospace text-warning">${hp.latitude ? hp.latitude.toFixed(5) : 0}° N, ${hp.longitude ? hp.longitude.toFixed(5) : 0}° E</td>
              </tr>
              <tr>
                <td class="text-muted">Fire Radiative Power:</td>
                <td><strong class="text-danger fs-6">${hp.frp_mw || 0} MW</strong></td>
              </tr>
              <tr>
                <td class="text-muted">Brightness Temp:</td>
                <td>${hp.brightness_k || 0} K</td>
              </tr>
              <tr>
                <td class="text-muted">FIRMS Confidence:</td>
                <td>
                  <div class="d-flex align-items-center gap-2">
                    <div class="progress flex-grow-1" style="height: 6px; background: #1E293B;">
                      <div class="progress-bar bg-success" style="width: ${hp.confidence || 80}%;"></div>
                    </div>
                    <span>${hp.confidence || 80}%</span>
                  </div>
                </td>
              </tr>
              <tr>
                <td class="text-muted">Observation Time:</td>
                <td>${hp.acquisition_date || ''} ${hp.acquisition_time || ''} UTC (${hp.daynight === 'N' ? 'Night Overpass' : 'Day Overpass'})</td>
              </tr>
            </table>
          </div>
        </div>

        <!-- 2. AI Fire Classification & XAI -->
        <div class="col-lg-6">
          <div class="tactical-card h-100 p-3">
            <div class="card-title-tactical">
              <i class="bi bi-cpu"></i> AI Fire Classification (8-Class ML Model)
            </div>
            <div class="d-flex align-items-center justify-content-between mb-2">
              <span class="badge bg-primary fs-6 px-3 py-1">
                ${ai.primary_class || (inc.classification || inc.fire_class || 'Industrial Fire').replace(/_/g, ' ')}
              </span>
              <span class="text-info fw-bold" style="font-size: 0.85rem;">
                Confidence: ${ai.confidence_pct || (inc.confidence ? Math.round(inc.confidence * 100) : 91.5)}%
              </span>
            </div>

            <!-- Explainability Box -->
            <div class="xai-box">
              <h6><i class="bi bi-info-circle"></i> AI Classification Rationale</h6>
              <ul class="xai-factor-list">
                ${factors.map(f => `<li><i class="bi bi-chevron-right"></i> <span>${f}</span></li>`).join("")}
              </ul>
            </div>

            <div class="mt-2 p-2 rounded" style="background: rgba(14, 165, 233, 0.08); border: 1px solid rgba(14, 165, 233, 0.2); font-size: 0.76rem;">
              <strong class="text-info d-block mb-1"><i class="bi bi-shield-exclamation"></i> Recommended Emergency Protocol:</strong>
              <div class="text-muted">${ai.recommended_response || inc.response_notes || 'Deploy containment perimeter.'}</div>
            </div>

            <div class="mt-2 text-muted" style="font-size: 0.68rem; font-style: italic;">
              * AI predictive assessment generated for situational awareness. Not certified as medical or forensic ground truth.
            </div>
          </div>
        </div>

        <!-- 3. Explainable Risk Score Breakdown -->
        <div class="col-lg-6">
          <div class="tactical-card h-100 p-3">
            <div class="card-title-tactical">
              <i class="bi bi-speedometer2"></i> Explainable Risk Engine (Score: ${inc.risk_score}/100)
            </div>
            <div class="progress mb-2" style="height: 10px; background: #1E293B;">
              <div class="progress-bar ${inc.risk_level === 'CRITICAL' ? 'bg-danger' : 'bg-warning'}" style="width: ${inc.risk_score}%;"></div>
            </div>
            <div class="text-light mb-2" style="font-size: 0.78rem; line-height: 1.5; white-space: pre-line;">
              ${risk.why_explanation || 'Risk evaluated based on facility proximity and thermal energy release.'}
            </div>

            <!-- Factor breakdown badges -->
            ${risk.factor_breakdown ? `
              <div class="d-flex flex-wrap gap-1 mt-2">
                <span class="badge bg-dark border border-secondary" style="font-size: 0.7rem;">Facility: ${risk.factor_breakdown.facility_proximity_pts} pts</span>
                <span class="badge bg-dark border border-secondary" style="font-size: 0.7rem;">Intensity: ${risk.factor_breakdown.thermal_intensity_pts} pts</span>
                <span class="badge bg-dark border border-secondary" style="font-size: 0.7rem;">Confidence: ${risk.factor_breakdown.satellite_confidence_pts} pts</span>
                <span class="badge bg-dark border border-secondary" style="font-size: 0.7rem;">Population: ${risk.factor_breakdown.population_exposure_pts} pts</span>
              </div>
            ` : ''}
          </div>
        </div>

        <!-- 4. Industrial Facility & Emergency Resources -->
        <div class="col-lg-6">
          <div class="tactical-card h-100 p-3">
            <div class="card-title-tactical">
              <i class="bi bi-geo"></i> Facility & Nearby Lifelines
            </div>
            <div class="mb-2">
              <div class="fw-bold text-info" style="font-size: 0.88rem;">${fac.name || 'Unmapped Industrial Zone'}</div>
              <div class="text-muted" style="font-size: 0.75rem;">${fac.address || 'Industrial Corridor'}</div>
              <div class="text-muted" style="font-size: 0.75rem;">Hazard Category: <span class="text-warning">${fac.hazard_category || 'TIER_1'}</span></div>
              <div class="text-muted" style="font-size: 0.75rem;">Plant Contact: <span class="text-light">${fac.emergency_contact_phone || '+91 101'}</span></div>
            </div>

            <hr style="border-color: rgba(255,255,255,0.08); margin: 0.5rem 0;">

            <div class="row g-2 text-center" style="font-size: 0.75rem;">
              <div class="col-6">
                <div class="p-2 rounded" style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3);">
                  <i class="bi bi-hospital text-danger d-block fs-5"></i>
                  <strong>Nearest Hospital</strong><br>
                  <span class="text-muted">${evac.nearest_hospital ? evac.nearest_hospital.distance_km + ' km' : '3.8 km'}</span>
                </div>
              </div>
              <div class="col-6">
                <div class="p-2 rounded" style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3);">
                  <i class="bi bi-fire text-warning d-block fs-5"></i>
                  <strong>Nearest Fire Hazmat</strong><br>
                  <span class="text-muted">${evac.nearest_fire_station ? evac.nearest_fire_station.distance_km + ' km' : '2.1 km'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  async setStatus(newStatus) {
    if (!this.currentIncident) return;
    const notes = prompt(`Enter tactical operational notes for status transition to [${newStatus}]:`, `Operator updated status to ${newStatus}`);
    if (notes === null) return;

    try {
      const res = await Api.updateIncidentStatus(this.currentIncident.id, newStatus, notes);
      const incObj = res.incident || res;
      this.currentIncident = incObj;
      AppState.activeIncident = incObj;

      // Update in local cache
      const idx = AppState.incidents.findIndex(i => i.id === incObj.id);
      if (idx !== -1) AppState.incidents[idx] = incObj;

      // Re-render views
      IncidentsView.render();
      DashboardView.render();
      this.renderModalContent(incObj);

      alert(`Incident status successfully updated to [${newStatus}].`);
    } catch (err) {
      alert("Failed to update status: " + err.message);
    }
  },

  openSafetyRoute() {
    if (!this.currentIncident) return;
    const modalEl = document.getElementById("incidentDossierModal");
    if (modalEl && typeof bootstrap !== "undefined") {
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
    }
    RoutingView.showForIncident(this.currentIncident.id);
  },

  async triggerSimulatedDispatch() {
    if (!this.currentIncident) return;
    try {
      const res = await Api.simulateDispatch(this.currentIncident.id);
      EmergencyView.showDispatchPayloadModal(res.payload || res);
    } catch (err) {
      alert("Dispatch simulation failed: " + err.message);
    }
  }
};
