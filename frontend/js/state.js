/**
 * FIREGUARD AI - Global State Management
 */
const AppState = {
  currentUser: {
    username: "operator",
    role: "operator",
    full_name: "Operations Controller",
    organization: "Disaster Management Cell"
  },
  systemStatus: {
    status: "OPERATIONAL",
    demo_mode: true,
    nasa_firms_connected: false,
    active_hotspots: 0,
    total_incidents: 0,
    critical_threats: 0
  },
  hotspots: [],
  incidents: [],
  facilities: [],
  persistentSources: [],
  alerts: [],
  activeIncident: null,
  activeTab: "dashboard",
  audioMuted: false,

  filters: {
    risk: "",
    fire_class: "",
    satellite: "",
    min_confidence: 0,
    is_industrial: null,
    is_persistent: null,
    search: ""
  },

  listeners: {},

  on(event, callback) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
  },

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => cb(data));
    }
  }
};
