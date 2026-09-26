/**
 * FIREGUARD AI - Alerts View Controller
 */
const AlertsView = {
  async render() {
    try {
      const data = await Api.fetchAlerts();
      const list = Array.isArray(data) ? data : (data.alerts || []);
      AppState.alerts = list;
      this.renderAlertsList(list);
    } catch (err) {
      console.warn("Failed to fetch alerts:", err);
    }
  },

  renderAlertsList(alerts) {
    const container = document.getElementById("alerts-feed-container");
    if (!container) return;

    if (!alerts || !alerts.length) {
      container.innerHTML = `<div class="text-center text-muted p-4">No active system alerts at this time.</div>`;
      return;
    }

    container.innerHTML = alerts.map(a => {
      const isCrit = a.severity === "CRITICAL";
      const isHigh = a.severity === "HIGH";
      const borderCol = isCrit ? "#EF4444" : (isHigh ? "#F97316" : "#06B6D4");

      return `
        <div class="tactical-card mb-2 p-3" style="background: rgba(15, 23, 42, 0.85); border-left: 4px solid ${borderCol};">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <div>
              <span class="badge ${isCrit ? 'bg-danger' : (isHigh ? 'bg-warning text-dark' : 'bg-info text-dark')} text-uppercase me-2" style="font-size: 0.72rem;">
                ${a.severity}
              </span>
              <span class="text-info fw-bold" style="font-size: 0.82rem;">${a.alert_type.replace(/_/g, ' ')}</span>
            </div>
            <span class="text-muted font-monospace" style="font-size: 0.72rem;">${(a.created_at || a.sent_at || '').slice(0, 19).replace('T', ' ')} UTC</span>
          </div>

          <p class="text-light mb-2" style="font-size: 0.84rem; line-height: 1.5;">${a.message}</p>

          <div class="d-flex justify-content-between align-items-center">
            ${a.incident_id ? `
              <button class="btn-tactical btn-sm py-0" onclick="IncidentModal.open('${a.incident_id}')">
                <i class="bi bi-file-earmark-medical"></i> Inspect Incident ${a.incident_id}
              </button>
            ` : '<span></span>'}

            ${(!a.acknowledged && !a.is_acknowledged) ? `
              <button class="btn btn-outline-success btn-sm py-0" onclick="AlertsView.ack('${a.id}')" style="font-size: 0.75rem;">
                <i class="bi bi-check2"></i> Acknowledge
              </button>
            ` : '<span class="text-success" style="font-size: 0.75rem;"><i class="bi bi-check2-all"></i> Acknowledged</span>'}
          </div>
        </div>
      `;
    }).join("");
  },

  async ack(alertId) {
    try {
      await Api.acknowledgeAlert(alertId);
      this.render();
      DashboardView.updateKpis();
    } catch (err) {
      alert("Failed to acknowledge alert: " + err.message);
    }
  }
};
