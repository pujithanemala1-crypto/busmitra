/**
 * BUSMITRA - Geolocation & Reverse Geocoding Services
 * Handles GPS permission flow, coordinates retrieval, and address detection.
 */

window.BUSMITRA_LOCATION = {
  isLocating: false,

  /**
   * Request user's current GPS location and update the target input
   */
  detectCurrentLocation: function(targetInputId, statusContainerId) {
    const inputEl = document.getElementById(targetInputId);
    const statusEl = document.getElementById(statusContainerId);

    if (!navigator.geolocation) {
      this.showStatus(statusEl, "Geolocation is not supported by your browser. Please type your starting stop manually.", "error");
      return;
    }

    this.showStatus(statusEl, "Requesting GPS permission from your browser...", "loading");
    if (inputEl) inputEl.setAttribute("placeholder", "Detecting your GPS location...");

    const options = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 30000
    };

    navigator.geolocation.getCurrentPosition(
      // Success Callback
      async (position) => {
        const { latitude, longitude, accuracy } = position.coords;
        this.showStatus(statusEl, `GPS signal locked (Accuracy: ±${Math.round(accuracy)}m). Finding nearest bus station...`, "loading");

        try {
          // Reverse geocoding via OpenStreetMap Nominatim
          const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1`, {
            headers: { 'Accept-Language': 'en' }
          });

          if (!res.ok) throw new Error("Geocoding service unavailable");
          const data = await res.json();
          
          let placeName = "Vijayawada (Near Current Location)";
          if (data && data.display_name) {
            const addr = data.address;
            const suburb = addr.suburb || addr.neighbourhood || addr.road || addr.quarter;
            const city = addr.city || addr.town || addr.county || "Vijayawada";
            placeName = suburb ? `${suburb}, ${city}` : (data.name || city);
          }

          if (inputEl) {
            inputEl.value = placeName;
            inputEl.dispatchEvent(new Event('input'));
          }

          this.showStatus(statusEl, `Location detected: ${placeName}`, "success");
          
          if (window.showToast) {
            window.showToast(`Location set to: ${placeName}`);
          }
        } catch (err) {
          // Clean fallback if Nominatim rate-limited or offline
          const fallbackPlace = "Vijayawada (GPS Detected Location)";
          if (inputEl) {
            inputEl.value = fallbackPlace;
            inputEl.dispatchEvent(new Event('input'));
          }
          this.showStatus(statusEl, `Coordinates detected [${latitude.toFixed(4)}, ${longitude.toFixed(4)}]. Using ${fallbackPlace}.`, "success");
        }
      },
      // Error Callback
      (error) => {
        let msg = "Could not obtain location.";
        switch (error.code) {
          case error.PERMISSION_DENIED:
            msg = "Location permission denied. Please enter your departure stop manually.";
            break;
          case error.POSITION_UNAVAILABLE:
            msg = "Location information is currently unavailable. Please enter manually.";
            break;
          case error.TIMEOUT:
            msg = "Location request timed out. Please enter manually or try again.";
            break;
          default:
            msg = "An unexpected error occurred while obtaining GPS. Please enter manually.";
        }
        this.showStatus(statusEl, msg, "error");
        if (inputEl) {
          inputEl.setAttribute("placeholder", "Enter starting bus stop or landmark...");
        }
      },
      options
    );
  },

  showStatus: function(containerEl, message, type) {
    if (!containerEl) return;
    containerEl.className = `location-status-badge ${type}`;
    containerEl.innerHTML = `
      <span class="status-indicator-icon"></span>
      <span>${message}</span>
    `;
    containerEl.style.display = "flex";
  }
};
