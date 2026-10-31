/**
 * BUSMITRA - Backend API Client & WebSocket Gateway
 * Prepares integration with FastAPI REST endpoints & WebSocket streams
 * Gracefully defaults to high-fidelity simulated demo state when backend is disconnected.
 */

window.BUSMITRA_API = {
  // Configurable base URL for FastAPI
  BASE_URL: localStorage.getItem("busmitra_api_url") || "http://localhost:8000",
  mode: localStorage.getItem("busmitra_mode") || "demo", // 'demo' | 'live'
  socket: null,

  isDemoMode: function() {
    return this.mode === "demo";
  },

  setMode: function(newMode) {
    this.mode = newMode === "live" ? "live" : "demo";
    localStorage.setItem("busmitra_mode", this.mode);
    window.location.reload();
  },

  setBaseUrl: function(url) {
    this.BASE_URL = url.trim().replace(/\/$/, "");
    localStorage.setItem("busmitra_api_url", this.BASE_URL);
  },

  /**
   * GET /api/buses
   * Retrieves list of active buses with current passenger counts
   */
  async getBuses(source, destination) {
    if (this.isDemoMode()) {
      let buses = window.BUSMITRA_DATA.buses.map(b => window.getBusById(b.id));
      if (source && destination) {
        // filter or return relevant
        buses = buses.filter(b => 
          b.source.toLowerCase().includes(source.toLowerCase()) || 
          b.destination.toLowerCase().includes(destination.toLowerCase())
        );
      }
      return buses.length > 0 ? buses : window.BUSMITRA_DATA.buses.map(b => window.getBusById(b.id));
    }

    try {
      const url = new URL(`${this.BASE_URL}/api/buses`);
      if (source) url.searchParams.append("source", source);
      if (destination) url.searchParams.append("destination", destination);

      const res = await fetch(url.toString(), { signal: AbortSignal.timeout(4000) });
      if (!res.ok) throw new Error(`HTTP Error ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn("Backend unavailable, falling back to verified demo data", err);
      return window.BUSMITRA_DATA.buses.map(b => window.getBusById(b.id));
    }
  },

  /**
   * GET /api/buses/{busId}/location
   */
  async getBusLocation(busId) {
    if (this.isDemoMode()) {
      const bus = window.getBusById(busId);
      return {
        busId,
        lat: 16.4812,
        lng: 80.6053,
        currentLocationName: bus.currentLocationName,
        speedKmH: 52,
        lastUpdated: new Date().toISOString(),
        isSimulated: true
      };
    }

    try {
      const res = await fetch(`${this.BASE_URL}/api/buses/${busId}/location`, { signal: AbortSignal.timeout(4000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return { error: err.message, fallback: true };
    }
  },

  /**
   * GET /api/buses/{busId}/occupancy
   */
  async getBusOccupancy(busId) {
    if (this.isDemoMode()) {
      const bus = window.getBusById(busId);
      return {
        busId,
        capacity: bus.capacity,
        currentPassengers: bus.currentPassengers,
        availableSeats: bus.availableSeats,
        occupancyPercent: bus.occupancyPercent,
        sensorInCount: bus.sensorInCount,
        sensorOutCount: bus.sensorOutCount,
        crowdLevel: bus.crowdLevel,
        isSimulated: true
      };
    }

    try {
      const res = await fetch(`${this.BASE_URL}/api/buses/${busId}/occupancy`, { signal: AbortSignal.timeout(4000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return { error: err.message, fallback: true };
    }
  },

  /**
   * GET /api/buses/{busId}/crowd-prediction
   */
  async getCrowdPrediction(busId) {
    if (this.isDemoMode()) {
      const bus = window.getBusById(busId);
      return {
        busId,
        ...bus.prediction,
        isSimulated: true
      };
    }

    try {
      const res = await fetch(`${this.BASE_URL}/api/buses/${busId}/crowd-prediction`, { signal: AbortSignal.timeout(4000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return { error: err.message, fallback: true };
    }
  },

  /**
   * POST /api/buses/{busId}/passenger-count
   * Hardware bridge for ESP32 IR sensors to post counts
   */
  async postPassengerEvent(busId, eventType) {
    if (this.isDemoMode()) {
      return { success: true, simulated: true, event: eventType };
    }

    try {
      const res = await fetch(`${this.BASE_URL}/api/buses/${busId}/passenger-count`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ eventType, timestamp: new Date().toISOString() })
      });
      return await res.json();
    } catch (err) {
      return { success: false, error: err.message };
    }
  },

  /**
   * Connect WebSocket: /ws/buses/{busId}
   */
  connectWebSocket(busId, onMessageCallback) {
    if (this.isDemoMode()) {
      console.log(`[BusMitra WS] Demo Mode: WebSocket mock active for ${busId}`);
      return;
    }

    try {
      const wsUrl = this.BASE_URL.replace(/^http/, "ws") + `/ws/buses/${busId}`;
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log(`[BusMitra WS] Connected to live telematics for ${busId}`);
        if (window.showToast) window.showToast("Connected to live bus telematics feed.");
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (onMessageCallback) onMessageCallback(data);
        } catch (e) {
          console.error("WS Parse error", e);
        }
      };

      this.socket.onerror = (err) => {
        console.warn("[BusMitra WS] Connection error, operating in demo mode", err);
      };

      this.socket.onclose = () => {
        console.log("[BusMitra WS] Closed");
      };
    } catch (e) {
      console.warn("WebSocket init error", e);
    }
  }
};
