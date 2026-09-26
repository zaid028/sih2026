/**
 * FIREGUARD AI - Settings & Demo Configuration Controller
 */
const SettingsView = {
  async render() {
    try {
      const s = await Api.fetchSettings();
      const demoToggle = document.getElementById("settings-demo-toggle");
      const keyInput = document.getElementById("settings-firms-key");
      const endpointInput = document.getElementById("settings-overpass-endpoint");

      if (demoToggle) demoToggle.checked = s.demo_mode;
      if (keyInput) keyInput.placeholder = s.firms_map_key_masked || "Enter your NASA FIRMS MAP_KEY";
      if (endpointInput) endpointInput.value = s.overpass_endpoint;
    } catch (err) {
      console.warn("Failed to load settings:", err);
    }
  },

  async save() {
    const demoToggle = document.getElementById("settings-demo-toggle");
    const keyInput = document.getElementById("settings-firms-key");
    const endpointInput = document.getElementById("settings-overpass-endpoint");

    const data = {
      demo_mode: demoToggle ? demoToggle.checked : true
    };
    if (keyInput && keyInput.value.trim()) {
      data.firms_map_key = keyInput.value.trim();
    }
    if (endpointInput && endpointInput.value.trim()) {
      data.overpass_endpoint = endpointInput.value.trim();
    }

    try {
      const res = await Api.updateSettings(data);
      alert(res.message || "Settings updated successfully!");
      App.refreshData();
    } catch (err) {
      alert("Failed to update settings: " + err.message);
    }
  },

  async syncNow() {
    try {
      const res = await Api.syncHotspots();
      alert(`Satellite Ingestion Complete!\nIngested: ${res.ingested_count} anomalies\nSource: ${res.source}`);
      App.refreshData();
    } catch (err) {
      alert("Satellite sync failed: " + err.message);
    }
  }
};
