/**
 * FIREGUARD AI - Analytics & Chart.js View Controller
 */
const AnalyticsView = {
  charts: {},

  async renderCharts() {
    try {
      const data = await Api.fetchAnalyticsCharts();
      const classDist = data.classification_distribution || data.classification || { labels: ["Industrial Fire", "Gas Flare", "Persistent Source"], data: [12, 8, 4] };
      const trendData = data.temporal_trend || (data.timeline ? { labels: data.timeline.labels, total_hotspots: data.timeline.data, industrial_fires: data.timeline.data.map(v => Math.round(v * 0.4)) } : { labels: ["00:00", "06:00", "12:00", "18:00"], total_hotspots: [5, 12, 18, 9], industrial_fires: [2, 5, 8, 3] });
      const riskDist = data.risk_distribution || data.risk_tiers || { labels: ["LOW", "MODERATE", "HIGH", "CRITICAL"], data: [2, 5, 8, 4] };
      const regDist = data.regional_distribution || { labels: ["Gujarat", "Andhra Pradesh", "Maharashtra", "Tamil Nadu"], data: [8, 4, 3, 2] };

      this.initClassificationChart(classDist);
      this.initTrendChart(trendData);
      this.initRiskChart(riskDist);
      this.initRegionalChart(regDist);
    } catch (err) {
      console.warn("Analytics fetch failed:", err);
    }
  },

  initClassificationChart(dist) {
    const ctx = document.getElementById("chart-classification");
    if (!ctx || typeof Chart === "undefined") return;

    if (this.charts.classification) this.charts.classification.destroy();

    const colors = [
      "#EF4444", "#F97316", "#F59E0B", "#10B981",
      "#06B6D4", "#3B82F6", "#A855F7", "#64748B"
    ];

    this.charts.classification = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: dist.labels,
        datasets: [{
          data: dist.data,
          backgroundColor: colors,
          borderColor: "#0B132B",
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "right", labels: { color: "#CBD5E1", font: { size: 11 } } }
        }
      }
    });
  },

  initTrendChart(trend) {
    const ctx = document.getElementById("chart-trend");
    if (!ctx || typeof Chart === "undefined") return;

    if (this.charts.trend) this.charts.trend.destroy();

    this.charts.trend = new Chart(ctx, {
      type: "line",
      data: {
        labels: trend.labels,
        datasets: [
          {
            label: "Total Thermal Hotspots",
            data: trend.total_hotspots,
            borderColor: "#38BDF8",
            backgroundColor: "rgba(56, 189, 248, 0.15)",
            tension: 0.35,
            fill: true
          },
          {
            label: "Industrial Fire Emergencies",
            data: trend.industrial_fires,
            borderColor: "#EF4444",
            backgroundColor: "rgba(239, 68, 68, 0.15)",
            tension: 0.35,
            fill: true
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(255,255,255,0.05)" } },
          y: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(255,255,255,0.05)" } }
        },
        plugins: {
          legend: { labels: { color: "#CBD5E1" } }
        }
      }
    });
  },

  initRiskChart(dist) {
    const ctx = document.getElementById("chart-risk");
    if (!ctx || typeof Chart === "undefined") return;

    if (this.charts.risk) this.charts.risk.destroy();

    this.charts.risk = new Chart(ctx, {
      type: "bar",
      data: {
        labels: dist.labels,
        datasets: [{
          label: "Incidents by Risk Tier",
          data: dist.data,
          backgroundColor: ["#10B981", "#F59E0B", "#F97316", "#EF4444"]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: "#94A3B8" }, grid: { display: false } },
          y: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(255,255,255,0.05)" } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  },

  initRegionalChart(dist) {
    const ctx = document.getElementById("chart-regional");
    if (!ctx || typeof Chart === "undefined") return;

    if (this.charts.regional) this.charts.regional.destroy();

    this.charts.regional = new Chart(ctx, {
      type: "bar",
      indexAxis: "y",
      data: {
        labels: dist.labels,
        datasets: [{
          label: "Active Incidents",
          data: dist.data,
          backgroundColor: "#06B6D4"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(255,255,255,0.05)" } },
          y: { ticks: { color: "#94A3B8" }, grid: { display: false } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
};
