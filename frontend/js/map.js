/**
 * FIREGUARD AI - Tactical Leaflet Map Controller
 * Manages satellite/dark base layers, tactical hotspots, danger buffers,
 * industrial facility perimeters, and safe evacuation corridors.
 */
const TacticalMap = {
  map: null,
  layerGroups: {
    hotspots: null,
    facilities: null,
    emergency: null,
    hazardZones: null,
    evacuationRoutes: null
  },
  baseLayers: {},

  init(containerId = "tactical-map-container") {
    if (this.map) return;

    const el = document.getElementById(containerId);
    if (!el) return;

    // Initialize Leaflet map
    this.map = L.map(containerId, {
      center: AppConfig.DEFAULT_MAP_CENTER,
      zoom: AppConfig.DEFAULT_MAP_ZOOM,
      zoomControl: false,
      attributionControl: false
    });

    // Add Tactical Zoom Control in bottom right
    L.control.zoom({ position: "bottomright" }).addTo(this.map);

    // Create Base Layers
    this.baseLayers.dark = L.tileLayer(AppConfig.MAP_TILES.DARK.url, {
      maxZoom: 18,
      subdomains: "abcd"
    }).addTo(this.map);

    this.baseLayers.satellite = L.tileLayer(AppConfig.MAP_TILES.SATELLITE.url, {
      maxZoom: 18
    });

    this.baseLayers.streets = L.tileLayer(AppConfig.MAP_TILES.STREETS.url, {
      maxZoom: 18
    });

    // Initialize Layer Groups
    this.layerGroups.hotspots = L.layerGroup().addTo(this.map);
    this.layerGroups.facilities = L.layerGroup().addTo(this.map);
    this.layerGroups.emergency = L.layerGroup().addTo(this.map);
    this.layerGroups.hazardZones = L.layerGroup().addTo(this.map);
    this.layerGroups.evacuationRoutes = L.layerGroup().addTo(this.map);

    // Layer Toggle Control in top-left
    const overlays = {
      "Thermal Hotspots": this.layerGroups.hotspots,
      "Industrial Facilities": this.layerGroups.facilities,
      "Emergency Infrastructure": this.layerGroups.emergency,
      "Hazard Danger Zones (500m/1.5km)": this.layerGroups.hazardZones,
      "Safe Evacuation Routes": this.layerGroups.evacuationRoutes
    };

    L.control.layers(
      { "Dark Tactical": this.baseLayers.dark, "Satellite Imagery": this.baseLayers.satellite, "OpenStreetMap": this.baseLayers.streets },
      overlays,
      { position: "topleft", collapsed: true }
    ).addTo(this.map);

    // Track mouse coordinates in HUD
    this.map.on("mousemove", (e) => {
      const coordEl = document.getElementById("hud-coordinates");
      if (coordEl) {
        coordEl.innerText = `${e.latlng.lat.toFixed(4)}° N, ${e.latlng.lng.toFixed(4)}° E`;
      }
    });

    // Invalidate size to ensure map fills container completely
    setTimeout(() => {
      if (this.map) this.map.invalidateSize();
    }, 200);
    setTimeout(() => {
      if (this.map) this.map.invalidateSize();
    }, 500);

    console.log("Tactical Leaflet Map initialized successfully.");
  },

  setBaseLayer(type) {
    if (!this.map || !this.baseLayers[type]) return;
    Object.values(this.baseLayers).forEach(layer => this.map.removeLayer(layer));
    this.baseLayers[type].addTo(this.map);
  },

  renderHotspots(hotspots = [], incidents = []) {
    if (!this.map || !this.layerGroups.hotspots) return;
    this.layerGroups.hotspots.clearLayers();

    hotspots.forEach(hp => {
      const inc = incidents.find(i => i.hotspot_id === hp.id);
      const isCritical = inc && inc.risk_level === "CRITICAL";
      const isHigh = inc && inc.risk_level === "HIGH";
      const isPersistent = hp.is_persistent;

      let markerClass = "tactical-marker-low";
      let pulseColor = "#10B981";

      if (isCritical) {
        markerClass = "tactical-marker-pulse";
        pulseColor = "#EF4444";
      } else if (isHigh) {
        markerClass = "tactical-marker-high";
        pulseColor = "#F97316";
      } else if (isPersistent) {
        markerClass = "tactical-marker-persistent";
        pulseColor = "#A855F7";
      }

      const icon = L.divIcon({
        className: "custom-tactical-pin",
        html: `<div class="${markerClass}" style="${!isCritical && !isPersistent ? 'background:'+pulseColor+';width:14px;height:14px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 6px '+pulseColor : ''}"></div>`,
        iconSize: [22, 22],
        iconAnchor: [11, 11]
      });

      const marker = L.marker([hp.latitude, hp.longitude], { icon });

      // Popup Content
      const popupHtml = `
        <div style="font-family: -apple-system, sans-serif; font-size: 13px; color: #0F172A; min-width: 220px;">
          <div style="font-weight: 800; font-size: 14px; margin-bottom: 4px; color: ${pulseColor};">
            ${inc ? inc.title : 'Satellite Thermal Hotspot'}
          </div>
          <div style="font-size: 11px; color: #64748B; margin-bottom: 8px;">
            ${hp.source_satellite} &bull; ${hp.acquisition_date} ${hp.acquisition_time || ''} UTC
          </div>
          <table style="width: 100%; font-size: 12px; margin-bottom: 8px;">
            <tr><td><strong>FRP:</strong></td><td>${hp.frp_mw} MW</td></tr>
            <tr><td><strong>Brightness:</strong></td><td>${hp.brightness_k} K</td></tr>
            <tr><td><strong>Confidence:</strong></td><td>${hp.confidence}%</td></tr>
            <tr><td><strong>Risk:</strong></td><td><span style="font-weight: bold; color: ${pulseColor}">${inc ? inc.risk_level : 'EVALUATING'}</span></td></tr>
            ${hp.facility_name ? `<tr><td><strong>Facility:</strong></td><td>${hp.facility_name}</td></tr>` : ''}
          </table>
          ${inc ? `<button onclick="IncidentModal.open('${inc.id}')" style="width:100%; background: #0284C7; color: #fff; border: none; padding: 6px; border-radius: 4px; font-weight: 700; cursor: pointer;">OPEN COMMAND DOSSIER</button>` : ''}
        </div>
      `;

      marker.bindPopup(popupHtml);
      marker.on("click", () => {
        if (inc) AppState.activeIncident = inc;
      });

      this.layerGroups.hotspots.addLayer(marker);
    });
  },

  renderFacilities(facilities = []) {
    if (!this.map || !this.layerGroups.facilities) return;
    this.layerGroups.facilities.clearLayers();

    facilities.forEach(f => {
      const icon = L.divIcon({
        className: "custom-fac-pin",
        html: `<div class="tactical-marker-facility" title="${f.name}"><i class="bi bi-buildings" style="font-size:10px; color:#fff; display:flex; align-items:center; justify-content:center; height:100%;"></i></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      });

      const marker = L.marker([f.latitude, f.longitude], { icon });
      const facType = (f.facility_type || 'Industrial').toUpperCase();
      const hazCat = f.hazard_category || f.hazmat_level || 'LEVEL-3';
      marker.bindPopup(`
        <div style="font-size: 12px; color: #0F172A;">
          <strong>${f.name}</strong><br>
          <span style="color: #64748B;">${facType} &bull; ${hazCat}</span><br>
          <em>${f.address || ''}</em><br>
          <strong>Contact:</strong> ${f.emergency_contact_phone || f.emergency_phone || 'N/A'}<br>
          <button onclick="Router.navigate('facilities');" style="margin-top:5px; background:#06B6D4; color:#fff; border:none; padding:4px 8px; border-radius:3px; cursor:pointer;">View Facility Profile</button>
        </div>
      `);
      this.layerGroups.facilities.addLayer(marker);

      // Render polygon boundary if present
      if (f.polygon_coords && f.polygon_coords.length >= 3) {
        const poly = L.polygon(f.polygon_coords, {
          color: "#06B6D4",
          weight: 1.5,
          opacity: 0.8,
          fillColor: "#06B6D4",
          fillOpacity: 0.12
        });
        this.layerGroups.facilities.addLayer(poly);
      }
    });
  },

  renderHazardZones(dangerBuffers) {
    if (!this.map || !this.layerGroups.hazardZones) return;
    this.layerGroups.hazardZones.clearLayers();

    if (!dangerBuffers) return;

    // 1. Red Blast Zone (500m)
    if (dangerBuffers.blast_zone_red) {
      const bz = dangerBuffers.blast_zone_red;
      const redCircle = L.circle(bz.center, {
        radius: bz.radius_m,
        color: bz.color,
        weight: 2,
        fillColor: bz.color,
        fillOpacity: 0.35,
        dashArray: "4, 4"
      }).bindTooltip(bz.label, { permanent: false, direction: "top" });
      this.layerGroups.hazardZones.addLayer(redCircle);
    }

    // 2. Yellow Caution / Smoke Zone (1500m)
    if (dangerBuffers.smoke_zone_yellow) {
      const sz = dangerBuffers.smoke_zone_yellow;
      const yellowCircle = L.circle(sz.center, {
        radius: sz.radius_m,
        color: sz.color,
        weight: 1.5,
        fillColor: sz.color,
        fillOpacity: 0.15,
        dashArray: "6, 6"
      }).bindTooltip(sz.label, { permanent: false, direction: "top" });
      this.layerGroups.hazardZones.addLayer(yellowCircle);
    }
  },

  renderEvacuationRoutes(routePlan) {
    if (!this.map || !this.layerGroups.evacuationRoutes) return;
    this.layerGroups.evacuationRoutes.clearLayers();

    if (!routePlan) return;

    // Handle array or object
    const routesList = Array.isArray(routePlan) ? routePlan : (routePlan.evacuation_routes || [routePlan]);
    if (!routesList.length) return;

    const r = routesList[0];

    // Standard v1 waypoints support
    const waypoints = r.waypoints || (r.recommended_route && r.recommended_route.waypoints) || [];
    if (waypoints.length >= 2) {
      const greenLine = L.polyline(waypoints, {
        color: "#10B981",
        weight: 6,
        opacity: 0.95
      }).bindTooltip(`RECOMMENDED SAFE CORRIDOR (${r.distance_km || r.distance || '12.4'} km)`, { sticky: true });
      this.layerGroups.evacuationRoutes.addLayer(greenLine);
      try {
        this.map.fitBounds(greenLine.getBounds(), { padding: [50, 50] });
      } catch (e) {}
    }

    // Legacy multi-segment fallback
    if (r.danger_route_red && r.danger_route_red.length) {
      const redLine = L.polyline(r.danger_route_red, {
        color: "#EF4444",
        weight: 5,
        opacity: 0.9,
        dashArray: "5, 5"
      }).bindTooltip("BLOCKED HAZARD SECTOR - DO NOT ENTER", { sticky: true });
      this.layerGroups.evacuationRoutes.addLayer(redLine);
    }
    if (r.caution_route_yellow && r.caution_route_yellow.length) {
      const yellowLine = L.polyline(r.caution_route_yellow, {
        color: "#F59E0B",
        weight: 5,
        opacity: 0.9
      }).bindTooltip("CAUTION PERIMETER TRANSITION", { sticky: true });
      this.layerGroups.evacuationRoutes.addLayer(yellowLine);
    }
    if (r.safe_route_green && r.safe_route_green.length) {
      const greenLine = L.polyline(r.safe_route_green, {
        color: "#10B981",
        weight: 6,
        opacity: 0.95
      }).bindTooltip(`RECOMMENDED SAFE CORRIDOR TO ${r.destination_name} (${r.distance_km} km)`, { sticky: true });
      this.layerGroups.evacuationRoutes.addLayer(greenLine);
      try {
        this.map.fitBounds(greenLine.getBounds(), { padding: [50, 50] });
      } catch (e) {}
    }
  },

  panTo(lat, lon, zoom = 12) {
    if (!this.map) return;
    this.map.flyTo([lat, lon], zoom, { duration: 1.2 });
  }
};
