/**
 * FIREGUARD AI - REST API Client Wrapper
 * Implements both /api/v1/* standard architecture and legacy backward-compatible calls.
 */
const Api = {
  async get(endpoint, params = {}) {
    const base = AppConfig.API_BASE_URL || window.location.origin;
    const url = new URL(endpoint.startsWith("http") ? endpoint : `${base}${endpoint}`);
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== "") {
        url.searchParams.append(key, params[key]);
      }
    });

    const headers = { "Content-Type": "application/json" };
    const token = localStorage.getItem("fireguard_token");
    if (token) headers["Authorization"] = `Bearer ${token}`;

    try {
      const response = await fetch(url.toString(), { method: "GET", headers });
      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.error?.message || `HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn(`API GET error on ${endpoint}:`, err);
      throw err;
    }
  },

  async post(endpoint, body = {}) {
    const base = AppConfig.API_BASE_URL || window.location.origin;
    const url = endpoint.startsWith("http") ? endpoint : `${base}${endpoint}`;
    const headers = { "Content-Type": "application/json" };
    const token = localStorage.getItem("fireguard_token");
    if (token) headers["Authorization"] = `Bearer ${token}`;

    try {
      const response = await fetch(url, {
        method: "POST",
        headers,
        body: JSON.stringify(body)
      });
      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.error?.message || `HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn(`API POST error on ${endpoint}:`, err);
      throw err;
    }
  },

  async patch(endpoint, body = {}) {
    const base = AppConfig.API_BASE_URL || window.location.origin;
    const url = endpoint.startsWith("http") ? endpoint : `${base}${endpoint}`;
    const headers = { "Content-Type": "application/json" };
    const token = localStorage.getItem("fireguard_token");
    if (token) headers["Authorization"] = `Bearer ${token}`;

    try {
      const response = await fetch(url, {
        method: "PATCH",
        headers,
        body: JSON.stringify(body)
      });
      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.error?.message || `HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn(`API PATCH error on ${endpoint}:`, err);
      throw err;
    }
  },

  async delete(endpoint) {
    const base = AppConfig.API_BASE_URL || window.location.origin;
    const url = endpoint.startsWith("http") ? endpoint : `${base}${endpoint}`;
    const headers = { "Content-Type": "application/json" };
    const token = localStorage.getItem("fireguard_token");
    if (token) headers["Authorization"] = `Bearer ${token}`;

    try {
      const response = await fetch(url, { method: "DELETE", headers });
      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.error?.message || `HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn(`API DELETE error on ${endpoint}:`, err);
      throw err;
    }
  },

  // v1 REST API Endpoints
  fetchHealthStatus() { return this.get("/api/v1/health"); },
  runSihDemoFlow() { return this.post("/api/v1/demo/run"); },
  fetchV1Hotspots(params = {}) { return this.get("/api/v1/hotspots", params); },
  ingestHotspots(country = "IND", dayRange = 1) { return this.post(`/api/v1/hotspots/ingest?country=${country}&day_range=${dayRange}`); },
  analyzeLocation(lat, lon, radiusKm = 25) { return this.post("/api/v1/analyze/location", { latitude: lat, longitude: lon, radius_km: radiusKm }); },
  classifyAnomaly(hotspotId, features = {}) { return this.post("/api/v1/ai/classify", { hotspot_id: hotspotId, features }); },
  calculateRisk(hotspotId, classification, confidence, features = {}) { return this.post("/api/v1/risk/calculate", { hotspot_id: hotspotId, classification, confidence, features }); },
  computeSafeRoute(origin, destination, incidentId = null) { return this.post("/api/v1/routes/safe", { origin, destination, incident_id: incidentId }); },

  // Compatibility & UI methods
  fetchSystemStatus() { return this.get("/api/system/status"); },
  fetchHotspots(filters = {}) { return this.get("/api/hotspots", filters); },
  fetchIncidents(filters = {}) { return this.get("/api/incidents", filters); },
  fetchIncidentDetail(id) { return this.get(`/api/incidents/${id}`); },
  updateIncidentStatus(id, status, notes = "") { return this.patch(`/api/incidents/${id}/status`, { status, notes }); },
  fetchFacilities() { return this.get("/api/facilities"); },
  fetchFacilityDetail(id) { return this.get(`/api/facilities/${id}`); },
  fetchPersistentSources() { return this.get("/api/persistent-sources"); },
  fetchRoutes(incidentId) { return this.get(`/api/routes/${incidentId}`); },
  fetchEmergencyContacts() { return this.get("/api/emergency/contacts"); },
  simulateDispatch(incidentId) { return this.post("/api/emergency/dispatch-sim", { incident_id: incidentId }); },
  fetchAnalyticsKpis() { return this.get("/api/analytics/kpis"); },
  fetchAnalyticsCharts() { return this.get("/api/analytics/charts"); },
  fetchAlerts() { return this.get("/api/alerts"); },
  acknowledgeAlert(id) { return this.patch(`/api/alerts/${id}/ack`); },
  syncHotspots() { return this.post("/api/hotspots/sync"); },
  fetchSettings() { return this.get("/api/settings"); },
  updateSettings(data) { return this.post("/api/settings", data); },
  switchDemoRole(role) { return this.post("/api/auth/demo-switch", { role }); },
  submitCitizenReport(data) { return this.post("/api/v1/incidents/citizen-report", data); }
};
