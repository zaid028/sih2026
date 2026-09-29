/**
 * FIREGUARD AI - Dashboard View Controller
 * Command Center Overview & Real-Time Tactical Threat Feeds
 */
const DashboardView = {
  render() {
    this.updateKpis();
    this.renderThreatCards();
  },

  animateValue(id, start, end, duration = 800) {
    const obj = document.getElementById(id);
    if (!obj) return;
    const range = end - start;
    const startTime = performance.now();

    function step(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const val = Math.round(start + (range * progress));
      obj.innerText = val < 10 && val >= 0 ? `0${val}` : val;
      if (progress < 1) {
        requestAnimationFrame(step);
      }
    }
    requestAnimationFrame(step);
  },

  async updateKpis() {
    try {
      const kpis = await Api.fetchAnalyticsKpis();
      const hotspots = kpis.total_hotspots !== undefined ? kpis.total_hotspots : 24;
      const indFires = kpis.industrial_fires !== undefined ? kpis.industrial_fires : 8;
      const highRisk = kpis.high_risk_incidents !== undefined ? kpis.high_risk_incidents : 3;
      const persist = kpis.persistent_sources !== undefined ? kpis.persistent_sources : 13;

      this.animateValue("kpi-total-hotspots", 0, hotspots);
      this.animateValue("kpi-industrial-fires", 0, indFires);
      this.animateValue("kpi-high-risk", 0, highRisk);
      this.animateValue("kpi-persistent-sources", 0, persist);

      const respEl = document.getElementById("kpi-avg-response");
      if (respEl) respEl.innerText = `${kpis.avg_response_time_min || 14.2}m`;

      // Update sidebar badges
      const bHp = document.getElementById("badge-hotspots-count");
      const bInc = document.getElementById("badge-incidents-count");
      const bPer = document.getElementById("badge-persistent-count");
      if (bHp) bHp.innerText = hotspots < 10 ? `0${hotspots}` : hotspots;
      if (bInc) bInc.innerText = indFires < 10 ? `0${indFires}` : indFires;
      if (bPer) bPer.innerText = persist < 10 ? `0${persist}` : persist;

      // Update navbar threat counter
      const threatPill = document.getElementById("nav-threat-count");
      if (threatPill) {
        threatPill.innerHTML = `
          <i class="bi bi-radioactive text-danger"></i>
          <span>${highRisk < 10 ? '0' + highRisk : highRisk} CRITICAL THREATS</span>
        `;
        if (highRisk > 0) {
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
