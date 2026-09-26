/**
 * FIREGUARD AI - Hotspots View Controller
 */
const HotspotsView = {
  render() {
    this.populateTable();
    this.bindFilters();
  },

  bindFilters() {
    const riskSelect = document.getElementById("filter-hotspots-risk");
    const classSelect = document.getElementById("filter-hotspots-class");
    const satSelect = document.getElementById("filter-hotspots-sat");
    const confSlider = document.getElementById("filter-hotspots-conf");
    const indCheck = document.getElementById("filter-hotspots-industrial");
    const persistCheck = document.getElementById("filter-hotspots-persist");

    const apply = () => {
      const filters = {
        risk: riskSelect ? riskSelect.value : "",
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

    if (riskSelect) riskSelect.onchange = apply;
    if (classSelect) classSelect.onchange = apply;
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
