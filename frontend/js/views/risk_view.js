/**
 * FIREGUARD AI - Explainable AI Risk Analysis View Controller
 */
const RiskView = {
  render() {
    this.populateIncidentDropdown();
    this.inspectIncident(AppState.incidents[0] ? AppState.incidents[0].id : null);
  },

  populateIncidentDropdown() {
    const sel = document.getElementById("risk-incident-select");
    if (!sel) return;

    sel.innerHTML = AppState.incidents.map(i => `
      <option value="${i.id}" ${AppState.activeIncident && AppState.activeIncident.id === i.id ? 'selected' : ''}>
        ${i.id} - ${i.title} (${i.risk_level})
      </option>
    `).join("");

    sel.onchange = (e) => {
      this.inspectIncident(e.target.value);
    };
  },

  inspectIncident(incidentId) {
    if (!incidentId) return;
    const inc = AppState.incidents.find(i => i.id === incidentId);
    if (!inc) return;

    const risk = inc.risk_breakdown || {};
    const factors = risk.factor_breakdown || {};

    const container = document.getElementById("risk-analysis-container");
    if (!container) return;

    container.innerHTML = `
      <div class="row g-3">
        <div class="col-lg-5">
          <div class="tactical-card h-100 p-3">
            <div class="card-title-tactical">
              <i class="bi bi-shield-shaded"></i> Composite Risk Score
            </div>
            <div class="text-center my-3">
              <div style="font-size: 3.5rem; font-weight: 900; font-family: var(--font-mono); color: ${inc.risk_level === 'CRITICAL' ? '#EF4444' : (inc.risk_level === 'HIGH' ? '#F97316' : '#F59E0B')}; line-height: 1;">
                ${inc.risk_score}
              </div>
              <div style="font-size: 0.85rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px;">
                Risk Category: <strong class="text-light">${inc.risk_level}</strong>
              </div>
            </div>

            <div class="xai-box">
              <h6><i class="bi bi-cpu"></i> Why Was This Score Generated?</h6>
              <div style="font-size: 0.8rem; color: #CBD5E1; line-height: 1.5; white-space: pre-line;">
                ${risk.why_explanation || 'Synthesized based on proximity to high-hazard industrial asset and radiant energy release.'}
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-7">
          <div class="tactical-card h-100 p-3">
            <div class="card-title-tactical">
              <i class="bi bi-bar-chart-steps"></i> Multi-Dimensional Factor Contribution
            </div>
            
            <div class="mb-3">
              <div class="d-flex justify-content-between text-muted" style="font-size: 0.78rem;">
                <span>Facility Proximity & Hazard Tier (Max 30 pts)</span>
                <strong class="text-info">${factors.facility_proximity_pts || 0} pts</strong>
              </div>
              <div class="progress" style="height: 8px; background: #1E293B;">
                <div class="progress-bar bg-info" style="width: ${((factors.facility_proximity_pts || 0)/30)*100}%;"></div>
              </div>
            </div>

            <div class="mb-3">
              <div class="d-flex justify-content-between text-muted" style="font-size: 0.78rem;">
                <span>Thermal Radiative Energy / FRP (Max 25 pts)</span>
                <strong class="text-danger">${factors.thermal_intensity_pts || 0} pts</strong>
              </div>
              <div class="progress" style="height: 8px; background: #1E293B;">
                <div class="progress-bar bg-danger" style="width: ${((factors.thermal_intensity_pts || 0)/25)*100}%;"></div>
              </div>
            </div>

            <div class="mb-3">
              <div class="d-flex justify-content-between text-muted" style="font-size: 0.78rem;">
                <span>NASA FIRMS Satellite Confidence (Max 15 pts)</span>
                <strong class="text-success">${factors.satellite_confidence_pts || 0} pts</strong>
              </div>
              <div class="progress" style="height: 8px; background: #1E293B;">
                <div class="progress-bar bg-success" style="width: ${((factors.satellite_confidence_pts || 0)/15)*100}%;"></div>
              </div>
            </div>

            <div class="mb-3">
              <div class="d-flex justify-content-between text-muted" style="font-size: 0.78rem;">
                <span>Proximity to Civilian Population (Max 10 pts)</span>
                <strong class="text-warning">${factors.population_exposure_pts || 0} pts</strong>
              </div>
              <div class="progress" style="height: 8px; background: #1E293B;">
                <div class="progress-bar bg-warning" style="width: ${((factors.population_exposure_pts || 0)/10)*100}%;"></div>
              </div>
            </div>

            <div class="mb-2">
              <div class="d-flex justify-content-between text-muted" style="font-size: 0.78rem;">
                <span>Critical Infrastructure Lifelines (Max 10 pts)</span>
                <strong class="text-primary">${factors.critical_infrastructure_pts || 0} pts</strong>
              </div>
              <div class="progress" style="height: 8px; background: #1E293B;">
                <div class="progress-bar bg-primary" style="width: ${((factors.critical_infrastructure_pts || 0)/10)*100}%;"></div>
              </div>
            </div>

            <div class="p-2 mt-3 rounded" style="background: rgba(14, 165, 233, 0.08); border: 1px solid rgba(14, 165, 233, 0.2); font-size: 0.75rem;">
              <i class="bi bi-lightbulb text-info me-1"></i>
              <strong>SIH Explainability Note:</strong> Every thermal anomaly undergoes real-time spatial joins with OSM infrastructure boundaries and multi-satellite confidence metrics to yield clear, explainable decision factors rather than an unexplainable black-box score.
            </div>
          </div>
        </div>
      </div>
    `;
  }
};
