/**
 * BUSMITRA - Live Map Tracking Module (Leaflet.js + OpenStreetMap)
 * Renders interactive routes, stop markers, polyline and smooth simulated bus animation.
 */

window.BUSMITRA_TRACKING = {
  map: null,
  busMarker: null,
  routePolyline: null,
  stopMarkers: [],
  animationInterval: null,
  currentCoordIndex: 0,
  waypoints: [],
  selectedBus: null,

  initMap: function(mapElementId, busId) {
    const el = document.getElementById(mapElementId);
    if (!el) return;

    // Check if Leaflet is loaded
    if (typeof L === 'undefined') {
      el.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:center;height:100%;color:#64748B;padding:2rem;text-align:center;">
          <div>
            <p style="font-weight:600;margin-bottom:0.5rem;">Interactive Map Loading...</p>
            <p style="font-size:0.875rem;">Initializing OpenStreetMap tiles and transit route geometry...</p>
          </div>
        </div>
      `;
      return;
    }

    const bus = window.getBusById(busId) || window.BUSMITRA_DATA.buses[0];
    this.selectedBus = bus;
    const route = window.BUSMITRA_DATA.routes[bus.routeId] || window.BUSMITRA_DATA.routes["vijayawada-guntur"];
    this.waypoints = route.waypoints;

    // Default center between Vijayawada and Guntur
    const centerLat = 16.42;
    const centerLng = 80.58;

    if (this.map) {
      this.map.remove();
      this.map = null;
    }

    this.map = L.map(mapElementId, {
      zoomControl: true,
      attributionControl: true
    }).setView([centerLat, centerLng], 11);

    // Add OpenStreetMap TileLayer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors | BusMitra Transit'
    }).addTo(this.map);

    // Draw route polyline
    this.routePolyline = L.polyline(this.waypoints, {
      color: '#1D4ED8',
      weight: 5,
      opacity: 0.85,
      dashArray: '8, 8',
      lineJoin: 'round'
    }).addTo(this.map);

    // Add Stop Markers
    this.stopMarkers = [];
    route.stops.forEach((stop, idx) => {
      const isStart = idx === 0;
      const isEnd = idx === route.stops.length - 1;
      const isCurrentStop = idx === bus.currentStopIndex;

      let markerBg = '#3B82F6';
      let labelText = `${stop.order}. ${stop.name}`;
      if (isStart) markerBg = '#10B981';
      if (isEnd) markerBg = '#EF4444';
      if (isCurrentStop) markerBg = '#06B6D4';

      const customStopIcon = L.divIcon({
        className: 'custom-stop-div-icon',
        html: `
          <div style="background:${markerBg}; width:16px; height:16px; border-radius:50%; border:3px solid #FFFFFF; box-shadow:0 2px 6px rgba(0,0,0,0.3); transform:translate(-8px,-8px);"></div>
        `,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
      });

      const marker = L.marker([stop.lat, stop.lng], { icon: customStopIcon })
        .addTo(this.map)
        .bindPopup(`
          <div style="font-family:inherit; min-width:180px;">
            <p style="font-weight:700; color:#0F172A; margin-bottom:4px;">${stop.name}</p>
            <p style="font-size:12px; color:#64748B; margin-bottom:2px;">Scheduled: ${stop.scheduledTime}</p>
            <p style="font-size:11px; color:#1D4ED8; font-weight:600;">${isStart ? 'Departure Terminal' : isEnd ? 'Destination Terminal' : isCurrentStop ? 'Next Approaching Stop' : 'En-route Stop'}</p>
          </div>
        `);
      this.stopMarkers.push(marker);
    });

    // Custom Bus Marker
    const initialCoord = this.waypoints[Math.min(bus.currentStopIndex * 2, this.waypoints.length - 1)];
    this.currentCoordIndex = Math.min(bus.currentStopIndex * 2, this.waypoints.length - 1);

    const busIcon = L.divIcon({
      className: 'bus-moving-marker',
      html: `
        <div class="bus-marker-icon" style="width:36px; height:36px; background:#1D4ED8; border:2.5px solid #FFFFFF; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 12px rgba(29,78,216,0.45); position:relative;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M8 6v6"/>
            <path d="M15 6v6"/>
            <path d="M2 12h19.6"/>
            <path d="M18 18h3s.5-1.7.8-2.8c.1-.4.2-.8.2-1.2 0-.4-.1-.8-.2-1.2l-1.4-5C20.1 6.6 19.1 6 18 6H4C2.9 6 1.9 6.6 1.6 7.8L.2 12.8c-.1.4-.2.8-.2 1.2 0 .4.1.8.2 1.2.3 1.1.8 2.8.8 2.8h3"/>
            <circle cx="7" cy="18" r="2"/>
            <path d="M9 18h5"/>
            <circle cx="16" cy="18" r="2"/>
          </svg>
        </div>
      `,
      iconSize: [36, 36],
      iconAnchor: [18, 18]
    });

    this.busMarker = L.marker(initialCoord, { icon: busIcon }).addTo(this.map);
    this.busMarker.bindPopup(`
      <div style="font-family:inherit;">
        <p style="font-weight:700; color:#1D4ED8; font-size:14px; margin-bottom:2px;">${bus.number} (${bus.name})</p>
        <p style="font-size:12px; color:#475569;">Route: ${bus.source} → ${bus.destination}</p>
        <p style="font-size:11px; color:#16A34A; font-weight:600; margin-top:4px;">SIMULATED LIVE TRACKING</p>
      </div>
    `);

    // Auto-fit bounds
    this.map.fitBounds(this.routePolyline.getBounds(), { padding: [30, 30] });

    // Start simulated movement along the path
    this.startSimulatedTracking();
  },

  startSimulatedTracking: function() {
    if (this.animationInterval) clearInterval(this.animationInterval);

    this.animationInterval = setInterval(() => {
      if (!this.busMarker || this.waypoints.length === 0) return;

      this.currentCoordIndex = (this.currentCoordIndex + 1) % this.waypoints.length;
      const nextPoint = this.waypoints[this.currentCoordIndex];
      this.busMarker.setLatLng(nextPoint);

      // Dynamically calculate approximate distance and ETA to next stop
      const progressRatio = this.currentCoordIndex / (this.waypoints.length - 1);
      const totalMinutes = 75;
      const remainingMin = Math.max(5, Math.round(totalMinutes * (1 - progressRatio)));

      const etaBadge = document.getElementById("tracking-live-eta");
      if (etaBadge) {
        etaBadge.textContent = `${remainingMin} mins`;
      }

      const speedBadge = document.getElementById("tracking-live-speed");
      if (speedBadge) {
        // Realistic fluctuated highway speed 48-58 km/h
        const simulatedSpeed = 48 + Math.floor(Math.sin(this.currentCoordIndex) * 8);
        speedBadge.textContent = `${simulatedSpeed} km/h`;
      }
    }, 2800);
  },

  resetView: function() {
    if (this.map && this.routePolyline) {
      this.map.fitBounds(this.routePolyline.getBounds(), { padding: [40, 40] });
    }
  },

  recenterOnBus: function() {
    if (this.map && this.busMarker) {
      this.map.setView(this.busMarker.getLatLng(), 14, { animate: true });
    }
  },

  destroy: function() {
    if (this.animationInterval) {
      clearInterval(this.animationInterval);
      this.animationInterval = null;
    }
  }
};
