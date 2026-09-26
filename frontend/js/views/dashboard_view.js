/**
 * FIREGUARD AI - Dashboard View Controller
 */
const DashboardView = {
  render() {
    this.updateKpis();
    this.renderThreatCards();
  },

  async updateKpis() {
    try {
      const kpis = await Api.fetchAnalyticsKpis();
      document.getElementById("kpi-total-hotspots").innerText = kpis.total_hotspots || 0;
      document.getElementById("kpi-industrial-fires").innerText = kpis.industrial_fires || 0;
      document.getElementById("kpi-high-risk").innerText = kpis.high_risk_incidents || 0;
      document.getElementById("kpi-persistent-sources").innerText = kpis.persistent_sources || 0;
      document.getElementById("kpi-avg-response").innerText = `${kpis.avg_response_time_min}m`;

      // Update navbar threat counter
      const threatPill = document.getElementById("nav-threat-count");
      if (threatPill) {
        threatPill.innerText = `${kpis.high_risk_incidents} CRITICAL THREATS`;
        if (kpis.high_risk_incidents > 0) {
          threatPill.classList.add("critical");
        } else {
          threatPill.classList.remove("critical");
        }
      }
    } catch (err) {
      console.warn("KPI update failed:", err);
    }
  },

  renderThreatCards() {
    const container = document.getElementById("dashboard-active-threats");
    if (!container) return;

    const criticalIncidents = AppState.incidents.filter(i => i.risk_level === "CRITICAL" || i.risk_level === "HIGH");

    if (!criticalIncidents.length) {
      container.innerHTML = `
        <div class="text-center p-3 text-muted" style="font-size: 0.85rem;">
          <i class="bi bi-shield-check text-success fs-4 d-block mb-1"></i>
          All monitored industrial perimeters currently report normal thermal baselines.
        </div>
      `;
      return;
    }

    container.innerHTML = criticalIncidents.map(inc => {
      const badgeClass = inc.risk_level === "CRITICAL" ? "critical" : "high";
      return `
        <div class="tactical-card mb-2 p-2" style="background: rgba(15, 23, 42, 0.9); border-left: 3px solid ${inc.risk_level === 'CRITICAL' ? '#EF4444' : '#F97316'};">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <span class="badge-risk ${badgeClass}" style="font-size: 0.65rem;">
              <i class="bi bi-exclamation-triangle-fill"></i> ${inc.risk_level} (${inc.risk_score}/100)
            </span>
            <span style="font-size: 0.7rem; color: #94A3B8; font-family: var(--font-mono);">${inc.id}</span>
          </div>
          <div style="font-size: 0.82rem; font-weight: 700; color: #F1F5F9; margin-bottom: 3px;">
            ${inc.title}
          </div>
          <div style="font-size: 0.72rem; color: #38BDF8; margin-bottom: 6px;">
            <i class="bi bi-building"></i> ${inc.facility_name || 'Industrial Facility'}
          </div>
          <div class="d-flex gap-2">
            <button class="btn-tactical btn-sm py-1" onclick="IncidentModal.open('${inc.id}')" style="font-size: 0.72rem;">
              <i class="bi bi-crosshair"></i> Dossier
            </button>
            <button class="btn-tactical btn-sm py-1 danger" onclick="RoutingView.showForIncident('${inc.id}')" style="font-size: 0.72rem;">
              <i class="bi bi-signpost-2"></i> Safety Route
            </button>
            <button class="btn-tactical btn-sm py-1" onclick="TacticalMap.panTo(${inc.hotspot ? inc.hotspot.latitude : 22.38}, ${inc.hotspot ? inc.hotspot.longitude : 69.87}, 14)" style="font-size: 0.72rem;">
              <i class="bi bi-geo-alt"></i> Locate
            </button>
          </div>
        </div>
      `;
    }).join("");
  }
};
