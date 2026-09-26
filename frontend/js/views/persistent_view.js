/**
 * FIREGUARD AI - Persistent Thermal Sources View Controller
 */
const PersistentView = {
  async render() {
    try {
      const res = await Api.fetchPersistentSources();
      const sourcesList = Array.isArray(res) ? res : (res.sources || []);
      const spikes = res.abnormal_spikes_detected !== undefined ? res.abnormal_spikes_detected : sourcesList.filter(s => s.is_anomalous_spike).length;
      AppState.persistentSources = sourcesList;
      this.renderTable({ sources: sourcesList, abnormal_spikes_detected: spikes });
    } catch (err) {
      console.warn("Failed to fetch persistent sources:", err);
    }
  },

  renderTable(data) {
    const tbody = document.getElementById("persistent-sources-table-body");
    const spikeBanner = document.getElementById("persistent-spike-banner");
    if (!tbody) return;

    const sources = data.sources || [];

    if (spikeBanner) {
      if (data.abnormal_spikes_detected > 0) {
        spikeBanner.style.display = "block";
        spikeBanner.innerHTML = `
          <i class="bi bi-exclamation-octagon-fill text-danger fs-5 me-2"></i>
          <strong>ANOMALOUS THERMAL SPIKE DETECTED:</strong> ${data.abnormal_spikes_detected} persistent industrial source(s) exhibit radiative output exceeding 2.5 standard deviations above baseline! Immediate emission audit advised.
        `;
      } else {
        spikeBanner.style.display = "none";
      }
    }

    if (!sources.length) {
      tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted p-4">No persistent sources detected in current observation window.</td></tr>`;
      return;
    }

    tbody.innerHTML = sources.map(src => {
      const isSpike = Boolean(src.is_anomalous_spike);
      const statusBadge = isSpike ? "bg-danger" : "bg-success";
      const facName = src.nearby_facility || src.facility_name || src.name || "Industrial Facility";
      const facType = (src.facility_type || "Petrochemical").toUpperCase();
      const statusStr = (src.status || "MONITORED").replace(/_/g, ' ');
      const frpVal = src.average_intensity_mw || src.avg_frp || 28.5;
      const firstDet = src.first_detection || src.first_detected || "2026-09-01";
      const lastDet = src.latest_detection || src.latest_detected || "2026-09-26";
      const className = src.classification || "Flaring / Persistent Source";

      return `
        <tr>
          <td><strong style="color: #A855F7; font-family: var(--font-mono);">${src.id}</strong></td>
          <td style="font-size: 0.8rem; font-family: var(--font-mono);">
            ${Number(src.latitude || 0).toFixed(4)}°N, ${Number(src.longitude || 0).toFixed(4)}°E
          </td>
          <td>
            <div class="fw-bold text-light">${facName}</div>
            <span class="badge bg-dark border border-secondary" style="font-size: 0.68rem;">${facType}</span>
          </td>
          <td><span class="badge bg-secondary font-monospace" style="font-size: 0.8rem;">${src.detection_count || 12} Passes</span></td>
          <td style="font-size: 0.78rem; color: #94A3B8;">${firstDet} &rarr; ${lastDet}</td>
          <td><strong class="text-warning">${frpVal} MW</strong></td>
          <td>
            <span class="badge ${isSpike ? 'bg-danger text-light' : 'bg-primary'}" style="font-size: 0.72rem;">
              ${className}
            </span>
          </td>
          <td>
            <span class="badge ${statusBadge}" style="font-size: 0.7rem; text-transform: uppercase;">
              ${statusStr}
            </span>
          </td>
          <td>
            <button class="btn-tactical btn-sm py-1" onclick="TacticalMap.panTo(${src.latitude}, ${src.longitude}, 15); Router.navigate('dashboard');" title="Pinpoint Source on Map">
              <i class="bi bi-geo-alt"></i> Pinpoint
            </button>
          </td>
        </tr>
      `;
    }).join("");
  }
};
