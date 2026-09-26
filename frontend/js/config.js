/**
 * FIREGUARD AI - Global Frontend Configuration
 */
const AppConfig = {
  API_BASE_URL: window.location.origin.includes("http") ? "" : "http://127.0.0.1:5000",
  DEFAULT_MAP_CENTER: [20.5937, 78.9629], // Center of India
  DEFAULT_MAP_ZOOM: 5,
  POLL_INTERVAL_MS: 15000,

  MAP_TILES: {
    DARK: {
      url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
      attribution: '&copy; <a href="https://carto.com/">CARTO</a>, &copy; <a href="https://openstreetmap.org">OSM</a>'
    },
    SATELLITE: {
      url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    },
    STREETS: {
      url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }
  },

  RISK_COLORS: {
    CRITICAL: "#EF4444",
    HIGH: "#F97316",
    MODERATE: "#F59E0B",
    LOW: "#10B981"
  }
};
