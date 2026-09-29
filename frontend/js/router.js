/**
 * FIREGUARD AI - Single Page Application View Router
 * Manages navigation between all tactical operations center views.
 */
const Router = {
  currentView: "dashboard",

  init() {
    // Bind all sidebar nav clicks
    document.querySelectorAll(".sidebar-nav-item").forEach(item => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const targetView = item.getAttribute("data-view");
        if (targetView) this.navigate(targetView);
      });
    });

    // Bind all top navbar center links (Command Center, Satellite Analysis, Incident Intelligence, Risk Analytics)
    document.querySelectorAll(".nav-link-item").forEach(item => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const targetView = item.getAttribute("data-view");
        if (targetView) this.navigate(targetView);
      });
    });

    // Handle deep-link hash if present
    const hash = window.location.hash.replace("#", "");
    if (hash && document.getElementById(`view-${hash}`)) {
      this.navigate(hash);
    } else {
      this.navigate("dashboard");
    }
  },

  navigate(viewName) {
    const targetEl = document.getElementById(`view-${viewName}`);
    if (!targetEl) return;

    // Update active sidebar state
    document.querySelectorAll(".sidebar-nav-item").forEach(item => {
      if (item.getAttribute("data-view") === viewName) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });

    // Update active top navbar links
    document.querySelectorAll(".nav-link-item").forEach(item => {
      if (item.getAttribute("data-view") === viewName) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });

    // Hide all view containers
    document.querySelectorAll(".tactical-view").forEach(el => {
      el.style.display = "none";
    });

    // Show selected view container
    targetEl.style.display = "block";
    this.currentView = viewName;
    AppState.activeTab = viewName;
    window.location.hash = viewName;

    // Trigger view-specific lifecycle hooks
    if (viewName === "dashboard" || viewName === "routes") {
      setTimeout(() => {
        if (TacticalMap.map) TacticalMap.map.invalidateSize();
      }, 100);
    }

    if (viewName === "hotspots" && typeof HotspotsView !== "undefined") {
      HotspotsView.render();
    }

    if (viewName === "analytics" && typeof AnalyticsView !== "undefined") {
      AnalyticsView.renderCharts();
    }

    if (viewName === "persistent" && typeof PersistentView !== "undefined") {
      PersistentView.render();
    }

    if (viewName === "facilities" && typeof FacilitiesView !== "undefined") {
      FacilitiesView.render();
    }

    if (viewName === "incidents" && typeof IncidentsView !== "undefined") {
      IncidentsView.render();
    }

    if (viewName === "risk" && typeof RiskView !== "undefined") {
      RiskView.render();
    }

    if (viewName === "emergency" && typeof EmergencyView !== "undefined") {
      EmergencyView.render();
    }

    if (viewName === "alerts" && typeof AlertsView !== "undefined") {
      AlertsView.render();
    }

    if (viewName === "settings" && typeof SettingsView !== "undefined") {
      SettingsView.render();
    }
  }
};
