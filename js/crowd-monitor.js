/**
 * BUSMITRA - IR Sensor Crowd Monitoring & Dynamic Occupancy Engine
 * Simulates directional ESP32 dual-beam IR sensors (Entrance & Exit)
 * Renders real-time Chart.js activity telemetry and keeps state unified.
 */

window.BUSMITRA_CROWD = {
  currentBus: null,
  chartInstance: null,
  historyData: {
    timestamps: ["10:00 AM", "10:10 AM", "10:20 AM", "10:30 AM", "10:40 AM", "10:50 AM"],
    inEvents: [12, 8, 14, 6, 9, 7],
    outEvents: [0, 2, 4, 3, 5, 4],
    occupancyRecord: [12, 18, 28, 31, 35, 38]
  },

  init: function(busId, chartCanvasId) {
    this.currentBus = window.getBusById(busId) || window.BUSMITRA_DATA.buses[0];
    this.renderMetrics();
    this.initChart(chartCanvasId);
    this.setupHardwareSimControls();
  },

  renderMetrics: function() {
    if (!this.currentBus) return;

    // Recalculate metrics strictly via the universal formula
    const metrics = window.calculateBusMetrics(this.currentBus);
    this.currentBus = { ...this.currentBus, ...metrics };

    // Update DOM IDs
    const inCountEl = document.getElementById("metric-in-count");
    const outCountEl = document.getElementById("metric-out-count");
    const passCountEl = document.getElementById("metric-passengers");
    const seatsEl = document.getElementById("metric-seats");
    const occEl = document.getElementById("metric-occupancy");
    const occProgressEl = document.getElementById("metric-occupancy-bar");
    const crowdTagEl = document.getElementById("metric-crowd-tag");
    const lastUpdateEl = document.getElementById("metric-last-update");

    if (inCountEl) inCountEl.textContent = this.currentBus.sensorInCount;
    if (outCountEl) outCountEl.textContent = this.currentBus.sensorOutCount;
    if (passCountEl) passCountEl.textContent = this.currentBus.currentPassengers;
    if (seatsEl) seatsEl.textContent = this.currentBus.availableSeats;
    
    if (occEl) occEl.textContent = `${this.currentBus.occupancyPercent}%`;
    if (occProgressEl) {
      occProgressEl.style.width = `${Math.min(100, this.currentBus.occupancyPercent)}%`;
      occProgressEl.style.backgroundColor = this.currentBus.crowdColor;
    }

    if (crowdTagEl) {
      crowdTagEl.className = `crowd-pill ${this.currentBus.crowdClass}`;
      crowdTagEl.innerHTML = `
        <span class="sensor-status-dot" style="background:${this.currentBus.crowdColor}"></span>
        ${this.currentBus.crowdLevel}
      `;
    }

    if (lastUpdateEl) {
      const now = new Date();
      lastUpdateEl.textContent = `${now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })} (ESP32 IR Pulse)`;
    }

    // Also update prediction panel if present
    if (window.BUSMITRA_PREDICTION && typeof window.BUSMITRA_PREDICTION.updatePrediction === 'function') {
      window.BUSMITRA_PREDICTION.updatePrediction(this.currentBus);
    }
  },

  /**
   * Hardware Simulation Event: Passenger boards via Entrance Door IR sensor
   */
  simulatePassengerBoard: function() {
    if (!this.currentBus) return;
    this.currentBus.sensorInCount += 1;
    this.recordActivity(1, 0);
    this.renderMetrics();
    this.triggerSensorFlash("entrance-sensor-indicator");
    if (window.showToast) window.showToast("ESP32 IR Sensor: Passenger Boarded (+1 IN)");
  },

  /**
   * Hardware Simulation Event: Passenger disembarks via Exit Door IR sensor
   */
  simulatePassengerAlight: function() {
    if (!this.currentBus) return;
    // Cannot alight if current passengers is 0
    if (this.currentBus.currentPassengers <= 0) {
      if (window.showToast) window.showToast("Bus is currently empty. No passenger can alight.");
      return;
    }
    this.currentBus.sensorOutCount += 1;
    this.recordActivity(0, 1);
    this.renderMetrics();
    this.triggerSensorFlash("exit-sensor-indicator");
    if (window.showToast) window.showToast("ESP32 IR Sensor: Passenger Alighted (+1 OUT)");
  },

  triggerSensorFlash: function(sensorElementId) {
    const el = document.getElementById(sensorElementId);
    if (el) {
      el.classList.add("sensor-flash-active");
      setTimeout(() => el.classList.remove("sensor-flash-active"), 400);
    }
  },

  recordActivity: function(inDiff, outDiff) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Add to chart history
    this.historyData.timestamps.push(timeStr);
    this.historyData.inEvents.push(inDiff);
    this.historyData.outEvents.push(outDiff);
    this.historyData.occupancyRecord.push(this.currentBus.currentPassengers);

    if (this.historyData.timestamps.length > 8) {
      this.historyData.timestamps.shift();
      this.historyData.inEvents.shift();
      this.historyData.outEvents.shift();
      this.historyData.occupancyRecord.shift();
    }

    if (this.chartInstance) {
      this.chartInstance.update();
    }
  },

  initChart: function(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return;

    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    this.chartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: this.historyData.timestamps,
        datasets: [
          {
            label: 'Total Onboard (Live)',
            data: this.historyData.occupancyRecord,
            borderColor: '#1D4ED8',
            backgroundColor: 'rgba(29, 78, 216, 0.08)',
            fill: true,
            tension: 0.35,
            borderWidth: 2.5,
            pointBackgroundColor: '#1D4ED8',
            pointRadius: 4
          },
          {
            label: 'Sensor IN Pulses',
            data: this.historyData.inEvents,
            borderColor: '#10B981',
            borderDash: [4, 4],
            tension: 0.2,
            borderWidth: 2,
            pointRadius: 3
          },
          {
            label: 'Sensor OUT Pulses',
            data: this.historyData.outEvents,
            borderColor: '#EF4444',
            borderDash: [4, 4],
            tension: 0.2,
            borderWidth: 2,
            pointRadius: 3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              boxWidth: 12,
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 }
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(226, 232, 240, 0.6)' },
            ticks: { font: { family: "'JetBrains Mono', monospace", size: 11 } }
          },
          x: {
            grid: { display: false },
            ticks: { font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 } }
          }
        }
      }
    });
  },

  setupHardwareSimControls: function() {
    const boardBtn = document.getElementById("sim-board-btn");
    const alightBtn = document.getElementById("sim-alight-btn");
    const resetSensorBtn = document.getElementById("sim-reset-sensors-btn");

    if (boardBtn) {
      boardBtn.addEventListener("click", () => this.simulatePassengerBoard());
    }
    if (alightBtn) {
      alightBtn.addEventListener("click", () => this.simulatePassengerAlight());
    }
    if (resetSensorBtn) {
      resetSensorBtn.addEventListener("click", () => {
        if (this.currentBus) {
          this.currentBus.sensorInCount = 20;
          this.currentBus.sensorOutCount = 5;
          this.renderMetrics();
          if (window.showToast) window.showToast("Sensor counters calibrated to benchmark state.");
        }
      });
    }
  }
};
