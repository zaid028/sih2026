/**
 * FIREGUARD AI - Main Application Bootstrap & Coordinator
 * Connects Frontend directly to FastAPI /api/v1/* architecture, WebSockets, Health Monitor & SIH Demo.
 */
const App = {
  async init() {
    console.log("Booting FIREGUARD AI Command Center...");

    // Start Mission Clocks
    this.startMissionClocks();

    // Initialize Router
    Router.init();

    // Initialize Tactical Map
    TacticalMap.init("tactical-map-container");

    // Load Authenticated User Profile
    await this.loadCurrentUser();

    // Connect Real-time WebSocket
    this.initWebSocket();

    // Fetch initial datasets
    await this.refreshData();

    // Setup Demo Role Switcher
    this.bindRoleSwitcher();

    // Start Periodic Background Polling (fallback to WS)
    setInterval(() => {
      this.refreshData(true);
    }, AppConfig.POLL_INTERVAL_MS);

    console.log("FIREGUARD AI Command Center ready.");
  },

  startMissionClocks() {
    const update = () => {
      const now = new Date();
      const utcEl = document.getElementById("clock-utc");
      const istEl = document.getElementById("clock-ist");

      if (utcEl) {
        utcEl.innerText = now.toUTCString().slice(17, 25) + " UTC";
      }
      if (istEl) {
        const istOffset = 5.5 * 60 * 60 * 1000;
        const istDate = new Date(now.getTime() + istOffset);
        istEl.innerText = istDate.toUTCString().slice(17, 25) + " IST";
      }
    };
    update();
    setInterval(update, 1000);
  },

  initWebSocket() {
    try {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.host || "127.0.0.1:5000";
      const wsUrl = `${protocol}//${host}/api/v1/ws/hotspots`;
      
      const ws = new WebSocket(wsUrl);
      ws.onopen = () => {
        console.log("[WebSocket] Connected to FIREGUARD AI live event bus.");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === "DEMO_INCIDENT_CREATED" || data.event === "NEW_CRITICAL_INCIDENT") {
            this.showTacticalToast(`SATELLITE DETECTION: ${data.payload.title}`);
            this.refreshData(true);
          }
        } catch (e) {}
      };

      ws.onclose = () => {
        // Auto-reconnect after 5 seconds
        setTimeout(() => this.initWebSocket(), 5000);
      };
    } catch (err) {
      console.warn("[WebSocket] Initialization skipped, relying on REST polling:", err);
    }
  },

  showTacticalToast(message) {
    const toast = document.createElement("div");
    toast.className = "alert alert-danger position-fixed bottom-0 end-0 m-3 shadow-lg z-3";
    toast.style.border = "1px solid #EF4444";
    toast.style.background = "rgba(15, 23, 42, 0.95)";
    toast.innerHTML = `<i class="bi bi-radioactive text-danger me-2"></i><strong>TACTICAL ALERT:</strong> ${message}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 6000);
  },

  async refreshData(isBackground = false) {
    try {
      const [status, hpRes, incRes, facRes] = await Promise.all([
        Api.fetchSystemStatus(),
        Api.fetchHotspots(),
        Api.fetchIncidents(),
        Api.fetchFacilities()
      ]);

      AppState.systemStatus = status;
      AppState.hotspots = hpRes.hotspots || hpRes || [];
      AppState.incidents = incRes.incidents || incRes || [];
      AppState.facilities = facRes.facilities || facRes || [];

      // Update Header Status Indicator (Requirement 23: Clearly show 🟡 DEMO MODE)
      const statusPill = document.getElementById("nav-system-status");
      if (statusPill) {
        if (status.demo_mode) {
          statusPill.className = "telemetry-pill border-warning text-warning";
          statusPill.innerHTML = `
            <span class="badge bg-warning text-dark me-1">🟡</span>
            <span>DEMO MODE ACTIVE</span>
          `;
        } else {
          statusPill.className = "telemetry-pill border-success text-success";
          statusPill.innerHTML = `
            <span class="badge bg-success text-light me-1">🟢</span>
            <span>LIVE SATELLITE (NASA FIRMS)</span>
          `;
        }
      }

      // Update Threat Count
      const threatPill = document.getElementById("nav-threat-count");
      if (threatPill && status.critical_threats !== undefined) {
        threatPill.innerHTML = `
          <i class="bi bi-radioactive text-danger"></i>
          <span>${status.critical_threats} CRITICAL THREATS</span>
        `;
      }

      // Update Map Layers
      TacticalMap.renderHotspots(AppState.hotspots, AppState.incidents);
      TacticalMap.renderFacilities(AppState.facilities);

      // Render Active View
      if (AppState.activeTab === "dashboard") DashboardView.render();
      else if (AppState.activeTab === "hotspots") HotspotsView.render();
      else if (AppState.activeTab === "incidents") IncidentsView.render();
      else if (AppState.activeTab === "facilities") FacilitiesView.render();

      DashboardView.updateKpis();
    } catch (err) {
      if (!isBackground) console.warn("Failed to load application state:", err);
    }
  },

  async loadCurrentUser() {
    let user = null;
    const storedUser = localStorage.getItem("fireguard_user");
    if (storedUser) {
      try {
        user = JSON.parse(storedUser);
      } catch (e) {}
    }

    const token = localStorage.getItem("fireguard_token");
    if (token) {
      try {
        const me = await Api.get("/api/v1/auth/me");
        if (me && me.username) {
          user = me;
          localStorage.setItem("fireguard_user", JSON.stringify(me));
        }
      } catch (err) {
        console.warn("Auth /me fetch error, using fallback profile:", err);
      }
    }

    if (!user) {
      user = {
        username: "operator",
        role: "OPERATOR",
        full_name: "Commander Rajesh Sharma",
        agency: "State Emergency Operation Center (SEOC) Gujarat",
        phone: "+91 79 2325 1900",
        email: "operator@fireguard.gov.in"
      };
    }

    AppState.currentUser = user;
    this.updateUserInterface(user);
  },

  updateUserInterface(user) {
    if (!user) return;
    const nameLabel = document.getElementById("user-name-label");
    const roleLabel = document.getElementById("user-role-label");
    const navName = document.getElementById("nav-user-fullname");
    const selector = document.getElementById("demo-role-selector");

    if (nameLabel) nameLabel.innerText = user.full_name || user.username;
    if (roleLabel) roleLabel.innerText = (user.role || "OPERATOR").toUpperCase();
    if (navName) navName.innerText = (user.full_name || user.username).split(" ")[0];

    if (selector && user.role) {
      const targetVal = user.role.toLowerCase();
      for (let i = 0; i < selector.options.length; i++) {
        if (selector.options[i].value === targetVal || targetVal.includes(selector.options[i].value)) {
          selector.selectedIndex = i;
          break;
        }
      }
    }

    // Enforce Role-Based Access Control dynamically across navigation & views
    this.applyRolePermissions(user.role || "OPERATOR");
  },

  applyRolePermissions(role) {
    const activeRole = (role || "OPERATOR").toUpperCase();

    // 1. Filter Sidebar Navigation according to data-roles attribute
    const navItems = document.querySelectorAll(".sidebar-nav-item[data-roles]");
    let allowedViews = [];
    navItems.forEach(item => {
      const allowedRoles = (item.getAttribute("data-roles") || "").split(",").map(r => r.trim().toUpperCase());
      const isAllowed = allowedRoles.includes(activeRole);
      item.style.display = isAllowed ? "flex" : "none";
      if (isAllowed) {
        const view = item.getAttribute("data-view");
        if (view) allowedViews.push(view);
      }
    });

    // 2. Hide Navigation Group Titles if no children are visible
    const groups = [
      { id: "group-title-ops", views: ["dashboard", "hotspots", "incidents", "facilities", "persistent"] },
      { id: "group-title-intel", views: ["risk", "routes", "emergency", "analytics"] },
      { id: "group-title-citizen", views: ["public_report"] },
      { id: "group-title-sys", views: ["alerts", "settings"] }
    ];

    groups.forEach(g => {
      const el = document.getElementById(g.id);
      if (el) {
        if (g.id === "group-title-citizen") {
          el.style.display = "block";
        } else {
          const hasVisible = g.views.some(v => allowedViews.includes(v));
          el.style.display = hasVisible ? "block" : "none";
        }
      }
    });

    // 3. Highlight citizen report sidebar button for PUBLIC users
    const citSidebar = document.getElementById("sidebar-citizen-report");
    if (citSidebar) {
      if (activeRole === "PUBLIC") {
        citSidebar.classList.add("bg-danger", "bg-opacity-25", "border", "border-danger");
      } else {
        citSidebar.classList.remove("bg-danger", "bg-opacity-25", "border", "border-danger");
      }
    }

    // 4. Header Action Controls (SIH demo pipeline button is for commanders/operators/analysts)
    const sihDemoBtn = document.getElementById("btn-trigger-sih-demo");
    if (sihDemoBtn) {
      sihDemoBtn.style.display = (activeRole === "PUBLIC") ? "none" : "inline-flex";
    }

    // 5. Header Fast Citizen Report Button
    const citHeaderBtn = document.getElementById("btn-citizen-report-header");
    if (citHeaderBtn) {
      if (activeRole === "PUBLIC") {
        citHeaderBtn.className = "btn btn-danger btn-sm fw-bold";
      } else {
        citHeaderBtn.className = "btn btn-outline-danger btn-sm";
      }
    }

    // 6. View redirection if active tab is unauthorized for current role
    if (AppState.activeTab && !allowedViews.includes(AppState.activeTab)) {
      console.warn(`[RBAC] Role ${activeRole} cannot access view '${AppState.activeTab}'. Redirecting to dashboard.`);
      Router.navigate("dashboard");
    }

    // 7. Update Emergency View if rendered
    if (typeof EmergencyView !== "undefined" && EmergencyView.applyViewPermissions) {
      EmergencyView.applyViewPermissions();
    }

    // 8. Inform public users of restricted authority scope
    if (activeRole === "PUBLIC") {
      this.showPublicNoticeToast();
    }
  },

  showPublicNoticeToast() {
    if (this._publicNoticeActive) return;
    this._publicNoticeActive = true;
    const toast = document.createElement("div");
    toast.className = "alert alert-warning position-fixed bottom-0 start-50 translate-middle-x m-3 shadow-lg z-3";
    toast.style.border = "1px solid #F59E0B";
    toast.style.background = "rgba(15, 23, 42, 0.96)";
    toast.style.maxWidth = "600px";
    toast.innerHTML = `
      <div class="d-flex align-items-center gap-2">
        <i class="bi bi-shield-lock-fill text-warning fs-4"></i>
        <div style="font-size: 0.8rem;">
          <strong>PUBLIC SAFETY CLEARANCE ACTIVE:</strong> Command dispatching & industrial settings are restricted. You are authorized to <strong>dial emergency hotlines (108/101/112)</strong>, <strong>view safe evacuation corridors</strong>, and <strong>upload ground fire photos</strong>.
        </div>
        <button type="button" class="btn-close btn-close-white ms-auto" onclick="this.closest('.alert').remove()"></button>
      </div>
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
      if (toast.parentElement) toast.remove();
      this._publicNoticeActive = false;
    }, 9000);
  },

  // -------------------------------------------------------------
  // CITIZEN FIRE OBSERVATION & GROUND PHOTO DISPATCH SYSTEM
  // -------------------------------------------------------------
  openCitizenReportModal() {
    const modalEl = document.getElementById("citizenReportModal");
    if (!modalEl) return;

    // Reset status alert
    const alertEl = document.getElementById("citizen-report-alert");
    if (alertEl) {
      alertEl.className = "alert d-none";
      alertEl.innerText = "";
    }

    // Reset submit button state
    const submitBtn = document.getElementById("btn-submit-cit-report");
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i class="bi bi-send-fill me-1"></i> Transmit Ground Observation to EOC`;
    }

    // Autofill user details
    const u = AppState.currentUser || {};
    const nameInput = document.getElementById("cit-reporter-name");
    const phoneInput = document.getElementById("cit-reporter-phone");
    if (nameInput) {
      nameInput.value = u.full_name || (u.role === "PUBLIC" ? "Concerned Citizen Observer" : u.username);
    }
    if (phoneInput && !phoneInput.value) {
      phoneInput.value = u.phone || "+91 98765 43210";
    }

    // Autofill coordinates from map center
    const latInput = document.getElementById("cit-lat");
    const lonInput = document.getElementById("cit-lon");
    if (latInput && lonInput && TacticalMap && TacticalMap.map) {
      const center = TacticalMap.map.getCenter();
      latInput.value = center.lat.toFixed(4);
      lonInput.value = center.lng.toFixed(4);
    }

    const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
    bsModal.show();
  },

  autoFillCitizenLocation() {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser. Please enter coordinates manually.");
      return;
    }
    const latInput = document.getElementById("cit-lat");
    const lonInput = document.getElementById("cit-lon");

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        if (latInput) latInput.value = pos.coords.latitude.toFixed(4);
        if (lonInput) lonInput.value = pos.coords.longitude.toFixed(4);
        this.showTacticalToast(`GPS Acquired: ${pos.coords.latitude.toFixed(4)}° N, ${pos.coords.longitude.toFixed(4)}° E`);
      },
      (err) => {
        console.warn("Geolocation lookup error:", err);
        alert("Could not retrieve GPS coordinates. Please ensure browser location permissions are granted.");
      },
      { enableHighAccuracy: true, timeout: 6000 }
    );
  },

  handlePhotoPreview(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please select a valid image file format (PNG, JPG, WebP).");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target.result;
      AppState.pendingCitizenPhoto = dataUrl;

      const previewEl = document.getElementById("cit-photo-preview");
      const containerEl = document.getElementById("cit-photo-preview-container");

      if (previewEl) previewEl.src = dataUrl;
      if (containerEl) containerEl.classList.remove("d-none");
    };
    reader.readAsDataURL(file);
  },

  clearPhotoPreview() {
    const fileInput = document.getElementById("cit-photo-file");
    if (fileInput) fileInput.value = "";

    AppState.pendingCitizenPhoto = null;

    const previewEl = document.getElementById("cit-photo-preview");
    const containerEl = document.getElementById("cit-photo-preview-container");

    if (previewEl) previewEl.src = "";
    if (containerEl) containerEl.classList.add("d-none");
  },

  async submitCitizenReport(event) {
    if (event) event.preventDefault();

    const titleEl = document.getElementById("cit-title");
    const typeEl = document.getElementById("cit-type");
    const latEl = document.getElementById("cit-lat");
    const lonEl = document.getElementById("cit-lon");
    const descEl = document.getElementById("cit-desc");
    const nameEl = document.getElementById("cit-reporter-name");
    const phoneEl = document.getElementById("cit-reporter-phone");
    const alertEl = document.getElementById("citizen-report-alert");
    const submitBtn = document.getElementById("btn-submit-cit-report");

    if (!titleEl || !latEl || !lonEl) return;

    const payload = {
      title: `${titleEl.value.trim()} (${typeEl ? typeEl.value : 'Visible Flare'})`,
      latitude: parseFloat(latEl.value),
      longitude: parseFloat(lonEl.value),
      description: descEl ? descEl.value.trim() : "",
      photo_data: AppState.pendingCitizenPhoto || "",
      reporter_name: nameEl ? nameEl.value.trim() : "Citizen Observer",
      reporter_phone: phoneEl ? phoneEl.value.trim() : "+91 99999 88888"
    };

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status"></span> Transmitting Observation to EOC...`;
    }

    try {
      const res = await Api.submitCitizenReport(payload);

      if (alertEl) {
        alertEl.className = "alert alert-success d-block";
        alertEl.innerHTML = `
          <strong><i class="bi bi-check-circle-fill me-1"></i> OBSERVATION LOGGED SUCCESSFULLY!</strong><br>
          Emergency Tracking ID: <span class="font-monospace fw-bold text-light">${res.tracking_number || 'REG-CITIZEN-01'}</span><br>
          <small class="text-white-50">Local emergency operations cell and hazmat team have been dispatched with ground telemetry.</small>
        `;
      }

      this.showTacticalToast(`CITIZEN REPORT RECORDED: Tracking ID ${res.tracking_number || 'EOC-OK'}`);

      // Add newly created incident to state and tactical map
      if (res.incident) {
        AppState.incidents = [res.incident, ...(AppState.incidents || [])];
        TacticalMap.renderHotspots(AppState.hotspots, AppState.incidents);
        if (AppState.activeTab === "incidents" && typeof IncidentsView !== "undefined") {
          IncidentsView.render();
        }
        if (typeof DashboardView !== "undefined") {
          DashboardView.updateKpis();
        }
      }

      // Refresh state from server
      setTimeout(() => {
        this.refreshData(true);
      }, 1000);

      // Close modal after brief pause
      setTimeout(() => {
        const modalEl = document.getElementById("citizenReportModal");
        if (modalEl) {
          const bsModal = bootstrap.Modal.getInstance(modalEl);
          if (bsModal) bsModal.hide();
        }
        this.clearPhotoPreview();
      }, 2500);

    } catch (err) {
      console.error("Citizen report submission failed:", err);
      if (alertEl) {
        alertEl.className = "alert alert-danger d-block";
        alertEl.innerHTML = `<strong>Submission Failed:</strong> ${err.message || 'Server error'}`;
      }
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="bi bi-send-fill me-1"></i> Retry Transmission`;
      }
    }
  },

  openUserProfileModal() {
    const modalEl = document.getElementById("userProfileModal");
    if (!modalEl) return;

    const u = AppState.currentUser || {};
    const fullNameEl = document.getElementById("profile-full-name");
    const roleBadgeEl = document.getElementById("profile-role-badge");
    const agencyEl = document.getElementById("profile-agency");
    const userEl = document.getElementById("profile-username");
    const emailEl = document.getElementById("profile-email");
    const phoneEl = document.getElementById("profile-phone");

    if (fullNameEl) fullNameEl.innerText = u.full_name || "Tactical Commander";
    if (roleBadgeEl) {
      roleBadgeEl.innerText = (u.role || "OPERATOR").toUpperCase();
      roleBadgeEl.className = `badge font-monospace mb-2 ${u.role === 'ADMIN' ? 'bg-danger' : (u.role === 'OPERATOR' ? 'bg-warning text-dark' : 'bg-info text-dark')}`;
    }
    if (agencyEl) agencyEl.innerText = u.agency || "National Disaster Management Authority";
    if (userEl) userEl.innerText = u.username || "operator";
    if (emailEl) emailEl.innerText = u.email || `${u.username || 'operator'}@fireguard.gov.in`;
    if (phoneEl) phoneEl.innerText = u.phone || "+91 11 2670 1700";

    const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
    bsModal.show();
  },

  logout() {
    if (confirm("Are you sure you want to log out of the command terminal?")) {
      localStorage.removeItem("fireguard_token");
      localStorage.removeItem("fireguard_user");
      window.location.href = "/login";
    }
  },

  bindRoleSwitcher() {
    const sel = document.getElementById("demo-role-selector");
    if (!sel) return;

    sel.onchange = async (e) => {
      const role = e.target.value;
      try {
        const res = await Api.switchDemoRole(role);
        AppState.currentUser = res.user;
        this.updateUserInterface(res.user);
      } catch (err) {
        console.warn("Failed to switch role:", err);
      }
    };
  },

  // Requirement 26: Health Monitor Modal
  async openHealthModal() {
    const modalEl = document.getElementById("healthMonitorModal");
    const bodyEl = document.getElementById("health-modal-body");
    if (!modalEl || !bodyEl) return;

    bodyEl.innerHTML = `<div class="text-center py-4"><div class="spinner-border text-info" role="status"></div><div class="mt-2 text-muted">Polling micro-component health...</div></div>`;
    const bsModal = new bootstrap.Modal(modalEl);
    bsModal.show();

    try {
      const health = await Api.fetchHealthStatus();
      const comp = health.components;

      const getBadge = (val) => {
        if (val === "ONLINE") return `<span class="badge bg-success">● ONLINE</span>`;
        if (val === "DEMO") return `<span class="badge bg-warning text-dark">● DEMO</span>`;
        return `<span class="badge bg-danger">● OFFLINE</span>`;
      };

      bodyEl.innerHTML = `
        <div class="card bg-black border-secondary mb-3">
          <div class="card-body p-3">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="text-muted small">OVERALL STATUS</span>
              <span class="badge ${health.status === 'OPERATIONAL' ? 'bg-success' : 'bg-warning'} fs-6">${health.status}</span>
            </div>
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="text-muted small">DEMO MODE FLAG</span>
              <span class="badge ${health.demo_mode ? 'bg-warning text-dark' : 'bg-info'}">${health.demo_mode ? 'TRUE (SYNTHETIC)' : 'FALSE (LIVE APIS)'}</span>
            </div>
            <div class="d-flex justify-content-between align-items-center">
              <span class="text-muted small">TIMESTAMP</span>
              <span class="font-monospace small text-light">${health.timestamp}</span>
            </div>
          </div>
        </div>

        <h6 class="text-info fw-bold mb-3"><i class="bi bi-hdd-network me-2"></i>Micro-component Telemetry</h6>
        <div class="table-responsive">
          <table class="table table-dark table-sm table-bordered">
            <thead>
              <tr class="text-secondary small">
                <th>Component</th>
                <th>Subsystem</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Backend Engine</strong></td>
                <td class="text-muted small">Python FastAPI v${health.version}</td>
                <td>${getBadge(comp.backend)}</td>
              </tr>
              <tr>
                <td><strong>Database & PostGIS</strong></td>
                <td class="text-muted small">SQLAlchemy Spatial Engine</td>
                <td>${getBadge(comp.database)}</td>
              </tr>
              <tr>
                <td><strong>NASA FIRMS</strong></td>
                <td class="text-muted small">VIIRS SNPP & MODIS Satellite Feed</td>
                <td>${getBadge(comp.nasa_firms)}</td>
              </tr>
              <tr>
                <td><strong>OpenStreetMap (OSM)</strong></td>
                <td class="text-muted small">Overpass Geospatial API</td>
                <td>${getBadge(comp.osm)}</td>
              </tr>
              <tr>
                <td><strong>AI Classification</strong></td>
                <td class="text-muted small">8-Class FireGuard-XAI Inference Engine</td>
                <td>${getBadge(comp.ai_engine)}</td>
              </tr>
              <tr>
                <td><strong>Safety Routing</strong></td>
                <td class="text-muted small">Dynamic Danger-Zone Bypass Router</td>
                <td>${getBadge(comp.routing)}</td>
              </tr>
              <tr>
                <td><strong>Notification Service</strong></td>
                <td class="text-muted small">Multi-Agency SMS / Email Dispatch</td>
                <td>${getBadge(comp.notification_service)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      `;
    } catch (err) {
      bodyEl.innerHTML = `<div class="alert alert-danger">Failed to fetch component health: ${err.message}</div>`;
    }
  },

  // Requirement 25: 12-Step End-to-End SIH Demo Flow
  async triggerSihDemoFlow() {
    const modalEl = document.getElementById("sihDemoModal");
    const bodyEl = document.getElementById("sih-demo-modal-body");
    if (!modalEl || !bodyEl) return;

    bodyEl.innerHTML = `
      <div class="text-center py-5">
        <div class="spinner-grow text-danger mb-3" style="width: 3rem; height: 3rem;" role="status"></div>
        <h5 class="text-light fw-bold">Executing SIH26162 End-to-End Simulation Pipeline...</h5>
        <div class="text-muted small mt-2">
          Step 1: Hotspot Detection &rarr; Step 3: OSM Match &rarr; Step 4: AI Classify &rarr; Step 6: Risk Engine &rarr; Step 9: Safe Route &rarr; Step 11: Realtime Broadcast
        </div>
      </div>
    `;

    const bsModal = new bootstrap.Modal(modalEl);
    bsModal.show();

    try {
      const res = await Api.runSihDemoFlow();
      const inc = res.incident;
      const ai = res.classification;
      const risk = res.risk;
      const fac = res.facility;
      const routes = res.routes;

      bodyEl.innerHTML = `
        <div class="alert alert-danger bg-danger bg-opacity-10 border-danger d-flex align-items-center justify-content-between mb-4">
          <div>
            <h5 class="alert-heading fw-bold mb-1"><i class="bi bi-shield-fill-exclamation me-2"></i>12/12 Pipeline Steps Successfully Executed</h5>
            <div class="small">SIH Problem Statement SIH26162 Demonstration Completed. New incident registered and broadcast via WebSockets.</div>
          </div>
          <span class="badge bg-danger fs-6 px-3 py-2">STATUS: COMPLETE</span>
        </div>

        <div class="row g-3">
          <!-- Incident Dossier -->
          <div class="col-md-6">
            <div class="card bg-black border-secondary h-100">
              <div class="card-header bg-dark text-info fw-bold py-2 small">
                <i class="bi bi-file-earmark-medical me-1"></i> STEP 1, 2, 7: INCIDENT DOSSIER
              </div>
              <div class="card-body p-3 small">
                <div class="d-flex justify-content-between mb-2">
                  <span class="text-muted">Incident ID:</span>
                  <span class="font-monospace text-light">${inc.incident_number}</span>
                </div>
                <div class="d-flex justify-content-between mb-2">
                  <span class="text-muted">Matched Facility:</span>
                  <span class="text-warning fw-bold">${fac.name}</span>
                </div>
                <div class="d-flex justify-content-between mb-2">
                  <span class="text-muted">Coordinates:</span>
                  <span class="font-monospace text-light">${inc.latitude.toFixed(4)}° N, ${inc.longitude.toFixed(4)}° E</span>
                </div>
                <div class="d-flex justify-content-between mb-2">
                  <span class="text-muted">Initial Triage State:</span>
                  <span class="badge bg-danger">${inc.status} (Verification Required)</span>
                </div>
                <div class="text-muted mt-2 border-top border-secondary pt-2">
                  <strong>Operator Protocol:</strong> ${inc.operator_notes}
                </div>
              </div>
            </div>
          </div>

          <!-- AI Classification & Explainability -->
          <div class="col-md-6">
            <div class="card bg-black border-secondary h-100">
              <div class="card-header bg-dark text-warning fw-bold py-2 small">
                <i class="bi bi-robot me-1"></i> STEP 4: 8-CLASS AI CLASSIFIER & XAI
              </div>
              <div class="card-body p-3 small">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <span class="text-muted">Class Assigned:</span>
                  <span class="badge bg-danger fs-6">${ai.classification}</span>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <span class="text-muted">Inference Confidence:</span>
                  <span class="text-info fw-bold">${(ai.confidence * 100).toFixed(0)}% (${ai.model_version})</span>
                </div>
                <span class="text-muted d-block mb-1">Explainable AI Attribution Factors:</span>
                <ul class="mb-0 ps-3 text-secondary">
                  ${ai.factors.map(f => `<li class="mb-1 text-light">${f}</li>`).join("")}
                </ul>
              </div>
            </div>
          </div>

          <!-- Multi-factor Risk Score -->
          <div class="col-md-6">
            <div class="card bg-black border-secondary h-100">
              <div class="card-header bg-dark text-danger fw-bold py-2 small">
                <i class="bi bi-speedometer me-1"></i> STEP 6: RISK ASSESSMENT ENGINE (ISO31000)
              </div>
              <div class="card-body p-3 small">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <span class="text-muted">Calculated Risk Score:</span>
                  <span class="badge bg-danger fs-5 px-3">${risk.risk_score} / 100 (${risk.risk_level})</span>
                </div>
                <div class="text-light mb-3">${risk.explanation}</div>
                <div class="row g-2 text-center">
                  <div class="col-4">
                    <div class="bg-dark p-2 rounded">
                      <div class="text-muted" style="font-size:0.65rem;">THERMAL</div>
                      <strong class="text-danger">${risk.factors.thermal_intensity?.score || 92}</strong>
                    </div>
                  </div>
                  <div class="col-4">
                    <div class="bg-dark p-2 rounded">
                      <div class="text-muted" style="font-size:0.65rem;">PROXIMITY</div>
                      <strong class="text-danger">${risk.factors.industrial_proximity?.score || 95}</strong>
                    </div>
                  </div>
                  <div class="col-4">
                    <div class="bg-dark p-2 rounded">
                      <div class="text-muted" style="font-size:0.65rem;">POPULATION</div>
                      <strong class="text-warning">${risk.factors.population_exposure?.score || 78}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Dynamic Evacuation Corridor -->
          <div class="col-md-6">
            <div class="card bg-black border-secondary h-100">
              <div class="card-header bg-dark text-success fw-bold py-2 small">
                <i class="bi bi-sign-turn-right me-1"></i> STEP 9: SAFETY ROUTING ENGINE
              </div>
              <div class="card-body p-3 small">
                <div class="d-flex justify-content-between mb-2">
                  <span class="text-muted">Corridor Name:</span>
                  <span class="text-light fw-bold">${routes.recommended_route.name}</span>
                </div>
                <div class="d-flex justify-content-between mb-2">
                  <span class="text-muted">Total Distance:</span>
                  <span class="text-info">${routes.distance} km</span>
                </div>
                <div class="d-flex justify-content-between mb-2">
                  <span class="text-muted">Estimated Evacuation Time:</span>
                  <span class="text-warning">${routes.estimated_time} minutes</span>
                </div>
                <div class="d-flex justify-content-between mb-2">
                  <span class="text-muted">Thermal Buffer Avoidance:</span>
                  <span class="badge bg-success">500m Hazard Zone Cleared</span>
                </div>
                <div class="text-muted small mt-2 fst-italic">
                  ${routes.disclaimer}
                </div>
              </div>
            </div>
          </div>
        </div>
      `;

      // Refresh dashboard datasets to display new demo incident immediately
      await this.refreshData(true);
    } catch (err) {
      bodyEl.innerHTML = `<div class="alert alert-danger">Error executing SIH demonstration pipeline: ${err.message}</div>`;
    }
  },

  openDispatchModal() {
    const modalEl = document.getElementById("dispatchUnitModal");
    if (!modalEl) return;
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  },

  confirmDispatchUnit() {
    const unitSelect = document.getElementById("dispatch-unit-type");
    const sectorSelect = document.getElementById("dispatch-target-sector");
    const prioritySelect = document.getElementById("dispatch-priority-level");

    const unit = unitSelect ? unitSelect.value : "Hazmat Foam Cannon Engine #04";
    const sector = sectorSelect ? sectorSelect.value : "Sector 4 (Jamnagar Petrochem C-4)";
    const priority = prioritySelect ? prioritySelect.value : "CODE RED";

    const modalEl = document.getElementById("dispatchUnitModal");
    if (modalEl) {
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
    }

    this.showTacticalToast(`DISPATCH CONFIRMED: ${unit} deployed to ${sector} [${priority}] - ETA: 6 mins`);

    // Add alert notification
    if (AppState.alerts) {
      AppState.alerts.unshift({
        id: `ALT-DISP-${Date.now().toString().slice(-4)}`,
        title: `Tactical Deployment: ${unit}`,
        message: `Unit assigned to ${sector}. Automated foaming deluge system activated.`,
        level: "CRITICAL",
        timestamp: new Date().toISOString()
      });
      const badge = document.getElementById("badge-alerts-count");
      if (badge) badge.innerText = AppState.alerts.length < 10 ? `0${AppState.alerts.length}` : AppState.alerts.length;
    }
  },

  openBroadcastModal() {
    const modalEl = document.getElementById("emergencyBroadcastModal");
    if (!modalEl) return;
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  },

  transmitEmergencyBroadcast() {
    const channelBoxes = document.querySelectorAll(".broadcast-channel-chk:checked");
    const channels = Array.from(channelBoxes).map(c => c.value).join(", ") || "Multi-Agency Emergency Bus";
    const modalEl = document.getElementById("emergencyBroadcastModal");
    if (modalEl) {
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
    }

    const broadcastId = `CAP-IN-2026-${Math.floor(1000 + Math.random() * 9000)}`;
    this.showTacticalToast(`EMERGENCY BROADCAST SENT: [${broadcastId}] across ${channels}. Evacuation siren active!`);

    if (AppState.alerts) {
      AppState.alerts.unshift({
        id: broadcastId,
        title: `Multi-Agency Emergency Broadcast (${broadcastId})`,
        message: `Common Alerting Protocol (CAP) issued to 1.5km hazard perimeter. Stand-off evacuation required.`,
        level: "CRITICAL",
        timestamp: new Date().toISOString()
      });
      const badge = document.getElementById("badge-alerts-count");
      if (badge) badge.innerText = AppState.alerts.length < 10 ? `0${AppState.alerts.length}` : AppState.alerts.length;
    }
  },

  openInitiateProtocolModal() {
    const modalEl = document.getElementById("initiateProtocolModal");
    if (!modalEl) return;
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  },

  executeInitiatedProtocol() {
    const btn = document.getElementById("btn-exec-protocol");
    const progressEl = document.getElementById("protocol-progress-bar");
    const logEl = document.getElementById("protocol-exec-log");

    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Executing Containment...`;
    }

    let step = 0;
    const steps = [
      "Phase 1: Automated emergency pipeline valve isolation engaged...",
      "Phase 2: High-pressure boundary deluge foam cannons activated...",
      "Phase 3: 500m thermal hazard stand-off corridor established...",
      "Phase 4: State Emergency Operation Center & NDRF Battalion notified."
    ];

    if (logEl) logEl.innerHTML = "";

    const interval = setInterval(() => {
      if (step < steps.length) {
        if (progressEl) progressEl.style.width = `${(step + 1) * 25}%`;
        if (logEl) {
          const item = document.createElement("div");
          item.className = "text-success small mb-1";
          item.innerHTML = `<i class="bi bi-check-circle-fill me-1"></i> ${steps[step]}`;
          logEl.appendChild(item);
        }
        step++;
      } else {
        clearInterval(interval);
        if (btn) {
          btn.className = "btn btn-success btn-sm w-100 fw-bold";
          btn.innerHTML = `<i class="bi bi-shield-check me-1"></i> Protocol SOP-IND-902 Fully Engaged`;
        }
        App.showTacticalToast("SOP-IND-902 ENGAGED: Industrial fire suppression protocol in active operation.");
      }
    }, 450);
  }
};

// Auto-boot on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
