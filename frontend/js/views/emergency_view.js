/**
 * FIREGUARD AI - Emergency Contacts & Multi-Agency Dispatch System
 */
const EmergencyView = {
  contacts: [],

  async render() {
    try {
      const data = await Api.fetchEmergencyContacts();
      this.contacts = Array.isArray(data) ? data : (data.contacts || []);
      this.renderContactsList();
      this.populateDispatchDropdown();
    } catch (err) {
      console.warn("Failed to fetch emergency contacts:", err);
    }
  },

  renderContactsList() {
    const container = document.getElementById("emergency-contacts-list");
    if (!container) return;

    if (!this.contacts.length) {
      container.innerHTML = `<div class="text-center text-muted p-4">No emergency contacts registered.</div>`;
      return;
    }

    container.innerHTML = this.contacts.map(c => `
      <div class="tactical-card mb-2 p-2" style="background: rgba(15, 23, 42, 0.8);">
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <div class="fw-bold text-light" style="font-size: 0.88rem;">${c.agency_name || c.name}</div>
            <div class="text-muted" style="font-size: 0.72rem;">${c.contact_type || 'Emergency Unit'} &bull; ${c.district || ''}, ${c.state || ''}</div>
          </div>
          ${c.is_primary ? '<span class="badge bg-danger text-uppercase" style="font-size: 0.65rem;">PRIMARY DISPATCH</span>' : ''}
        </div>
        <div class="d-flex justify-content-between align-items-center mt-2 pt-2 border-top border-secondary">
          <span class="text-warning font-monospace" style="font-size: 0.85rem;"><i class="bi bi-telephone"></i> ${c.phone}</span>
          <div class="d-flex gap-1">
            <a href="tel:${c.phone}" class="btn-tactical btn-sm py-0"><i class="bi bi-telephone-fill"></i> Call</a>
            <button class="btn-tactical btn-sm py-0" onclick="navigator.clipboard.writeText('${c.phone}'); alert('Phone copied!');"><i class="bi bi-clipboard"></i></button>
          </div>
        </div>
      </div>
    `).join("");
  },

  populateDispatchDropdown() {
    const sel = document.getElementById("dispatch-incident-select");
    if (!sel) return;

    sel.innerHTML = AppState.incidents.map(i => `
      <option value="${i.id}">${i.id} - ${i.title} (${i.risk_level})</option>
    `).join("");
  },

  async triggerDispatch() {
    const sel = document.getElementById("dispatch-incident-select");
    const incId = sel ? sel.value : null;
    if (!incId) {
      alert("Please select an incident to simulate dispatch.");
      return;
    }

    try {
      const res = await Api.simulateDispatch(incId);
      this.showDispatchPayloadModal(res.payload || res);
    } catch (err) {
      alert("Failed to simulate dispatch: " + err.message);
    }
  },

  showDispatchPayloadModal(payload) {
    const modalEl = document.getElementById("dispatchSimModal");
    const bodyEl = document.getElementById("dispatch-sim-body");
    const p = payload || {};
    const dispId = p.dispatch_id || "DISP-2026-LIVE";
    const msg = p.formatted_dispatch_message || p.message || "Simulated emergency dispatch payload transmitted.";
    const channels = p.simulated_broadcast_channels || p.units_alerted || [
      "District Fire & Emergency Services",
      "Regional Hazmat Foam Operations Unit",
      "Civil Hospital Burn Trauma Center"
    ];

    if (bodyEl) {
      bodyEl.innerHTML = `
        <div class="alert alert-success d-flex align-items-center gap-2 mb-3" role="alert">
          <i class="bi bi-check-circle-fill fs-4"></i>
          <div>
            <strong>DISPATCH TRANSMISSION SIMULATION SUCCESSFUL</strong><br>
            <span style="font-size: 0.78rem;">Broadcast dispatched across simulated multi-agency responder networks.</span>
          </div>
        </div>

        <div class="tactical-card p-3 mb-3">
          <div class="card-title-tactical mb-2">
            <i class="bi bi-file-earmark-text"></i> Standardized Emergency Dispatch Payload (${dispId})
          </div>
          <pre style="background: #020617; color: #38BDF8; padding: 12px; border-radius: 6px; font-size: 0.76rem; max-height: 220px; overflow-y: auto; white-space: pre-wrap;">${msg}</pre>
        </div>

        <div class="tactical-card p-3">
          <div class="card-title-tactical mb-2">
            <i class="bi bi-broadcast"></i> Simulated Recipient Command Nodes
          </div>
          <ul class="text-light ps-3 mb-0" style="font-size: 0.8rem; line-height: 1.6;">
            ${channels.map(ch => `<li><i class="bi bi-check2 text-success me-1"></i> ${ch}</li>`).join("")}
          </ul>
        </div>
      `;
    }

    if (modalEl && typeof bootstrap !== "undefined") {
      bootstrap.Modal.getOrCreateInstance(modalEl).show();
    }
  },

  copyBroadcastText() {
    const pre = document.querySelector("#dispatch-sim-body pre");
    if (pre) {
      navigator.clipboard.writeText(pre.innerText);
      alert("Broadcast payload copied to clipboard!");
    }
  }
};
