/**
 * FIREGUARD AI - Incidents Command View Controller
 */
const IncidentsView = {
  render() {
    this.populateTable();
    this.bindSearchAndFilters();
  },

  bindSearchAndFilters() {
    const searchInput = document.getElementById("incident-search-input");
    const statusSelect = document.getElementById("incident-status-filter");
    const riskSelect = document.getElementById("incident-risk-filter");

    const apply = () => {
      const q = searchInput ? searchInput.value.toLowerCase().trim() : "";
      const status = statusSelect ? statusSelect.value : "";
      const risk = riskSelect ? riskSelect.value : "";

      let list = [...AppState.incidents];
      if (q) {
        list = list.filter(i => i.title.toLowerCase().includes(q) || (i.facility_name && i.facility_name.toLowerCase().includes(q)) || i.id.toLowerCase().includes(q));
      }
      if (status) {
        list = list.filter(i => i.status === status);
      }
      if (risk) {
        list = list.filter(i => i.risk_level === risk);
      }

      this.renderRows(list);
    };

    if (searchInput) searchInput.oninput = apply;
    if (statusSelect) statusSelect.onchange = apply;
    if (riskSelect) riskSelect.onchange = apply;
  },

  populateTable() {
    this.renderRows(AppState.incidents);
  },

  renderRows(list) {
    const tbody = document.getElementById("incidents-table-body");
    if (!tbody) return;

    if (!list.length) {
      tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted p-4">No incidents match current filter parameters.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(inc => {
      const riskClass = (inc.risk_level || "high").toLowerCase();
      let statusBadge = "bg-secondary";
      if (inc.status === "DISPATCH_REQUIRED") statusBadge = "bg-danger";
      else if (inc.status === "ESCALATED") statusBadge = "bg-danger text-light border border-warning";
      else if (inc.status === "VERIFIED") statusBadge = "bg-warning text-dark";
      else if (inc.status === "UNDER_REVIEW") statusBadge = "bg-info text-dark";
      else if (inc.status === "DETECTED") statusBadge = "bg-primary";
      else if (inc.status === "RESOLVED") statusBadge = "bg-success";
      else if (inc.status === "FALSE_ALARM") statusBadge = "bg-dark text-muted";

      const timeStr = inc.created_at || inc.detected_at || "Recent";
      const displayTime = timeStr.length > 16 ? timeStr.slice(0, 16).replace("T", " ") : timeStr;
      const incClass = inc.classification || (inc.fire_class ? inc.fire_class.replace(/_/g, ' ') : "Industrial Fire");
      const incLat = inc.latitude || (inc.hotspot ? inc.hotspot.latitude : 22.4707);
      const incLon = inc.longitude || (inc.hotspot ? inc.hotspot.longitude : 70.0577);
      const incLabel = inc.incident_number || inc.id;

      return `
        <tr>
          <td><strong style="color: #38BDF8; font-family: var(--font-mono);">${incLabel}</strong></td>
          <td style="font-size: 0.78rem; color: #94A3B8;">${displayTime}</td>
          <td>
            <div style="font-weight: 700; color: #F8FAFC;">${inc.title}</div>
            <div style="font-size: 0.72rem; color: #06B6D4;"><i class="bi bi-buildings"></i> ${inc.facility_name || 'Unmapped Site'}</div>
          </td>
          <td>
            <span class="badge bg-dark border border-secondary" style="font-size: 0.75rem;">
              ${incClass}
            </span>
          </td>
          <td>
            <span class="badge-risk ${riskClass}">
              ${inc.risk_level} (${Math.round(inc.risk_score || 0)})
            </span>
          </td>
          <td>
            <span class="badge ${statusBadge}" style="font-size: 0.72rem; text-transform: uppercase;">
              ${(inc.status || "DETECTED").replace(/_/g, ' ')}
            </span>
          </td>
          <td>
            <div class="d-flex gap-1">
              <button class="btn-tactical btn-sm py-1" onclick="IncidentModal.open('${inc.id}')" title="Inspect Full Incident Dossier">
                <i class="bi bi-file-earmark-medical"></i> Dossier
              </button>
              <button class="btn-tactical btn-sm py-1 danger" onclick="RoutingView.showForIncident('${inc.id}')" title="Generate Safe Evacuation Route">
                <i class="bi bi-signpost-2"></i> Route
              </button>
              <button class="btn-tactical btn-sm py-1" onclick="TacticalMap.panTo(${incLat}, ${incLon}, 14); Router.navigate('dashboard');" title="Center Map">
                <i class="bi bi-geo-alt"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");
  }
};
